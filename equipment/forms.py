# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:33:09 2026

@author: ianbrown
"""

from decimal import Decimal
from django import forms
from .models import EquipmentItem
from .units import to_meters

class EquipmentItemAdminForm(forms.ModelForm):
    DIMENSION_UNIT_CHOICES = (
        ("m", "Meters"),
        ("cm", "Centimeters"),
        ("in", "Inches"),
        ("ft", "Feet"),
    )

    dimension_unit = forms.ChoiceField(
        choices=DIMENSION_UNIT_CHOICES,
        initial="m",
        required=False,
        label="Dimension Units"
    )

    storage_length_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Storage Length",
    )
    storage_width_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Storage Width",
    )
    storage_height_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Storage Height",
    )

    class Meta:
        model = EquipmentItem
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        unit = cleaned.get("dimension_unit") or "m"

        # Convert entered values → meters
        cleaned["storage_length_m"] = to_meters(
            cleaned.get("storage_length_input"), unit
        )
        cleaned["storage_width_m"] = to_meters(
            cleaned.get("storage_width_input"), unit
        )
        cleaned["storage_height_m"] = to_meters(
            cleaned.get("storage_height_input"), unit
        )

        return cleaned