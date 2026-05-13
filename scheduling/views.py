# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:50:40 2026

@author: ianbrown
"""


from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from scheduling.models import AcademicTerm, LabOffering
from equipment.models import Experiment
from scheduling.conflicts import detect_equipment_conflicts
from equipment.storage import total_storage_for_courses
from equipment.utils import equipment_list_for_experiment
from equipment.models import ExperimentEquipmentRequirement
from equipment.utils import build_equipment_type_map_for_experiments



def term_equipment_conflicts_view(request, term_id):
    term = get_object_or_404(AcademicTerm, id=term_id)

    conflict_data = []

    offerings = LabOffering.objects.filter(academic_term=term)

    for offering in offerings:
        weeks_with_conflicts = []

        for week in offering.schedule_weeks.prefetch_related("meetings__experiment"):

            meeting_conflicts = []

            # FIX: now checking EACH meeting independently
            for meeting in week.meetings.all():
                if not meeting.experiment:
                    continue

                equipment_type_map = build_equipment_type_map_for_experiments(
                    [meeting.experiment]
                )

                conflicts = detect_equipment_conflicts(equipment_type_map)

                if conflicts:
                    meeting_conflicts.append({
                        "meeting": meeting,
                        "conflicts": conflicts,
                    })

            if meeting_conflicts:
                weeks_with_conflicts.append({
                    "week": week,
                    "meetings": meeting_conflicts,
                })

        if weeks_with_conflicts:
            conflict_data.append({
                "offering": offering,
                "weeks": weeks_with_conflicts,
            })

    return render(
        request,
        "scheduling/term_equipment_conflicts.html",
        {
            "term": term,
            "conflict_data": conflict_data,
        },
    )


def experiment_equipment_view(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)

    equipment_list = []

    for req in experiment.equipment_requirements.select_related("equipment_type"):
        et = req.equipment_type

        # Skip invalid/missing data safely
        if not et:
            continue

        qty = req.quantity_required or 0
        vol_per = getattr(et, "storage_volume_m3", None)

        # Safe calculation
        if vol_per is not None:
            total = vol_per * qty
        else:
            total = None

        equipment_list.append({
            "equipment_type": et,
            "quantity_required": qty,
            "volume_per_item_m3": vol_per,
            "total_volume_m3": total,
        })

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


def equipment_by_week_view(request, course_code, term_id):
    lab_offering = get_object_or_404(
        LabOffering,
        lab_course__course_code=course_code,
        academic_term__id=term_id,
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
