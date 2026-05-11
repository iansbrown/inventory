# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 14:06:47 2026

@author: ianbrown
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from equipment.units import meters_to_inches, meters_to_feet
from equipment.models.equipment_type import EquipmentType

SQ_METER_TO_SQ_FOOT = Decimal("10.7639104167")

class EquipmentItem(models.Model):
    """
    Represents a single trackable inventory entity.

    An EquipmentItem may represent:
    - One serialized physical object
    - One non-serialized but individually tracked object
    - A bulk pool of interchangeable items
    """

    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="items",    
        null=True,
        blank=True,

    )

    # ---- Identification ----
    inventory_tag = models.CharField(
        max_length=50,
        unique=True,
        help_text="Barcode / human-readable inventory identifier"
    )


    serial_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Manufacturer serial number, if present"
    )

    asset_tag = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Institutional asset or property tag"
    )
    
    # ---- Relationships ----
    purchase_record = models.ForeignKey(
        "equipment.PurchaseRecord",
        on_delete=models.PROTECT,
        related_name="equipment_items",
        help_text="Purchase record associated with this item"
    )

    current_location = models.ForeignKey(
        "equipment.StorageLocation",
        on_delete=models.PROTECT,
        related_name="equipment_items",
        help_text="Current physical storage location"
    )

    # ---- Tracking semantics ----
    TRACKING_INDIVIDUAL_SERIALIZED = "individual_serialized"
    TRACKING_INDIVIDUAL_NON_SERIALIZED = "individual_non_serialized"
    TRACKING_BULK = "bulk"

    TRACKING_LEVEL_CHOICES = [
        (TRACKING_INDIVIDUAL_SERIALIZED, "Individual (Serialized)"),
        (TRACKING_INDIVIDUAL_NON_SERIALIZED, "Individual (Non-Serialized)"),
        (TRACKING_BULK, "Bulk"),
    ]

    tracking_level = models.CharField(
        max_length=40,
        choices=TRACKING_LEVEL_CHOICES,
        help_text="Defines how this item is tracked"
    )


    # ---- Usage and planning ----
    ACCESS_HIGH = "high"
    ACCESS_MEDIUM = "medium"
    ACCESS_LOW = "low"

    ACCESS_FREQUENCY_CHOICES = [
        (ACCESS_HIGH, "High"),
        (ACCESS_MEDIUM, "Medium"),
        (ACCESS_LOW, "Low"),
    ]

    access_frequency = models.CharField(
        max_length=10,
        choices=ACCESS_FREQUENCY_CHOICES,
        blank=True
    )

    STATUS_AVAILABLE = "available"
    STATUS_CHECKED_OUT = "checked_out"
    STATUS_UNDER_REPAIR = "under_repair"
    STATUS_SURPLUS = "surplus"
    STATUS_RETIRED = "retired"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_CHECKED_OUT, "Checked out"),
        (STATUS_UNDER_REPAIR, "Under repair"),
        (STATUS_SURPLUS, "Surplus"),
        (STATUS_RETIRED, "Retired"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE
    )

    handling_notes = models.TextField(
        blank=True,
        help_text="Special handling notes or legacy comments"
    )

    migration_flags = models.TextField(
        blank=True,
        help_text="Flags created during initial data migration"
    )

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


    # ------------------------------------------------------------------
    # Validation and derived-field logic
    # ------------------------------------------------------------------

    '''
    def has_storage_dimensions(self):
        return (
            self.storage_length_m is not None
            and self.storage_width_m is not None
            and self.storage_height_m is not None
        )

    has_storage_dimensions.boolean = True
    has_storage_dimensions.short_description = "Has Storage Dimensions"
    '''


    @property
    def storage_volume_m3(self):
        if not self.equipment_type:
            return None
        return self.equipment_type.storage_volume_m3

    

    @property
    def storage_footprint_m2(self):
        if not self.equipment_type:
            return None
        return self.equipment_type.storage_footprint_m2



    @property
    def storage_footprint_ft2(self):
        if self.storage_footprint_m2 is None:
            return None
        return self.storage_footprint_m2 * SQ_METER_TO_SQ_FOOT



    def __str__(self):
        if self.equipment_type:
            return f"{self.inventory_tag} — {self.equipment_type.name}"
        return self.inventory_tag

