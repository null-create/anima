"""
Short composition for string quartet.

Starts with a long choral in unison, then, at the end of the
unison section, each last notes value for each part is different, which will
case them all to go out of phase. From here, we will repeat each line each part
just played, this time out of sync with each other.

Instrumentation: string quartet
Tempo: 56-71
"""

import argparse
from tqdm import trange
from random import randint, seed

from utils.midi import export_midi
from utils.tools import scale_to_tempo
from utils.txtfile import gen_info_doc

from core.generate import Generate
from core.constants import DYNAMICS, RANGE, RHYTHMS, TEMPOS

from containers.melody import Melody
from containers.composition import Composition

# initialize generator
create = Generate()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name", type=str, help="(string) name of the composition (optional)"
    )
    parser.add_argument(
        "--tempo", type=str, help="(string) tempo of the composition (optional)"
    )
    args = parser.parse_args()
    return args


def melt(tempo: str = None, title: str = None) -> Composition:
    if tempo is None or tempo == "":
        comp = create.init_comp(TEMPOS[randint(20, 29)])
    else:
        comp = create.init_comp(tempo)
    if title is None or title == "":
        comp.title + " for string trio"
    else:
        comp.title = title + " for string trio"

    trio = [
        Melody(tempo=comp.tempo, instrument="Viola"),
        Melody(tempo=comp.tempo, instrument="Cello"),
        Melody(tempo=comp.tempo, instrument="Cello"),
    ]
    trio_empty = trio  # used to reset qtet for each subsequent section
    comp.ensemble = "string trio"

    # these will be used as empty containers for each new section
    comp.instruments += trio

    # dictionary of different sections from the composition.
    # can be used to mix and match material!
    sections = {}

    # introduce our root and source scales here. Should be up to around the 6th octave as our highest,
    # so we have enough room for interesting voicings but hopefully make it still somewhat
    # human playable.
    mode, pcs, root_scale = create.pick_scale(transpose=True)
    source = create.new_source_scale(root_scale)
    print("...using", root_scale[0], mode)
    print("...notes:", root_scale)
    print("...pcs:", pcs)

    # add source info to each Melody() object
    for inst in range(len(trio)):
        trio[inst].pcs.append(pcs)
        trio[inst].source_notes = source

    # write individual *choral* lines
    total_notes = randint(12, 30)
    for inst in range(len(trio)):
        trio[inst] = write_line(trio[inst], source, total_notes)

    # create rhythms and dynamics
    rhy = [RHYTHMS[randint(1, 3)] for _ in range(total_notes)]
    dyn = [65 for _ in range(total_notes)]

    # add shared rhythms and dynamics to each part
    for inst in range(len(trio)):
        trio[inst].rhythms.extend(rhy)
        trio[inst].dynamics.extend(dyn)

    # export_midi all parts then write out
    for inst in range(len(trio)):
        comp.add_part(trio[inst], trio[inst].instrument)

    # export_midi MIDI output
    export_midi(comp)

    print("\n...success!")

    # display results
    comp.display()

    return comp


def write_line(part: Melody, scale: list, total: int, asyn: bool = False) -> Melody:
    """
    writes each individual melodic line for each part.
    **doesn't add rhythm or dynamics** if asyn==False,
    which it is by default. if asyn==true, then any supplied
    total will be overwritten! still working on that
    quirk...

    returns a modified Melody() object
    """
    if asyn:
        # NOTE: this will redefine supplied total if asyn is True
        total = randint(12, 30)

    for _ in range(total):
        # limited to octaves 4 and 5 for violins
        if part.instrument == "Violin":
            note = scale[randint(13, len(scale) - 1)]
            # trying to account for random notes chosen out of range...
            while note not in RANGE["Violin"]:
                note = scale[randint(13, len(scale) - 1)]
            part.notes.append(note)

        # limit to octaves 3 and 4 for viola
        elif part.instrument == "Viola":
            note = scale[randint(7, len(scale) - 8)]
            while note not in RANGE["Viola"]:
                note = scale[randint(7, len(scale) - 8)]
            part.notes.append(note)

        # limit to octaves 2 and 3 for cello
        elif part.instrument == "Cello":
            note = scale[randint(0, len(scale) - 16)]
            while note not in RANGE["Cello"]:
                note = scale[randint(0, len(scale) - 16)]
            part.notes.append(note)

    if asyn:
        # add independent rhythms and dynamics of n length
        part.rhythms.extend(create.new_rhythms(total=len(part.notes), tempo=part.tempo))
        part.dynamics.extend(create.new_dynamics(total=len(part.notes)))

    return part


if __name__ == "__main__":
    args = parse_args()
    melt(tempo=args.tempo)
