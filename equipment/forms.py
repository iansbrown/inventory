# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:33:09 2026

@author: ianbrown
"""

from decimal import Decimal
from django import forms
from equipment.utils import DimensionInputMixin
from django.utils import timezone
from equipment.units import meters_to_inches, meters_to_feet, to_meters
from .models import (
    EquipmentItem,
    PurchaseRecord,
    StorageLocation,
    RepairLog,
    EquipmentImage,
    Experiment,
    EquipmentExperiment,
    EquipmentType
)



# Simple form for repair requests
class RepairLogForm(forms.ModelForm):
    class Meta:
        model = RepairLog
        fields = [
            "equipment",
            "issue_description",
            "date_reported",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_reported"].initial = timezone.now().date()
    
class StorageLocationAdminForm(DimensionInputMixin, forms.ModelForm):
    usable_length_input = forms.DecimalField(required=False, min_value=0)
    usable_width_input = forms.DecimalField(required=False, min_value=0)
    usable_height_input = forms.DecimalField(required=False, min_value=0)

    class Meta:
        model = StorageLocation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["usable_length_input"].initial = self.instance.usable_length_m
            self.fields["usable_width_input"].initial = self.instance.usable_width_m
            self.fields["usable_height_input"].initial = self.instance.usable_height_m

    def clean(self):
        cleaned = super().clean()

        self.apply_dimension_inputs(
            self.instance,
            {
                "usable_length_input": "usable_length_m",
                "usable_width_input": "usable_width_m",
                "usable_height_input": "usable_height_m",
            }
        )

        return cleaned



class ExperimentAdminForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = "__all__"



class EquipmentTypeAdminForm(DimensionInputMixin, forms.ModelForm):
    storage_length_input = forms.DecimalField(required=False, min_value=0)
    storage_width_input = forms.DecimalField(required=False, min_value=0)
    storage_height_input = forms.DecimalField(required=False, min_value=0)

    class Meta:
        model = EquipmentType
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate inputs on edit
        if self.instance.pk:
            self.fields["storage_length_input"].initial = self.instance.storage_length_m
            self.fields["storage_width_input"].initial = self.instance.storage_width_m
            self.fields["storage_height_input"].initial = self.instance.storage_height_m

    def clean(self):
        cleaned = super().clean()

        self.apply_dimension_inputs(
            self.instance,
            {
                "storage_length_input": "storage_length_m",
                "storage_width_input": "storage_width_m",
                "storage_height_input": "storage_height_m",
            }
        )

        return cleaned

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


class EquipmentItemInlineForm(forms.ModelForm):
    class Meta:
        model = EquipmentItem
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()

        # Enforce a default BEFORE save if user leaves it blank
        if not cleaned.get("status"):
            cleaned["status"] = EquipmentItem.STATUS_AVAILABLE

        return cleaned




class PurchaseRecordForm(forms.ModelForm):

    class Meta:
        model = PurchaseRecord
        fields = [
            "date_ordered",
            "vendor",
            "fiscal_year",
            "extended_cost",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Auto-set today's date
        self.fields["date_ordered"].initial = timezone.now().date()



    
