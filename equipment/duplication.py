# -*- coding: utf-8 -*-
"""
Created on Wed May  6 11:54:27 2026

@author: ianbrown
"""

from copy import copy


def duplicate_equipment_item(
    original_item,
    count: int,
    *,
    inventory_tag_generator=None,
):
    """
    Duplicate an EquipmentItem `count` times, excluding unique identifiers.

    Parameters:
        original_item: EquipmentItem instance to duplicate
        count: number of copies to create
        inventory_tag_generator: optional callable(index) -> str

    Returns:
        list of newly created EquipmentItem instances
    """
    new_items = []

    for i in range(count):
        new_item = copy(original_item)

        # Reset identity fields
        new_item.pk = None
        new_item.id = None

        # Clear or regenerate unique identifiers
        if hasattr(new_item, "inventory_tag"):
            if inventory_tag_generator:
                new_item.inventory_tag = inventory_tag_generator(i)
            else:
                new_item.inventory_tag = ""

        new_item.save()
        new_items.append(new_item)

    return new_items

def sequential_tag_generator(base_tag):
    def generator(index):
        return f"{base_tag}-{index + 1:03d}"
    return generator