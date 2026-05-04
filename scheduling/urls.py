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
]