# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:34 2026

@author: ianbrown
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class StorageLocation(models.Model):
    """
    Represents a physical storage location.

    A location may represent:
    - A current storage location in the existing building
    - A temporary location used during a move
    - A planned future location in a new building
    """

    # ---- Location identity ----
    building = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Building identifier (if known)"
    )

    room = models.CharField(
        max_length=100,
        help_text="Room number or room identifier"
    )

    cabinet = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cabinet identifier (if applicable)"
    )

    shelf = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shelf or sub-location within cabinet"
    )

    # ---- Location classification ----
    LOCATION_CURRENT = "current"
    LOCATION_TEMPORARY = "temporary"
    LOCATION_FUTURE = "future"

    LOCATION_TYPE_CHOICES = [
        (LOCATION_CURRENT, "Current"),
        (LOCATION_TEMPORARY, "Temporary"),
        (LOCATION_FUTURE, "Future"),
    ]

    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default=LOCATION_CURRENT,
        help_text="Indicates whether this is a current, temporary, or future location"
    )

    is_final_location = models.BooleanField(
        default=False,
        help_text="True if this is the intended final storage location"
    )

    # ---- Capacity planning (optional but move-critical) ----
    floor_area_allocated = models.FloatField(
        null=True,
        blank=True,
        help_text="Square footage allocated to this location"
    )

    volume_capacity = models.FloatField(
        null=True,
        blank=True,
        help_text="Total volume capacity of this location"
    )

    weight_capacity = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum supported weight for this location"
    )

    # ---- Notes ----
    location_notes = models.TextField(
        blank=True,
        help_text="Freeform notes about this location"
    )

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    # --- Canonical metric capacity fields (meters) ---
    usable_length_m = models.DecimalField(
        "Usable Length (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
        help_text="Usable length of the lab space in meters"
    )

    usable_width_m = models.DecimalField(
        "Usable Width (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )

    usable_height_m = models.DecimalField(
        "Usable Height (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
        help_text="Clear usable height in meters"
    )
    
    @property
    def usable_floor_area_m2(self):
        if self.usable_length_m and self.usable_width_m:
            return self.usable_length_m * self.usable_width_m
        return None



    class Meta:
        ordering = ["building", "room", "cabinet", "shelf"]

    def __str__(self):
        parts = [self.building, self.room, self.cabinet, self.shelf]
        display = " / ".join([p for p in parts if p])
        return display
