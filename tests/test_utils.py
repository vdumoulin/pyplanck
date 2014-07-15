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
                            check_is_valid_item_price,
                            check_is_valid_item_quantity,
                            check_is_valid_quantity_delta)


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


def test_check_is_valid_item_price_accepts_int():
    check_is_valid_item_price(2)


def test_check_is_valid_item_price_accepts_float():
    check_is_valid_item_price(2.5)


@raises(ValueError)
def test_check_is_valid_item_price_rejects_non_numbers():
    check_is_valid_item_price("gum")


@raises(ValueError)
def test_check_is_valid_item_price_rejects_negative_prices():
    check_is_valid_item_price(-1.5)


def test_check_is_valid_item_price_accepts_free_price():
    check_is_valid_item_price(0.0)


def test_check_is_valid_item_quantity_accepts_positive_integers():
    check_is_valid_item_quantity(1)


def test_check_is_valid_item_quantity_accepts_zero():
    check_is_valid_item_quantity(0)


@raises(ValueError)
def test_check_is_valid_item_quantity_rejects_non_integers():
    check_is_valid_item_quantity("gum")


@raises(ValueError)
def test_check_is_valid_item_quantity_rejects_negative():
    check_is_valid_item_quantity(-1)


def test_check_is_valid_quantity_delta_accepts_positive_integers():
    check_is_valid_quantity_delta(1)


@raises(ValueError)
def test_check_is_valid_quantity_delta_rejects_zero():
    check_is_valid_quantity_delta(0)


@raises(ValueError)
def test_check_is_valid_quantity_delta_rejects_non_integers():
    check_is_valid_quantity_delta("gum")


@raises(ValueError)
def test_check_is_valid_quantity_delta_rejects_negative():
    check_is_valid_quantity_delta(-1)
