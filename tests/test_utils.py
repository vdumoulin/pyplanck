# -*- coding: utf-8 -*-
"""Tests for utility functions defined in `utils.py`."""
from nose.tools import raises

from pyplanck.utils import (validate_name, validate_item_shortcut,
                            validate_amount, validate_employee_level)


class TestValidateName(object):
    def test_accepts_str(self):
        validate_name('gum')

    @raises(ValueError)
    def test_rejects_empty_str(self):
        validate_name('')

    @raises(ValueError)
    def test_rejects_non_str(self):
        validate_name(3)


class TestValidateItemShortcut(object):
    def test_accepts_str(self):
        validate_item_shortcut('gum')

    def test_accepts_none(self):
        validate_item_shortcut(None)


class TestValidateAmount(object):
    def test_accepts_int(self):
        validate_amount(2)

    def test_accepts_float(self):
        validate_amount(2.5)

    @raises(ValueError)
    def test_rejects_non_numbers(self):
        validate_amount('gum')

    @raises(ValueError)
    def test_rejects_negative_prices(self):
        validate_amount(-1.5)

    def test_accepts_free_price(self):
        validate_amount(0.0)


class TestValidateEmployeeLevel(object):
    def test_accepts_0_1_2(self):
        validate_employee_level(0)
        validate_employee_level(1)
        validate_employee_level(2)

    @raises(ValueError)
    def test_rejects_non_integers(self):
        validate_employee_level('gum')

    @raises(ValueError)
    def test_rejects_invalid_integers(self):
        validate_employee_level(3)
