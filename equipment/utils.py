# -*- coding: utf-8 -*-
"""
Created on Thu May  7 16:19:41 2026

@author: ianbrown
"""
from decimal import Decimal
from django import forms
from collections import defaultdict

METERS_PER_UNIT = {
    "m": Decimal("1"),
    "cm": Decimal("0.01"),
    "ft": Decimal("0.3048"),
    "in": Decimal("0.0254"),
}


DIMENSION_UNIT_CHOICES = [
    ("m", "Meters"),
    ("cm", "Centimeters"),
    ("ft", "Feet"),
    ("in", "Inches"),
]


class DimensionInputMixin(forms.Form):
    """
    Adds unit-aware dimension input fields and
    safely persists canonical meter values.
    """

    dimension_unit = forms.ChoiceField(
        choices=DIMENSION_UNIT_CHOICES,
        required=False,
        initial="m",
        label="Dimension Unit",
        help_text="Unit for entered dimensions"
    )

    def _convert_to_meters(self, value, unit):
        if value is None:
            return None
        factor = METERS_PER_UNIT.get(unit, Decimal("1"))
        return (value * factor).quantize(Decimal("0.0001"))

    def apply_dimension_inputs(self, instance, mapping):
        """
        mapping = {
            "input_field": "model_field_m",
            ...
        }
        """
        unit = self.cleaned_data.get("dimension_unit") or "m"

        for input_field, model_field in mapping.items():
            raw_val = self.cleaned_data.get(input_field)

            # Only write if user actually entered a value
            if raw_val is not None:
                setattr(
                    instance,
                    model_field,
                    self._convert_to_meters(raw_val, unit)
                )

def equipment_list_for_experiment(experiment):
    """
    Returns a list of equipment required for an experiment,
    including quantity and storage metadata.
    """
    return [
        {
            "equipment": link.equipment,
            "quantity": link.quantity_used or 1,
            "storage_volume_m3": link.equipment.storage_volume_m3,
            "storage_footprint_m2": link.equipment.storage_footprint_m2,
        }
        for link in experiment.equipment_links.select_related("equipment")
    ]

def available_count(equipment_type):
    total = 0
    for item in equipment_type.items.filter(status="available"):
        if item.tracking_level == "bulk":
            total += item.quantity or 0
        else:
            total += 1
    return total


def can_schedule_experiment(experiment):
    """
    Returns True if all equipment requirements
    for an experiment can be met.

    This function must NEVER raise.
    """
    # If there are no requirements, we treat this as unschedulable
    # (safer default than True).
    requirements = experiment.equipment_requirements.select_related(
        "equipment_type"
    )

    if not requirements.exists():
        return False

    for req in requirements:
        # Missing equipment type ⇒ cannot schedule
        if not req.equipment_type:
            return False

        # Quantity must be valid and positive
        if not req.quantity_required or req.quantity_required <= 0:
            return False

        try:
            available = available_count(req.equipment_type)
        except Exception:
            # Any error counting availability ⇒ cannot schedule
            return False

        if available < req.quantity_required:
            return False

    return True

def build_equipment_type_map_for_experiments(experiments):
    """
    experiments: iterable of Experiment objects

    Returns:
        {EquipmentType: total_required_quantity}
    """
    equipment_type_map = defaultdict(int)

    for experiment in experiments:
        for req in experiment.equipment_requirements.select_related(
            "equipment_type"
        ):
            if not req.equipment_type:
                continue
            equipment_type_map[req.equipment_type] += req.quantity_required

    return equipment_type_map