# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:33:09 2026

@author: ianbrown
"""

from decimal import Decimal
from django import forms
from equipment.units import meters_to_inches, meters_to_feet, to_meters
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
    usable_length_input = forms.DecimalField(
        label="Usable Length",
        required=False,
        min_value=Decimal("0"),
    )
    usable_width_input = forms.DecimalField(
        label="Usable Width",
        required=False,
        min_value=Decimal("0"),
    )
    usable_height_input = forms.DecimalField(
        label="Usable Height",
        required=False,
        min_value=Decimal("0"),
    )
    
    class Meta:
        model = StorageLocation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate inputs when editing existing object
        if self.instance and self.instance.pk:
            self.fields["usable_length_input"].initial = self.instance.usable_length_m
            self.fields["usable_width_input"].initial = self.instance.usable_width_m
            self.fields["usable_height_input"].initial = self.instance.usable_height_m

    def clean(self):
        cleaned = super().clean()

        # Only assign if user actually supplied a value
        for field_name, model_field in [
            ("usable_length_input", "usable_length_m"),
            ("usable_width_input", "usable_width_m"),
            ("usable_height_input", "usable_height_m"),
        ]:
            val = cleaned.get(field_name)
            if val is not None:
                setattr(self.instance, model_field, val)

        return cleaned


class ExperimentAdminForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = "__all__"

class EquipmentTypeAdminForm(forms.ModelForm):
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only populate on edit (instance already exists)
        if self.instance.pk:
            unit = self.initial.get("dimension_unit", "m")

            if self.instance.storage_length_m is not None:
                self.initial["storage_length_input"] = self._convert_from_meters(
                    self.instance.storage_length_m, unit
                )

            if self.instance.storage_width_m is not None:
                self.initial["storage_width_input"] = self._convert_from_meters(
                    self.instance.storage_width_m, unit
                )

            if self.instance.storage_height_m is not None:
                self.initial["storage_height_input"] = self._convert_from_meters(
                    self.instance.storage_height_m, unit
                )

    def _convert_from_meters(self, value, unit):
        if unit == "m":
            return value
        if unit == "cm":
            return value * Decimal("100")
        if unit == "in":
            return meters_to_inches(value)
        if unit == "ft":
            return meters_to_feet(value)
        return value

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
        
    def save(self, commit=True):
        instance = super().save(commit=False)
    
        if self.cleaned_data.get("storage_length_input") is not None:
            instance.storage_length_m = self.cleaned_data.get("storage_length_m")
    
        if self.cleaned_data.get("storage_width_input") is not None:
            instance.storage_width_m = self.cleaned_data.get("storage_width_m")
    
        if self.cleaned_data.get("storage_height_input") is not None:
            instance.storage_height_m = self.cleaned_data.get("storage_height_m")
    
        if commit:
            instance.save()
    
        return instance
    
class EquipmentItemAdminForm(forms.ModelForm):
    
    create_duplicates = forms.BooleanField(
        required=False,
        label="Create multiple identical items",
        help_text="Check this to create multiple identical copies of this item."
    )

    duplicate_count = forms.IntegerField(
        required=False,
        min_value=2,
        label="Total number of items",
        help_text="Total number of items to create (including this one)."
    )

    inventory_tag_prefix = forms.CharField(
        required=False,
        label="Inventory tag prefix",
        help_text="Prefix used to generate tags (e.g. PSU, CART)."
    )

    class Meta:
        model = EquipmentItem
        fields = "__all__"


    
