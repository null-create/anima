"""
Utility functions for working with MIDI data and I/O
"""

from __future__ import annotations
from typing import Tuple, List
from os.path import join
from mido import MidiFile
from pretty_midi import PrettyMIDI, Instrument

from utils.tools import normalize_str
from core.constants import INSTRUMENTS, NOTES, MIDI_FOLDER, MIN_MIDI_NOTE, MAX_MIDI_NOTE
from containers.note import Note
from containers.melody import Melody
from containers.chord import Chord
from containers.composition import Composition


def is_valid_midi_num(num: int) -> bool:
    """
    Check if the MIDI number is valid.

    Args:
        num: MIDI note number

    Returns:
        True if valid, False otherwise
    """
    return MIN_MIDI_NOTE <= num <= MAX_MIDI_NOTE


def note_name_to_MIDI_num(note: str) -> int:
    """
    Convert a note name string to its MIDI note number.

    MIDI numbers start at 21 (A0) and go to 108 (C8).

    Args:
        note: Note name string with octave (e.g., "C4")

    Returns:
        MIDI note number
    """
    return NOTES.index(note) + MIN_MIDI_NOTE


def MIDI_num_to_note_name(num: int) -> str:
    """
    Convert a MIDI note number to its note name string.

    Args:
        num: MIDI note number (21-108)

    Returns:
        Note name string with octave

    Raises:
        ValueError: If MIDI number is out of valid range
    """
    if not is_valid_midi_num(num):
        raise ValueError(
            f"MIDI number must be between {MIN_MIDI_NOTE} and {MAX_MIDI_NOTE}"
        )
    return NOTES[num - MIN_MIDI_NOTE]


def instrument_to_program(instr: str) -> int:
    """
    Convert instrument name to MIDI program number.

    Args:
        instr: Instrument name string

    Returns:
        MIDI program number (0-127)
    """
    inst_name = normalize_str(instr)
    inst_list = [normalize_str(name) for name in INSTRUMENTS]
    return inst_list.index(inst_name)


def tempo2bpm(tempo: int) -> int:
    """
    Convert MIDI file tempo to BPM.

    Args:
        tempo: MIDI tempo in microseconds per quarter note

    Returns:
        Tempo in BPM
    """
    return int(round((60 * 1000000) / tempo))


def load_midi_file(file_name: str) -> MidiFile:
    """
    Load a MIDI file.

    Args:
        file_name: Name of MIDI file (must end with .mid)

    Returns:
        Loaded MidiFile object

    Raises:
        ValueError: If file name doesn't end with .mid
    """
    if not file_name.endswith(".mid"):
        raise ValueError(f"Must be a MIDI file name (ending in .mid). Got: {file_name}")
    return MidiFile(filename=file_name)


def parse_midi(file_name: str) -> Tuple[dict, list]:
    """
    Open and parse a MIDI file into tracks and messages.

    Args:
        file_name: Name of MIDI file to parse

    Returns:
        Tuple of (tracks_dict, messages_list)
        - tracks_dict: Dict with track numbers as keys, track data as values
        - messages_list: Flat list of all MIDI messages
    """
    msgs = []
    tracks = {}
    midi_file = load_midi_file(file_name)

    for i, track in enumerate(midi_file.tracks):
        tracks[f"track {i}"] = track
        msgs.extend(track)

    return tracks, msgs


def create_instrument(instrument_name: str) -> Instrument:
    """
    Create a PrettyMIDI Instrument from an instrument name.

    Args:
        instrument_name: Name of the instrument

    Returns:
        PrettyMIDI Instrument object
    """
    return Instrument(program=instrument_to_program(instrument_name))


def melody_to_notes(melody: Melody, start_time: float) -> Tuple[List[Note], float]:
    """
    Convert a Melody object to a list of MIDI Note objects.

    Args:
        melody: Melody object to convert
        start_time: Starting time in seconds

    Returns:
        Tuple of (note_list, next_start_time)
    """
    notes = []
    current_time = start_time

    for note_str, rhythm, dynamic in zip(melody.notes, melody.rhythms, melody.dynamics):
        end_time = current_time + rhythm
        notes.append(
            Note(
                velocity=dynamic,
                pitch=note_name_to_MIDI_num(note_str),
                start=current_time,
                end=end_time,
            )
        )
        current_time = end_time

    return notes, current_time


def chord_to_notes(chord: Chord, start_time: float) -> Tuple[List[Note], float]:
    """
    Convert a Chord object to a list of MIDI Note objects.

    Args:
        chord: Chord object to convert
        start_time: Starting time in seconds

    Returns:
        Tuple of (note_list, next_start_time)
    """
    notes = []
    end_time = start_time + chord.rhythm

    for note_str in chord.notes:
        notes.append(
            Note(
                velocity=chord.dynamic,
                pitch=note_name_to_MIDI_num(note_str),
                start=start_time,
                end=end_time,
            )
        )

    return notes, end_time


def part_to_instrument(part, start_time: float = 0.0) -> Instrument:
    """
    Convert a musical part (Melody, Chord, or list) to a MIDI Instrument.

    Args:
        part: Melody, Chord, or list of Melody/Chord objects
        start_time: Starting time in seconds

    Returns:
        PrettyMIDI Instrument with all notes added
    """
    if isinstance(part, Melody):
        instrument = create_instrument(part.instrument)
        notes, _ = melody_to_notes(part, start_time)
        instrument.notes.extend(notes)

    elif isinstance(part, Chord):
        instrument = create_instrument(part.instrument)
        notes, _ = chord_to_notes(part, start_time)
        instrument.notes.extend(notes)

    elif isinstance(part, list):
        if not part:
            raise ValueError("Part list cannot be empty")

        instrument = create_instrument(part[0].instrument)
        current_time = start_time

        for item in part:
            if isinstance(item, Melody):
                notes, current_time = melody_to_notes(item, current_time)
                instrument.notes.extend(notes)
            elif isinstance(item, Chord):
                notes, current_time = chord_to_notes(item, current_time)
                instrument.notes.extend(notes)
            else:
                raise TypeError(
                    f"List items must be Melody or Chord objects. Got: {type(item)}"
                )
    else:
        raise TypeError(f"Part must be Melody, Chord, or list. Got: {type(part)}")

    return instrument


def export_midi(comp: Composition) -> None:
    """
    Export a Composition object to a MIDI file.

    Args:
        comp: Composition object to export

    Raises:
        ValueError: If composition has no parts
    """
    if len(comp.parts) == 0:
        raise ValueError("Cannot export composition with no parts")

    midi_writer = PrettyMIDI(initial_tempo=comp.tempo)

    for part_name, part in comp.parts.items():
        try:
            instrument = part_to_instrument(part)
            midi_writer.instruments.append(instrument)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error processing part '{part_name}': {str(e)}") from e

    output_path = join(MIDI_FOLDER, comp.midi_file_name)
    print(f"Saving {comp.midi_file_name}...")
    midi_writer.write(output_path)
    print(f"MIDI file saved to {output_path}")
