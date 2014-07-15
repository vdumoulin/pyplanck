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

import io
from utils import (check_is_valid_menu_file_path,
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
        menu = set()
        with io.open(menu_file_path, encoding='utf-8') as menu_file:
            # Read all lines in the file
            lines = menu_file.readlines()
            # Strip all lines from trailing white space and carriage returns
            lines = [line.strip() for line in lines]
            import ipdb; ipdb.set_trace()
        return menu

    def _load_employees(self, employees_file_path):
        employees = set()
        with io.open(employees_file_path, encoding='utf-8') as employees_file:
            lines = employees_file.readlines()
        return employees


if __name__ == "__main__":
    register = Register("sample_menu.txt", "sample_employees.txt")
