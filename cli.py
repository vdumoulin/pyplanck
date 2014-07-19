# -*- coding: utf-8 -*-
"""
Command-line interface for the register
"""
__authors__ = "Vincent Dumoulin"
__copyright__ = "Copyright 2014, Vincent Dumoulin"
__credits__ = ["Vincent Dumoulin"]
__license__ = "GPL v2"
__maintainer__ = "Vincent Dumoulin"
__email__ = "vincent.dumoulin@umontreal.ca"

import argparse
from pyplanck.register import Register
from pyplanck.exceptions import CredentialException, ItemNotFoundException


class CLI(object):
    def quit(self):
        self.end = True
    
    def login(self, token):
        try:
            self.register.login_employee(token)
            self.prompt = self.register.get_employee_name() + " > "
        except CredentialException:
            self.logger.warning("invalid employee token '" + token + "', " +
                                "unable to login")

    def logout(self):
        self.register.logout_employee()
        self.prompt = self.default_prompt

    def print_count(self):
        try:
            print self.register.get_register_count()
        except CredentialException:
            self.logger.warning("insufficient privileges to print register " +
                                "count")

    def print_order(self):
        try:
            print self.register.order_to_string()
        except CredentialException:
            self.logger.warning("insufficient privileges to print current " +
                                "order")

    def add(self, token):
        try:
            self.register.add(token)
        except CredentialException:
            self.logger.warning("insufficient privileges to add an item")
        except ValueError:
            pass

    def add_custom(self, name, price):
        try:
            self.register.add_custom(name, price)
        except CredentialException:
            self.logger.warning("insufficient privileges to add a custom item")
        except ValueError as e:
            self.logger.warning(e.__str__)

    def remove(self, token):
        try:
            self.register.remove(token)
        except CredentialException:
            self.logger.warning("insufficient privileges to scan an item")
        except ValueError:
            self.logger.warning("token does not correspond to any item")
        except ItemNotFoundException:
            self.logger.warning("item not in order, unable to remove it")

    def adjust(self, token):
        try:
            amount = float(token)
            self.register.adjust(amount)
        except CredentialException:
            self.logger.warning("insufficient privileges to adjust register " +
                                "count")
        except ValueError as e:
            self.logger.warning("invalid adjustment amount: " + e)

    def checkout(self):
        try:
            self.register.checkout_order()
        except CredentialException:
            self.logger.warning("insufficient privileges to checkout order")

    def count(self, count_string):
        try:
            count = float(count_string)
            self.register.count_register(count)
        except CredentialException:
            self.logger.warning("insufficient privileges to count register")
        except ValueError as e:
            self.logger.warning("invalid count: " + e)

    valid_commands = {
        'quit': quit,
        'login': login,
    }

    def __init__(self, register, default_prompt="caisse-planck > "):
        self.register = register
        self.logger = register.get_events_logger()
        self.default_prompt = default_prompt
        self.prompt = self.default_prompt
        self.end = False

    def start(self):
        while not self.end:
            command = raw_input(self.prompt).strip()
            tokens = command.split(" ")
            if tokens[0] == "q":
                self.quit()
            elif tokens[0] == "login":
                if len(tokens) < 2:
                    self.logger.warning("need a login token")
                    continue
                self.login(tokens[1])
            elif tokens[0] == "logout":
                self.logout()
            elif tokens[0] == "print_count":
                self.print_count()
            elif tokens[0] == "print_order":
                self.print_order()
            elif tokens[0] == "remove":
                if len(tokens) < 2:
                    self.logger.warning("need an item to remove")
                    continue
                self.remove(tokens[1])
            elif tokens[0] == "adjust_count":
                if len(tokens) < 2:
                    self.logger.warning("need an adjustment amount")
                    continue
                self.adjust(tokens[1])
            elif tokens[0] == "custom":
                if len(tokens) < 3:
                    self.logger.warning("need an name and a price")
                    continue
                try:
                    self.add_custom(tokens[1], float(tokens[2]))
                except ValueError:
                    self.logger.warning("price is not valid")
            elif tokens[0] == "checkout":
                self.checkout()
            elif tokens[0] == "count":
                if len(tokens) < 2:
                    self.logger.warning("need an register count")
                    continue
                else:
                    self.count(tokens[1])
            else:
                if tokens[0] != "":
                    self.add(tokens[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--menu_path", help="path to the menu file",
                        type=str, default="sample_menu.txt")
    parser.add_argument("-e", "--employees_path", help="path to the " +
                        "employees file", type=str,
                        default="sample_employees.txt")
    parser.add_argument("-r", "--register_count_path", help="path to the " +
                        "register count file", type=str,
                        default="sample_register_count.bin")
    parser.add_argument("-l", "--log_path", help="path to the " +
                        "directory of log files", type=str,
                        default="./")
    args = parser.parse_args()

    menu_path = args.menu_path
    employees_path = args.employees_path
    register_count_path = args.register_count_path
    log_path = args.log_path

    register = Register(menu_file_path=menu_path,
                        employees_file_path=employees_path,
                        register_count_file_path=register_count_path,
                        log_path=log_path)

    cli = CLI(register=register)
    cli.start()
