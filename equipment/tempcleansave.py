# -*- coding: utf-8 -*-
"""
Created on Thu May  7 09:37:14 2026

@author: ianbrown
"""

    def clean(self):
        """
        Enforces consistency rules between tracking_level,
        quantity, and serial_number.
        """

        if self.tracking_level == self.TRACKING_BULK:
            if self.quantity < 1:
                raise ValidationError("Bulk items must have quantity ≥ 1.")
            if self.serial_number:
                raise ValidationError("Bulk items must not have serial numbers.")

        if self.tracking_level in (
            self.TRACKING_INDIVIDUAL_SERIALIZED,
            self.TRACKING_INDIVIDUAL_NON_SERIALIZED,
        ):
            if self.quantity != 1:
                raise ValidationError(
                    "Individually tracked items must have quantity = 1."
                )

        if self.tracking_level == self.TRACKING_INDIVIDUAL_SERIALIZED:
            if not self.serial_number:
                raise ValidationError(
                    "Serialized items must have a serial number."
                )

        if self.tracking_level == self.TRACKING_INDIVIDUAL_NON_SERIALIZED:
            if self.serial_number:
                raise ValidationError(
                    "Non-serialized items must not have a serial number."
                )

    def save(self, *args, **kwargs):
        """
        Automatically compute derived storage values before saving.
        """

        if self.storage_length is not None and self.storage_width is not None:
            self.storage_footprint_area = (
                self.storage_length * self.storage_width
            )
        else:
            self.storage_footprint_area = None

        if (
            self.storage_length is not None
            and self.storage_width is not None
            and self.storage_height is not None
        ):
            self.storage_volume = (
                self.storage_length *
                self.storage_width *
                self.storage_height
            )
        else:
            self.storage_volume = None

        super().save(*args, **kwargs)