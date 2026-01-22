"""
Module for generating "Today We Go Home And Rest" - a solo guitar composition.

This module creates a structured musical piece with a predefined form (A|B|A|C|D|C|A|B|A)
using procedural generation for sections B, C, and D. Section A uses fixed melodic material.

Constants:
    TITLE (str): Composition title
    TEMPO (float): Tempo in BPM (73.0)
    FORM (list): Sequence of sections defining the piece structure
    DYNAMIC (int): Default MIDI velocity for generated sections
    RHYTHMS (list): Available note durations for generation
    ROOT (list): Available pitch range for generation
    A (dict): Pre-composed section A with fixed notes, rhythms, and dynamics
    B, C, D (dict): Empty section containers to be populated by generation
    SECTS (list): Collection of all section dictionaries

Functions:
    rest() -> None: Main composition function that initializes, generates, assembles,
        and exports the piece as MIDI format.
"""

from random import randint, choice, seed

from tqdm import trange

from utils.midi import export_midi
from utils.tools import scale_to_tempo
from core.analyze import get_pcs
from core.generate import Generate
from containers.melody import Melody

# base material + containers for each generated section
TITLE = "Today We Go Home And Rest"
TEMPO = 73.0
FORM = ["A", "B", "A", "C", "D", "C", "A", "B", "A"]
DYNAMIC = 54
RHYTHMS = [0.5, 1.0, 2.0]
ROOT = [
    "F3",
    "G3",
    "A3",
    "Bb3",
    "C4",
    "D4",
    "E4",
    "F4",
    "G4",
    "A4",
    "B4",
    "C5",
    "D5",
    "E5",
    "F5",
    "G5",
    "A5",
]
A = {
    "Name": "A",
    "Notes": [
        "F3",
        "F4",
        "D4",
        "E4",
        "F3",
        "F4",
        "D4",
        "E4",
        "C4",
        "F3",
        "F4",
        "D4",
        "E4",
        "F3",
        "F4",
        "D4",
        "E4",
        "Bb3",
        "G4",
        "F3",
        "F4",
        "D4",
        "E4",
        "C4",
        "G4",
        "A4",
    ],
    "Rhythms": [
        1.0,
        0.5,
        0.5,
        2.0,
        1.0,
        0.5,
        0.5,
        2.0,
        2.0,
        1.0,
        0.5,
        0.5,
        2.0,
        1.0,
        0.5,
        0.5,
        1.0,
        1.0,
        1.0,
        1.0,
        0.5,
        0.5,
        1.0,
        1.0,
        0.5,
        0.5,
    ],
    "Dynamics": [52] * 26,
}
B = {"Name": "B", "Notes": [], "Rhythms": [], "Dynamics": []}
C = {"Name": "C", "Notes": [], "Rhythms": [], "Dynamics": []}
D = {"Name": "D", "Notes": [], "Rhythms": [], "Dynamics": []}
SECTS = [A, B, C, D]


# Today we go home and rest, for solo guitar
def rest() -> None:
    """
    Today We Go Home And Rest, for solo guitar

    Form: A|B|A|C|D|C|A|B|A
    """
    # initilize stuff
    print("\ninitializing...")
    seed()
    comp = Generate().initialize_composition(
        tempo=TEMPO, title=TITLE, composer="contra sigma"
    )
    gtr = Melody(tempo=comp.tempo, instrument="Electric Guitar (clean)")

    # generate B, C, and D sections
    print("\ngenerating...")
    for s in trange((len(SECTS)), desc="progress"):
        if SECTS[s]["Name"] == "A":
            continue
        total = randint(13, 27)
        SECTS[s]["Notes"] = [choice(ROOT) for n in range(total)]
        SECTS[s]["Rhythms"] = [choice(RHYTHMS) for r in range(total)]
        SECTS[s]["Dynamics"] = [DYNAMIC] * total

    # assemble
    print("\nassembling...")
    for f in trange((len(FORM)), desc="progress"):
        for s in range(len(SECTS)):
            if FORM[f] == SECTS[s]["Name"]:
                gtr.notes.extend(SECTS[s]["Notes"])
                gtr.rhythms.extend(
                    scale_to_tempo(tempo=comp.tempo, rhythms=SECTS[s]["Rhythms"])
                )
                gtr.dynamics.extend(SECTS[s]["Dynamics"])

    # analyze and write out
    print("\nwriting out...")
    gtr.pcs = get_pcs(gtr.notes)
    gtr.source_notes = ROOT
    gtr.source_data = "None"
    comp.instruments.append(gtr)
    comp.midi_file_name = f"{comp.title}.mid"

    export_midi(comp)


if __name__ == "__main__":
    rest()
