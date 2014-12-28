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
from Tkinter import Tk, N, S, E, W, StringVar
from ttk import Frame, Button, Entry, Label
from pyplanck.register import Register
from pyplanck.exceptions import CredentialException, ItemNotFoundException


class GUI(Frame):
    def __init__(self, parent, register):
        # TODO: clean this up
        Frame.__init__(self, parent, padding=(3, 3, 3, 3))
        self.parent = parent
        self.register = register
        self.logger = register.get_events_logger()
        self.init_ui()

    def login(self, token):
        try:
            self.register.login_employee(token)
        except CredentialException:
            self.logger.warning("invalid employee token '" + token + "', " +
                                "unable to login")

    def logout(self):
        self.register.logout_employee()

    def print_count(self):
        try:
            print self.register.get_register_count()
        except CredentialException:
            self.logger.warning("insufficient privileges to print register " +
                                "count")

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

    def parse_barcode_field(self, event):
        command = self.barcode_field.get().strip()
        self.barcode_var.set("")
        tokens = command.split(" ")
        if tokens[0] == "login":
            if len(tokens) < 2:
                self.logger.warning("need a login token")
                return None
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
                return None
            self.remove(tokens[1])
        elif tokens[0] == "adjust_count":
            if len(tokens) < 2:
                self.logger.warning("need an adjustment amount")
                return None
            self.adjust(tokens[1])
        elif tokens[0] == "custom":
            if len(tokens) < 3:
                self.logger.warning("need an name and a price")
                return None
            try:
                self.add_custom(tokens[1], float(tokens[2]))
            except ValueError:
                self.logger.warning("price is not valid")
        elif tokens[0] == "checkout":
            self.checkout()
        elif tokens[0] == "count":
            if len(tokens) < 2:
                self.logger.warning("need an register count")
                return None
            else:
                self.count(tokens[1])
        else:
            if tokens[0] != "":
                self.add(tokens[0])

    def init_ui(self):
        # Window configuration
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.parent.geometry(
            '%dx%d+%d+%d' % (screen_width, screen_height, 0, 0))
        self.parent.title("Caisse Planck")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

        self.items_list = Frame(self, relief="sunken")
        self.items_list.grid(row=1, column=0, rowspan=3, sticky=(N, S, E, W))

        self.barcode_var = StringVar(self)
        self.barcode_field = Entry(self, textvariable=self.barcode_var)
        self.barcode_field.bind("<KeyPress-Return>", self.parse_barcode_field)
        self.barcode_field.grid(row=0, column=0, sticky=(N, E, W))

        self.name_var = StringVar(self, value="Name")
        self.name_label = Label(self, textvar=self.name_var)
        self.name_label.grid(row=0, column=1, columnspan=2, sticky=(N, E, W))

        self.some_button = Button(self, text="Something")
        self.some_button.grid(row=1, column=1, columnspan=2, sticky=(E, W))

        self.ok_button = Button(self, text="Ok")
        self.ok_button.grid(row=2, column=1, sticky=(S, E, W))

        self.cancel_button = Button(self, text="Cancel")
        self.cancel_button.grid(row=2, column=2, sticky=(S, E, W))

        # Put focus in barcode field
        self.barcode_field.focus_set()


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

    root = Tk()
    gui = GUI(root, register)
    root.mainloop()
