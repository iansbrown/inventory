# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:32 2026

@author: ianbrown
"""

from django.db import models


class PurchaseRecord(models.Model):
    """
    Represents a single purchasing event (order, invoice, or acquisition).

    One PurchaseRecord may be associated with:
    - One EquipmentItem
    - Or multiple EquipmentItems derived from the same purchase

    This table preserves accounting, audit, and procurement history.
    """

    # ---- Legacy reference ----
    legacy_access_id = models.PositiveIntegerField(
    unique=True,
    null=True,
    blank=True,
    help_text="Primary key of the original Access database row (migration only)"
    )

    # ---- Vendor / accounting information ----
    vendor = models.CharField(
        max_length=255,
        help_text="Vendor or supplier name"
    )

    fiscal_year = models.PositiveIntegerField(
        help_text="Fiscal year charged for this purchase"
    )

    date_ordered = models.DateField(
        null=True,
        blank=True,
        help_text="Date the item(s) were ordered"
    )

    date_received = models.DateField(
        null=True,
        blank=True,
        help_text="Date the item(s) were received"
    )

    order_number = models.CharField(
        max_length=255,
        blank=True,
        help_text="Vendor order number"
    )

    po_number = models.CharField(
        max_length=255,
        blank=True,
        help_text="Purchase order number (if applicable)"
    )

    payment_method = models.CharField(
        max_length=255,
        blank=True,
        help_text="Credit card, contract vendor, etc."
    )

    # ---- Cost breakdown ----
    item_unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Unit cost of one item"
    )

    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Shipping cost for the purchase"
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tax charged on the purchase"
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discount applied to the purchase"
    )

    extended_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total extended cost for the purchase"
    )

    # ---- Backorder tracking ----
    backorder_flag = models.BooleanField(
        default=False,
        help_text="Indicates whether any items were backordered"
    )

    backorder_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of items on backorder"
    )

    backorder_received_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date backordered items were received"
    )

    # ---- Move & lifecycle planning ----
    purchase_relevance_notes = models.TextField(
        blank=True,
        help_text="Notes regarding relevance for move or replacement decisions"
    )

    replacement_priority = models.CharField(
        max_length=20,
        blank=True,
        help_text="Low / Medium / High replacement priority"
    )

    # ---- General notes ----
    notes = models.TextField(
        blank=True,
        help_text="General notes or legacy comments"
    )

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor} — FY{self.fiscal_year} (Access ID {self.legacy_access_id})"