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
from utils import check_is_valid_name_string, check_is_valid_item_price


def test_check_is_valid_name_string_accepts_str():
    check_is_valid_name_string("gum")


@raises(ValueError)
def test_check_is_valid_name_string_rejects_empty_str():
    check_is_valid_name_string("")


@raises(ValueError)
def test_check_is_valid_name_string_rejects_non_str():
    check_is_valid_name_string(3)
