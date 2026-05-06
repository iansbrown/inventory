# -*- coding: utf-8 -*-
"""
Created on Wed May  6 10:33:40 2026

@author: ianbrown
"""

from decimal import Decimal
from collections import defaultdict
from equipment.models import EquipmentExperiment


def experiment_storage_volume_m3(experiment) -> Decimal:
    """
    Returns the permanent storage volume (m³) required to support
    this experiment.

    Calculation:
    - Sum(storage volume of each equipment item × quantity required)
    - Each equipment item is counted once for this experiment
    """

    total_volume = Decimal("0")

    equipment_links = (
        EquipmentExperiment.objects
        .filter(experiment=experiment)
        .select_related("equipment_item")
    )

    for link in equipment_links:
        item = link.equipment_item
        if not item:
            continue

        volume_per_item = item.storage_volume_m3
        if volume_per_item is None:
            continue  # ignore items without defined storage dims

        quantity = link.quantity_used or 1
        total_volume += volume_per_item * quantity

    return total_volume

def experiment_storage_breakdown(experiment):
    """
    Returns a structured breakdown of storage contributors:
    [
        {
            "equipment": EquipmentItem,
            "quantity": int,
            "volume_per_item_m3": Decimal,
            "total_volume_m3": Decimal,
        },
        ...
    ]
    """
    breakdown = []

    equipment_links = (
        EquipmentExperiment.objects
        .filter(experiment=experiment)
        .select_related("equipment_item")
    )

    for link in equipment_links:
        item = link.equipment_item
        if not item or item.storage_volume_m3 is None:
            continue

        qty = link.quantity_used or 1
        breakdown.append({
            "equipment": item,
            "quantity": qty,
            "volume_per_item_m3": item.storage_volume_m3,
            "total_volume_m3": item.storage_volume_m3 * qty,
        })

    return breakdown


def course_storage_volume_m3(lab_offering) -> Decimal:
    """
    Returns the permanent storage volume (m³) required to support
    this lab course.

    Rules:
    - Equipment is deduplicated across experiments
    - Quantity used is the MAX required by any experiment
    - Time / schedule is irrelevant
    """

    # Track max quantity required per equipment item
    equipment_quantities: dict = defaultdict(int)

    experiments = (
        lab_offering.experiments
        .all()
        .prefetch_related("equipment_links__equipment_item")
    )

    for experiment in experiments:
        for link in experiment.equipment_links.all():
            item = link.equipment_item
            if not item:
                continue

            qty = link.quantity_used or 1
            equipment_quantities[item] = max(
                equipment_quantities[item],
                qty
            )

    # Calculate volume
    total_volume = Decimal("0")

    for item, qty in equipment_quantities.items():
        if item.storage_volume_m3 is None:
            continue

        total_volume += item.storage_volume_m3 * qty

    return total_volume

def course_storage_breakdown(lab_offering):
    """
    Returns a detailed breakdown of permanent storage contributors:
    [
        {
            "equipment": EquipmentItem,
            "max_quantity": int,
            "volume_per_item_m3": Decimal,
            "total_volume_m3": Decimal,
        },
        ...
    ]
    """

    from collections import defaultdict

    equipment_quantities = defaultdict(int)

    experiments = (
        lab_offering.experiments
        .all()
        .prefetch_related("equipment_links__equipment_item")
    )

    for experiment in experiments:
        for link in experiment.equipment_links.all():
            item = link.equipment_item
            if not item:
                continue

            qty = link.quantity_used or 1
            equipment_quantities[item] = max(
                equipment_quantities[item],
                qty
            )

    breakdown = []

    for item, qty in equipment_quantities.items():
        if item.storage_volume_m3 is None:
            continue

        breakdown.append({
            "equipment": item,
            "max_quantity": qty,
            "volume_per_item_m3": item.storage_volume_m3,
            "total_volume_m3": item.storage_volume_m3 * qty,
        })

    return breakdown

def course_equipment_requirements(lab_offering):
    """
    Returns a dict:
        { EquipmentItem: max_quantity_required_for_course }
    """

    equipment_quantities = defaultdict(int)

    experiments = (
        lab_offering.experiments
        .all()
        .prefetch_related("equipment_links__equipment_item")
    )

    for experiment in experiments:
        for link in experiment.equipment_links.all():
            item = link.equipment_item
            if not item:
                continue

            qty = link.quantity_used or 1
            equipment_quantities[item] = max(
                equipment_quantities[item],
                qty
            )

    return dict(equipment_quantities)

from decimal import Decimal


def shared_equipment_storage_between_courses(course_a, course_b):
    """
    Returns shared equipment storage between two courses.

    Output:
    {
        "total_storage_m3": Decimal,
        "equipment": [
            {
                "equipment": EquipmentItem,
                "quantity": int,
                "volume_per_item_m3": Decimal,
                "total_volume_m3": Decimal,
            },
            ...
        ]
    }
    """

    req_a = course_equipment_requirements(course_a)
    req_b = course_equipment_requirements(course_b)

    shared_items = set(req_a.keys()) & set(req_b.keys())

    total_volume = Decimal("0")
    breakdown = []

    for item in shared_items:
        if item.storage_volume_m3 is None:
            continue

        # Permanent storage needs max quantity across both courses
        qty = max(req_a[item], req_b[item])
        vol = item.storage_volume_m3 * qty

        total_volume += vol

        breakdown.append({
            "equipment": item,
            "quantity": qty,
            "volume_per_item_m3": item.storage_volume_m3,
            "total_volume_m3": vol,
        })

    return {
        "total_storage_m3": total_volume,
        "equipment": breakdown,
    }

def shared_equipment_storage_across_courses(lab_offerings):
    """
    Returns storage driven by equipment used by >=2 courses.

    lab_offerings: iterable of LabOffering

    Output:
    {
        "total_storage_m3": Decimal,
        "equipment": [
            {
                "equipment": EquipmentItem,
                "courses": [LabOffering, ...],
                "quantity": int,
                "total_volume_m3": Decimal,
            },
            ...
        ]
    }
    """

    from collections import defaultdict
    from decimal import Decimal

    equipment_usage = defaultdict(list)
    equipment_quantity_by_course = {}

    for course in lab_offerings:
        reqs = course_equipment_requirements(course)
        for item, qty in reqs.items():
            equipment_usage[item].append(course)
            equipment_quantity_by_course[(item, course)] = qty

    total_volume = Decimal("0")
    breakdown = []

    for item, courses in equipment_usage.items():
        if len(courses) < 2:
            continue  # only shared equipment

        if item.storage_volume_m3 is None:
            continue

        max_qty = max(
            equipment_quantity_by_course[(item, course)]
            for course in courses
        )

        vol = item.storage_volume_m3 * max_qty
        total_volume += vol

        breakdown.append({
            "equipment": item,
            "courses": courses,
            "quantity": max_qty,
            "total_volume_m3": vol,
        })

    return {
        "total_storage_m3": total_volume,
        "equipment": breakdown,
    }

def total_storage_for_courses(lab_offerings):
    """
    Calculates total permanent storage required for a selection of courses.

    Rules:
    - Equipment is deduplicated across all courses
    - Quantity is the MAX required by any course
    - Time / schedule is irrelevant

    Parameters:
        lab_offerings: iterable of LabOffering

    Returns:
        {
            "total_storage_m3": Decimal,
            "equipment": [
                {
                    "equipment": EquipmentItem,
                    "max_quantity": int,
                    "volume_per_item_m3": Decimal,
                    "total_volume_m3": Decimal,
                },
                ...
            ]
        }
    """

    # Track max quantity per equipment item across all courses
    equipment_quantities = defaultdict(int)

    for course in lab_offerings:
        course_requirements = course_equipment_requirements(course)

        for item, qty in course_requirements.items():
            equipment_quantities[item] = max(
                equipment_quantities[item],
                qty
            )

    total_volume = Decimal("0")
    breakdown = []

    for item, qty in equipment_quantities.items():
        if item.storage_volume_m3 is None:
            continue

        vol = item.storage_volume_m3 * qty
        total_volume += vol

        breakdown.append({
            "equipment": item,
            "max_quantity": qty,
            "volume_per_item_m3": item.storage_volume_m3,
            "total_volume_m3": vol,
        })

    return {
        "total_storage_m3": total_volume,
        "equipment": breakdown,
    }