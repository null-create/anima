"""
a module containing a variety of tools to analyze and manipulate melody()
objects and chord() lists. these methods will likely be used in other large
classes in the analyze.py and modify.py files.
"""

from __future__ import annotations

from math import floor
from random import randint
from core.constants import NOTES, PITCH_CLASSES


def all_same(a_list: list) -> bool:
    """
    Returns true if all elements in the list are the same
    """
    return True if all(e == a_list[0] for e in a_list) else False


def to_str(pcs: list, octave: int = None, oct_eq: bool = True) -> list:
    """
    Converts a list of pitch class integers to note name strings, with or without
    a supplied octave. Works within one octave or beyond one octave.

    Returns a list of strings representing pitches, i.e. C#, Gb or D5, Ab6, etc.
    """
    scale = []
    if oct_eq:
        pcs_eq = oct_equiv(pcs)
        if octave is None:
            pcs_len = len(pcs_eq)
            for i in range(pcs_len):
                scale.append(PITCH_CLASSES[pcs_eq[i]])
        elif type(octave) == int and 1 < octave < 6:
            pcs_len = len(pcs_eq)
            for i in range(pcs_len):
                note = f"{PITCH_CLASSES[pcs_eq[i]]}{octave}"
                scale.append(note)
        else:
            raise ValueError("octave must be within 2-6!")
    else:
        # this only uses pcs, even if an octave is supplied.
        # NOTES has note strings with assigned octaves.
        # assigning an octave value as an arg is redundant
        # here since a list of any ints such that
        # int < len(NOTES) will do.
        pcs_len = len(pcs)
        for i in range(pcs_len):
            scale.append(NOTES[pcs[i]])
    return scale


def normalize_str(name: str) -> str:
    """
    removes all non-alphanumeric characters from a string and converts
    it to all lowercase characters. This will be useful for mapping
    index values/pitch class integers to their corresponding characters.
    """
    return "".join(ch for ch in name if ch.isalnum()).lower()


def is_pos(num: int) -> bool:
    """
    helper method to tell if an int is positive or negative.
    zero counts as positive here because pitch class notion
    starts with 0. 0 = 'C', 1 = 'C#', etc.
    """
    return True if num >= 0 else False


def remove_oct(a_note: str) -> str:
    """
    removes octave integer from a note name string.
    shouldn't be called directly.
    """
    # split single note into two or three parts:
    # either name + oct or name + acc + oct.
    n = [char for char in a_note]
    if len(n) == 3:
        return f"{n[0]}{n[1]}"
    elif len(n) == 2 and n[1] == "b" or n[1] == "#":
        return f"{n[0]}{n[1]}"
    else:
        return n[0]


def oct_equiv(pitch: int | list) -> int | list:
    """
    Octave equivalence. Handles either a single int or list[int].
    Keeps a single pitch class integer within span of an octave (0 - 11).

    Pitch should be an int or a list[int]

    Returns either a modified int or list[int]
    """
    if type(pitch) == int:
        pitch %= 12
    elif type(pitch) == list:
        pitch_len = len(pitch)
        for p in range(pitch_len):
            if pitch[p] > 11 or pitch[p] < 0:
                pitch[p] %= 12
    else:
        raise TypeError(
            f"must be single int or list[int]. supplied arg is type: {type(pitch)}"
        )
    return pitch


def _scale(rhythms: float, diff: float, revert: bool = False) -> float:
    """
    Scale the given rhythm to the given difference. Set revert to True
    if you want to revert the rhythmic values to their original values at generation time.
    """
    if revert:
        rhythms /= diff
    else:
        rhythms *= diff
    return rhythms


def scale_to_tempo(tempo: float, rhythms, revert: bool = False) -> float | list:
    """
    Converts a supplied float or list[float] of rhythmic values to
    actual value in seconds at a given tempo. can also convert back to base
    rhythmic values of revert is set to True.

    Returns either a single float or list[float]

    ex: [base] q = 60, quarter_note = 1 sec,
        [new tempo] q = 72, quarter_note = 0.8333(...) sec

    60/72 = .83 - The result becomes the converter value to multiply or divide
    all supplied durations against to get the new tempo-accurate durations in seconds.

    NOTE: the round() method keeps the results within three decimal places to help
          facilitate clearer sheet music generation.
    """
    diff = 60 / tempo
    if type(rhythms) == float:
        rhythms = round(_scale(rhythms, diff, revert), 3)
    elif type(rhythms) == list:
        rhythm_len = len(rhythms)
        for i in range(rhythm_len):
            rhythms[i] = round(_scale(rhythms[i], diff, revert), 3)
    else:
        raise TypeError("incorrect input type. must be single float or list of floats!")
    return rhythms


def scale_limit(given_total_items: int) -> int:
    """
    scales repetition limits according to total notes
    higher total == fewer reps, basically
    """
    """
    TODO: look at proportional scaling methods...
    """
    if given_total_items < 1:
        raise ValueError("total cannot be less than 1")

    rep_limit = 0
    if 1 <= given_total_items <= 10:
        given_total_items = randint(1, 3)
    elif 11 <= given_total_items <= 100:
        rep_limit = randint(1, floor(given_total_items * 0.2))
    elif 101 <= given_total_items <= 300:
        rep_limit = randint(1, floor(given_total_items * 0.075))
    elif 301 <= given_total_items <= 500:
        rep_limit = randint(1, floor(given_total_items * 0.05))
    elif 501 <= given_total_items <= 700:
        rep_limit = randint(1, floor(given_total_items * 0.035))
    elif 701 <= given_total_items <= 1000:
        rep_limit = randint(1, floor(given_total_items * 0.02))
    elif given_total_items > 1000:
        rep_limit = randint(1, floor(given_total_items * 0.001))

    return rep_limit
