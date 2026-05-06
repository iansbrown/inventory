# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:34 2026

@author: ianbrown
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django import forms
from equipment.units import to_meters
from equipment.units import meters_to_inches, meters_to_feet

@property
def required_length_feet(self):
    if self.required_length_m is None:
        return None
    return round(meters_to_feet(self.required_length_m), 2)

@property
def required_length_inches(self):
    if self.required_length_m is None:
        return None
    return round(meters_to_inches(self.required_length_m), 2)

@property
def permanent_storage_m3(self):
    from equipment.storage import experiment_storage_volume_m3
    return experiment_storage_volume_m3(self)


class Experiment(models.Model):
    """
    Represents a lab experiment, course lab, or instructional activity
    that uses one or more pieces of equipment.
    """

    # ---- Identity ----
    course_code = models.CharField(
        max_length=255,
        unique=True,
        help_text="Course or lab identifier (e.g. PHY 215 Lab)"
    )

    experiment_title = models.CharField(
        max_length=255,
        help_text="Human-readable title of the experiment"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of the experiment and its purpose"
    )

    # ---- Space and move relevance ----
    preferred_lab_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Preferred lab type (optics, electronics, general, etc.)"
    )

    requires_fixed_installation = models.BooleanField(
        default=False,
        help_text="True if experiment requires permanent or semi-permanent installation"
    )

    move_sensitive = models.BooleanField(
        default=False,
        help_text="True if experiment is sensitive to move timing or disruption"
    )

    setup_space_required = models.FloatField(
        null=True,
        blank=True,
        help_text="Approximate floor area required when the experiment is set up"
    )

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    # --- Canonical metric dimensions (meters) ---
    required_length_m = models.DecimalField(
        "Required Length (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
        help_text="Minimum bench or floor length required, in meters"
    )

    required_width_m = models.DecimalField(
        "Required Width (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )

    required_height_m = models.DecimalField(
        "Required Height (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )


    class Meta:
        ordering = ["course_code"]

    def __str__(self):
        return f"{self.course_code} — {self.experiment_title}"


class EquipmentExperiment(models.Model):
    """
    Join table linking equipment to experiments.

    Allows many-to-many relationships between EquipmentItem and Experiment,
    with additional metadata about how the equipment is used.
    """

    equipment = models.ForeignKey(
        "equipment.EquipmentItem",
        on_delete=models.CASCADE,
        related_name="experiment_links"
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="equipment_links"
    )

    # ---- Usage details ----
    quantity_used = models.PositiveIntegerField(
        default=1,
        help_text="Number of units of this item used in the experiment"
    )

    is_core_to_experiment = models.BooleanField(
        null=True,
        help_text="True if this equipment is essential to the experiment"
    )

    temporary_substitution_allowed = models.BooleanField(
        null=True,
        help_text="Indicates whether a temporary substitute could be used"
    )

    # ---- Move and storage grouping ----
    storage_group_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Label for grouping related equipment during storage or moves"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes about usage or legacy information"
    )

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("equipment", "experiment")

    def __str__(self):
        return f"{self.equipment} → {self.experiment}"

