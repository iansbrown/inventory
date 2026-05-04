# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:18:38 2026

@author: ianbrown
"""

from django.db import models


class LabCourse(models.Model):
    """
    Represents a lab course independent of any specific academic term.
    """

    course_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Course code (e.g. PHYS 215)"
    )

    course_title = models.CharField(
        max_length=255,
        help_text="Official course title"
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the lab course"
    )

    class Meta:
        ordering = ["course_code"]

    def __str__(self):
        return f"{self.course_code} — {self.course_title}"