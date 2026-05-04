# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:11:05 2026

@author: ianbrown
"""

from django.db import models


class AcademicTerm(models.Model):
    """
    Represents an academic term such as Fall 2026, Spring 2027, or Summer 2026.
    """

    TERM_FALL = "fall"
    TERM_SPRING = "spring"
    TERM_SUMMER = "summer"

    TERM_TYPE_CHOICES = [
        (TERM_FALL, "Fall"),
        (TERM_SPRING, "Spring"),
        (TERM_SUMMER, "Summer"),
    ]

    name = models.CharField(
        max_length=50,
        help_text="Human-readable term name (e.g. Fall 2026)"
    )

    term_type = models.CharField(
        max_length=10,
        choices=TERM_TYPE_CHOICES,
        help_text="Determines scheduling assumptions (weekly vs condensed)"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    notes = models.TextField(
        blank=True,
        help_text="Optional notes about calendar irregularities"
    )

    class Meta:
        ordering = ["start_date"]
        unique_together = ("name", "term_type")

    def __str__(self):
        return self.name