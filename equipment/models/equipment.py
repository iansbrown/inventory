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


SQ_METER_TO_SQ_FOOT = Decimal("10.7639104167")

class EquipmentItem(models.Model):
    """
    Represents a single trackable inventory entity.

    An EquipmentItem may represent:
    - One serialized physical object
    - One non-serialized but individually tracked object
    - A bulk pool of interchangeable items
    """

    # ---- Identification ----
    inventory_tag = models.CharField(
        max_length=50,
        unique=True,
        help_text="Barcode / human-readable inventory identifier"
    )

    name = models.CharField(
        max_length=255,
        help_text="Canonical item name"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of the item"
    )

    keywords = models.TextField(
        blank=True,
        help_text="Alternate names, synonyms, and search terms"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Broad category, e.g. Optics, Electronics, Mechanics"
    )

    manufacturer = models.CharField(
        max_length=255,
        blank=True
    )

    model_number = models.CharField(
        max_length=255,
        blank=True
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

    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Number of items (only >1 for bulk items)"
    )

    
# --- Canonical metric dimensions (meters) ---
    storage_length_m = models.DecimalField(
        "Storage Length (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
        help_text="Internal storage length in meters"
    )

    storage_width_m = models.DecimalField(
        "Storage Width (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )

    storage_height_m = models.DecimalField(
        "Storage Height (m)",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )

    
    # ---- Storage geometry (authoritative) ----
    storage_length = models.FloatField(
        null=True,
        blank=True,
        help_text="Length of item in storage"
    )

    storage_width = models.FloatField(
        null=True,
        blank=True,
        help_text="Width of item in storage"
    )

    storage_height = models.FloatField(
        null=True,
        blank=True,
        help_text="Height of item in storage"
    )

    # ---- Derived geometry (system managed) ----
    storage_footprint_area = models.FloatField(
        null=True,
        blank=True,
        editable=False
    )

    storage_volume = models.FloatField(
        null=True,
        blank=True,
        editable=False
    )

    # ---- Setup geometry ----
    setup_length = models.FloatField(null=True, blank=True)
    setup_width = models.FloatField(null=True, blank=True)
    setup_height = models.FloatField(null=True, blank=True)

    # ---- Physical / storage constraints ----
    weight = models.FloatField(null=True, blank=True)

    is_stackable = models.BooleanField(default=False)

    max_stack_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of identical items that can be stacked"
    )

    STORAGE_ORIENTATION_ANY = "any"
    STORAGE_ORIENTATION_FLAT = "flat"
    STORAGE_ORIENTATION_UPRIGHT = "upright"

    STORAGE_ORIENTATION_CHOICES = [
        (STORAGE_ORIENTATION_ANY, "Any"),
        (STORAGE_ORIENTATION_FLAT, "Flat"),
        (STORAGE_ORIENTATION_UPRIGHT, "Upright"),
    ]

    storage_orientation = models.CharField(
        max_length=20,
        choices=STORAGE_ORIENTATION_CHOICES,
        default=STORAGE_ORIENTATION_ANY
    )

    requires_heavy_duty_shelving = models.BooleanField(default=False)

    # ---- Environmental requirements ----
    requires_climate_control = models.BooleanField(default=False)
    requires_dark_storage = models.BooleanField(default=False)
    requires_secure_storage = models.BooleanField(default=False)

    hazard_class = models.CharField(
        max_length=100,
        blank=True,
        null=True
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
    # Imperial dimension helpers (derived, read-only)
    # ------------------------------------------------------------------

    @property
    def storage_length_inches(self):
        if self.storage_length_m is None:
            return None
        return round(meters_to_inches(self.storage_length_m), 2)

    @property
    def storage_width_inches(self):
        if self.storage_width_m is None:
            return None
        return round(meters_to_inches(self.storage_width_m), 2)

    @property
    def storage_height_inches(self):
        if self.storage_height_m is None:
            return None
        return round(meters_to_inches(self.storage_height_m), 2)

    @property
    def storage_length_feet(self):
        if self.storage_length_m is None:
            return None
        return round(meters_to_feet(self.storage_length_m), 2)

    @property
    def storage_width_feet(self):
        if self.storage_width_m is None:
            return None
        return round(meters_to_feet(self.storage_width_m), 2)

    @property
    def storage_height_feet(self):
        if self.storage_height_m is None:
            return None
        return round(meters_to_feet(self.storage_height_m), 2)

    # ------------------------------------------------------------------
    # Validation and derived-field logic
    # ------------------------------------------------------------------

    
    @property
    def storage_volume_m3(self) -> Decimal | None:
        """
        Permanent storage volume required for ONE unit of this equipment item.
        Stored canonically in cubic meters (m³).
        """
        if (
            self.storage_length_m is None
            or self.storage_width_m is None
            or self.storage_height_m is None
        ):
            return None

        return (
            self.storage_length_m
            * self.storage_width_m
            * self.storage_height_m
        )


    @property
    def storage_footprint_m2(self) -> Decimal | None:
        """
        Permanent storage footprint (floor or shelf area)
        required for ONE unit of this item, in square meters (m²).
        """
        if self.storage_length_m is None or self.storage_width_m is None:
            return None

        return self.storage_length_m * self.storage_width_m


    @property
    def storage_footprint_ft2(self):
        if self.storage_footprint_m2 is None:
            return None
        return self.storage_footprint_m2 * SQ_METER_TO_SQ_FOOT



    def __str__(self):
        return f"{self.inventory_tag} — {self.name}"