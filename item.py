# -*- coding: utf-8 -*-
"""
Menu-related classes
"""
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

from pyplanck.utils import (check_is_valid_item_name,
                            check_is_valid_item_price,
                            check_is_valid_item_barcode,
                            check_is_valid_item_category,
                            check_is_valid_item_shortcut)


class Item(object):
    """
    Abstract item class used in the menu.

    Parameters
    ----------
    name : str
        Name of the item
    price : int or float
        Price of the item
    barcode : str
        Barcode identifier for the item
    category : str, optional
        Item category. Defaults to "General".
    shortcut : str, optional
        Additional identifier for the item. Defaults to `None`, in which case
        no shortcut is set.
    """
    def __init__(self, name, price, barcode, category="General",
                 shortcut=None):
        # Input sanitizing
        check_is_valid_item_name(name)
        check_is_valid_item_price(price)
        check_is_valid_item_barcode(barcode)
        check_is_valid_item_category(category)
        check_is_valid_item_shortcut(shortcut)

        self.name = name
        self.price = price
        self.barcode = barcode
        self.category = category
        self.shortcut = shortcut

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return (self.barcode + "|" + self.name + "|" + self.category + "|" +
                str(self.price))

    def __eq__(self, other):
        if type(other) == type(self) and other.barcode == self.barcode:
            return True
        else:
            return False

    def get_name(self):
        return self.name

    def get_price(self):
        return self.price

    def get_barcode(self):
        return self.barcode

    def get_category(self):
        return self.category

    def get_shortcut(self):
        return self.shortcut
