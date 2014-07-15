# -*- coding: utf-8 -*-
"""
Employee-related classes
"""
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

from utils import (check_is_valid_employee_name,
                   check_is_valid_employee_barcode,
                   check_is_valid_employee_code,
                   check_is_valid_employee_level)


class Employee(object):
    """
    Employee class used in the employees list

    Parameters
    ----------
    name : str
        Name of the employee
    barcode : str
        Barcode identifier for the employee
    code : str
        Permanent code of the employee
    level : int
        Employee level
    """
    def __init__(self, name, barcode, code, level):
        # Input sanitizing
        check_is_valid_employee_name(name)
        check_is_valid_employee_barcode(barcode)
        check_is_valid_employee_code(code)
        check_is_valid_employee_level(level)

        self.name = name
        self.barcode = barcode
        self.code = code
        self.level = level

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return (self.name + "|" + self.barcode + "|" + self.code + "|" +
                str(self.level))

    def __eq__(self, other):
        if type(other) == type(self) and other.barcode == self.barcode:
            return True
        else:
            return False

    def get_name(self):
        return self.name
    
    def get_barcode(self):
        return self.barcode

    def get_code(self):
        return self.code

    def get_level(self):
        return self.level
