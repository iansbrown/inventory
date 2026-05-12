# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:50:40 2026

@author: ianbrown
"""


from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from scheduling.models import LabOffering
from equipment.models import Experiment
from scheduling.conflicts import detect_equipment_conflicts
from equipment.storage import total_storage_for_courses
from equipment.utils import equipment_list_for_experiment
from equipment.models import ExperimentEquipmentRequirement



def build_equipment_type_map_for_experiments(experiments):
    """
    Returns {EquipmentType: total_required_quantity}
    """
    equipment_type_map = defaultdict(int)

    for experiment in experiments:
        if not experiment:
            continue
        for req in experiment.equipment_requirements.select_related(
            "equipment_type"
        ):
            if req.equipment_type:
                equipment_type_map[req.equipment_type] += req.quantity_required

    return equipment_type_map


def experiment_equipment_view(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)

    requirements = experiment.equipment_requirements.select_related(
        "equipment_type"
    )

    equipment_list = [
        {
            "equipment_type": req.equipment_type,
            "quantity_required": req.quantity_required,
        }
        for req in requirements
        if req.equipment_type
    ]

    return render(
        request,
        "equipment/equipment_list.html",
        {
            "experiment": experiment,
            "equipment_list": equipment_list,
        },
    )


def storage_planning_view(request):
    offerings = LabOffering.objects.select_related(
        "lab_course", "academic_term"
    ).order_by(
        "academic_term__name",
        "lab_course__course_code",
    )

    selected_ids = request.GET.getlist("offerings")

    selected_offerings = LabOffering.objects.filter(
        id__in=selected_ids
    ) if selected_ids else []

    result = None
    if selected_offerings:
        result = total_storage_for_courses(selected_offerings)

    context = {
        "offerings": offerings,
        "selected_ids": [int(i) for i in selected_ids],
        "result": result,
    }

    return render(
        request,
        "scheduling/storage_planning.html",
        context,
    )

def lab_schedule_view(request, course_code, term_name):
    lab_offering = get_object_or_404(
        LabOffering,
        lab_course__course_code=course_code,
        academic_term__name=term_name,
    )

    schedule_weeks = (
        lab_offering.schedule_weeks
        .prefetch_related("meetings__experiment")
        .order_by("week_number")
    )

    context = {
        "lab_offering": lab_offering,
        "schedule_weeks": schedule_weeks,
    }

    return render(
        request,
        "scheduling/lab_schedule.html",
        context,
    )


def lab_schedule_door_view(request, course_code, term_name):
    lab_offering = get_object_or_404(
        LabOffering,
        lab_course__course_code=course_code,
        academic_term__name=term_name,
    )

    schedule_weeks = (
        lab_offering.schedule_weeks
        .prefetch_related("meetings__experiment")
        .order_by("week_number")
    )

    context = {
        "lab_offering": lab_offering,
        "schedule_weeks": schedule_weeks,
    }

    return render(
        request,
        "scheduling/lab_schedule_door.html",
        context,
    )


def equipment_by_week_view(request, course_code, term_name):
    lab_offering = get_object_or_404(
        LabOffering,
        lab_course__course_code=course_code,
        academic_term__name=term_name,
    )

    schedule_weeks = (
        lab_offering.schedule_weeks
        .prefetch_related("meetings__experiment")
        .order_by("week_number")
    )

    equipment_per_week = []

    for week in schedule_weeks:
        experiments = [
            m.experiment for m in week.meetings.all() if m.experiment
        ]

        equipment_type_map = build_equipment_type_map_for_experiments(
            experiments
        )

        conflicts = detect_equipment_conflicts(equipment_type_map)

        equipment_per_week.append({
            "week": week,
            "equipment": equipment_type_map,
            "conflicts": conflicts,
        })

    return render(
        request,
        "scheduling/equipment_by_week.html",
        {
            "lab_offering": lab_offering,
            "equipment_per_week": equipment_per_week,
        },
    )
