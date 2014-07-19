# -*- coding: utf-8 -*-
"""
Tests for Register class
"""
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

import io, os, struct, logging
from nose.tools import raises, with_setup
from pyplanck.register import Register
from pyplanck.item import Item
from pyplanck.employee import Employee
from pyplanck.exceptions import CredentialException, ItemNotFoundException

# No logging for unit tests
logging.disable(logging.CRITICAL)


def setup_module():
    if not os.path.isdir('tmp'):
        os.makedirs('tmp')
    with io.open('tmp/register_count.bin', 'wb') as f:
        data = struct.pack('d', 11.57)
        f.write(data)
    with io.open('tmp/menu.txt', 'w') as f:
        f.write(u"#Candy|1.00\n001|Chocolate bar\n002|Gum|0.75\n" +
                u"#Beverage|0.50\n003|Hot chocolate|0.50|hc\n")
    with io.open('tmp/employees.txt', 'w') as f:
        f.write(u"Admin|2222|admin|2\nEmployee|1111|employee|1\n" +
                u"Guest|0000|guest|0\n")


def teardown_module():
    os.remove('tmp/menu.txt')
    os.remove('tmp/employees.txt')
    os.remove('tmp/register_count.bin')
    try:
        os.rmdir('tmp')
    except OSError:
        pass


def test_register_reads_menu():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    menu = register.menu
    correct_menu = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("Gum", 0.75, "002", category="Candy", shortcut=None),
        Item("Hot chocolate", 0.5, "003", category="Beverage", shortcut="hc")
    ]

    assert all([item in menu for item in correct_menu])
    assert all([item in correct_menu for item in menu])

    for item in correct_menu:
        corresponding_item = menu[menu.index(item)]
        assert item.get_name() == corresponding_item.get_name()
        assert item.get_price() == corresponding_item.get_price()
        assert item.get_barcode() == corresponding_item.get_barcode()
        assert item.get_category() == corresponding_item.get_category()
        assert item.get_shortcut() == corresponding_item.get_shortcut()


def test_register_reads_employees_list():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    employees = register.employees
    correct_employees = [
        Employee("Admin", "2222", "admin", 2),
        Employee("Employee", "1111", "employee", 1),
        Employee("Guest", "0000", "guest", 0)
    ]

    assert all([employee in employees for employee in correct_employees])
    assert all([employee in correct_employees for employee in employees])

    for employee in correct_employees:
        corresponding_employee = employees[employees.index(employee)]
        assert employee.get_name() == corresponding_employee.get_name()
        assert employee.get_barcode() == corresponding_employee.get_barcode()
        assert employee.get_code() == corresponding_employee.get_code()
        assert employee.get_level() == corresponding_employee.get_level()


def test_register_reads_register_count():
    with io.open('tmp/register_count.bin', 'wb') as f:
        data = struct.pack('d', 11.57)
        f.write(data)
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    assert register.register_count == 11.57


def test_register_initial_employee_is_none():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    assert register.employee is None


def test_register_initial_order_is_empty():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    assert register.order == {}


def test_register_login_per_barcode():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    employee = Employee("Admin", "2222", "admin", 2)
    register.login_employee("2222")
    assert register.employee == employee


def test_register_login_per_code():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    employee = Employee("Admin", "2222", "admin", 2)
    register.login_employee("admin")
    assert register.employee == employee


@raises(CredentialException)
def test_register_raises_exception_on_invalid_login():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("gum")


def test_register_logout_employee():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.logout_employee()
    assert register.employee is None


def test_register_get_employee_name_returns_employee_name():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    assert register.get_employee_name() == "Admin"


def test_register_get_employee_name_returns_none():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    assert register.get_employee_name() == "None"


def test_register_add():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.add("001")

    correct_added_item = Item("Chocolate bar", 1.0, "001", category="Candy",
                              shortcut=None)
    correct_quantity = 1
    assert register.order == {correct_added_item: correct_quantity}


def test_register_add_custom():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.add_custom("gum", 0.47)

    correct_added_item = Item("gum", 0.47, "custom_gum", category="Custom",
                              shortcut=None)
    correct_quantity = 1
    assert register.order == {correct_added_item: correct_quantity}


def test_register_remove():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")

    items = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    ]
    initial_order = {items[0]: 1, items[1]: 1}
    final_order = {items[1]: 1}

    register.order = initial_order
    register.remove("001")
    assert register.order == final_order


def test_register_remove_custom():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")

    items = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("gum", 0.47, "custom_gum", category="Custom", shortcut=None)
    ]
    initial_order = {items[0]: 1, items[1]: 1}
    final_order = {items[0]: 1}

    correct_added_item = Item("gum", 0.47, "custom_gum", category="Custom",
                              shortcut=None)
    register.order = initial_order
    register.remove("custom_gum")
    assert register.order == final_order


def test_register_clear_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")

    items = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    ]
    initial_order = {items[0]: 1, items[1]: 1}
    final_order = {}

    register.order = initial_order
    register.clear_order()
    assert register.order == final_order


def test_register_checkout_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")

    items = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    ]
    order = {items[0]: 1, items[1]: 1}

    register.register_count = 1.5
    register.order = order
    register.checkout_order()
    assert register.register_count == 3.25
    assert register.order == {}
    with io.open('tmp/register_count.bin', 'rb') as f:
        (register_count, ) = struct.unpack('d', f.read(8))
    assert register_count == 3.25


def test_register_order_to_string():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")

    items = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    ]
    order = {items[0]: 1, items[1]: 1}
    register.order = order

    representation = register.order_to_string().split('\n')
    correct_representation = ['Chocolate bar x 1', 'Gum x 1']
    assert all([line in correct_representation for line in representation])
    assert all([line in representation for line in correct_representation])


def test_register_get_register_count():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.register_count = 11.57
    assert register.get_register_count() == 11.57


@raises(ValueError)
def test_register_count_register_rejects_negative_counts():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.count_register(-1)


def test_register_adjust():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.register_count = 2.5
    register.adjust(2.5)
    assert register.register_count == 5.0
    with io.open('tmp/register_count.bin', 'rb') as f:
        (register_count, ) = struct.unpack('d', f.read(8))
    assert register_count == 5.0


def test_register_find_by_barcode():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = register._find_in_menu("001")
    assert item == Item("Chocolate bar", 1.0, "001", category="Candy",
                        shortcut=None)


def test_register_find_by_shortcut():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = register._find_in_menu("hc")
    assert item == Item("Hot chocolate", 0.5, "003", category="Beverage",
                        shortcut="hc")


@raises(ValueError)
def test_register_find_raises_exception_on_nonexistent_item():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = register._find_in_menu("nothing")


def test_register_verify_credential_allows_right_employee():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register._verify_credentials(Employee("E", "1111", "employee", 1), 0)
    register._verify_credentials(Employee("E", "1111", "employee", 1), 1)


@raises(CredentialException)
def test_register_verify_credential_raises_exception_on_wrong_employee():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register._verify_credentials(Employee("E", "1111", "employee", 1), 2)


@raises(CredentialException)
def test_register_verify_credential_raises_exception_on_none():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register._verify_credentials(None, 1)


def test_register_verify_credential_can_allow_none():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register._verify_credentials(None, None)


def test_register_add_existing_item_to_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    order = {item: 1}
    register.order = order

    register._add_to_order(item)
    assert register.order == {item: 2}


def test_register_add_new_item_to_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    items = [
        Item("Chocolate bar", 1.0, "001", category="Candy", shortcut=None),
        Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    ]
    order = {items[0]: 1}
    register.order = order

    register._add_to_order(items[1])
    assert register.order == {items[0]: 1, items[1]: 1}


def test_register_remove_duplicate_item_from_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    order = {item: 2}
    register.order = order

    register._remove_from_order(item)
    assert register.order == {item: 1}


def test_register_remove_unique_item_from_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    order = {item: 1}
    register.order = order

    register._remove_from_order(item)
    assert register.order == {}


@raises(ItemNotFoundException)
def test_register_remove_raises_exception_if_item_not_in_order():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    item = Item("Gum", 0.75, "002", category="Candy", shortcut=None)
    order = {}
    register.order = order

    register._remove_from_order(item)


@raises(ValueError)
def test_register_substract_raises_exception_if_amount_too_large():
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")
    register.register_count = 1
    register._substract_from_register_count(2)


def test_register_update_register_count():
    with io.open('tmp/register_count.bin', 'wb') as f:
        data = struct.pack('d', 11.57)
        f.write(data)
    register = Register('tmp/menu.txt', 'tmp/employees.txt',
                        'tmp/register_count.bin')
    register.login_employee("admin")

    register.register_count = 2.0
    register._update_register_count()
    with io.open('tmp/register_count.bin', 'rb') as f:
        (register_count, ) = struct.unpack('d', f.read(8))
    assert register_count == 2.0
