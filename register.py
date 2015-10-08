# -*- coding: utf-8 -*-
"""Register-related classes."""
import io
import os
import logging
import struct
from collections import OrderedDict
from logging.handlers import TimedRotatingFileHandler

from .immutables import Employee, Item, validate_employee, validate_item
from .exceptions import CredentialException, ItemNotFoundException
from .utils import validate_amount, validate_file_path


class Register(object):
    """Class implementing the register's functionalities.

    Parameters
    ----------
    menu_file_path : :class:`str`
        Path to the menu file.
    employees_file_path : :class:`str`
        Path to the employees file.
    register_count_file_path : :class:`str`
        Path to the register count file.
    log_path : :class:`str`
        Where to save logs.

    """
    def __init__(self, menu_file_path, employees_file_path,
                 register_count_file_path, log_path):

        self.register_count_file_path = register_count_file_path

        self.transaction_logger = self.create_logger(
            name='transaction',
            log_path=os.path.join(log_path, 'transactions.log'),
            log_format='%(asctime)s\n%(message)s')
        self.count_logger = self.create_logger(
            name='count',
            log_path=os.path.join(log_path, 'counts.log'),
            log_format='%(asctime)s\n%(message)s')
        self.logger = self.create_logger(
            name='event',
            log_path=os.path.join(log_path, 'events.log'),
            log_format='%(asctime)s - %(levelname)s - %(message)s')

        validate_file_path(menu_file_path, 'menu')
        validate_file_path(employees_file_path, 'employees')

        self.menu = self._load_menu(menu_file_path)
        self.employees = self._load_employees(employees_file_path)
        self._register_count = self._load_register_count(
            self.register_count_file_path)

        self.employee = None
        self.order_dict = OrderedDict()

    @property
    def events_logger(self):
        return self.logger

    @property
    def employee_name(self):
        if not self.employee:
            return 'None'
        else:
            return self.employee.name

    @property
    def order(self):
        return tuple(self.order_dict.items())

    @property
    def order_total(self):
        return sum(item.price * quantity for item, quantity in self.order)

    @property
    def register_count(self):
        self._verify_credentials(self.employee, 2)
        return self._register_count

    @staticmethod
    def create_logger(name, log_path, log_format):
        """Creates a a rotating logger set to rotate at midnight.

        Parameters
        ----------
        name : :class:`str`
            Logger name.
        log_path : :class:`str`
            In which file to save the log.
        log_format : :class:`str`
            Logging format.

        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler(log_path, 'midnight')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def find_in_list(items_list, token):
        """Finds an item in a list by a token.

        The token can either be its barcode or its shortcut.

        Parameters
        ----------
        token : :class:`str`
            Token by which to search the item.

        Raises
        ------
        ValueError
            If the token corresponds to no item in the list.

        """
        try:
            return next(
                i for i in items_list if token in (i.shortcut, i.barcode))
        except StopIteration:
            raise ValueError("item not found with token '{}'".format(token))

    def login_employee(self, token):
        """Finds and logs in an employee via a token.

        The token can either be a barcode or a permanent code.

        Parameters
        ----------
        token : str
            Token by which to search the employee.

        Raises
        ------
        CredentialException
            If the login token corresponds to no employee.

        """
        try:
            employee = next(
                e for e in self.employees if token in (e.barcode, e.code))
            self.employee = employee
            self.logger.info("logged in employee '{}' ".format(employee.name) +
                             "using token '{}'".format(token))
        except StopIteration:
            raise CredentialException('invalid employee login')

    def logout_employee(self):
        """Logs out an employee."""
        employee = self.employee
        self.employee = None
        self.logger.info("logged out employee '{}'".format(employee.name))

    def add(self, token):
        """Adds an item to the order.

        Parameters
        ----------
        token : str
            Token representing the item to add.

        """
        self._verify_credentials(self.employee, 0)
        item = self._find_in_menu(token)
        self._add_to_order(item)

    def add_custom(self, name, price):
        """Adds a custom item to the order.

        Parameters
        ----------
        name : str
            Name of the custom item.
        price : int or float
            Price of the custom item.

        """
        self._verify_credentials(self.employee, 1)
        barcode = 'custom_{}'.format(name)
        category = 'Custom'
        shortcut = None
        validate_item(name, price, barcode, category, shortcut)
        self._add_to_order(Item(name, price, barcode, category, shortcut))

    def remove(self, token):
        """Removes an item from the current order.

        Parameters
        ----------
        token : str
            Token representing the item to remove.

        """
        self._verify_credentials(self.employee, 0)
        item = self._find_in_order(token)
        self._remove_from_order(item)

    def clear_order(self):
        """Clears the register's order."""
        self._verify_credentials(self.employee, 0)
        self.order_dict = OrderedDict()

    def checkout_order(self):
        """Adds order total to register count and logs the transaction."""
        self._verify_credentials(self.employee, 1)
        self._add_to_register_count(self.order_total)
        self._log_order()
        self.clear_order()

    def order_to_string(self):
        """Returns a string representation of the current order."""
        self._verify_credentials(self.employee, 0)
        return '\n'.join('{} x {}'.format(item.name, quantity)
                         for item, quantity in self.order)

    def count_register(self, count):
        """Counts the register.

        Compares an employee's register count with the internal count and logs
        the operation.

        Parameters
        ----------
        count : float
            Employee register count.

        """
        self._verify_credentials(self.employee, 1)
        self._log_count(count)
        self.logger.info(
            'employee {} counted the register'.format(self.employee_name))

    def adjust(self, amount):
        """Adjusts the register count.

        Parameters
        ----------
        amount : number
            Adjustment amount.

        """
        self._verify_credentials(self.employee, 2)
        self._adjust_register_count(amount)

    def _find_in_menu(self, token):
        """Finds an item in the menu."""
        return self.find_in_list(self.menu, token)

    def _find_in_order(self, token):
        """Finds an item in the order."""
        return self.find_in_list(list(self.order_dict.keys()), token)

    def _verify_credentials(self, employee, authorized_level):
        """Verifies the credentials of an employee.

        Parameters
        ----------
        employee : Employee
            Employee to verify.
        authorized_level : :class:`int`
            Minimum access-granting level.

        Raises
        ------
        CredentialException
            If the employee has unsufficient privileges.

        """
        if employee is None and authorized_level is not None:
            raise CredentialException(
                'unauthorized operation while no employee logged in')
        if employee is not None:
            if employee.level < authorized_level:
                raise CredentialException(
                    'insufficient privileges for this operation')

    def _add_to_order(self, item):
        """Adds an item to the order.

        Parameters
        ----------
        item : Item
            Item to add.

        """
        if item in self.order_dict:
            self.order_dict[item] += 1
        else:
            self.order_dict[item] = 1

    def _remove_from_order(self, item):
        """Removes an item from the order.

        Parameters
        ----------
        item : Item
            Item to remove.

        Raises
        ------
        ItemNotFoundException
            If the item to be removed does not exist in the order.

        """
        if item in self.order_dict:
            if self.order_dict[item] == 1:
                del self.order_dict[item]
            else:
                self.order_dict[item] -= 1
        else:
            raise ItemNotFoundException(
                "item '{}' not in current order".format(item.name))

    def _load_menu(self, file_path):
        """Loads and returns the menu.

        Parameters
        ----------
        file_path : :class:`str`
            Path to the menu file.

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

            current_category = 'General'
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
                if item[0].startswith('#'):
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
                try:
                    validate_item(name, price, barcode, category, shortcut)
                except ValueError:
                    errors_detected = True
                    continue
                menu.append(Item(name, price, barcode, category, shortcut))

        if errors_detected:
            self.logger.warning('Some lines of the menu contained errors and '
                                'were ignored')

        return list(set(menu))

    def _load_employees(self, file_path):
        """Loads and returns the employees list.

        Parameters
        ----------
        file_path : :class:`str`
            Path to the employees file.

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
                if len(employee) != 4:
                    errors_detected = True
                    continue
                else:
                    name = employee[0]
                    barcode = employee[1]
                    code = employee[2]
                    try:
                        level = int(employee[3])
                        validate_employee(name, barcode, code, level)
                    except ValueError:
                        errors_detected = True
                        continue
                employees_list.append(Employee(name, barcode, code, level))

        if errors_detected:
            self.logger.warning('Some lines of the employee file contained ' +
                                'errors and were ignored')

        return list(set(employees_list))

    def _load_register_count(self, file_path):
        """Loads and returns the register count.

        Parameters
        ----------
        file_path : :class:`str`
            Path to the register count file.

        """
        if not os.path.isfile(file_path):
            register_count = 0.0
            with io.open(file_path, 'wb') as f:
                data = struct.pack('d', register_count)
                f.write(data)
            abs_path = os.path.abspath(file_path)
            self.logger.warning('register count file not found, creating ' +
                                'one with value 0.0 at '.format(abs_path))
        else:
            with io.open(file_path, 'rb') as f:
                (register_count, ) = struct.unpack('d', f.read(8))
        return register_count

    def _adjust_register_count(self, amount):
        """Adjusts the register count.

        Parameters
        ----------
        amount : number
            Adjustment amount.

        """
        old_register_count = self._register_count
        if amount < 0:
            self._substract_from_register_count(abs(amount))
        else:
            self._add_to_register_count(amount)
        new_register_count = self._register_count
        message = '\n'.join([
            'Adjustment by {}'.format(self.employee_name),
            ' Old count: {:.2f}$'.format(old_register_count),
            ' New count: {:.2f}$'.format(new_register_count),
            'Difference: {:.2f}$'.format(amount)])
        self.count_logger.info(message)

    def _add_to_register_count(self, amount):
        """Adds an amount to the register count.

        Parameters
        ----------
        amount : number
            Amount to add.

        """
        self._register_count += amount
        self._update_register_count()

    def _substract_from_register_count(self, amount):
        """Substracts an amount from the register count.

        Parameters
        ----------
        amount : float
            Amount to substract.

        Raises
        ------
        ValueError
            If the amount to substract is larger than the register
            count.

        """
        count = self._register_count
        # The register amount cannot go negative because it is supposed to
        # represent the quantity of physical money in the register.
        if amount > count:
            raise ValueError(
                'cannot substract amount ({:.2f}) '.format(amount) +
                'greater than register count ({:.2f})'.format(count))
        self._register_count -= amount
        self._update_register_count()

    def _update_register_count(self):
        """Writes the register count to file."""
        with io.open(self.register_count_file_path, 'wb') as f:
            data = struct.pack('d', self._register_count)
            f.write(data)

    def _log_order(self):
        """Logs a completed order."""
        self.transaction_logger.info('{}\n'.format(self.employee_name) +
                                     self.order_to_string())

    def _log_count(self, count):
        """Logs a register count."""
        validate_amount(count, 'count')
        mismatch = count - self._register_count
        message = '\n'.join([
            'Count by {}'.format(self.employee_name),
            'Employee count: {:.2f}$'.format(count),
            'Register count: {:.2f}$'.format(self._register_count),
            '      Mismatch: {:.2f}$'.format(mismatch)])
        self.count_logger.info(message)
