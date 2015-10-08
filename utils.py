# -*- coding: utf-8 -*-
"""Utility functions."""
import os

import six


def validate_name(name, type_='name'):
    """Validates a name.

    Parameters
    ----------
    name : :class:`object`
        Name to validate.
    type_ : :class:`str`, optional
        What is being named (e.g. 'item name'). Defaults to ``'name'``.

    Raises
    ------
    ValueError
        If ``name`` is not a non-empty string.

    """
    if not isinstance(name, six.string_types):
        raise ValueError('{} must be a string'.format(type_))
    if not name:
        raise ValueError('{} must not be empty'.format(type_))


def validate_amount(amount, type_='amount'):
    """Validates an amount.

    Parameters
    ----------
    amount : :class:`object`
        Amount to validate.
    type_ : class:`str`, optional
        Type of amount (e.g. 'item price'). Defaults to ``'amount'``.

    Raises
    ------
    ValueError
        If ``amount`` is not a positive number.

    """
    if not isinstance(amount, (float,) + six.integer_types):
        raise ValueError('{} must be a number'.format(type_))
    if amount < 0:
        raise ValueError('{} must be positive'.format(type_))


def validate_item_shortcut(item_shortcut):
    """Validates an item shortcut.

    Parameters
    ----------
    item_shortcut : :class:`object`
        Item shortcut to validate.

    Raises
    ------
    ValueError
        If ``item_shortcut`` is not ``None`` or a not valid name.

    """
    if item_shortcut is not None:
        validate_name(item_shortcut, 'item shortcut')


def validate_employee_level(employee_level):
    """Validates an employee level.

    Parameters
    ----------
    employee_level : :class:`object`

    Raises
    ------
    ValueError
        If ``employee_level`` is not an integer in {0, 1, 2}.

    """
    if not isinstance(employee_level, six.integer_types):
        raise ValueError('employee level must be an integer')
    if employee_level not in (0, 1, 2):
        raise ValueError('employee level must be in {0, 1, 2}')


def validate_file_path(file_path, type_='file'):
    """Validates a file path.

    Parameters
    ----------
    file_path : :class:`str`
        File path to validate.
    type_ : :class:`str`, optional
        What the path corresponds to (e.g. 'menu file'). Defaults to
        ``'file'``.

    Raises
    ------
    ValueError
        If ``file_path`` does not exist.

    """
    if not os.path.isfile(file_path):
        raise ValueError("path for file '{}' does not exist".format(type_))
