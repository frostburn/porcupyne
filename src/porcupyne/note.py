# coding: utf-8
"""
Notation and containers for multi-dimensional MIDI style data
"""
from functools import total_ordering
from numpy import array, dot, exp
from .temperament import JI_5LIMIT, mod_comma, canonize, canonize2, JI_ISLAND, JI_7LIMIT, JI_11LIMIT, JI_3_7, canonize_3_7, canonize2_3_7, canonize_7_11, JI_7_11
from .util import note_unicode
from hewmp.parser import parse_text, RealTuning, RealDynamic, GatedNote


LYDIAN = ("F", "C", "G", "D", "A", "E", "B")
LYDIAN_INDEX_A = LYDIAN.index("A")
REFERENCE_OCTAVE = 4


def notate(threes, fives, twos=None, horogram="JI"):
    """
    Gives the notation for a 5-limit pitch vector in terms of letter, sharp signs, arrows and octaves.
    """

    if horogram == "JI":
        index = LYDIAN_INDEX_A + threes + fives*4
        sharps = index // len(LYDIAN)
        letter = LYDIAN[index % len(LYDIAN)]
        arrows = -fives

    if twos is None:
        if horogram == "JI":
            return letter, sharps, arrows
        if horogram == "dicot":
            permutation = [0, 4, 1, 5, 2, 6, 3]
            num = fives + 2*threes
            return notate((num//len(permutation))*len(permutation) + permutation[num % len(permutation)], 0, horogram="JI")
        if horogram == "blackwood":
            threes = threes - ((threes + 1)//5)*5
            if threes == 3:
                return notate(threes + 4*fives + 4, -1, horogram="JI")
            return notate(threes + 4*fives, 0, horogram="JI")
        if horogram == "magic":
            fifths_19edo = [0, 7, 14, 2, 9, 16, 4, 11, 18, 6, 13, 1, 8, 15, 3, 10, 17, 5, 12]
            index = fives + 5*threes
            edo19 = (threes*30 + fives*44) % 19
            meantone = (fifths_19edo[edo19] + 9) % 19 - 9
            arrows = index // 19
            return notate(meantone + arrows*4, -arrows, horogram="JI")
        if horogram == "würschmidt":
            fifths_31edo = [0, 19, 7, 26, 14, 2, 21, 9, 28, 16, 4, 23, 11, 30, 18, 6, 25, 13, 1, 20, 8, 27, 15, 3, 22, 10, 29, 17, 5, 24, 12]
            index = fives + 8*threes
            edo31 = (threes*49 + fives*72) % 31
            meantone = (fifths_31edo[edo31] + 11) % 31 - 11
            arrows = index // 31
            return notate(meantone + arrows*4, -arrows, horogram="JI")
        threes, fives = canonize(threes, fives, horogram=horogram)
        return notate(threes, fives, horogram="JI")

    if horogram == "JI":
        edo12 = twos*12 + threes*19 + fives*28
        octaves = REFERENCE_OCTAVE + (edo12 + 9)//12
        return letter, sharps, arrows, octaves
    if horogram == "magic":
        letter, sharps, arrows = notate(threes, fives, horogram="magic")
        index = fives + 5*threes
        corrections = [0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6]
        correction = 2*index + (index // 19)*6 + corrections[index % 19]
        return letter, sharps, arrows, twos + REFERENCE_OCTAVE + correction
    twos, threes, fives = canonize2(twos, threes, fives, horogram=horogram)
    return notate(threes, fives, twos=twos, horogram="JI")


def notate_island(threes, supermajors, twos=None, horogram="JI", flatward=False):
    """
    Gives the notation for a 2.3.13/5 subgroup pitch vector in terms of letter, (half) sharp signs, arrows and octaves.
    """
    if horogram == "JI":
        if flatward:
            index = LYDIAN_INDEX_A + threes + supermajors*4 - ((supermajors+1)//2)*5
            sharps = index // len(LYDIAN) - 0.5*(supermajors % 2)
            letter = LYDIAN[index % len(LYDIAN)]
            arrows = (supermajors + 1)//2
        else:
            index = LYDIAN_INDEX_A + threes + supermajors*4 - (supermajors//2)*5
            sharps = index // len(LYDIAN) + 0.5*(supermajors % 2)
            letter = LYDIAN[index % len(LYDIAN)]
            arrows = supermajors // 2

    if twos is None:
        if horogram == "JI":
            return letter, sharps, arrows
        if horogram == "barbados":
            letter, sharps, arrows = notate_island(threes, supermajors, horogram="JI")
            return letter, sharps, 0

    if horogram == "JI":
        edo24 = twos*24 + threes*38 + supermajors*33
        octaves = REFERENCE_OCTAVE + (edo24 + 18)//24
        return letter, sharps, arrows, octaves
    if horogram == "barbados":
        letter, sharps, arrows, octaves = notate_island(threes, supermajors, twos=twos, horogram="JI")
        return letter, sharps, 0, octaves

    raise ValueError("Unknown temperament")


def notate_3_7(threes, sevens, twos=None, horogram="JI"):
    """
    Gives the notation for a 2.3.7 subgroup pitch vector in terms of letter, sharp signs, (sagittal septimal) arrows and octaves.
    """
    if horogram == "JI":
        index = LYDIAN_INDEX_A + threes - sevens*2
        sharps = index // len(LYDIAN)
        letter = LYDIAN[index % len(LYDIAN)]
        arrows = -sevens

    if twos is None:
        if horogram == "JI":
            return letter, sharps, arrows
        if horogram == "slendric":
            fifths_5edo = [0, 2, 4, 1, 3]
            index = sevens -3*threes
            edo5 = (threes*8 + sevens*14) % 5
            archy = (fifths_5edo[edo5] + 2) % 5 - 2
            arrows = index // 5
            return notate_3_7(archy - arrows*2, arrows, horogram="JI")
        threes, sevens = canonize_3_7(threes, sevens, horogram=horogram)
        return notate_3_7(threes, sevens, horogram="JI")

    if horogram == "JI":
        edo12 = twos*12 + threes*19 + sevens*34
        octaves = REFERENCE_OCTAVE + (edo12 + 9)//12
        return letter, sharps, arrows, octaves
    twos, threes, sevens = canonize2_3_7(twos, threes, sevens, horogram=horogram)
    return notate_3_7(threes, sevens, twos=twos, horogram="JI")


DARK_24EDO = {
    0: ("C", -0.0),
    1: ("D", -1.5),
    2: ("D", -1.0),
    3: ("D", -0.5),
    4: ("D", -0.0),
    5: ("E", -1.5),
    6: ("E", -1.0),
    7: ("E", -0.5),
    8: ("E", -0.0),
    9: ("F", -0.5),
    10: ("F", -0.0),
    11: ("G", -1.5),
    12: ("G", -1.0),
    13: ("G", -0.5),
    14: ("G", -0.0),
    15: ("A", -1.5),
    16: ("A", -1.0),
    17: ("A", -0.5),
    18: ("A", -0.0),
    19: ("B", -1.5),
    20: ("B", -1.0),
    21: ("B", -0.5),
    22: ("B", -0.0),
    23: ("C", -0.5),
}

LIGHT_24EDO = {
    0: ("C", 0.0),
    1: ("C", 0.5),
    2: ("C", 1.0),
    3: ("C", 1.5),
    4: ("D", 0.0),
    5: ("D", 0.5),
    6: ("D", 1.0),
    7: ("D", 1.5),
    8: ("E", 0.0),
    9: ("E", 0.5),
    10: ("F", 0.0),
    11: ("F", 0.5),
    12: ("F", 1.0),
    13: ("F", 1.5),
    14: ("G", 0.0),
    15: ("G", 0.5),
    16: ("G", 1.0),
    17: ("G", 1.5),
    18: ("A", 0.0),
    19: ("A", 0.5),
    20: ("A", 1.0),
    21: ("A", 1.5),
    22: ("B", 0.0),
    23: ("B", 0.5),
}


def notate_7_11(sevens, elevens, twos=None, horogram="JI"):
    """
    Gives the notation for a 2.7.11 subgroup pitch vector in terms of letter, (half) sharp signs, (frostburn?) arrows and octaves.
    """
    # Note: Centers around C  TODO: Consider centering around A
    if horogram == "JI":
        index = elevens + 4*sevens
        edo24 = 83*index
        if index < 0:
            stratum = 1 + index // 24
            letter, sharps = DARK_24EDO[(edo24 - 4*stratum)%len(DARK_24EDO)]
            if stratum: # Preserve signed zeros
                sharps += 2*stratum
        else:
            stratum = index // 24
            # Note: Theres some room to do {edo24 - 2*stratum; sharps += stratum} here as B# is unused, but not enough it turns out.
            letter, sharps = LIGHT_24EDO[(edo24 - 4*stratum)%len(LIGHT_24EDO)]
            sharps += 2*stratum
        arrows = sevens

    if twos is None:
        if horogram == "JI":
            return letter, sharps, arrows
        if horogram == "orga":
            superfourths_31edo = [0, 20, 9, 29, 18, 7, 27, 16, 5, 25, 14, 3, 23, 12, 1, 21, 10, 30, 19, 8, 28, 17, 6, 26, 15, 4, 24, 13, 2, 22, 11]
            index = sevens + 8*elevens
            edo31 = (sevens*87 + elevens*107) % 31
            frostburn = (superfourths_31edo[edo31] + 11) % 31 - 11
            arrows = index // 31
            return notate_7_11(-arrows, frostburn + arrows*4, horogram="JI")
        sevens, elevens = canonize_7_11(sevens, elevens, horogram=horogram)
        return notate_7_11(sevens, elevens, horogram="JI")

    if horogram == "JI":
        edo24 = 24*twos + 83*elevens + 67*sevens  # TODO: Figure out if this is right at all
        octaves = REFERENCE_OCTAVE + edo24//24
        return letter, sharps, arrows, octaves

    raise ValueError("Unknown temperament")


def note_unicode_5limit(threes, fives, twos=None, horogram="JI"):
    octaves = None
    if twos is None:
        letter, sharps, arrows = notate(threes, fives, horogram=horogram)
    else:
        letter, sharps, arrows, octaves = notate(threes, fives, twos=twos, horogram=horogram)
    return note_unicode(letter, sharps, arrows, octaves)


@total_ordering
class Note:
    """
    Notes carry pitch vector, duration, note on time, note on velocity and note off velocity data.
    A Note instance is associated with a tuning for interpreting pitch vectors as frequencies
    """
    def __init__(self, pitch=None, duration=None, time=None, velocity=0.7, off_velocity=0.5, tuning=None):
        self.pitch = pitch
        self.duration = duration
        self.time = time
        self.velocity = velocity
        self.off_velocity = off_velocity
        self.tuning = tuning

    @property
    def off_time(self):
        if self.duration is None or self.time is None:
            return None
        return self.time + self.duration

    @property
    def freq(self):
        if self.pitch is None:
            return None
        return self.tuning.pitch_to_freq_rads(self.pitch)[0]

    @property
    def rads(self):
        if self.pitch is None:
            return None
        return self.tuning.pitch_to_freq_rads(self.pitch)[1]

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        return self.tuning.equals(self.pitch, other.pitch)

    def __repr__(self):
        try:
            p = tuple(self.pitch)
        except TypeError:
            p = self.pitch
        return "{}({}, {}, {}, {}, {})".format(self.__class__.__name__, p, self.duration, self.time, self.velocity, self.off_velocity)

    def copy(self):
        return self.__class__(self.pitch[:], self.duration, self.time, self.velocity, self.off_velocity, self.tuning)

    @classmethod
    def from_gated_note(cls, gated_note, dynamic, tuning):
        return cls(gated_note.pitch, gated_note.realduration, gated_note.realtime, dynamic.velocity, tuning=tuning)

    @classmethod
    def from_note(cls, note, dynamic, tuning):
        return cls(note.pitch, note.duration, note.time, dynamic.velocity, tuning=tuning)


def sonorities(notes, tolerance=1e-6):
    """
    Break notes into groups that sound together.
    """
    notes = list(sorted(notes, key=lambda n: n.time))
    result = []
    sonority = []
    while notes:
        time = notes[0].time
        for note in sonority[:]:
            if note.off_time < time + tolerance:
                sonority.remove(note)
        while notes and abs(notes[0].time - time) < tolerance:
            sonority.append(notes.pop(0))
        result.append((time, sonority[:]))
    if sonority:
        off_time = max(note.off_time for note in sonority)
        result.append((off_time, []))
    return result


def from_midi(filename):
    import mido
    midi = mido.MidiFile(filename)

    results = []
    for track in midi.tracks:
        result = []
        note_ons = {}
        current_time = 0
        for message in track:
            current_time += message.time
            if message.type == "note_on":
                note_ons[(message.channel, message.note)] = (current_time, message.velocity)
            if message.type == "note_off":
                on_time, on_velocity = note_ons.pop((message.channel, message.note))
                result.append(Note(message.note, current_time - on_time, on_time, on_velocity, message.velocity))
        for key, value in note_ons.items():
            channel, note = key
            on_time, on_velocity = value
            result.append(Note(note, current_time - on_time, on_time, on_velocity))
        results.append(result)
    return results


def from_hewmp(text):
    tracks, _ = parse_text(text)

    notes = []
    for track in tracks:
        for event in track.realize().events:
            if isinstance(event, RealTuning):
                tuning = event
            if isinstance(event, RealDynamic):
                dynamic = event
            if isinstance(event, GatedNote):
                notes.append(Note.from_gated_note(event, dynamic, tuning))
    return notes
