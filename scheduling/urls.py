# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:44:57 2026

@author: ianbrown
"""

from django.urls import path
from . import views

urlpatterns = [
    path(
        "<str:course_code>/<str:term_name>/",
        views.lab_schedule_view,
        name="lab_schedule",
    ),
    path(
        "<str:course_code>/<str:term_name>/door/",
        views.lab_schedule_door_view,
        name="lab_schedule_door",
    ),
    
    path(
        "academic-term/<int:term_id>/equipment-conflicts/",
        views.term_equipment_conflicts_view,
        name="term_equipment_conflicts",
    ),

    path(
        "<int:course_id>/<int:term_id>/equipment/",
        views.equipment_by_week_view,
        name="equipment_by_week",
    ),    
    path(
        "storage/planning/",
        views.storage_planning_view,
        name="storage_planning",
),

]
