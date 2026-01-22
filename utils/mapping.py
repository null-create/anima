"""
This module handles mapping functions when converting raw data to index numbers,
which will be used to map against newNotes()'s generated source scale in newMelody()
"""

from __future__ import annotations

from core.constants import ALPHABET


def float_to_int(data: list[float]) -> list[int]:
    """
    Converts an array of floats to an array of ints
    """
    result = []
    for i in range(len(data)):
        result.append(int(data[i]))
    return result


def scale_the_scale(data: list[int]) -> list[int]:
    """
    Scales individual data set integers such that data[i] <= len(data)-1

    Returns inputted list[int] with any ints i > len(data) 1 altered to
    adhere to this limit. This will keep the newly inputted data array's
    values within the bounds of the scale array. These values function
    as a collection of index numbers to sequentially map to a new source
    scale to generate melodic ideas.

    """
    for i in range(len(data)):
        if data[i] > len(data) - 1:
            data[i] %= len(data) - 1
    return data


def letters_to_numbers(letters: str) -> list[int]:
    """
    Takes a string of any length as an argument,
    then maps the letters to index numbers, which will then be
    translated into notes (strings). Accounts for number chars
    as well
    """
    letters_list = list(letters)
    numbers = []
    for i in range(len(letters_list)):
        # make all uppercase characters lowercase
        if letters_list[i].isupper():
            letters_list[i] = letters_list[i].lower()
        if letters_list[i] in ALPHABET:
            numbers.append(ALPHABET.index(letters_list[i]))
        # is this str a str of an int???
        elif letters_list[i].isnumeric():
            # convert to int, keep within bounds of len(letters)-1,
            # then add to list.
            num = int(letters[i])
            if num > len(ALPHABET) - 1:
                num %= len(ALPHABET) - 1
            numbers.append(num)
    return numbers


def hex_to_int_list(hex_str: str) -> list[int]:
    """
    Converts a prefixed hex number to an array of integers.
    """
    hex_int = int(hex_str, 0)
    return [int(x) for x in str(hex_int)]


def map_data(data, data_type: str):
    """
    Wrapper method to map data used by newMelody()

    Returns modified data and modified melody() object, or -1
    on failure. melody() object has original source data saved.
    """
    if data_type == "int":
        data_scaled = scale_the_scale(data)
    elif data_type == "float":
        data_scaled = scale_the_scale(float_to_int(data))
    elif data_type == "chars":
        data_scaled = letters_to_numbers(data)
    elif data_type == "hex":
        data_scaled = hex_to_int_list(data)
    else:
        raise ValueError(f"unsupported data type: {data_type}")
    return data_scaled
