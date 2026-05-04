# -*- coding: utf-8 -*-
"""
Created on Mon May  4 15:44:02 2026

@author: ianbrown
"""

def detect_equipment_conflicts(equipment_map):
    """
    equipment_map:
        { EquipmentItem: required_quantity }
    """
    conflicts = []

    for item, required in equipment_map.items():
        available = item.quantity if item.tracking_level == "bulk" else 1

        if required > available:
            conflicts.append({
                "item": item,
                "required": required,
                "available": available,
            })

    return conflicts
