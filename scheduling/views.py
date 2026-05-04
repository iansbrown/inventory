# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:50:40 2026

@author: ianbrown
"""

from django.shortcuts import get_object_or_404, render
from .models import LabOffering


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