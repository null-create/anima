"""

"""

from random import randint, choice

from utils.midi import export_midi
from core.generate import Generate
from containers.melody import Melody
from containers.chord import Chord

TEMPO = 146  # global composition tempo
DYNAMIC = 100  # dynamic for every note generated. velocities are handled during editing in the DAW
PIANO = "Acoustic Grand Piano"  # MIDI instrument name
STRINGS = "String Ensemble 1"  # MIDI instrument name
BASS = "Contrabass"  # MIDI instrument name

# initialize generator & composition objects
create = Generate()
comp = create.init_comp(tempo=TEMPO, title=create.new_title(), composer="contra sigma")


# used for slow middle break down after an initial build
def gen_piano_chords() -> list:
    """
    Generates a slow, deep, series of piano chords
    """

    # each of these rhythms will be used with a single chord.
    source_rhythms = [2.0, 2.5, 3.0, 5.0]

    # pick initial notes.
    print("generating piano chords...")

    # f natural minor
    source_scale = [
        "F1",
        "G1",
        "G#1",
        "Bb1",
        "C2",
        "C#2",
        "Eb2",
        "F2",
        "G2",
        "G#2",
        "Bb2",
        "C3",
        "C#3",
        "Eb3",
        "F3",
        "G3",
        "G#3",
        "Bb3",
        "C4",
        "C#4",
        "Eb4",
    ]

    # pick five different chords
    chords = []
    for _ in range(5):
        # pick the notes and dynamic for each chord before
        # determining rhythm and repetition totals
        total_notes = randint(3, 6)
        chord_notes = create.choose_notes(source_scale, total_notes)
        chord_dynamic = DYNAMIC

        # repeat each chord 6 to 9 times, each with a different
        # rhythm chosen from the rhythms list
        total_reps = randint(2, 5)
        for _ in range(total_reps):
            chord = Chord(tempo=TEMPO, instrument=PIANO)
            chord.notes = chord_notes
            chord.dynamic = chord_dynamic
            chord.rhythm = choice(source_rhythms)
            chords.append(chord)

    return chords


def gen_melody() -> Melody:
    print("writing melody...")

    melody = Melody(tempo=TEMPO, instrument=PIANO)

    melody.notes = ["F5", "C5", "G#5", "G5", "C6", "E5", "C#6", "C6", "Bb5", "Eb5"]
    melody.rhythms = [2.0, 2.0, 3.0, 4.0, 2.0, 2.0, 4.0, 4.0, 3.0, 2.0]
    melody.dynamics = [DYNAMIC] * len(melody.notes)

    return melody


def gen_rand_melody() -> Melody:
    print("writing longer random melody...")

    melody = Melody(tempo=TEMPO, instrument=PIANO)

    source_scale = [
        "F4",
        "G4",
        "G#4",
        "Bb4",
        "C5",
        "C#5",
        "Eb5",
        "F5",
        "G5",
        "G#5",
        "Bb5",
        "C6",
        "C#6",
        "Eb6",
        "F6",
        "G6",
        "G#6",
        "Bb6",
    ]
    # NOTE: 0.5 was added twice on purpose  in order to make it twice
    # as likely to be chosen as it ordinarily would have been
    source_rhythms = [0.5, 0.5, 2.0, 3.0]

    # Choose elements
    total = randint(9, 19)
    melody.notes = [choice(source_scale) for _ in range(total)]
    melody.rhythms = [choice(source_rhythms) for _ in range(total)]
    melody.dynamics = [DYNAMIC] * total

    return melody


def gen_octaves_ostinato() -> list:
    octaves = Chord(tempo=TEMPO)
    octaves.notes = ["G5", "G6"]
    octaves.dynamic = DYNAMIC
    octaves.rhythm = 1  # quarter note

    chords = []
    total_reps = randint(6, 12)
    for _ in range(total_reps):
        chords.append(octaves)

    return chords


def gen_slow_bass_line() -> Melody:
    bass = Melody(tempo=TEMPO, instrument="Contrabass")
    bass.source_data = "None"
    bass.info = "None"

    source_rhythms = [2, 4, 5, 6]
    source_notes = [
        "C0",
        "C#0",
        "Eb0",
        "F0",
        "G0",
        "G#0",
        "Bb0",
        "C1",
        "C#1",
        "Eb1",
        "F1",
        "G1",
        "G#1",
        "Bb1",
        "C2",
        "C#2",
        "Eb2",
    ]

    total_notes = randint(6, 11)

    bass.notes = create.choose_notes(source_notes=source_notes, total=total_notes)
    bass.rhythms = create.new_rhythms(
        total=total_notes, tempo=bass.tempo, source_rhythms=source_rhythms
    )
    bass.dynamics = [DYNAMIC] * total_notes

    return bass


if __name__ == "__main__":
    bass_line = gen_slow_bass_line()
    comp.add_part(part=bass_line, instr=bass_line.instrument)

    export_midi(comp)
