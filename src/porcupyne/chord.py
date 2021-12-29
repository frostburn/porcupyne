from functools import reduce
from .util import gcd


class Chord(object):
    """
    Set of frequencies that can be compactified using octave equivalency
    """
    def __init__(self, *freqs):
        if 0 in freqs:
            raise ValueError("Zero is not a valid frequency")
        self.freqs = tuple(sorted(freqs))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(map(repr, self.freqs)))

    def has_duplicates(self):
        """
        Check if the chord contains octave-repeated notes.
        """
        simple = self.simplify()
        for i in range(len(self.freqs)):
            for j in range(i+1, len(self.freqs)):
                if simple[i] == simple[j]:
                    return True
        return False

    def simplify(self):
        """
        Create a new possibly wider chord with factors of two removed from the frequencies.
        """
        freqs = []
        for freq in self.freqs:
            while freq % 2 == 0:
                freq //= 2
            freqs.append(freq)
        return self.__class__(*freqs)

    def reduce(self):
        """
        Create a new chord with common factors eliminated.
        """
        divisor = reduce(gcd, self.freqs)
        return self.__class__(*[f // divisor for f in self.freqs])

    def height(self):
        """
        Return the ratio between the highest and lowest frequencies
        """
        return self.freqs[-1] / self.freqs[0]

    def center_of_gravity(self):
        """
        Return a dimensionless measure of the top-heaviness of the chord between 0 and 1
        """
        return sum(self.freqs) / (len(self.freqs) * self.freqs[0])

    def inversions(self):
        """
        Return all inversions of the chord in compact form
        """
        result = []
        inversion = self.compact()
        for _ in range(len(self)):
            result.append(inversion)
            inversion = self.__class__(inversion[0]*2, *inversion[1:])
        return result

    def compact(self, iterations=16):
        """
        Return the inversion that fits inside the smallest interval with the lowest center of gravity.
        """
        best = self
        candidate = self
        for _ in range(iterations):
            candidate = self.__class__(candidate[0]*2, *candidate[1:])
            if candidate.is_more_compact_than(best):
                best = candidate
        return best.reduce()

    def is_more_compact_than(self, other):
        """
        Compare compactness by chord height and bottom-heaviness
        """
        if self.height() < other.height():
            return True
        if self.freqs[-1] * other.freqs[0] == other.freqs[-1] * self.freqs[0]:
            if self.center_of_gravity() < other.center_of_gravity():
                return True
        return False

    def negative(self):
        """
        Returns the negative harmony version of the chord.
        """
        numerator = 1
        for f in self.freqs:
            numerator *= f
        return self.__class__(*[numerator // f for f in self.freqs])

    def __eq__(self, other):
        return self.freqs == other.freqs

    def __hash__(self):
        return hash(self.freqs)

    def __lt__(self, other):
        return self.freqs < other.freqs

    def __getitem__(self, key):
        return self.freqs[key]

    def __iter__(self):
        return self.freqs.__iter__()

    def __len__(self):
        return len(self.freqs)


def unique_chords(freqs, num_notes):
    """
    Return all unique chords that can be built from a set of frequencies in compact form.
    """
    freqs = tuple(freqs)
    def build(fs, i, n):
        if n == 0:
            return [fs]
        res = []
        for j, f in enumerate(freqs[i+1:], start=i+1):
            res.extend(build(fs + [f], j, n-1))
        return res

    chords = set()
    for chord in build([], -1, num_notes):
        chord = Chord(*chord)
        if chord.has_duplicates():
            continue
        chords.add(chord.compact())

    return chords
