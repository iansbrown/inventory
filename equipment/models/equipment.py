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
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.html import format_html

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
        blank=True,   #  allow empty in forms
        null=True,    # allow empty in DB
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

    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of physical units represented by this item (bulk only)",
    )

    
    qr_code_image = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True,
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

    def generate_qr_code(self):
        """
        Generates a QR code pointing to the admin change page for this item.
        """
        if not self.pk:
            return None
    
        url = reverse(
            "admin:equipment_equipmentitem_change",
            args=[self.pk],
        )
    
        # IMPORTANT: add full domain
        full_url = f"https://inventory-aekg.onrender.com{url}"
    
        qr = qrcode.make(full_url)
    
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
    
        file_name = f"qr_equipment_{self.pk}.png"
    
        return ContentFile(buffer.getvalue(), name=file_name)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        # Generate QR if not already present
        if not self.qr_code_image:
            qr_file = self.generate_qr_code()
            if qr_file:
                self.qr_code_image.save(qr_file.name, qr_file, save=False)
    
        super().save(update_fields=["qr_code_image"])
    
    def clean(self):
        if self.tracking_level == "bulk":
            if self.quantity is None or self.quantity <= 0:
                raise ValidationError({
                    "quantity": "Bulk items must have a positive quantity."
                })
        else:
            # Individual items should not carry a quantity
            self.quantity = None



    def __str__(self):
        parts = []
    
        if self.equipment_type:
            parts.append(self.equipment_type.name)
    
        if self.inventory_tag:
            parts.append(f"[{self.inventory_tag}]")
    
        if self.serial_number:
            parts.append(f"(SN: {self.serial_number})")
    
        return " ".join(parts)
    
