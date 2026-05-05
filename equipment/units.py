# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:32:20 2026

@author: ianbrown
"""

from decimal import Decimal

# Length conversions → meters
INCH_TO_METER = Decimal("0.0254")
FOOT_TO_METER = Decimal("0.3048")

def to_meters(value: Decimal, unit: str) -> Decimal:
    if value is None:
        return None

    if unit == "m":
        return value
    if unit == "cm":
        return value / Decimal("100")
    if unit == "in":
        return value * INCH_TO_METER
    if unit == "ft":
        return value * FOOT_TO_METER

    raise ValueError(f"Unsupported unit: {unit}")


def meters_to_inches(value: Decimal) -> Decimal:
    return value / INCH_TO_METER


def meters_to_feet(value: Decimal) -> Decimal:
    return value / FOOT_TO_METER