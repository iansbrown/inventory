# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:09:13 2026

@author: ianbrown
"""

# experiments/urls.py (or project-level urls.py)

from scheduling.views import experiment_equipment_view
from django.urls import path



urlpatterns = [
    path(
        "experiments/<int:experiment_id>/equipment/",
        experiment_equipment_view,
        name="experiment_equipment",
    ),
]