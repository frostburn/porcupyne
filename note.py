"""
Containers for multi-dimensional MIDI style data
"""
from functools import total_ordering
from numpy import array, dot, exp
from temperament import JI_5LIMIT, mod_comma


class PitchContext:
    """
    Defines how pitch vectors are interpreted as frequencies
    """

    def __init__(self, mapping, base_frequency=440, comma=None):
        self.mapping = mapping
        self.base_frequency = base_frequency
        self.comma = comma

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
        return self.__class__(self.mapping, self.base_frequency*2)

    def bass(self):
        """
        Return a copy of the pitch context tuned down by a pure octave
        """
        return self.__class__(self.mapping, self.base_frequency/2)


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
