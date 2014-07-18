# -*- coding: utf-8 -*-
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

import os


def check_is_valid_name_string(name_string, string_type="name string"):
    """
    Checks that `name_string` is a valid name string, and raises an error
    otherwise.

    A valid name string must be a non-empty string.
    """
    if type(name_string) not in (str, unicode):
        raise ValueError(string_type + " must be a string")
    if len(name_string) == 0:
        raise ValueError(string_type + " must not be empty")


def check_is_valid_item_name(item_name):
    """
    Checks that `item_name` is a valid item name, and raises an error
    otherwise. Validity conditions are defined in `check_is_valid_name_string`.
    """
    check_is_valid_name_string(name_string=item_name, string_type="item name")


def check_is_valid_item_barcode(item_barcode):
    """
    Checks that `item_barcode` is a valid item barcode, and raises an error
    otherwise. Validity conditions are defined in `check_is_valid_name_string`.
    """
    check_is_valid_name_string(name_string=item_barcode,
                               string_type="item barcode")


def check_is_valid_item_category(item_category):
    """
    Checks that `item_category` is a valid item category, and raises an error
    otherwise. Validity conditions are defined in `check_is_valid_name_string`.
    """
    check_is_valid_name_string(name_string=item_category,
                               string_type="item category")


def check_is_valid_item_shortcut(item_shortcut):
    """
    Checks that `item_shortcut` is a valid item shortcut, and raises an error
    otherwise. Validity conditions are defined in `check_is_valid_name_string`.
    """
    if item_shortcut is not None:
        check_is_valid_name_string(name_string=item_shortcut,
                                   string_type="item shortcut")


def check_is_valid_item_price(item_price):
    """
    Checks that `item_price` is a valid item price, and raises an error
    otherwise.

    A valid item price must be a positive (>= 0) float or int.
    """
    if type(item_price) not in (float, int):
        raise ValueError("item price must be either float or int")
    if item_price < 0:
        raise ValueError("item price must be positive")


def check_is_valid_employee_name(employee_name):
    """
    Checks that `employee_name` is a valid employee name, and raises an error
    otherwise. Validity conditions are defined in `check_is_valid_name_string`.
    """
    check_is_valid_name_string(name_string=employee_name,
                               string_type="employee name")


def check_is_valid_employee_barcode(employee_barcode):
    """
    Checks that `employee_barcode` is a valid employee barcode, and raises an
    error otherwise. Validity conditions are defined in
    `check_is_valid_name_string`.
    """
    check_is_valid_name_string(name_string=employee_barcode,
                               string_type="employee barcode")


def check_is_valid_employee_code(employee_code):
    """
    Checks that `employee_code` is a valid employee code, and raises an error
    otherwise. Validity conditions are defined in `check_is_valid_name_string`.
    """
    check_is_valid_name_string(name_string=employee_code,
                               string_type="employee code")


def check_is_valid_employee_level(employee_level):
    """
    Checks that `employee_level` is a valid employee level, and raises an error
    otherwise.

    A valid employee level is an int in {0, 1, 2}.
    """
    if type(employee_level) is not int:
        raise ValueError("employee level must be an int")
    if employee_level not in (0, 1, 2):
        raise ValueError("employee level must be in {0, 1, 2}")


def check_is_valid_file_path(file_path, file_type="file"):
    """
    Checks that `file_path` is a valid file path, and raises an error
    otherwise.
    """
    if not os.path.isfile(file_path):
        raise ValueError("path for " + file_type + " file does not exist")


def check_is_valid_menu_file_path(menu_file_path):
    """
    Checks that `menu_file_path` is a valid menu file path, and raises an error
    otherwise.
    """
    check_is_valid_file_path(file_path=menu_file_path, file_type="menu")


def check_is_valid_employees_file_path(employees_file_path):
    """
    Checks that `employees_file_path` is a valid employees file path, and
    raises an error otherwise.
    """
    check_is_valid_file_path(file_path=employees_file_path,
                             file_type="employees")
