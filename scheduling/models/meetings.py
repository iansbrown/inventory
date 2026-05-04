# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:23:44 2026

@author: ianbrown
"""

from django.db import models


class WeekMeeting(models.Model):
    """
    Represents a single lab meeting within a ScheduleWeek.
    """

    schedule_week = models.ForeignKey(
        "scheduling.ScheduleWeek",
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    meeting_order = models.PositiveIntegerField(
        help_text="Order of the meeting within the week (1 = first, 2 = second)"
    )

    label = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional label (e.g. Mon, Wed, Meeting A)"
    )

    experiment = models.ForeignKey(
        "equipment.Experiment",
        on_delete=models.PROTECT,
        related_name="scheduled_meetings"
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional notes specific to this meeting"
    )

    class Meta:
        ordering = ["meeting_order"]
        unique_together = ("schedule_week", "meeting_order")

    def __str__(self):
        label = self.label or f"Meeting {self.meeting_order}"
        return f"{self.schedule_week} — {label}"