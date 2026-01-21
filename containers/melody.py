"""
Module for the Melody() class/container. Used for individual melody data in compositions.
"""

from containers.container import Container


class Melody(Container):
    """
    A class/container for managing all data relevant to melodies.

    Does not adhere to any strict time signature. Use Bar() if using a
    time signature is preferred.

    Stores: original Forte number, inputted source data, original source scale,
    tempo, instrument, notes, rhythms, and dynamics.
    """

    def __init__(self, tempo=None, instrument=None):
        super().__init__()

        if tempo is None:
            self.tempo = 0.0
        else:
            self.tempo = tempo
        if instrument is None:
            self.instrument = "None"
        else:
            self.instrument = instrument

        self.notes = []
        self.rhythms = []
        self.dynamics = []

    def duration(self) -> float:
        """
        Returns the duration (float) of a melody in seconds.
        """
        duration = 0.0
        for rhythm in self.rhythms:
            duration += rhythm
        return duration

    def is_empty(self) -> bool:
        """
        Returns true if the container is empty, otherwise false
        """
        return (
            len(self.notes) == 0 and len(self.rhythms) == 0 and len(self.dynamics) == 0
        )

    def get_meta_data(self) -> dict:
        """
        returns meta-data as a dictionary
        """
        return {
            "Info": self.info,
            "PCS": self.pcs,
            "Source Data": self.source_data,
            "Source Scale": self.source_notes,
        }

    def get_pcs(self) -> list:
        """
        return a list[int] of all pitch classes in this melody.

        NOTE: may need to use tools.get_pcs() prior to calling this
        """
        return self.pcs if len(self.pcs) != 0 else [0]

    def copy(self) -> "Melody":
        """
        Returns a deep copy of the Melody object.
        """
        new_melody = Melody(tempo=self.tempo, instrument=self.instrument)
        new_melody.notes = self.notes.copy()
        new_melody.rhythms = self.rhythms.copy()
        new_melody.dynamics = self.dynamics.copy()
        new_melody.info = self.info
        new_melody.pcs = self.pcs
        new_melody.source_data = self.source_data
        new_melody.source_notes = self.source_notes
        return new_melody
