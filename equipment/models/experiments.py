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



class Experiment(models.Model):
    """
    A lab experiment.

    Experiments do NOT have intrinsic storage dimensions.
    All storage footprint and volume are derived from required equipment.
    """

    # ------------------------------------------------------------------
    # Identity & Metadata
    # ------------------------------------------------------------------

    course_code = models.CharField(
        max_length=50,
        help_text="Course code this experiment is typically associated with"
    )

    experiment_title = models.CharField(
        max_length=255,
        help_text="Human-readable experiment title"
    )

    preferred_lab_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Preferred lab environment (e.g. optics, electronics)"
    )

    requires_fixed_installation = models.BooleanField(
        default=False,
        help_text="Experiment requires fixed lab infrastructure"
    )

    move_sensitive = models.BooleanField(
        default=False,
        help_text="Experiment equipment is sensitive to movement"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Derived Storage Properties (equipment-driven)
    # ------------------------------------------------------------------


    @property
    def storage_volume_m3(self):
        try:
            requirements = self.equipment_requirements.select_related("equipment_type")
        except Exception:
            return None
    
        total = Decimal("0")
        used = False
    
        for req in requirements:
            if not req.equipment_type:
                continue
            vol = req.equipment_type.storage_volume_m3
            if vol is None:
                continue
            total += vol * req.quantity_required
            used = True
    
        return total if used else None
    
    
    @property
    def storage_footprint_m2(self):
        try:
            requirements = self.equipment_requirements.select_related("equipment_type")
        except Exception:
            return None
    
        total = Decimal("0")
        used = False
    
        for req in requirements:
            if not req.equipment_type:
                continue
            area = req.equipment_type.storage_footprint_m2
            if area is None:
                continue
            total += area * req.quantity_required
            used = True
    
        return total if used else None


    # Optional helper
    def has_storage_dimensions(self):
        return any(
            req.equipment_type and req.equipment_type.has_storage_dimensions()
            for req in self.equipment_requirements.all()
        )

    has_storage_dimensions.boolean = True
    has_storage_dimensions.short_description = "Has Storage Data"

    def __str__(self):
        return f"{self.course_code} — {self.experiment_title}"

    class Meta:
        ordering = ["course_code"]


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

class ExperimentEquipmentRequirement(models.Model):
    """
    Defines how many units of an equipment type
    an experiment requires.
    """

    experiment = models.ForeignKey(
        "Experiment",
        on_delete=models.CASCADE,
        related_name="equipment_requirements",
    )

    equipment_type = models.ForeignKey(
        "equipment.EquipmentType",
        on_delete=models.PROTECT,
    )

    quantity_required = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("experiment", "equipment_type")
