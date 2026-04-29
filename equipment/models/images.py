# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:34 2026

@author: ianbrown
"""

from django.db import models


class EquipmentImage(models.Model):
    """
    Stores images associated with a specific EquipmentItem.

    Images may document:
    - Current condition
    - Storage configuration
    - Setup configuration
    - Move-related condition (pre/post move)
    """

    # ---- Relationship ----
    equipment = models.ForeignKey(
        "equipment.EquipmentItem",
        on_delete=models.CASCADE,
        related_name="images"
    )

    # ---- Image data ----
    image = models.ImageField(
        upload_to="equipment_images/",
        help_text="Uploaded image file"
    )

    IMAGE_TYPE_CONDITION = "condition"
    IMAGE_TYPE_STORAGE = "storage"
    IMAGE_TYPE_SETUP = "setup"
    IMAGE_TYPE_MOVE = "move"
    IMAGE_TYPE_OTHER = "other"

    IMAGE_TYPE_CHOICES = [
        (IMAGE_TYPE_CONDITION, "Condition"),
        (IMAGE_TYPE_STORAGE, "Storage"),
        (IMAGE_TYPE_SETUP, "Setup"),
        (IMAGE_TYPE_MOVE, "Move-related"),
        (IMAGE_TYPE_OTHER, "Other"),
    ]

    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default=IMAGE_TYPE_OTHER,
        help_text="Category describing what the image represents"
    )

    caption = models.TextField(
        blank=True,
        help_text="Optional caption or description of the image"
    )

    date_taken = models.DateField(
        null=True,
        blank=True,
        help_text="Date the photo was taken (if known)"
    )

    # ---- Metadata ----
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.equipment} ({self.image_type})"