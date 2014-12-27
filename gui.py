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
from Tkinter import Tk, N, S, E, W
from ttk import Frame, Button, Entry, Label
from pyplanck.register import Register


class GUI(Frame):
    def __init__(self, parent, register):
        # TODO: clean this up
        Frame.__init__(self, parent, padding=(3, 3, 3, 3))
        self.parent = parent
        self.register = register
        self.init_ui()

    def init_ui(self):
        # Full screen
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

        items_list = Frame(self, relief="sunken")
        items_list.grid(row=1, column=0, rowspan=3, sticky=(N, S, E, W))

        barcode_field = Entry(self)
        barcode_field.grid(row=0, column=0, sticky=(N, E, W))

        name_label = Label(self, text="Name")
        name_label.grid(row=0, column=1, columnspan=2, sticky=(N, E, W))

        some_button = Button(self, text="Something")
        some_button.grid(row=1, column=1, columnspan=2, sticky=(E, W))

        ok_button = Button(self, text="Ok")
        ok_button.grid(row=2, column=1, sticky=(S, E, W))

        cancel_button = Button(self, text="Cancel")
        cancel_button.grid(row=2, column=2, sticky=(S, E, W))


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
