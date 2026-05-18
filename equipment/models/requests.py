# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:32:39 2026

@author: ianbrown
"""

from django.conf import settings
from django.db import models

class EquipmentRequest(models.Model):

    REQUEST_TYPE_EQUIPMENT = "equipment"
    REQUEST_TYPE_EXPERIMENT = "experiment"

    REQUEST_TYPE_CHOICES = [
        (REQUEST_TYPE_EQUIPMENT, "Equipment"),
        (REQUEST_TYPE_EXPERIMENT, "Experiment/Demo"),
    ]

    # ---- Request Type ----
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES
    )

    equipment_type = models.ForeignKey(
        "equipment.EquipmentType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    experiment = models.ForeignKey(
        "equipment.Experiment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # ---- Request Details ----
    quantity = models.PositiveIntegerField(default=1)

    location = models.CharField(
        max_length=255,
        help_text="Where the equipment should be delivered"
    )

    requires_setup = models.BooleanField(default=False)

    # ---- Scheduling ----
    start_datetime = models.DateTimeField()
    duration_hours = models.PositiveIntegerField()

    # ---- Request Metadata ----
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DENIED = "denied"
    STATUS_FULFILLED = "fulfilled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DENIED, "Denied"),
        (STATUS_FULFILLED, "Fulfilled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_type} request by {self.requested_by}"