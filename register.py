# -*- coding: utf-8 -*-
"""
Register-related classes
"""
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

import io, logging
from pyplanck.item import Item
from pyplanck.employee import Employee
from pyplanck.utils import (check_is_valid_menu_file_path,
                            check_is_valid_employees_file_path)


class Register(object):
    def __init__(self, menu_file_path, employees_file_path):
        # Input sanitization
        check_is_valid_menu_file_path(menu_file_path)
        check_is_valid_employees_file_path(employees_file_path)

        self.menu = self._load_menu(menu_file_path)
        self.employees = self._load_employees(employees_file_path)
        self.order = None

    def _load_menu(self, menu_file_path):
        menu = []
        with io.open(menu_file_path, encoding='utf-8') as menu_file:
            # Read all lines in the file
            lines = menu_file.readlines()
            # Strip all lines from trailing white space and carriage returns
            lines = [line.strip() for line in lines]
            # Remove empty lines
            lines = [line for line in lines if line != '']
            # Split lines into lists of tokens separated by '|' (items)
            items = [line.split('|') for line in lines]

            # This flag tells whether the file contains errors
            errors_detected = False

            current_category = "General"
            current_default_price = None

            # Loop over items and try to add them to the menu as MenuItem
            # instances. If errors occur, faulty lines are ignored and the
            # `errors_detected` flag is raised.
            for item in items:
                # Strip all tokens from leading and trailing white space
                item = [token.strip() for token in item]
                # Items must have at least two tokens (name and barcode) and at
                # most four (name, barcode, price and shortcut)
                if not len(item) in (2, 3, 4):
                    errors_detected = True
                    continue
                # If '#' is the first character of the line, this is a category
                # command to set a new category and a new default price.
                if item[0].startswith("#"):
                    current_category = item[0][1:].strip()
                    try:
                        current_default_price = float(item[1])
                        continue
                    except ValueError:
                        errors_detected = True
                        continue
                # The third token is always considered as the custom price, and
                # the fourth one is the shortcut. Items with a shortcut must
                # therefore have a price set. Items without a custom price must
                # belong to a category which sets a default price.
                if len(item) == 2 and current_default_price is None:
                    errors_detected = True
                    continue
                # Parse the actual item
                if len(item) == 2:
                    barcode = item[0]
                    name = item[1]
                    category = current_category
                    price = current_default_price
                    shortcut = None
                if len(item) == 3:
                    barcode = item[0]
                    name = item[1]
                    category = current_category
                    try:
                        price = float(item[2])
                    except ValueError:
                        errors_detected = True
                        continue
                    shortcut = None
                if len(item) == 4:
                    barcode = item[0]
                    name = item[1]
                    category = current_category
                    try:
                        price = float(item[2])
                    except ValueError:
                        errors_detected = True
                        continue
                    shortcut = item[3]
                # Add item to menu
                it = Item(name=name, barcode=barcode, category=category,
                          price=price, shortcut=shortcut)
                menu.append(it)

        if errors_detected:
            logging.warning("Some lines of the menu contained errors and " +
                            "were ignored")

        return list(set(menu))

    def _load_employees(self, employees_file_path):
        employees_list = []

        with io.open(employees_file_path, encoding='utf-8') as employees_file:
            # Read all lines in the file
            lines = employees_file.readlines()
            # Strip all lines from trailing white space and carriage returns
            lines = [line.strip() for line in lines]
            # Remove empty lines
            lines = [line for line in lines if line != '']
            # Split lines into lists of tokens separated by '|' (employees)
            employees = [line.split('|') for line in lines]

            # This flag tells whether the file contains errors
            errors_detected = False

            # Loop over employees and try to add them to the menu as Employee
            # instances. If errors occur, faulty lines are ignored and the
            # `errors_detected` flag is raised.
            for employee in employees:
                # Strip all tokens from leading and trailing white space
                employee = [token.strip() for token in employee]
                # Employees must have four tokens (name, barcode, permanent
                # code and employee level)
                # most four (name, barcode, price and shortcut)
                if len(employee) != 4:
                    errors_detected = True
                    continue
                else:
                    name = employee[0]
                    barcode = employee[1]
                    code = employee[2]
                    try:
                        level = int(employee[3])
                    except ValueError:
                        errors_detected = True
                        continue
                # Add employee to employee list
                em = Employee(name=name, barcode=barcode, code=code,
                              level=level)
                employees_list.append(em)

        if errors_detected:
            logging.warning("Some lines of the employee file contained " +
                            "errors and were ignored")

        return list(set(employees_list))


if __name__ == "__main__":
    register = Register("sample_menu.txt", "sample_employees.txt")
