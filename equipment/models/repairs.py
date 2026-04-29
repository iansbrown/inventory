# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:49 2026

@author: ianbrown
"""

from django.db import models


class RepairLog(models.Model):
    """
    Records repair, maintenance, or damage events for an EquipmentItem.

    Repair logs are append-only and provide a chronological history
    of issues, repairs, and outcomes.
    """

    # ---- Relationship ----
    equipment = models.ForeignKey(
        "equipment.EquipmentItem",
        on_delete=models.CASCADE,
        related_name="repair_logs"
    )

    # ---- Repair details ----
    date_reported = models.DateField(
        help_text="Date the issue was reported or observed"
    )

    issue_description = models.TextField(
        help_text="Description of the problem or damage"
    )

    repair_action = models.TextField(
        blank=True,
        help_text="Description of repair action taken"
    )

    performed_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="Person or service that performed the repair"
    )

    # ---- Cost and outcome ----
    repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost of repair (if applicable)"
    )

    outcome = models.TextField(
        blank=True,
        help_text="Outcome of the repair (successful, temporary fix, not repairable, etc.)"
    )

    # ---- Move-related flags ----
    move_related = models.BooleanField(
        default=False,
        help_text="True if the issue was caused by or discovered during a move"
    )

    pre_move_condition_documented = models.BooleanField(
        default=False,
        help_text="True if condition was documented prior to the move"
    )

    post_move_condition_documented = models.BooleanField(
        default=False,
        help_text="True if condition was documented after the move"
    )

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_reported", "-created_at"]

    def __str__(self):
        return f"Repair on {self.equipment} ({self.date_reported})"
