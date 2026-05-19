# -*- coding: utf-8 -*-
"""
Created on Tue May 19 10:23:21 2026

@author: ianbrown
"""

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)