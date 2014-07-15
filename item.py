from utils import (check_is_valid_item_name, check_is_valid_item_price,
                   check_is_valid_item_barcode, check_is_valid_item_category,
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
        self.quantity = quantity

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

    def make_menu_item(self):
        return MenuItem(name=self.name, price=self.price, barcode=self.barcode,
                        category=self.category, shortcut=self.shortcut,
                        quantity=0)


class MenuItem(Item):
    """
    WRITEME
    """
    def __init__(self, name, price, barcode, category="General",
                 shortcut=None, quantity=0):
        # Initialize super-class
        super(MenuItem, self).__init__(name=name, price=price, barcode=barcode,
                                       category=category, shortcut=shortcut)
        # Input sanitization
        if type(quantity) is not int:
            raise ValueError("item quantity must be an int")
        if quantity < 0:
            raise ValueError("item quantity must be positive")
        self.quantity = quantity

    def __eq__(self, other):
        if type(other) == type(self):
            return (other.barcode == self.barcode and
                    self.quantity == other.quantity)
        else:
            return False

    def make_menu_item(self):
        raise NotImplementedError("MenuItem does not implement " +
                                  "`make_menu_item`. Only Item does.")

    def get_quantity(self):
        return self.quantity

    def is_empty(self):
        return self.quantity == 0

    def add(self, quantity=1):
        if type(quantity) is not int:
            raise ValueError("added quantity must be an int")
        if quantity < 1:
            raise ValueError("added quantity must be at least 1")
        self.quantity += quantity

    def sub(self, quantity=1):
        if type(quantity) is not int:
            raise ValueError("substracted quantity must be an int")
        if quantity < 1:
            raise ValueError("substracted quantity must be at least 1")
        if self.quantity < quantity:
            raise ValueError("substracted quantity must not be greater than " +
                             "item quantity (" + str(self.get_quantity()) +
                             " items left and trying to remove " +
                             str(quantity) + " items)")
        self.quantity -= quantity
