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


# def is_valid_midi_num(num: int) -> bool:
#     """
#     Returns True if the midi number is valid
#     """
#     return True if num >= 21 and num <= 108 else False


# def note_name_to_MIDI_num(note: str) -> int:
#     """
#     returns the corresponding MIDI note for a
#     given note name string.

#     Midi numbers start at 21 and go to 108 because reasons.
#     See: https://newt.phys.unsw.edu.au/jw/notes.html

#     Our implementation uses indicies to match note names to note numbers,
#     so we compensate for the difference in value between the index and the
#     MIDI number by adding (or subtracting) 21.
#     """
#     return NOTES.index(note) + 21


# def MIDI_num_to_note_name(num: int) -> str:
#     """
#     returns the corresponding note name string from a
#     given MIDI note number.
#     """
#     if num < 21 or num > 108:
#         raise ValueError("MIDI number must be between 21 and 108")
#     return NOTES[num - 21]


# def instrument_to_program(instr: str) -> int:
#     """
#     returns an instrument program number using INSTRUMENTS, which
#     maps names to number via their index values.
#     """
#     inst_name = normalize_str(instr)
#     inst_list = [normalize_str(name) for name in INSTRUMENTS]
#     return inst_list.index(inst_name)


# def tempo2bpm(tempo: int) -> int:
#     """
#     converts a MIDI file tempo to tempo in BPM.
#     can also take a BPM and return a MIDI file tempo

#     - 250000 => 240
#     - 500000 => 120
#     - 1000000 => 60

#     1 minute is 60,000,000 microseconds
#     """
#     return int(round((60 * 1000000) / tempo))


# def load_midi_file(file_name: str) -> MidiFile:
#     """
#     loads a MIDI file using a supplied file name (i.e "song.mid")
#     """
#     if not file_name.endswith(".mid"):
#         raise ValueError("must be a midi file name!")
#     return MidiFile(filename=file_name)


# def parse_midi(file_name: str) -> tuple[dict, list]:
#     """
#     opens and parses a MIDI file into a dictionary
#     containing individual tracks and individual MIDI messages.

#     returns a tuple:
#         - a dict with each key being a string representing
#           the track number, i.e. "track 1", with the value being
#           an individual track (list of Message() objects)
#         - a list[Message()] of individual messages,
#           ***that are separated from their original tracks! ***
#     """
#     msgs = []
#     tracks = {}
#     file = load_midi_file(file_name)
#     for i, track in enumerate(file.tracks):
#         tracks.update(
#             {
#                 f"track {str(i)}": track,
#             }
#         )
#         for msg in track:
#             msgs.append(msg)
#     return tracks, msgs


# def to_instrument(part: Chord | Melody) -> Instrument:
#     return Instrument(program=instrument_to_program(part.instrument))


# def _build_melody(
#     start: float, end: float, cur_part: Melody, mel_inst: Instrument
# ) -> tuple[float, float, Instrument]:
#     end += cur_part.rhythms[0]
#     for i in range(1, len(cur_part.notes)):
#         mel_inst.notes.append(
#             Note(
#                 velocity=cur_part.dynamics[i - 1],
#                 pitch=note_name_to_MIDI_num(cur_part.notes[i - 1]),
#                 start=start,
#                 end=end,
#             )
#         )
#         start += cur_part.rhythms[i - 1]
#         end += cur_part.rhythms[i]

#     return start, end, mel_inst


# def _build_chord(
#     start: float, end: float, cur_part: Chord, chord_inst: Instrument
# ) -> tuple[float, float, Instrument]:
#     end += cur_part.rhythm
#     for note in cur_part.notes:
#         chord_inst.notes.append(
#             Note(
#                 velocity=cur_part.dynamic,
#                 pitch=note_name_to_MIDI_num(note),
#                 start=start,
#                 end=end,
#             )
#         )
#     start += cur_part.rhythm

#     return start, end, chord_inst


# def export_midi(comp: Composition) -> None:
#     """
#     Takes a composition object and constructs data to be written out to a MIDI file
#     """
#     if len(comp.parts) == 0:
#         print("No tracks! Exiting...")
#         return

#     midi_writer = PrettyMIDI(initial_tempo=comp.tempo)

#     # iterate over comp.parts dictionary
#     for part in comp.parts:
#         # reset start and end markers for each track
#         start, end = 0.0, 0.0
#         cur_part = comp.parts[part]

#         # handle Melody() object
#         if isinstance(cur_part, Melody):
#             _, _, instrument = _build_melody(
#                 start, end, cur_part, to_instrument(cur_part)
#             )
#             midi_writer.instruments.append(instrument)
#         # handle Chord() object
#         elif isinstance(cur_part, Chord):
#             _, _, instrument = _build_chord(
#                 start, end, cur_part, to_instrument(cur_part)
#             )
#             midi_writer.instruments.append(instrument)

#         # handle a list of Chord() or Melody() objects (or both!)
#         # should be a single track!
#         elif isinstance(cur_part, list):
#             # we pick the instrument using the first object. instruments will
#             # all have the same MIDI instrument since every object in this list will
#             # also have the same instrument.
#             instrument = to_instrument(cur_part[0])
#             for item in cur_part:
#                 if isinstance(item, Melody):
#                     start, end, instrument = _build_melody(start, end, item, instrument)
#                 elif isinstance(item, Chord):
#                     start, end, instrument = _build_chord(start, end, item, instrument)
#                 else:
#                     raise TypeError(
#                         f"Unsupported type! Cur_part is type: {type(cur_part)} "
#                         "Should be a Melody or Chord object, or list of either (or both)"
#                     )
#             midi_writer.instruments.append(instrument)
#         else:
#             raise TypeError(
#                 f"Unsupported type! Cur_part is type: {type(cur_part)} "
#                 "Should be a Melody or Chord object, or list of either(or both)"
#             )

#     # write to MIDI file
#     print(f"saving {comp.midi_file_name} ... ")
#     midi_writer.write(join(MIDI_FOLDER, comp.midi_file_name))


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
