# -*- coding: utf-8 -*-
"""Tests for Register class."""
import io
import os
import struct
import logging
import shutil
import tempfile
from collections import OrderedDict

from nose.tools import raises, assert_equal

from pyplanck.register import Register
from pyplanck.immutables import Item, Employee
from pyplanck.exceptions import CredentialException, ItemNotFoundException

# No logging for unit tests
logging.disable(logging.CRITICAL)


class TestRegister(object):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.mkdtemp()
        cls.menu_path = os.path.join(cls.tempdir, 'menu.txt')
        cls.employees_path = os.path.join(cls.tempdir, 'employees.txt')
        cls.count_path = os.path.join(cls.tempdir, 'register_count.bin')
        with io.open(cls.menu_path, 'w') as f:
            f.write(u'#Candy|1.00\n001|Chocolate bar\n002|Gum|0.75\n' +
                    u'#Beverage|0.50\n003|Hot chocolate|0.50|hc\n')
        with io.open(cls.employees_path, 'w') as f:
            f.write(u'Admin|2222|admin|2\nEmployee|1111|employee|1\n' +
                    u'Guest|0000|guest|0\n')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)

    def setUp(self):
        with io.open(self.count_path, 'wb') as f:
            data = struct.pack('d', 11.57)
            f.write(data)
        self.register = Register(self.menu_path, self.employees_path,
                                 self.count_path, self.tempdir)

    def test_reads_menu(self):
        menu = self.register.menu
        correct_menu = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                        Item('Gum', 0.75, '002', 'Candy', None),
                        Item('Hot chocolate', 0.5, '003', 'Beverage', 'hc')]
        assert_equal(set(menu), set(correct_menu))

    def test_reads_employees_list(self):
        employees = self.register.employees
        correct_employees = [Employee('Admin', '2222', 'admin', 2),
                             Employee('Employee', '1111', 'employee', 1),
                             Employee('Guest', '0000', 'guest', 0)]
        assert_equal(set(employees), set(correct_employees))

    def test_reads_register_count(self):
        assert_equal(self.register._register_count, 11.57)

    def test_initial_employee_is_none(self):
        assert_equal(self.register.employee, None)

    def test_initial_order_is_empty(self):
        assert_equal(self.register.order_dict, OrderedDict())

    def test_login_per_barcode(self):
        employee = Employee('Admin', '2222', 'admin', 2)
        self.register.login_employee('2222')
        assert_equal(self.register.employee, employee)

    def test_login_per_code(self):
        employee = Employee('Admin', '2222', 'admin', 2)
        self.register.login_employee('admin')
        assert_equal(self.register.employee, employee)

    @raises(CredentialException)
    def test_raises_exception_on_invalid_login(self):
        self.register.login_employee('gum')

    def test_logout_employee(self):
        self.register.employee = self.register.employees[0]
        self.register.logout_employee()
        assert_equal(self.register.employee, None)

    def test_employee_name_returns_employee_name(self):
        self.register.login_employee('admin')
        assert_equal(self.register.employee_name, 'Admin')

    def test_employee_name_returns_none(self):
        assert_equal(self.register.employee_name, 'None')

    def test_add(self):
        self.register.login_employee('admin')
        self.register.add('001')
        correct_added_item = Item('Chocolate bar', 1.0, '001', 'Candy', None)
        correct_quantity = 1
        correct_dict = OrderedDict([(correct_added_item, correct_quantity)])
        assert_equal(self.register.order_dict, correct_dict)

    def test_add_custom(self):
        self.register.login_employee('admin')
        self.register.add_custom('gum', 0.47)
        correct_added_item = Item('gum', 0.47, 'custom_gum', 'Custom', None)
        correct_quantity = 1
        correct_dict = OrderedDict([(correct_added_item, correct_quantity)])
        assert_equal(self.register.order_dict, correct_dict)

    def test_remove(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('Gum', 0.75, '002', 'Candy', None)]
        self.register.order_dict = OrderedDict([(items[0], 1), (items[1], 1)])
        self.register.remove('001')
        assert_equal(self.register.order_dict, OrderedDict([(items[1], 1)]))

    def test_remove_custom(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('gum', 0.47, 'custom_gum', 'Custom', None)]
        self.register.order_dict = OrderedDict([(items[0], 1), (items[1], 1)])
        self.register.remove('custom_gum')
        assert_equal(self.register.order_dict, OrderedDict([(items[0], 1)]))

    def test_order(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('gum', 0.47, 'custom_gum', 'Custom', None)]
        order = ((items[0], 1), (items[1], 1))
        self.register.order_dict = OrderedDict(order)
        assert_equal(self.register.order, order)

    def test_clear_order(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('Gum', 0.75, '002', 'Candy', None)]
        self.register.order_dict = OrderedDict([(items[0], 1), (items[1], 1)])
        self.register.clear_order()
        assert_equal(self.register.order_dict, OrderedDict())

    def test_checkout_order(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('Gum', 0.75, '002', 'Candy', None)]
        self.register._register_count = 1.5
        self.register.order_dict = OrderedDict([(items[0], 1), (items[1], 1)])
        self.register.checkout_order()
        assert_equal(self.register._register_count, 3.25)
        assert_equal(self.register.order_dict, OrderedDict())
        with io.open(self.count_path, 'rb') as f:
            (register_count, ) = struct.unpack('d', f.read(8))
        assert_equal(register_count, 3.25)

    def test_checkout_empty_order(self):
        self.register.login_employee('admin')
        self.register._register_count = 1.5
        self.register.order_dict = OrderedDict()
        self.register.checkout_order()
        assert_equal(self.register._register_count, 1.5)
        assert_equal(self.register.order_dict, OrderedDict())
        with io.open(self.count_path, 'rb') as f:
            register_count, = struct.unpack('d', f.read(8))
        assert_equal(register_count, 1.5)

    def test_order_to_string(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('Gum', 0.75, '002', 'Candy', None)]
        self.register.order_dict = OrderedDict([(items[0], 1), (items[1], 1)])
        representation = self.register.order_to_string().split('\n')
        correct_representation = ['Chocolate bar x 1', 'Gum x 1']
        assert_equal(set(representation), set(correct_representation))

    def test_order_total_non_empty_order(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('gum', 0.47, 'custom_gum', 'Custom', None)]
        self.register.order_dict = OrderedDict([(items[0], 1), (items[1], 1)])
        assert_equal(self.register.order_total, 1.47)

    def test_order_total_empty_order(self):
        self.register.login_employee('admin')
        self.register.order_dict = OrderedDict()
        assert_equal(self.register.order_total, 0.0)

    def test_count(self):
        self.register.login_employee('admin')
        self.register._register_count = 11.57
        assert_equal(self.register.register_count, 11.57)

    @raises(ValueError)
    def test_count_register_rejects_negative_counts(self):
        self.register.login_employee('admin')
        self.register.count_register(-1)

    def test_adjust(self):
        self.register.login_employee('admin')
        self.register._register_count = 2.5
        self.register.adjust(2.5)
        assert_equal(self.register._register_count, 5.0)
        with io.open(self.count_path, 'rb') as f:
            register_count, = struct.unpack('d', f.read(8))
        assert_equal(register_count, 5.0)

    def test_find_by_barcode(self):
        self.register.login_employee('admin')
        item = self.register._find_in_menu('001')
        assert_equal(item, Item('Chocolate bar', 1.0, '001', 'Candy', None))

    def test_find_by_shortcut(self):
        self.register.login_employee('admin')
        item = self.register._find_in_menu('hc')
        assert_equal(item, Item('Hot chocolate', 0.5, '003', 'Beverage', 'hc'))

    @raises(ValueError)
    def test_find_raises_exception_on_nonexistent_item(self):
        self.register.login_employee('admin')
        self.register._find_in_menu('nothing')

    def test_verify_credential_allows_right_employee(self):
        self.register._verify_credentials(
            Employee('E', '1111', 'employee', 1), 0)
        self.register._verify_credentials(
            Employee('E', '1111', 'employee', 1), 1)

    @raises(CredentialException)
    def test_verify_credential_raises_exception_on_wrong_employee(self):
        self.register._verify_credentials(
            Employee('E', '1111', 'employee', 1), 2)

    @raises(CredentialException)
    def test_verify_credential_raises_exception_on_none(self):
        self.register._verify_credentials(None, 1)

    def test_verify_credential_can_allow_none(self):
        self.register._verify_credentials(None, None)

    def test_add_existing_item_to_order(self):
        self.register.login_employee('admin')
        item = Item('Gum', 0.75, '002', 'Candy', None)
        self.register.order_dict = OrderedDict([(item, 1)])
        self.register._add_to_order(item)
        assert_equal(self.register.order_dict, OrderedDict([(item, 2)]))

    def test_add_new_item_to_order(self):
        self.register.login_employee('admin')
        items = [Item('Chocolate bar', 1.0, '001', 'Candy', None),
                 Item('Gum', 0.75, '002', 'Candy', None)]
        self.register.order_dict = OrderedDict([(items[0], 1)])
        self.register._add_to_order(items[1])
        assert_equal(self.register.order_dict,
                     OrderedDict([(items[0], 1), (items[1], 1)]))

    def test_remove_duplicate_item_from_order(self):
        self.register.login_employee('admin')
        item = Item('Gum', 0.75, '002', 'Candy', None)
        self.register.order_dict = OrderedDict([(item, 2)])
        self.register._remove_from_order(item)
        assert_equal(self.register.order_dict, OrderedDict([(item, 1)]))

    def test_remove_unique_item_from_order(self):
        self.register.login_employee('admin')
        item = Item('Gum', 0.75, '002', 'Candy', None)
        self.register.order_dict = OrderedDict([(item, 1)])
        self.register._remove_from_order(item)
        assert_equal(self.register.order_dict, OrderedDict())

    @raises(ItemNotFoundException)
    def test_remove_raises_exception_if_item_not_in_order(self):
        self.register.login_employee('admin')
        item = Item('Gum', 0.75, '002', 'Candy', None)
        self.register.order_dict = OrderedDict()
        self.register._remove_from_order(item)

    @raises(ValueError)
    def test_substract_raises_exception_if_amount_too_large(self):
        self.register.login_employee('admin')
        self.register._register_count = 1
        self.register._substract_from_register_count(2)

    def test_update_register_count(self):
        self.register.login_employee('admin')
        self.register._register_count = 2.0
        self.register._update_register_count()
        with io.open(self.count_path, 'rb') as f:
            register_count, = struct.unpack('d', f.read(8))
        assert_equal(register_count, 2.0)
