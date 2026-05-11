# -*- coding: utf-8 -*-
"""
Created on Thu May  7 16:19:41 2026

@author: ianbrown
"""


def equipment_list_for_experiment(experiment):
    """
    Returns a list of equipment required for an experiment,
    including quantity and storage metadata.
    """
    return [
        {
            "equipment": link.equipment,
            "quantity": link.quantity_used or 1,
            "storage_volume_m3": link.equipment.storage_volume_m3,
            "storage_footprint_m2": link.equipment.storage_footprint_m2,
        }
        for link in experiment.equipment_links.select_related("equipment")
    ]

def available_count(equipment_type):
    """
    Return the number of usable (available) instances of an equipment type.
    """
    return equipment_type.items.filter(
        status="available"
    ).count()

def can_schedule_experiment(experiment):
    """
    Returns True if all equipment requirements
    for an experiment can be met.

    This function must NEVER raise.
    """
    # If there are no requirements, we treat this as unschedulable
    # (safer default than True).
    requirements = experiment.equipment_requirements.select_related(
        "equipment_type"
    )

    if not requirements.exists():
        return False

    for req in requirements:
        # Missing equipment type ⇒ cannot schedule
        if not req.equipment_type:
            return False

        # Quantity must be valid and positive
        if not req.quantity_required or req.quantity_required <= 0:
            return False

        try:
            available = available_count(req.equipment_type)
        except Exception:
            # Any error counting availability ⇒ cannot schedule
            return False

        if available < req.quantity_required:
            return False

    return True