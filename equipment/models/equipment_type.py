# -*- coding: utf-8 -*-
"""
Created on Fri May  8 13:08:34 2026

@author: ianbrown
"""

from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from equipment.units import meters_to_inches, meters_to_feet
from django.core.exceptions import ValidationError


def _any_set(*values):
    return any(v is not None for v in values)


def _all_set(*values):
    return all(v is not None for v in values)


class EquipmentType(models.Model):
    """
    Represents an interchangeable type of equipment.
    Experiments depend on EquipmentType, not individual items.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(
        blank=True,
        help_text="Alternate names, synonyms, and search terms"
    )
    manufacturer = models.CharField(max_length=255, blank=True)
    model_number = models.CharField(max_length=255, blank=True)
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Broad category, e.g. Optics, Electronics, Mechanics"
    )

    # ---- Physical / storage constraints ----
    weight = models.DecimalField(
        max_digits=8, decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True, blank=True,)
    is_stackable = models.BooleanField(default=False)
    max_stack_height = models.PositiveIntegerField(null=True, blank=True)
    requires_heavy_duty_shelving = models.BooleanField(default=False)
    
    STORAGE_ORIENTATION_ANY = "any"
    STORAGE_ORIENTATION_FLAT = "flat"
    STORAGE_ORIENTATION_UPRIGHT = "upright"
    
    STORAGE_ORIENTATION_CHOICES = [
        (STORAGE_ORIENTATION_ANY, "Any"),
        (STORAGE_ORIENTATION_FLAT, "Flat"),
        (STORAGE_ORIENTATION_UPRIGHT, "Upright"),
    ]

    storage_orientation = models.CharField(
        max_length=20,
        choices=STORAGE_ORIENTATION_CHOICES,
        default=STORAGE_ORIENTATION_ANY
    )

    # ---- Environmental requirements ----
    requires_climate_control = models.BooleanField(default=False)
    requires_dark_storage = models.BooleanField(default=False)
    requires_secure_storage = models.BooleanField(default=False)

    hazard_class = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
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
    
    
    def has_storage_dimensions(self):
        return (
            self.storage_length_m is not None
            and self.storage_width_m is not None
            and self.storage_height_m is not None
        )

    has_storage_dimensions.boolean = True
    has_storage_dimensions.short_description = "Has Storage Dimensions"
    

    def clean(self):
        """
        Model-level validation to ensure internal physical consistency.

        This is called automatically by Django admin and ModelForms.
        """
        errors = {}

        # ------------------------------------------------------------
        # 1. Storage dimensions must be all-or-nothing
        # ------------------------------------------------------------
        length = self.storage_length_m
        width = self.storage_width_m
        height = self.storage_height_m

        if _any_set(length, width, height) and not _all_set(length, width, height):
            errors["storage_length_m"] = (
                "If any storage dimension is set, length, width, and height "
                "must all be provided."
            )
            errors["storage_width_m"] = errors["storage_length_m"]
            errors["storage_height_m"] = errors["storage_length_m"]

        # ------------------------------------------------------------
        # 2. Stackability constraints
        # ------------------------------------------------------------
        if not self.is_stackable:
            if self.max_stack_height not in (None, 1):
                errors["max_stack_height"] = (
                    "Max stack height must be empty or 1 for non-stackable equipment."
                )

        else:
            # is_stackable == True
            if self.max_stack_height is None:
                errors["max_stack_height"] = (
                    "Stackable equipment must define a maximum stack height."
                )
            elif self.max_stack_height < 2:
                errors["max_stack_height"] = (
                    "Max stack height must be 2 or greater for stackable equipment."
                )

        # ------------------------------------------------------------
        # 3. Physical sanity checks (defensive, not excessive)
        # ------------------------------------------------------------
        if self.weight is not None and self.weight <= Decimal("0"):
            errors["weight"] = "Weight must be a positive value."

        # ------------------------------------------------------------
        # Finalize
        # ------------------------------------------------------------
        if errors:
            raise ValidationError(errors)
            
    def __str__(self):
        if self.model_number:
            return f"{self.name} ({self.model_number})"
        return self.name