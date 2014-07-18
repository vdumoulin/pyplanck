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

import io, os, logging, struct
from pyplanck.item import Item
from pyplanck.employee import Employee
from pyplanck.exceptions import CredentialException, ItemNotFoundException
from pyplanck.utils import (check_is_valid_menu_file_path,
                            check_is_valid_employees_file_path)


class Register(object):
    """
    Class implementing the register's functionalities.

    Parameters
    ----------
    menu_file_path : str
        Path to the menu file
    employees_file_path : str
        Path to the employees file
    register_count_file_path : str
        Path to the register count file
    """
    def __init__(self, menu_file_path, employees_file_path,
                 register_count_file_path):
        # Input sanitization
        check_is_valid_menu_file_path(menu_file_path)
        check_is_valid_employees_file_path(employees_file_path)

        self.register_count_file_path = register_count_file_path

        self.menu = self._load_menu(menu_file_path)
        self.employees = self._load_employees(employees_file_path)
        self.register_count = self._load_register_count(
            self.register_count_file_path
        )

        self.employee = None
        self.order = {}

    def get_register_count(self):
        """
        Returns the register count.
        """
        self._verify_credentials(self.employee, 2)
        return self.register_count

    def logout_employee(self):
        """
        Logs out an employee.
        """
        self.employee = None

    def get_employee_name(self):
        if self.employee is None:
            return "None"
        else:
            return self.employee.get_name()

    def scan(self, string):
        """
        Scans an input of the register.

        Parameters
        ----------
        string : str
            Input string
        """
        self._verify_credentials(self.employee, 0)
        item = self.find(string)
        self._add_to_order(item)

    def remove(self, string):
        """
        Scans an input of the register.

        Parameters
        ----------
        string : str
            Input string
        """
        self._verify_credentials(self.employee, 0)
        item = self.find(string)
        self._remove_from_order(item)

    def remove_from_order(self, item):
        """
        Removes an item from the order.

        Parameters
        ----------
        item : pyplanck.item.Item
            Item to remove
        """
        self._verify_credentials(self.employee, 1)
        if item in self.order:
            if self.order[item] == 1:
                del self.order[item]
            else:
                self.order[item] = self.order[item] - 1
        else:
            raise ValueError("item '" + item.name + "' not in current order")

    def find(self, token):
        """
        Finds an item in the menu by a token, either its barcode or its
        shortcut.

        Parameters
        ----------
        token : str
            Token by which to search the item
        """
        self._verify_credentials(self.employee, 0)
        item = next((i for i in self.menu if (i.get_shortcut() == token
                     or i.get_barcode() == token)), None)
        if item is None:
            raise ValueError("item not found with token '" + token + "'")
        return item

    def clear_order(self):
        """
        Clear the register's order.
        """
        self._verify_credentials(self.employee, 0)
        self.order = {}

    def checkout_order(self):
        """
        Adds order total to register count and logs the transaction.
        """
        self._verify_credentials(self.employee, 1)
        order_total = reduce(lambda x, y: x + y,
                             [item.get_price() * quantity
                              for (item, quantity) in self.order.items()])
        self._add_to_register_count(order_total)
        self._log_order()
        self.clear_order()

    def order_to_string(self):
        """
        Returns a string representation of the current order.
        """
        self._verify_credentials(self.employee, 0)
        rval = ""
        for (item, quantity) in self.order.items():
            rval += item.name + " x " + str(quantity) + "\n"
        return rval.strip()

    def _verify_credentials(self, employee, authorized_level):
        if employee is None and authorized_level is not None:
            raise CredentialException("unauthorized operation while no " +
                                      "employee logged in")
        employee_level = employee.get_level()
        if employee_level < authorized_level:
            raise CredentialException("insufficient privileges for this " +
                                      "operation")

    def _add_to_order(self, item):
        """
        Adds an item to the order.

        Parameters
        ----------
        item : pyplanck.item.Item
            Item to add
        """
        if item in self.order:
            self.order[item] = self.order[item] + 1
        else:
            self.order[item] = 1

    def _remove_from_order(self, item):
        """
        Removes an item from the order.

        Parameters
        ----------
        item : pyplanck.item.Item
            Item to remove
        """
        if item in self.order:
            if self.order[item] == 1:
                del self.order[item]
            else:
                self.order[item] = self.order[item] - 1
        else:
            raise ItemNotFoundException("item '" + item.name +
                                        "' not in current order")


    def _load_menu(self, file_path):
        """
        Loads and returns the menu.

        Parameters
        ----------
        file_path : str
            Path to the menu file
        """
        menu = []
        with io.open(file_path, encoding='utf-8') as f:
            # Read all lines in the file
            lines = f.readlines()
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

    def _load_employees(self, file_path):
        """
        Loads and returns the employees list.

        Parameters
        ----------
        file_path : str
            Path to the employees file
        """
        employees_list = []

        with io.open(file_path, encoding='utf-8') as f:
            # Read all lines in the file
            lines = f.readlines()
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

    def _load_register_count(self, file_path):
        """
        Loads and returns the register count.

        Parameters
        ----------
        file_path : str
            Path to the register count file
        """
        if not os.path.isfile(file_path):
            register_count = 0.0
            with io.open(file_path, 'wb') as f:
                data = struct.pack('d', register_count)
                f.write(data)
            logging.warning("register count file not found, creating one " +
                            "with value 0.0 at " +
                            os.path.abspath(file_path))
        else:
            with io.open(file_path, 'rb') as f:
                (register_count, ) = struct.unpack('d', f.read(8))
        return register_count

    def _add_to_register_count(self, amount):
        """
        Adds an amount to the register count.

        Parameters
        ----------
        amount : float
            Amout to add
        """
        self.register_count += amount
        self._update_register_count()

    def _substract_from_register_count(self, amount):
        """
        Substracts an amount from the register count.

        Parameters
        ----------
        amount : float
            Amout to substract
        """
        # The register amount cannot go negative because it is supposed to
        # represent the quantity of physical money in the register.
        if amount > self.register_count:
            raise ValueError("cannot substract amount (" + str(amount) + ") " +
                             "greater than register count (" +
                             str(self.register_count) + ")")
        self.register_count -= amount
        self._update_register_count()

    def _update_register_count(self):
        """
        Writes the register count to file in order to have a persistent state.
        """
        with io.open(self.register_count_file_path, 'wb') as f:
            data = struct.pack('d', self.register_count)
            f.write(data)

    def _log_order(self):
        """
        WRITEME
        """
        pass


if __name__ == "__main__":
    register = Register("sample_menu.txt", "sample_employees.txt",
                        "sample_register_count.bin")
    register.login_employee('2222')
    print register.get_register_count()
    register.logout_employee()
    register.login_employee('1111')
    print register.get_register_count()
