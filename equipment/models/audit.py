# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:49 2026

@author: ianbrown
"""

from django.db import models


class ChangeLog(models.Model):
    """
    Records changes made to EquipmentItem records.

    This model provides a complete audit trail of who changed what,
    when it was changed, and why.
    """

    # ---- Relationship ----
    equipment = models.ForeignKey(
        "equipment.EquipmentItem",
        on_delete=models.CASCADE,
        related_name="change_logs"
    )

    # ---- Change details ----
    field_name = models.CharField(
        max_length=100,
        help_text="Name of the field that was changed"
    )

    old_value = models.TextField(
        blank=True,
        help_text="Previous value of the field"
    )

    new_value = models.TextField(
        blank=True,
        help_text="New value of the field"
    )

    # ---- Accountability ----
    changed_by = models.CharField(
        max_length=255,
        help_text="User or system that made the change"
    )

    change_reason = models.CharField(
        max_length=50,
        help_text="Reason for the change (migration, review, move, correction, etc.)"
    )

    related_move_phase = models.CharField(
        max_length=50,
        blank=True,
        help_text="Pre-move, in-transit, or post-move (if applicable)"
    )

    # ---- Metadata ----
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return (
            f"{self.equipment} | {self.field_name} "
            f"changed at {self.timestamp}"
        )