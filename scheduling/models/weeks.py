# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:22:35 2026

@author: ianbrown
"""

from django.db import models


class ScheduleWeek(models.Model):
    """
    Represents an instructional week within a lab offering.
    """

    lab_offering = models.ForeignKey(
        "scheduling.LabOffering",
        on_delete=models.CASCADE,
        related_name="schedule_weeks"
    )

    week_number = models.PositiveIntegerField(
        help_text="Instructional week number (e.g. Week 1, Week 2)"
    )

    week_start_date = models.DateField(
        help_text="Date of the Monday for this instructional week"
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional notes (holiday adjustments, skipped content, etc.)"
    )

    class Meta:
        ordering = ["week_number"]
        unique_together = ("lab_offering", "week_number")

    def __str__(self):
        return f"{self.lab_offering} — Week {self.week_number}"
