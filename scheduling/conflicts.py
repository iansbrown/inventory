# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:16:53 2026

@author: ianbrown
"""

from equipment.models import EquipmentType,EquipmentItem
from equipment.utils import available_count


def detect_equipment_conflicts(equipment_type_map):
    """
    equipment_type_map: dict {EquipmentType: required_quantity}

    Returns a list of conflict dicts:
    {
        "equipment_type": EquipmentType,
        "required": int,
        "available": int,
        "shortfall": int,
    }
    """
    conflicts = []

    for equipment_type, required in equipment_type_map.items():
        # Defensive: missing or invalid data ⇒ unschedulable, not crash
        if not equipment_type or not required or required <= 0:
            continue



        try:
            items = EquipmentItem.objects.filter(
                equipment_type=equipment_type
            )
            
            print(f"{equipment_type.name} TOTAL ITEMS:", items.count())
            
            for item in items:
                print(
                    f"id={item.id}, "
                    f"status={item.status}, "
                    f"tracking={item.tracking_level}, "
                    f"qty={item.quantity}"
                )

            available = 0
        
            for item in items:
                status = (item.status or "").strip().lower()
        
                if status != "available":
                    continue
        
                if item.tracking_level == EquipmentItem.TRACKING_BULK:
                    available += item.quantity or 0
                else:
                    available += 1
        
        except Exception:
            available = 0


        if required > available:
            conflicts.append({
                "equipment_type": equipment_type,
                "required": required,
                "available": available,
                "shortfall": required - available,
            })

    return conflicts
