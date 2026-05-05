# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:33:09 2026

@author: ianbrown
"""

from decimal import Decimal
from django import forms
from django import forms
from equipment.units import to_meters
from .models import (
    EquipmentItem,
    PurchaseRecord,
    StorageLocation,
    RepairLog,
    EquipmentImage,
    Experiment,
    EquipmentExperiment,
)



class StorageLocationAdminForm(forms.ModelForm):
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
        label="Capacity Units"
    )

    usable_length_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Usable Length",
    )

    usable_width_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Usable Width",
    )

    usable_height_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Usable Height",
    )

    class Meta:
        model = StorageLocation
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        unit = cleaned.get("dimension_unit") or "m"

        cleaned["usable_length_m"] = to_meters(
            cleaned.get("usable_length_input"), unit
        )
        cleaned["usable_width_m"] = to_meters(
            cleaned.get("usable_width_input"), unit
        )
        cleaned["usable_height_m"] = to_meters(
            cleaned.get("usable_height_input"), unit
        )

        return cleaned



class ExperimentAdminForm(forms.ModelForm):
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

    required_length_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Required Length",
    )

    required_width_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Required Width",
    )

    required_height_input = forms.DecimalField(
        required=False,
        min_value=0,
        label="Required Height",
    )

    class Meta:
        model = Experiment
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        unit = cleaned.get("dimension_unit") or "m"

        cleaned["required_length_m"] = to_meters(
            cleaned.get("required_length_input"), unit
        )
        cleaned["required_width_m"] = to_meters(
            cleaned.get("required_width_input"), unit
        )
        cleaned["required_height_m"] = to_meters(
            cleaned.get("required_height_input"), unit
        )

        return cleaned
    
    
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
    
