"""
This module handles the analysis of composition() objects and MIDI files.

TODO:
    convert MIDI file data to composition() object, as best as possible.
    mainly need to retrieve MIDI note numbers, velocities, and start/end times
    possibly parse_midi other parts of MIDI file as I learn more about them...

    comp object analysis:

        - list source data

        - get all PC's from each part
        - count all PCS
        - find most common pitch classes
        - match PCS against sets, scales, intervals

        - convert given rhythms to base rhythms (RHYTHMS),
        and create a rhythm analysis.
        - count most common base rhythms (rhythm classes?)

TODO: generate spectrogram of a given audio file
"""

from __future__ import annotations
from typing import Dict, List, Union

from core.constants import NOTES, PITCH_CLASSES, BEATS
from containers.composition import Composition
from containers.melody import Melody
from containers.chord import Chord
from utils.midi import tempo2bpm, MIDI_num_to_note_name, parse_midi
from utils.tools import remove_oct


def get_pcs(notes: Union[str, List[str]]) -> Union[int, List[int]]:
    """
    Match pitch strings to pitch class integers.

    Args:
        notes: Either a single note string or list of note strings

    Returns:
        Corresponding pitch class integer(s) in original order
    """
    if isinstance(notes, str):
        note = remove_oct(notes) if not notes.isalpha() else notes
        return PITCH_CLASSES.index(note)
    elif isinstance(notes, list):
        pcs = []
        for note_str in notes:
            note = remove_oct(note_str) if not note_str.isalpha() else note_str
            pcs.append(PITCH_CLASSES.index(note))
        return pcs
    else:
        raise TypeError(f"Notes must be a str or list[str]. Got: {type(notes)}")


def get_index(notes: Union[str, List[str]]) -> Union[int, List[int]]:
    """
    Get the index or list of indices of given notes in NOTES.

    Note name string must have an assigned octave between 0-8.

    Args:
        notes: Single note string or list of note strings with octaves

    Returns:
        Index or list of indices in NOTES
    """
    if isinstance(notes, str):
        return NOTES.index(notes)
    elif isinstance(notes, list):
        return [NOTES.index(note) for note in notes]
    else:
        raise TypeError(f"Notes must be a str or list[str]. Got: {type(notes)}")


def get_intervals(notes: List[str]) -> List[int]:
    """
    Generate a list of intervals from a given melody.
    Total intervals will be len(notes) - 1.

    Difference between index values in NOTES corresponds to distance in semitones.

    Args:
        notes: List of note strings with octaves

    Returns:
        List of interval distances in semitones
    """
    indices = get_index(notes)
    return [indices[i] - indices[i - 1] for i in range(1, len(indices))]


def count_pcs(all_tracks: Dict) -> Dict[int, int]:
    """
    Count the number of instances of each pitch class in all tracks.

    Args:
        all_tracks: Dictionary of parsed MIDI tracks

    Returns:
        Dictionary mapping pitch class integers to total appearances
    """
    pc_totals = {i: 0 for i in range(12)}
    notes = []

    for track_key in all_tracks:
        if track_key == "track 0":
            continue

        curr_track = all_tracks[track_key]
        for msg in curr_track:
            if hasattr(msg, "note") and hasattr(msg, "velocity"):
                if msg.velocity != 0:
                    note_name = MIDI_num_to_note_name(msg.note)
                    notes.append(get_pcs(note_name))

    for pc in notes:
        pc_totals[pc] += 1

    return pc_totals


def check_range(notes: List[str], inst_range: List[str]) -> List[str]:
    """
    Check for and remove any notes not within the range of a given instrument.

    Args:
        notes: List of note strings
        inst_range: List of valid notes for the instrument

    Returns:
        Modified note list with out-of-range notes removed
    """
    diff = get_diff(notes, inst_range)
    if diff:
        notes = [note for note in notes if note not in diff]
    return notes


def get_diff(notes: List[str], inst_range: List[str]) -> List[str]:
    """
    Get notes not in range of a given instrument.

    Args:
        notes: List of note strings
        inst_range: List of valid notes for the instrument

    Returns:
        List of notes outside the instrument range
    """
    return [note for note in notes if note not in inst_range]


def get_range(notes: List[str]) -> tuple:
    """
    Get the lowest and highest note in a given set of notes.

    Args:
        notes: List of note strings with octaves

    Returns:
        Tuple of (min_index, max_index) in NOTES
    """
    indices = [NOTES.index(note) for note in notes]
    return min(indices), max(indices)


def get_comp_pcs(comp: Composition) -> Dict:
    """
    Build a dictionary of pitch class information from a given composition object.

    Args:
        comp: Composition object to analyze

    Returns:
        Dictionary containing pitch class information for each part
    """
    if len(comp.parts) == 0:
        return {}

    info = {}
    for part_name, part in comp.parts.items():
        if isinstance(part, (Melody, Chord)):
            pcs = part.pcs if part.pcs else get_pcs(part.notes)
            info[part_name] = {"name": part.instrument, "pcs": pcs}
        elif isinstance(part, list):
            for idx, item in enumerate(part):
                if isinstance(item, (Melody, Chord)):
                    pcs = item.pcs if item.pcs else get_pcs(item.notes)
                    info[f"{part_name}_{idx}"] = {"name": item.instrument, "pcs": pcs}
                else:
                    raise TypeError(
                        f"Invalid part type. Expected Melody or Chord, got: {type(item)}"
                    )
        else:
            raise TypeError(
                f"Invalid part type. Expected Melody, Chord, or list, got: {type(part)}"
            )

    return info


def parse_midi_file(file_name: str) -> Dict:
    """
    Analyze a given MIDI file.

    Args:
        file_name: Name of MIDI file to parse

    Returns:
        Dictionary containing tempo, pitch classes, rhythms, and dynamics for each track
    """
    result = {"Tempo": 0, "Pitch Classes": {}, "Rhythms": {}, "Dynamics": {}}

    tracks, msgs = parse_midi(file_name)

    if msgs and hasattr(msgs[0], "tempo"):
        result["Tempo"] = tempo2bpm(msgs[0].tempo)

    pitch_classes = {}
    dynamics = {}

    for track_idx, track in tracks.items():
        pcs = []
        vel = []

        for msg in track:
            if hasattr(msg, "velocity") and hasattr(msg, "note"):
                if msg.velocity == 0:
                    continue

                note = MIDI_num_to_note_name(msg.note)
                pcs.append(get_pcs(note))
                vel.append(msg.velocity)

        pitch_classes[track_idx] = pcs
        dynamics[track_idx] = vel

    result["Pitch Classes"] = pitch_classes
    result["Dynamics"] = dynamics

    return result


def is_simple(meter: tuple) -> bool:
    """Check if meter is a simple meter."""
    return is_valid(meter)


def is_compound(meter: tuple) -> bool:
    """Check if meter is a compound meter."""
    return is_valid(meter) and meter[0] % 3 == 0 and meter[0] >= 6


def is_valid(meter: tuple) -> bool:
    """Check if meter is valid (rational)."""
    return meter[0] > 0 and valid_beat_duration(meter)


def valid_beat_duration(meter: tuple) -> bool:
    """Check if meter denominator is a valid beat duration."""
    return meter[1] in BEATS
