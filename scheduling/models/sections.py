# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:27:21 2026

@author: ianbrown
"""

from django.conf import settings
from django.db import models


class LabSection(models.Model):
    """
    Represents an individual lab section within a lab offering.
    """

    lab_offering = models.ForeignKey(
        "scheduling.LabOffering",
        on_delete=models.CASCADE,
        related_name="sections"
    )

    section_code = models.CharField(
        max_length=10,
        help_text="Section identifier (e.g. L01, L02, A1)"
    )

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lab_sections",
        help_text="Graduate TA or instructor leading this section"
    )

    meeting_day = models.CharField(
        max_length=20,
        blank=True,
        help_text="Day of the week this section meets (for reference only)"
    )

    meeting_time = models.CharField(
        max_length=20,
        blank=True,
        help_text="Meeting time (for reference only)"
    )

    room = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lab room where this section meets"
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional notes specific to this section"
    )

    class Meta:
        ordering = ["section_code"]
        unique_together = ("lab_offering", "section_code")

    def __str__(self):
        return f"{self.lab_offering} — Section {self.section_code}"