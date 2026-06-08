# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:09:13 2026

@author: ianbrown
"""

# experiments/urls.py (or project-level urls.py)

from scheduling.views import experiment_equipment_view
from django.urls import path
from . import views, api


urlpatterns = [
    path(
        "api/equipment/<int:equipment_id>/capture-image/",
        api.capture_image,
        name="capture_image",
    ),
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
    
    path(
        "repairs/",
        views.repair_dashboard_view,
        name="repair_dashboard",
    ),
    
    path(
        "requests/",
        views.request_dashboard_view,
        name="request_dashboard",
    ),
    
    path(
        "experiments/",
        views.experiment_dashboard_view,
        name="experiment_dashboard",
    ),
    
    path(
        "scheduling/",
        views.scheduling_dashboard_view,
        name="scheduling_dashboard",
    ),


]