# -*- coding: utf-8 -*-
"""
Tests for utility functions defined in `utils.py`
"""
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

from nose.tools import raises
from pyplanck.utils import (check_is_valid_name_string,
                            check_is_valid_item_shortcut,
                            check_is_valid_amount,
                            check_is_valid_employee_level)


def test_check_is_valid_name_string_accepts_str():
    check_is_valid_name_string("gum")


@raises(ValueError)
def test_check_is_valid_name_string_rejects_empty_str():
    check_is_valid_name_string("")


@raises(ValueError)
def test_check_is_valid_name_string_rejects_non_str():
    check_is_valid_name_string(3)


def test_check_is_valid_item_shortcut_accepts_none():
    check_is_valid_item_shortcut(None)


def test_check_is_valid_amount_accepts_int():
    check_is_valid_amount(2)


def test_check_is_valid_amount_accepts_float():
    check_is_valid_amount(2.5)


@raises(ValueError)
def test_check_is_valid_amount_rejects_non_numbers():
    check_is_valid_amount("gum")


@raises(ValueError)
def test_check_is_valid_amount_rejects_negative_prices():
    check_is_valid_amount(-1.5)


def test_check_is_valid_amount_accepts_free_price():
    check_is_valid_amount(0.0)


def test_check_is_valid_employee_level_accepts_0_1_2():
    check_is_valid_employee_level(0)
    check_is_valid_employee_level(1)
    check_is_valid_employee_level(2)


@raises(ValueError)
def test_check_is_valid_employee_level_rejects_non_integers():
    check_is_valid_employee_level("gum")


@raises(ValueError)
def test_check_is_valid_employee_level_rejects_invalid_integers():
    check_is_valid_employee_level(3)
