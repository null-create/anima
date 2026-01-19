import os

from core.generate import Generate
from core.modify import Modify
from core.analyze import Analyze
from containers.melody import Melody
from utils.midi import load_midi_file, parse_midi, export_midi
from utils.tools import to_str

create = Generate()
modify = Modify()
analyze = Analyze()
comp = create.init_comp(tempo=60.0, title="test-file", composer="your mom")
midi_dir = os.path.join(os.getcwd(), "midi")


def main():
    notes = ["E2", "F2", "E2", "E2", "G2"]

    # create a temp MIDI file
    melody = Melody(instrument="Acoustic Grand Piano")
    melody.notes = notes
    melody.rhythms = [2.0] * len(notes)
    melody.dynamics = [100] * len(notes)
    comp.add_part(part=melody, instr=melody.instrument)

    # export MIDI, then open and parse before counting pitch classes
    export_midi(comp)
    tracks, _ = parse_midi(file_name=os.path.join(midi_dir, comp.midi_file_name))

    pcs_counts = analyze.count_pcs(all_tracks=tracks)

    print("notes: ", melody.notes)
    print("total notes: ", len(melody.notes))
    print("pc totals: ")
    for key in pcs_counts:
        print(f"{key}: {pcs_counts[key]}")

    # remove test file
    os.remove(os.path.join(midi_dir, comp.midi_file_name))


if __name__ == "__main__":
    main()
