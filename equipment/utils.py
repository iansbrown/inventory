# -*- coding: utf-8 -*-
"""
Created on Thu May  7 16:19:41 2026

@author: ianbrown
"""


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