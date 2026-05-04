# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:19:09 2026

@author: ianbrown
"""

from django.conf import settings
from django.db import models


class LabOffering(models.Model):
    """
    Represents a specific offering of a lab course during an academic term.
    """

    lab_course = models.ForeignKey(
        "scheduling.LabCourse",
        on_delete=models.PROTECT,
        related_name="offerings"
    )

    academic_term = models.ForeignKey(
        "scheduling.AcademicTerm",
        on_delete=models.PROTECT,
        related_name="lab_offerings"
    )

    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coordinated_lab_offerings",
        help_text="Faculty coordinator for this lab course offering"
    )

    default_lab_room = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary lab room used for door postings and schedules"
    )

    notes = models.TextField(
        blank=True,
        help_text="Coordinator notes specific to this offering"
    )

    class Meta:
        unique_together = ("lab_course", "academic_term")
        ordering = ["academic_term", "lab_course"]

    def __str__(self):
        return f"{self.lab_course} — {self.academic_term}"