"""
Module for modifying composition() objects and musical elements.

TODO:

    Implement a method to repeat an entire section of music and append it to a given MIDI file

    Implement a method to take a given section of music and modify notes and rhythms at random (or
    with specified user input)

    Implement a method to add notes and rhythms to the end of the file.
"""

from __future__ import annotations
from typing import List, Union
from random import randint, shuffle

from utils.tools import to_str, is_pos, oct_equiv
from containers.melody import Melody
from containers.chord import Chord
from core.constants import NOTES, MIN_TRANSPOSITION, MAX_TRANSPOSITION


def transpose(
    pcs: List[int], dist: Union[int, List[int]], oct_eq: bool = True
) -> List[int]:
    """
    Transpose a list of pitch classes using a supplied interval or list of intervals.

    Args:
        pcs: List of pitch class integers
        dist: Single interval (int) or list of intervals to transpose by
        oct_eq: If True, keep results within 0-11 range (octave equivalence)

    Returns:
        Modified list of pitch class integers
    """
    result = pcs.copy()

    if isinstance(dist, int):
        result = [pc + dist for pc in result]
    elif isinstance(dist, list):
        if len(dist) != len(pcs):
            raise ValueError(
                f"Interval list length ({len(dist)}) must match "
                f"pitch class list length ({len(pcs)})"
            )
        result = [pc + interval for pc, interval in zip(result, dist)]
    else:
        raise TypeError(f"Distance must be int or list[int]. Got: {type(dist)}")

    if oct_eq:
        result = oct_equiv(result)

    return result


def is_valid_transposition(dist: int) -> bool:
    """
    Check if transposition distance is valid.

    Args:
        dist: Transposition distance in semitones

    Returns:
        True if distance is within valid range
    """
    return MIN_TRANSPOSITION <= dist <= MAX_TRANSPOSITION


def transpose_melody(notes: List[str], dist: int) -> List[str]:
    """
    Transpose a melody by a given distance.

    Args:
        notes: List of note strings with octaves
        dist: Transposition distance in semitones (1-11)

    Returns:
        New list of transposed note strings
    """
    if not is_valid_transposition(dist):
        raise ValueError(
            f"Distance must be between {MIN_TRANSPOSITION} and {MAX_TRANSPOSITION}. "
            f"Got: {dist}"
        )

    indices = [NOTES.index(note) for note in notes]
    transposed_indices = transpose(indices, dist=dist, oct_eq=False)
    return to_str(transposed_indices, oct_eq=False)


def transpose_chords(chords: List[Chord], dist: int) -> List[Chord]:
    """
    Transpose a list of chords by a given distance.

    Args:
        chords: List of Chord objects
        dist: Transposition distance in semitones (1-11)

    Returns:
        List of transposed Chord objects
    """
    if not is_valid_transposition(dist):
        raise ValueError(
            f"Distance must be between {MIN_TRANSPOSITION} and {MAX_TRANSPOSITION}. "
            f"Got: {dist}"
        )

    result = []
    for chord in chords:
        new_chord = Chord(instrument=chord.instrument, tempo=chord.tempo)
        new_chord.notes = transpose_melody(chord.notes, dist)
        new_chord.rhythm = chord.rhythm
        new_chord.dynamic = chord.dynamic
        new_chord.info = chord.info
        new_chord.pcs = chord.pcs
        new_chord.source_data = chord.source_data
        new_chord.source_notes = chord.source_notes
        result.append(new_chord)

    return result


def retrograde(orig_melody: Melody) -> Melody:
    """
    Reverse the melodic parameters in a melody object.

    Args:
        orig_melody: Melody object to reverse

    Returns:
        New melody object is a deep copy of the original with notes, rhythms,
        and dynamics reversed.
    """
    retro = orig_melody.copy()
    retro.notes = list(reversed(orig_melody.notes))
    retro.rhythms = list(reversed(orig_melody.rhythms))
    retro.dynamics = list(reversed(orig_melody.dynamics))
    return retro


def invert(notes: List[str]) -> List[str]:
    """
    Invert a melody by inverting all intervals.

    Args:
        notes: List of note strings with octaves

    Returns:
        New list of inverted note strings
    """
    indices = [NOTES.index(note) for note in notes]
    intervals = [indices[i] - indices[i - 1] for i in range(1, len(indices))]

    inverted_intervals = [-interval for interval in intervals]

    result_indices = [indices[0]]
    for interval in inverted_intervals:
        result_indices.append(result_indices[-1] + interval)

    return to_str(result_indices, oct_eq=False)


def retrograde_inversion(melody: Melody) -> Melody:
    """
    Apply both retrograde and inversion operations.

    Args:
        melody: Melody object to transform

    Returns:
        New Melody object with retrograde inversion applied
    """
    ret = retrograde(melody)
    ret.notes = invert(ret.notes)
    return ret


def fragment(melody: Melody) -> Melody:
    """
    Extract a random subset of notes, rhythms, and dynamics from a melody.

    Args:
        melody: Original melody to fragment

    Returns:
        New Melody object containing the fragment
    """
    if len(melody.notes) < 4:
        raise ValueError("Melody must have at least 4 notes to fragment")

    frag = Melody(tempo=melody.tempo, instrument=melody.instrument)
    frag.info = melody.info
    frag.pcs = melody.pcs
    frag.source_data = melody.source_data
    frag.source_notes = melody.source_notes

    frag_len = randint(3, len(melody.notes) - 2)
    start_idx = randint(0, len(melody.notes) - frag_len)

    frag.notes = melody.notes[start_idx : start_idx + frag_len]
    frag.rhythms = melody.rhythms[start_idx : start_idx + frag_len]
    frag.dynamics = melody.dynamics[start_idx : start_idx + frag_len]

    return frag


def mutate(orig_melody: Melody) -> Melody:
    """
    Randomly permutate the order of notes, rhythms, and dynamics independently.

    Args:
        orig_melody: Melody object to mutate

    Returns:
        New Melody object with permuted elements created as a deep copy of the original
    """
    mutant = orig_melody.copy()

    shuffle(mutant.notes)
    shuffle(mutant.rhythms)
    shuffle(mutant.dynamics)

    return mutant


def rotate(notes: List[str]) -> List[str]:
    """
    Move the first note of a list to the end.

    Use in a loop to rotate n times to generate a series of modes.

    Args:
        notes: List of note strings

    Returns:
        Rotated list of note strings
    """
    if not notes:
        return notes
    return notes[1:] + [notes[0]]


def change_dynamics(
    dynamics: Union[int, List[int]], diff: int
) -> Union[int, List[int]]:
    """
    Make dynamics louder or softer by a specified amount.

    Args:
        dynamics: Single dynamic or list of dynamics
        diff: Amount to change (must be multiple of 4)

    Returns:
        Modified dynamic(s)
    """
    if isinstance(dynamics, int):
        if dynamics > 123:
            raise ValueError(f"Dynamic too high. Max is 123. Got: {dynamics}")
        return dynamics + diff
    elif isinstance(dynamics, list):
        return [d + diff if d <= 123 else d for d in dynamics]
    else:
        raise TypeError(f"Dynamics must be int or list[int]. Got: {type(dynamics)}")


def change_duration(rhythm: float, val: float) -> float:
    """
    Augment or diminish a single rhythmic duration.

    Args:
        rhythm: Original rhythm duration
        val: Amount to change

    Returns:
        Modified rhythm duration
    """
    return rhythm + val


def change_durations(
    rhythms: List[float], val: Union[float, List[float]]
) -> List[float]:
    """
    Augment or diminish rhythm durations by specified amounts.

    Args:
        rhythms: List of rhythm durations
        val: Single value or list of values to change by

    Returns:
        List of modified rhythm durations
    """
    if isinstance(val, float):
        return [r + val for r in rhythms]
    elif isinstance(val, list):
        if len(val) != len(rhythms):
            raise ValueError(
                f"Alteration values list ({len(val)}) must match "
                f"rhythms list length ({len(rhythms)})"
            )
        return [r + v for r, v in zip(rhythms, val)]
    else:
        raise TypeError(f"Val must be float or list[float]. Got: {type(val)}")
