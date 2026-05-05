# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:50:40 2026

@author: ianbrown
"""


from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from scheduling.models import LabOffering
from equipment.models import EquipmentExperiment
from scheduling.conflicts import detect_equipment_conflicts

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
        # This dict will accumulate equipment counts for ONE week
        equipment_map = defaultdict(int)
    
        # Loop over meetings in this week (1 for Spring/Fall, 2 for Summer)
        for meeting in week.meetings.all():
            experiment = meeting.experiment
    
            # Find all equipment used by this experiment
            equipment_links = EquipmentExperiment.objects.filter(
                experiment=experiment
            ).select_related("equipment_item")
    
            # Add the quantities needed
            for link in equipment_links:
                if link.equipment_item:
                    equipment_map[link.equipment_item] += link.quantity_used or 1
    
        # 👉 THIS is where conflict detection gets hooked in
        conflicts = detect_equipment_conflicts(equipment_map)
    
        # Store everything for this week
        equipment_per_week.append({
            "week": week,
            "equipment": dict(equipment_map),
            "conflicts": conflicts,
        })

