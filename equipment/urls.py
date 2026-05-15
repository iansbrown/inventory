# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:09:13 2026

@author: ianbrown
"""

# experiments/urls.py (or project-level urls.py)

from scheduling.views import experiment_equipment_view
from django.urls import path
from . import views


urlpatterns = [
    path(
        "experiment/<int:experiment_id>/equipment/",
        experiment_equipment_view,
        name="experiment_equipment",
    ),
    
    path(
        "purchasing/",
        views.purchasing_dashboard_view,
        name="purchasing_dashboard",
    ),

]