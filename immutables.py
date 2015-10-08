# -*- coding: utf-8 -*-
"""Immutable objects."""
from collections import namedtuple

from .utils import (validate_name, validate_employee_level, validate_amount,
                    validate_item_shortcut)


Employee = namedtuple(
    'Employee', 'name barcode code level', verbose=False)

Item = namedtuple(
    'Item', 'name price barcode category shortcut', verbose=False)
Item.__new__.__defaults__ = ('General', None)


def validate_employee(name, barcode, code, level):
    validate_name(name, 'employee name')
    validate_name(barcode, 'employee barcode')
    validate_name(code, 'employee code')
    validate_employee_level(level)


def validate_item(name, price, barcode, category, shortcut):
    validate_name(name, 'item name')
    validate_amount(price, 'item price')
    validate_name(barcode, 'item barcode')
    validate_name(category, 'item category')
    validate_item_shortcut(shortcut)
