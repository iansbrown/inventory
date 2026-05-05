# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:16:53 2026

@author: ianbrown
"""

from equipment.models import EquipmentItem


def detect_equipment_conflicts(equipment_map):
    """
    equipment_map: dict {EquipmentItem: required_quantity}

    Returns a list of conflict dicts:
    {
        "item": EquipmentItem,
        "required": int,
        "available": int,
    }
    """
    conflicts = []

    for item, required in equipment_map.items():
        if item.tracking_level == "bulk":
            available = item.quantity or 0
        else:
            # individual / serialized items
            available = 1

        if required > available:
            conflicts.append({
                "item": item,
                "required": required,
                "available": available,
            })

    return conflicts
