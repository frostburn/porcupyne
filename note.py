# coding: utf-8
"""
Notation and containers for multi-dimensional MIDI style data
"""
from functools import total_ordering
from numpy import array, dot, exp
from temperament import JI_5LIMIT, mod_comma, canonize, canonize2
from util import note_unicode


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
                return (threes + 4*fives + 4, -1)
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


def note_unicode_5limit(threes, fives, twos=None, horogram="JI"):
    octaves = None
    if twos is None:
        letter, sharps, arrows = notate(threes, fives, horogram=horogram)
    else:
        letter, sharps, arrows, octaves = notate(threes, fives, twos=twos, horogram=horogram)
    return note_unicode(letter, sharps, arrows, octaves)


class PitchContext:
    """
    Defines how pitch vectors are interpreted as frequencies
    """

    def __init__(self, mapping, comma=None, base_frequency=440):
        self.mapping = mapping
        self.comma = comma
        self.base_frequency = base_frequency

    def pitch_to_freq(self, vector):
        return exp(dot(self.mapping, vector)) * self.base_frequency

    def interval_to_ratio(self, vector):
        return exp(dot(self.mapping, vector))

    def equals(self, vector_a, vector_b):
        if self.comma is None:
            return (array(vector_a) == array(vector_b)).all()
        return (mod_comma(vector_a, self.comma) == mod_comma(vector_b, self.comma)).all()

    def treble(self):
        """
        Return a copy of the pitch context tuned up by a pure octave
        """
        return self.__class__(self.mapping, self.comma, self.base_frequency*2)

    def bass(self):
        """
        Return a copy of the pitch context tuned down by a pure octave
        """
        return self.__class__(self.mapping, self.comma, self.base_frequency/2)


DEFAULT_PITCH_CONTEXT = PitchContext(JI_5LIMIT)


@total_ordering
class Note:
    """
    Notes carry pitch vector, duration, note on time, note on velocity, note off velocity data.
    A Note instance is associated with a context for interpreting pitch vectors as frequencies
    """
    def __init__(self, pitch=None, duration=None, time=None, velocity=0.7, off_velocity=0.5, context=None):
        self.pitch = pitch
        self.duration = duration
        self.time = time
        self.velocity = velocity
        self.off_velocity = off_velocity
        self._context = context

    @property
    def off_time(self):
        if self.duration is None or self.time is None:
            return None
        return self.time + self.duration

    @property
    def context(self):
        return self._context or DEFAULT_PITCH_CONTEXT

    @property
    def freq(self):
        if self.pitch is None:
            return None
        return self.context.pitch_to_freq(self.pitch)

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        return self.context.equals(self.pitch, other.pitch)

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, tuple(self.pitch), self.duration, self.time)
