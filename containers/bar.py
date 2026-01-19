"""
Class/container for dealing with individual measures.
"""

from containers.container import Container
from containers.melody import Melody
from core.analyze import is_valid
from core.constants import INSTRUMENTS
from utils.tools import scale_to_tempo


class Bar(Container):
    """
    Class/container for dealing with individual measures.
    """

    def __init__(self, meter=None, tempo=None, instrument=None):
        super().__init__()

        if meter is None:
            self.meter = (4, 4)
        else:
            if is_valid(meter):
                self.meter = (meter[0], meter[1])
            else:
                raise TypeError("Invalid meter!")

        if tempo is None:
            self.tempo = 60.0
        else:
            if isinstance(tempo, (int, float)) and 40 < tempo < 240:
                self.tempo = float(tempo)
            else:
                raise TypeError(
                    f"Tempo must be a float between 40 and 240. Tempo supplied: {tempo}"
                )

        self.length = self.meter[0] * scale_to_tempo(
            tempo=self.tempo, rhythms=self.meter[1]
        )

        if instrument is None:
            self.instrument = "Acoustic Grand Piano"
        elif instrument in INSTRUMENTS:
            self.instrument = instrument
        else:
            raise TypeError(
                f"Unsupported instrument: {instrument}. "
                "Can only use MIDI supported instruments."
            )

        self.current_beat = 0.0
        self.full = False
        self.bar = {
            "Notes": [],
            "Rhythms": [],
            "Dynamics": [],
        }

    def space_left(self) -> float:
        """Return the remaining time left in the bar in seconds."""
        return self.length - self.current_beat

    def clear(self) -> None:
        """Clear all fields."""
        self.meter = ()
        self.tempo = 0.0
        self.length = 0.0
        self.instrument = ""
        self.current_beat = 0.0
        self.bar["Notes"].clear()
        self.bar["Rhythms"].clear()
        self.bar["Dynamics"].clear()

    def duration(self) -> float:
        """
        Get the duration of the bar in seconds.
        Assumes supplied rhythms have already been scaled to the tempo.

        Note: This might not equal self.length if this is a partially completed bar.
        """
        if len(self.bar["Rhythms"]) == 0:
            return 0.0

        duration = sum(self.bar["Rhythms"])
        assert duration <= self.length, (
            f"Calculated duration exceeds estimated length! "
            f"Duration: {duration}, Length: {self.length}"
        )
        return duration

    def set_meter(self, meter: tuple):
        """Take a supplied tuple and determine if it's a valid meter."""
        if not isinstance(meter, tuple):
            raise TypeError(f"Supplied meter was not a tuple. Got: {type(meter)}")

        if is_valid(meter):
            self.meter = (meter[0], meter[1])
        else:
            raise ValueError("Invalid meter!")

    def add_notes(self, mel: Melody) -> Melody:
        """
        Take a Melody() object and add notes, rhythms, and dynamics
        until either the bar is filled or the melody object is empty.

        If the last rhythm of the Melody() object is too long to input,
        the remaining difference will be subtracted from its initial value.
        This is intended to handle syncopation.

        Returns a MODIFIED Melody() object containing any remaining notes.

        Note: If the last rhythm exceeds the total duration of the bar,
        notes will be re-attacked across the bar boundary since MIDI
        doesn't care about bar lines.
        """
        self.tempo = mel.tempo
        self.instrument = mel.instrument

        while not mel.is_empty() and not self.full:
            if len(mel.rhythms) == 0:
                break

            self.current_beat += mel.rhythms[0]

            if self.current_beat < self.length:
                self.bar["Notes"].append(mel.notes.pop(0))
                self.bar["Rhythms"].append(mel.rhythms.pop(0))
                self.bar["Dynamics"].append(mel.dynamics.pop(0))
            elif self.current_beat >= self.length:
                diff = self.current_beat - self.length
                self.bar["Notes"].append(mel.notes[0])
                self.bar["Rhythms"].append(mel.rhythms[0] - diff)
                self.bar["Dynamics"].append(mel.dynamics[0])

                mel.rhythms[0] = diff
                self.full = True

        return mel
