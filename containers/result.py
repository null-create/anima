from typing import List


class NoteGenerationResult:
    """Container for note generation results."""

    def __init__(self, notes: List[str], meta_data: List[str], source_notes: List[str]):
        self.notes = notes
        self.meta_data = meta_data
        self.source_notes = source_notes
