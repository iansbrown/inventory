# -*- coding: utf-8 -*-
"""
Created on Fri May  8 13:08:34 2026

@author: ianbrown
"""

from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from equipment.units import meters_to_inches, meters_to_feet

class EquipmentType(models.Model):
    """
    Represents an interchangeable type of equipment.
    Experiments depend on EquipmentType, not individual items.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    manufacturer = models.CharField(max_length=255, blank=True)
    model_number = models.CharField(max_length=255, blank=True)

    # Canonical storage geometry (meters)
    storage_length_m = models.DecimalField(
        max_digits=8, decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True, blank=True
    )
    storage_width_m = models.DecimalField(
        max_digits=8, decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True, blank=True
    )
    storage_height_m = models.DecimalField(
        max_digits=8, decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Imperial dimension helpers (derived, read-only)
    # ------------------------------------------------------------------

    @property
    def storage_length_inches(self):
        if self.storage_length_m is None:
            return None
        return round(meters_to_inches(self.storage_length_m), 2)

    @property
    def storage_width_inches(self):
        if self.storage_width_m is None:
            return None
        return round(meters_to_inches(self.storage_width_m), 2)

    @property
    def storage_height_inches(self):
        if self.storage_height_m is None:
            return None
        return round(meters_to_inches(self.storage_height_m), 2)

    @property
    def storage_length_feet(self):
        if self.storage_length_m is None:
            return None
        return round(meters_to_feet(self.storage_length_m), 2)

    @property
    def storage_width_feet(self):
        if self.storage_width_m is None:
            return None
        return round(meters_to_feet(self.storage_width_m), 2)

    @property
    def storage_height_feet(self):
        if self.storage_height_m is None:
            return None
        return round(meters_to_feet(self.storage_height_m), 2)

    # --- Derived storage ---
    @property
    def storage_volume_m3(self):
        if (
            self.storage_length_m is None
            or self.storage_width_m is None
            or self.storage_height_m is None
        ):
            return None
        return (
            self.storage_length_m
            * self.storage_width_m
            * self.storage_height_m
        )

    @property
    def storage_footprint_m2(self):
        if self.storage_length_m is None or self.storage_width_m is None:
            return None
        return self.storage_length_m * self.storage_width_m

    def __str__(self):
        if self.model_number:
            return f"{self.name} ({self.model_number})"
        return self.name