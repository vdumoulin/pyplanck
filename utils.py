__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"


def check_is_valid_name_string(name_string, string_type="name string"):
    """
    Checks that `name_string` is a valid name string, and raises an error
    otherwise.

    A valid name string must be a non-empty string.
    """
    if type(name_string) is not str:
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


def check_is_valid_item_quantity(item_quantity):
    """
    Checks that `item_quantity` is a valid item quantity, and raises an error
    otherwise.

    A valid item quantity must be a positive (>= 0) int.
    """
    if type(item_quantity) is not int:
        raise ValueError("item quantity must be an int")
    if item_quantity < 0:
        raise ValueError("item quantity must be positive")


def check_is_valid_quantity_delta(delta):
    """
    Checks that `delta` is a valid quantity variation, and raises an error
    otherwise.

    A valid quantity variation must be a positive (>= 0) int.
    """
    if type(delta) is not int:
        raise ValueError("quantity variation must be an int")
    if delta < 1:
        raise ValueError("quantity variation must be at least 1")
