"""
This module handles all generative methods for musical composition.
"""

import urllib.request
from math import floor
from names import get_full_name
from datetime import datetime as date
from random import Random
from typing import List, Tuple, Dict, Optional, Union

from utils.mapping import map_data
from utils.midi import export_midi
from utils.tools import to_str, scale_to_tempo, scale_limit

from core.constants import (
    NOTES,
    PITCH_CLASSES,
    RHYTHMS,
    REST,
    DYNAMICS,
    TEMPOS,
    INSTRUMENTS,
    SCALES,
    ARPEGGIOS,
    SETS,
    RANGE,
    MIN_NOTES,
    MAX_NOTES,
    MIN_RHYTHMS,
    MAX_RHYTHMS,
    MIN_DYNAMICS,
    MAX_DYNAMICS,
    MIN_CHORDS,
    MAX_CHORDS,
    MIN_SCALES,
    MAX_SCALES,
    MIN_SCALE_SIZE,
    MAX_SCALE_SIZE,
    MIN_CHORD_NOTES,
    MAX_CHORD_NOTES,
    MIN_OCTAVE,
    MAX_OCTAVE,
    MELODIC_INSTRUMENT_END,
    KEYBOARD_INSTRUMENT_START,
    KEYBOARD_INSTRUMENT_END,
    GENERATION_OCTAVE_START,
    GENERATION_OCTAVE_END,
    BASE_TEMPO,
)

from containers.bar import Bar
from containers.chord import Chord
from containers.melody import Melody
from containers.composition import Composition
from containers.result import NoteGenerationResult


class Generate:
    """
    Class handling all generative functions for musical composition.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize generator with optional random seed.

        Args:
            random_seed: Optional seed for reproducible random generation
        """
        self.random = Random(random_seed)

    def _randint(self, a: int, b: int) -> int:
        """Wrapper for random integer generation."""
        return self.random.randint(a, b)

    def _choice(self, seq):
        """Wrapper for random choice."""
        return self.random.choice(seq)

    def _get_default_count(self, min_val: int, max_val: int) -> int:
        """Get a random count within a default range."""
        return self._randint(min_val, max_val)

    def generate_title(self) -> str:
        """
        Generate a composition title from 1-4 random words.

        Returns:
            Generated title string or "untitled" if word list unavailable
        """
        try:
            url = "https://www.mit.edu/~ecprice/wordlist.10000"
            response = urllib.request.urlopen(url)
            text = response.read().decode()
            words = text.splitlines()

            word_count = self._randint(1, 3)
            title_words = [self._choice(words) for _ in range(word_count + 1)]
            return " ".join(title_words)

        except urllib.error.URLError as e:
            print(f"Unable to retrieve word list: {e}")
            return "untitled"
        except Exception as e:
            print(f"Exception retrieving word list: {e}")
            return "untitled"

    def generate_composer(self) -> str:
        """Generate a random composer name."""
        return get_full_name()

    def initialize_composition(
        self,
        tempo: Optional[float] = None,
        title: Optional[str] = None,
        composer: Optional[str] = None,
    ) -> Composition:
        """
        Initialize a Composition object with title, composer, tempo, and metadata.

        Args:
            tempo: Optional tempo in BPM
            title: Optional composition title
            composer: Optional composer name

        Returns:
            Initialized Composition object
        """
        comp = Composition()

        comp.tempo = self._validate_tempo(tempo) if tempo else self.generate_tempo()
        comp.title = title if title else self.generate_title()
        comp.composer = composer if composer else self.generate_composer()
        comp.date = date.now().strftime("%d-%b-%y %H:%M:%S")
        comp.midi_file_name = f"{comp.title}.mid"
        comp.txt_file_name = f"{comp.title}.txt"

        return comp

    def _validate_tempo(self, tempo: float) -> float:
        """Validate tempo is within acceptable range."""
        if 40.0 <= tempo <= 208.0:
            return tempo
        return BASE_TEMPO

    def generate_tempo(self) -> float:
        """Generate a random tempo between 40-208 BPM."""
        return self._choice(TEMPOS)

    def generate_instrument(self) -> str:
        """Generate a random melodic/harmonic instrument (not percussion)."""
        return INSTRUMENTS[self._randint(0, MELODIC_INSTRUMENT_END)]

    def generate_instruments(self, total: int) -> List[str]:
        """
        Generate a list of random instruments.

        Args:
            total: Number of instruments to generate

        Returns:
            List of instrument names
        """
        return [self.generate_instrument() for _ in range(total)]

    def generate_random_note(self) -> str:
        """Generate a random note between octaves 1 and 7."""
        pitch_class = self._choice(PITCH_CLASSES)
        octave = self._randint(1, 7)
        return f"{pitch_class}{octave}"

    def choose_note(self, scale: List[str]) -> str:
        """Choose a random note from a given scale."""
        return self._choice(scale)

    def choose_notes(self, source_notes: List[str], total: int) -> List[str]:
        """
        Choose a set of notes at random from a given set.

        Args:
            source_notes: Source scale to choose from
            total: Number of notes to choose

        Returns:
            List of randomly chosen notes
        """
        return [self._choice(source_notes) for _ in range(total)]

    def pick_root(
        self, transpose: bool = True, octave: Optional[int] = None
    ) -> Tuple[List[str], str]:
        """
        Pick a randomly chosen and optionally transposed scale or pitch class set.

        Args:
            transpose: Whether to transpose the root
            octave: Optional octave to assign

        Returns:
            Tuple of (note_list, description_string)
        """
        choice_type = self._randint(1, 3)

        if choice_type == 1:
            mode, pcs, scale = self.pick_scale(transpose=transpose)
            info = f"{scale[0]} {mode}"
        elif choice_type == 2:
            fn, pcs, scale = self.pick_set(transpose=transpose)
            info = (
                f"set {fn} transposed to {scale[0]}"
                if transpose
                else f"set {fn} un-transposed {scale[0]}"
            )
        else:
            scale, pcs = self.generate_scale(transpose=transpose)
            info = f"invented scale: {scale} pcs: {pcs}"

        scale = to_str(pcs=pcs, octave=octave)
        return scale, info

    def pick_scale(
        self, transpose: bool = True, octave: Optional[int] = None
    ) -> Tuple[str, List[int], List[str]]:
        """
        Pick a scale and optionally transpose it.

        Args:
            transpose: Whether to transpose the scale
            octave: Optional octave to assign

        Returns:
            Tuple of (scale_name, pitch_classes, note_list)
        """
        from core.modify import transpose as transpose_func

        scale_name = self._choice(list(SCALES.keys()))
        pcs = SCALES[scale_name]

        if transpose:
            pcs_t = transpose_func(pcs, self._randint(1, 11), oct_eq=False)
            notes = to_str(pcs_t, octave=octave)
        else:
            notes = to_str(pcs, octave=octave)

        return scale_name, pcs, notes

    def pick_set(
        self, transpose: bool = True, octave: Optional[int] = None
    ) -> Tuple[str, List[int], List[str]]:
        """
        Select a pitch class set and optionally transpose it.

        Args:
            transpose: Whether to transpose the set
            octave: Optional octave to assign

        Returns:
            Tuple of (forte_number, pitch_classes, note_list)
        """
        from core.modify import transpose as transpose_func

        forte_number = self._choice(list(SETS.keys()))
        pcs = SETS[forte_number]

        if transpose:
            pcs_t = transpose_func(pcs, self._randint(1, 11), oct_eq=False)
            scale = to_str(pcs_t, octave=octave)
        else:
            scale = to_str(pcs, octave=octave)

        return forte_number, pcs, scale

    def generate_scale(
        self, transpose: bool = True, octave: Optional[int] = None
    ) -> Tuple[List[str], List[int]]:
        """
        Generate a random 5-8 note scale.

        Args:
            transpose: Whether to transpose the scale
            octave: Optional octave to assign

        Returns:
            Tuple of (note_list, pitch_classes)
        """
        from core.modify import transpose as transpose_func

        pcs = []
        total = self._randint(MIN_SCALE_SIZE, MAX_SCALE_SIZE)

        while len(pcs) < total:
            n = self._randint(0, 11)
            if n not in pcs:
                pcs.append(n)

        pcs.sort()

        if transpose:
            pcs = transpose_func(pcs, self._randint(1, 11), oct_eq=False)

        scale = to_str(pcs, octave)
        return scale, pcs

    def generate_source_scale(self, root: List[str]) -> List[str]:
        """
        Generate a multi-octave source scale from a root scale.

        Args:
            root: Root scale (note strings without octaves)

        Returns:
            List of notes with octaves (2-6)
        """
        scale = []
        n = 0
        octave = GENERATION_OCTAVE_START

        for _ in range(28):
            scale.append(f"{root[n]}{octave}")
            n += 1
            if n == len(root):
                octave += 1
                if octave == 6:
                    octave = GENERATION_OCTAVE_START
                n = 0

        return scale

    def generate_source_scales(
        self, total: Optional[int] = None
    ) -> Tuple[Dict[int, List[str]], List[str]]:
        """
        Generate a dictionary of source scales.

        Args:
            total: Optional number of scales to generate

        Returns:
            Tuple of (scales_dict, scale_info_list)
        """
        if total is None:
            total = self._get_default_count(MIN_SCALES, MAX_SCALES)

        sources = {}
        scale_info = []

        for i in range(total):
            root, info = self.pick_root()
            scale_info.append(info)
            sources[i] = self.generate_source_scale(root)

        return sources, scale_info

    def generate_notes(
        self,
        data: Optional[List] = None,
        root: Optional[List[str]] = None,
        total: Optional[int] = None,
    ) -> NoteGenerationResult:
        """
        Generate a set of notes for a melody.

        Args:
            data: Optional data list to map to notes
            root: Optional root scale to use
            total: Optional number of notes to generate

        Returns:
            NoteGenerationResult containing notes, metadata, and source notes
        """
        meta_data = []
        octave = self._randint(GENERATION_OCTAVE_START, 3)

        if root is None:
            root, info = self.pick_root(transpose=True, octave=None)
            meta_data.append(info)

        if data is None:
            gen_total = (
                total
                if total
                else self._get_default_count(MIN_NOTES - 1, MAX_NOTES - 1)
            )
        else:
            gen_total = max(data) + 1

        scale = self._build_source_scale(root, gen_total, octave, meta_data)
        notes = self._select_notes_from_scale(scale, data, total)

        return NoteGenerationResult(notes, meta_data, scale)

    def _build_source_scale(
        self, root: List[str], gen_total: int, octave: int, meta_data: List[str]
    ) -> List[str]:
        """Build a source scale for note generation."""
        scale = []
        n = 0

        for _ in range(gen_total):
            note = f"{root[n]}{octave}"
            scale.append(note)
            n += 1

            if n == len(root):
                octave += 1
                if octave > 5:
                    octave = self._randint(GENERATION_OCTAVE_START, 3)
                    root, info = self.pick_root(transpose=True, octave=None)
                    meta_data.append(info)
                n = 0

        return scale

    def _select_notes_from_scale(
        self, scale: List[str], data: Optional[List], total: Optional[int]
    ) -> List[str]:
        """Select notes from the source scale."""
        if data is None:
            pick_total = total if total else self._randint(3, len(scale))
            return [self._choice(scale) for _ in range(pick_total)]
        else:
            return [scale[i] for i in data]

    def derive_scales(
        self, pcs: List[int], octave: Optional[int] = None
    ) -> Dict[int, List[str]]:
        """
        Generate derivative scales based on each note in a given scale.

        Args:
            pcs: Pitch class set
            octave: Optional octave to assign

        Returns:
            Dictionary of variant scales
        """
        variants = {}

        for i, pc in enumerate(pcs):
            scale_variant = []
            note = pc
            while len(scale_variant) < len(pcs):
                note += self._randint(1, 3)
                scale_variant.append(note)
            variants[i] = scale_variant

        for key in variants:
            variants[key] = to_str(variants[key], octave=octave, oct_eq=False)

        return variants

    def pick_arpeggio(self, key: str) -> List[int]:
        """
        Get pitch classes outlining a one-octave arpeggio.

        Args:
            key: Arpeggio type key

        Returns:
            List of pitch class integers

        Raises:
            ValueError: If key is invalid
        """
        if key not in ARPEGGIOS:
            raise ValueError(
                f"'{key}' is not valid. Available: {list(ARPEGGIOS.keys())}"
            )
        return ARPEGGIOS[key]

    def generate_12tone_row(self) -> List[str]:
        """Generate a 12-tone row."""
        return self.random.sample(PITCH_CLASSES, len(PITCH_CLASSES))

    def generate_12tone_intervals(self) -> List[int]:
        """Generate 11 non-repeating intervals for 12-tone row transpositions."""
        chromatic = list(range(1, 12))
        return self.random.sample(chromatic, len(chromatic))

    def create_palindrome(
        self, melody: Union[Melody, List[Chord]]
    ) -> Union[Melody, List[Chord]]:
        """
        Create a palindrome from a melody or chord list.

        Args:
            melody: Melody object or list of Chord objects

        Returns:
            Modified melody or chord list as palindrome
        """
        if isinstance(melody, list):
            return melody + list(reversed(melody))
        elif isinstance(melody, Melody):
            melody.notes = melody.notes + list(reversed(melody.notes))
            melody.rhythms = melody.rhythms + list(reversed(melody.rhythms))
            melody.dynamics = melody.dynamics + list(reversed(melody.dynamics))
            return melody
        else:
            raise TypeError(f"Must be Melody or list. Got: {type(melody)}")

    def generate_rhythm(self) -> float:
        """Generate a single rhythm (not scaled to tempo)."""
        return self._choice(RHYTHMS)

    def generate_rhythms(
        self,
        total: Optional[int] = None,
        tempo: Optional[float] = None,
        source_rhythms: Optional[List[float]] = None,
    ) -> List[float]:
        """
        Generate a series of rhythms.

        Args:
            total: Optional number of rhythms to generate
            tempo: Optional tempo to scale to
            source_rhythms: Optional source rhythms to choose from

        Returns:
            List of rhythm values (in seconds if tempo provided)
        """
        if total is None:
            total = self._get_default_count(MIN_RHYTHMS, MAX_RHYTHMS)

        rhythms_source = source_rhythms if source_rhythms else RHYTHMS
        rhythms = []

        while len(rhythms) < total:
            rhythm = self._choice(rhythms_source)

            if self._randint(1, 2) == 1:
                limit = self._get_repetition_limit(total)
                total_reps = self._randint(1, limit)
                for _ in range(total_reps):
                    rhythms.append(rhythm)
                    if len(rhythms) == total:
                        break
            else:
                rhythms.append(rhythm)

        if tempo is not None and tempo != BASE_TEMPO:
            rhythms = scale_to_tempo(tempo, rhythms)

        return rhythms

    def _get_repetition_limit(self, total: int) -> int:
        """Calculate repetition limit based on total items."""
        limit = scale_limit(total)
        return max(limit, 2)

    def generate_dynamic(self, allow_rests: bool = True) -> int:
        """
        Generate a single dynamic/velocity.

        Args:
            allow_rests: Whether to allow rest (velocity 0)

        Returns:
            MIDI velocity value
        """
        if allow_rests and self._randint(0, 1) == 1:
            return REST
        return self._choice(DYNAMICS)

    def generate_dynamics(
        self, total: Optional[int] = None, allow_rests: bool = True
    ) -> List[int]:
        """
        Generate a list of dynamics.

        Args:
            total: Optional number of dynamics to generate
            allow_rests: Whether to allow rests

        Returns:
            List of MIDI velocity values
        """
        if total is None:
            total = self._get_default_count(MIN_DYNAMICS, MAX_DYNAMICS)

        dynamics = []

        while len(dynamics) < total:
            dynamic = self.generate_dynamic(allow_rests=allow_rests)

            if self._randint(1, 2) == 1:
                limit = self._get_repetition_limit(total)
                total_reps = self._randint(1, limit if dynamic != REST else 2)
                for _ in range(total_reps):
                    dynamics.append(dynamic)
                    if len(dynamics) == total:
                        break
            else:
                dynamics.append(dynamic)

        return dynamics

    def generate_chord(
        self,
        tempo: Optional[float] = None,
        scale: Optional[List[str]] = None,
        include_rhythm: bool = True,
    ) -> Chord:
        """
        Generate a 2-9 note chord.

        Args:
            tempo: Optional tempo
            scale: Optional scale to choose notes from
            include_rhythm: Whether to include rhythm and dynamic

        Returns:
            Chord object
        """
        chord = Chord()
        chord.tempo = tempo if tempo else BASE_TEMPO

        if scale is None:
            if self._randint(1, 2) == 1:
                chord.source_notes, chord.info = self.pick_root(
                    octave=self._randint(MIN_OCTAVE, MAX_OCTAVE)
                )
                chord.pcs = []
            else:
                chord.source_notes, chord.pcs = self.generate_scale(
                    octave=self._randint(MIN_OCTAVE, MAX_OCTAVE)
                )
                chord.info = "Invented Scale"
        else:
            chord.source_notes = scale

        total_notes = self._randint(MIN_CHORD_NOTES, MAX_CHORD_NOTES)
        chord.notes = [self._choice(chord.source_notes) for _ in range(total_notes)]

        if include_rhythm:
            rhythm = self.generate_rhythm()
            if chord.tempo != BASE_TEMPO:
                rhythm = scale_to_tempo(chord.tempo, rhythm)
            chord.rhythm = rhythm
            chord.dynamic = self.generate_dynamic(allow_rests=False)

        return chord

    def generate_chords(
        self,
        total: Optional[int] = None,
        tempo: Optional[float] = None,
        scale: Optional[List[str]] = None,
    ) -> List[Chord]:
        """
        Generate a chord progression.

        Args:
            total: Optional number of chords to generate
            tempo: Optional tempo
            scale: Optional scale to derive chords from

        Returns:
            List of Chord objects
        """
        if total is None:
            total = self._get_default_count(MIN_CHORDS, MAX_CHORDS)

        if tempo is None:
            tempo = self.generate_tempo()

        if scale is None:
            note_result = self.generate_notes()
            scale = note_result.notes

        return [self.generate_chord(tempo, scale) for _ in range(total)]

    def generate_triads(self, scale: List[str], total: int) -> List[Chord]:
        """
        Generate triads from a given multi-octave source scale.

        Args:
            scale: Multi-octave source scale
            total: Number of triads to generate

        Returns:
            List of Chord objects representing triads
        """
        triads = []

        for i in range(4, len(scale)):
            triad = Chord()
            triad.notes = [scale[i - 4], scale[i - 2], scale[i]]
            triad.rhythm = 2.0
            triad.dynamic = 100
            triads.append(triad)

            if len(triads) == total:
                break

        return triads

    def generate_symmetric_triad(self, root: int, interval: int, n: int) -> List[int]:
        """
        Generate an intervallically symmetrical chord.

        Args:
            root: Root pitch class (0-11)
            interval: Interval distance (1-6)
            n: Number of notes in chord

        Returns:
            List of pitch class integers

        Raises:
            ValueError: If interval is out of valid range
        """
        if not (1 <= interval <= 6):
            raise ValueError("Interval must be between 1 and 6")

        from utils.tools import oct_equiv

        if not (0 <= root <= 11):
            root = oct_equiv(root)

        chord = []
        current = root

        while len(chord) < n:
            chord.append(current)
            current += interval
            if current > 11:
                current = oct_equiv(current)

        return chord

    def generate_melody(
        self,
        tempo: Optional[float] = None,
        raw_data: Optional[List] = None,
        data_type: Optional[str] = None,
        total: Optional[int] = None,
        inst_range: Optional[List[str]] = None,
        allow_rests: bool = True,
    ) -> Melody:
        """
        Generate a melody with notes, rhythms, and dynamics.

        Args:
            tempo: Optional tempo in BPM
            raw_data: Optional data to map to notes
            data_type: Type of data ('int', 'float', 'chars', 'hex')
            total: Optional number of notes to generate
            inst_range: Optional instrument range to constrain notes
            allow_rests: Whether to allow rests in dynamics

        Returns:
            Melody object (instrument NOT assigned)
        """
        melody = Melody()

        processed_data = None
        if data_type is not None and raw_data is not None:
            melody.source_data = raw_data
            processed_data = map_data(raw_data, data_type)
        else:
            melody.source_data = []

        melody.tempo = tempo if tempo else self.generate_tempo()

        if raw_data is None:
            result = self.generate_notes(total=total)
        else:
            result = self.generate_notes(data=processed_data)

        melody.notes = result.notes
        melody.info = result.meta_data
        melody.source_notes = result.source_notes

        if inst_range is not None:
            melody.notes = [note for note in melody.notes if note in inst_range]

        melody.rhythms = self.generate_rhythms(len(melody.notes), melody.tempo)
        melody.dynamics = self.generate_dynamics(len(melody.notes), allow_rests)

        return melody

    def write_string_line(
        self, part: Melody, scale: List[str], total: int, include_rhythm: bool = False
    ) -> Melody:
        """
        Write a melodic line for a string instrument.

        Args:
            part: Melody object with instrument assigned
            scale: Source scale to choose notes from
            total: Number of notes to add
            include_rhythm: Whether to add independent rhythms and dynamics

        Returns:
            Modified Melody object

        Raises:
            ValueError: If instrument is not a string instrument
        """
        valid_instruments = ["Violin", "Viola", "Cello", "Contrabass"]
        if part.instrument not in valid_instruments:
            raise ValueError(f"Instrument must be one of {valid_instruments}")

        if include_rhythm:
            total = self._randint(12, 30)

        octave_ranges = {
            "Violin": (13, len(scale) - 1, "Violin"),
            "Viola": (7, len(scale) - 8, "Viola"),
            "Cello": (0, len(scale) - 16, "Cello"),
        }

        if part.instrument in octave_ranges:
            min_idx, max_idx, inst_name = octave_ranges[part.instrument]
            for _ in range(total):
                note = scale[self._randint(min_idx, max_idx)]
                while note not in RANGE[inst_name]:
                    note = scale[self._randint(min_idx, max_idx)]
                part.notes.append(note)

        if include_rhythm:
            part.rhythms.extend(
                self.generate_rhythms(total=len(part.notes), tempo=part.tempo)
            )
            part.dynamics.extend(self.generate_dynamics(total=len(part.notes)))

        return part

    def generate_composition(
        self, data: Optional[List] = None, data_type: Optional[str] = None
    ) -> Composition:
        """
        Generate a complete composition with melody and harmonies.

        Args:
            data: Optional data to map to melody
            data_type: Type of data if provided

        Returns:
            Complete Composition object with MIDI file exported
        """
        comp = self.initialize_composition()
        comp.ensemble = "duet"

        if data is not None and data_type is not None:
            melody = self.generate_melody(
                tempo=comp.tempo, raw_data=data, data_type=data_type
            )
        else:
            melody = self.generate_melody(tempo=comp.tempo)

        melody.instrument = self.generate_instrument()
        comp.add_part(melody, melody.instrument)

        chord_total = self._randint(floor(len(melody.notes) / 2), len(melody.notes))
        chords = self.generate_chords(
            total=chord_total, tempo=comp.tempo, scale=melody.notes
        )

        keyboard_instrument = INSTRUMENTS[
            self._randint(KEYBOARD_INSTRUMENT_START, KEYBOARD_INSTRUMENT_END)
        ]

        for chord in chords:
            chord.instrument = keyboard_instrument

        comp.add_part(chords, keyboard_instrument)
        comp.title = f"{comp.title} for mixed duet"

        export_midi(comp)
        comp.display()

        return comp
