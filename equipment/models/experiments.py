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
    def storage_volume_m3(self) -> Decimal:
        """
        Total permanent storage volume required for this experiment,
        derived from its equipment and quantities.
        """
        total = Decimal("0")

        for link in self.equipment_links.select_related("equipment_item"):
            item = link.equipment_item
            if not item or item.storage_volume_m3 is None:
                continue

            qty = link.quantity_used or 1
            total += item.storage_volume_m3 * qty

        return total

    @property
    def storage_footprint_m2(self) -> Decimal:
        """
        Total permanent storage footprint (area) required for this experiment,
        derived from its equipment and quantities.
        """
        total = Decimal("0")

        for link in self.equipment_links.select_related("equipment_item"):
            item = link.equipment_item
            if not item or item.storage_footprint_m2 is None:
                continue

            qty = link.quantity_used or 1
            total += item.storage_footprint_m2 * qty

        return total

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

