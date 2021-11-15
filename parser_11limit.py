"""
Parsing tools for turning strings into 2.3.5.7.11 subgroup pitch vectors
"""

from fractions import Fraction
from numpy import array
from parser_5limit import CHORDS_5LIMIT
from parser_5limit import parse as base_parser
from note import PITCH_CONTEXT_11LIMIT


BASIC_INTERVALS = {
    "d2": (19, -12, 0, 0, 0),
    "d6": (18, -11, 0, 0, 0),
    "d3": (16, -10, 0, 0, 0),
    "d7": (15, -9, 0, 0, 0),
    "d4": (13, -8, 0, 0, 0),
    "d1": (11, -7, 0, 0, 0),
    "d5": (10, -6, 0, 0, 0),
    "m2": (8, -5, 0, 0, 0),
    "m6": (7, -4, 0, 0, 0),
    "m3": (5, -3, 0, 0, 0),
    "m7": (4, -2, 0, 0, 0),
    "P4": (2, -1, 0, 0, 0),
    "P1": (0, 0, 0, 0, 0),
    "P5": (-1, 1, 0, 0, 0),
    "M2": (-3, 2, 0, 0, 0),
    "M6": (-4, 3, 0, 0, 0),
    "M3": (-6, 4, 0, 0, 0),
    "M7": (-7, 5, 0, 0, 0),
    "A4": (-9, 6, 0, 0, 0),
    "A1": (-11, 7, 0, 0, 0),
    "A5": (-12, 8, 0, 0, 0),
    "A2": (-14, 9, 0, 0, 0),
    "A6": (-15, 10, 0, 0, 0),
    "A3": (-17, 11, 0, 0, 0),
    "A7": (-18, 12, 0, 0, 0),

    "vd5": (4, -4, 0, 1, 0),  # vd5u = 7/5
    "vm2": (2, -3, 0, 1, 0),
    "vm6": (1, -2, 0, 1, 0),  # = 14/9
    "vm3": (-1, -1, 0, 1, 0),  # = 7/6
    "vm7": (-2, 0, 0, 1, 0),  # harmonic 7th = 7/4
    "v4": (-4, 1, 0, 1, 0),
    "v1": (-6, 2, 0, 1, 0),
    "v5": (-7, 3, 0, 1, 0),

    "^4": (8, -3, 0, -1, 0),
    "^1": (6, -2, 0, -1, 0),  # = 64/63
    "^5": (5, -1, 0, -1, 0),  # = 32/21
    "^M2": (3, 0, 0, -1, 0),  # = 8/7
    "^M6": (2, 1, 0, -1, 0),  # = 12/7
    "^M3": (0, 2, 0, -1, 0),  # = 9/7
    "^M7": (-1, 3, 0, -1, 0),
    "^A4": (-3, 4, 0, -1, 0),  # ^A4d = 10/7

    "U4": (-3, 0, 0, 0, 1),  # undecimal superfourth = 11/8
    "U1": (-5, 1, 0, 0, 1),  # al-Farabi quartertone = 33/32
    "U5": (-6, 2, 0, 0, 1),

    "u4": (7, -2, 0, 0, -1),
    "u1": (5, -1, 0, 0, -1),  # u8 = undecimal infraoctave = 64/33
    "u5": (4, 0, 0, 0, -1),  # undecimal subfifth = 16/11

    "u2": (1, -1, 0, -1, 1),  # = 22/21
    "u6": (0, 0, 0, -1, 1),  # undecimal minor sixth = 11/7
    "u3": (-2, 1, 0, -1, 1),
    "u7": (-3, 2, 0, -1, 1),

    "U2": (4, -2, 0, 1, -1),
    "U6": (3, -1, 0, 1, -1),
    "U3": (1, 0, 0, 1, -1),  # undecimal major third = 14/11
    "U7": (0, 1, 0, 1, -1),
}


def parse_interval(token):
    """
    Parse an interval like vd5u given in terms of size and syntonic commas into a relative pitch vector
    """

    if token[1].isdigit():
        quality, token = token[0], token[1:]
    else:
        quality, token = token[:2], token[2:]
    if "u" in token:
        token, arrow_token = token.split("u", 1)
        if arrow_token.isdigit():
            arrows = int(arrow_token)
        else:
            arrows = 1
    elif "d" in token:
        token, arrow_token = token.split("d", 1)
        if arrow_token.isdigit():
            arrows = -int(arrow_token)
        else:
            arrows = -1
    else:
        arrows = 0
    interval_class = int(token)
    octave = (interval_class-1)//7
    basic_class = interval_class - octave*7

    result = array(BASIC_INTERVALS["{}{}".format(quality, basic_class)]) + array([octave, 0, 0, 0, 0])

    return result + arrows * array([-4, 4, -1, 0, 0])


CHORDS_11LIMIT = {
    "^M": ("P1", "^M3", "P5"),
    "^M7": ("P1", "^M3", "P5", "^M7"),

    "vm": ("P1", "vm3", "P5"),
    "vm7": ("P1", "vm3", "P5", "vm7"),

    "^v7": ("P1", "^M3", "P5", "vm7"),
    "^dom": ("P1", "^M3", "P5", "m7"),
    "h7": ("P1", "M3d", "P5", "vm7"),

    "^6": ("P1", "^M3", "P5", "^M6"),

    "h11": ("P1", "M3d", "P5", "vm7", "P8", "M9", "M10d", "U11"),
    "h12": ("P1", "M3d", "P5", "vm7", "P8", "M9", "M10d", "U11", "P12"),

    "UM": ("P1", "U3", "P5"),
    "UM7": ("P1", "U3", "P5", "U7"),

    "um": ("P1", "u3", "P5"),
    "um7": ("P1", "u3", "P5", "u7"),
}


CHORDS_11LIMIT.update(CHORDS_5LIMIT)


def parse(text, beat_duration=Fraction(1), initial_pitch=(0, 0, 0, 0, 0), extra_intervals=None, extra_chords=None, pitch_context=None):
    """
    Parse a string of intervals separated by whitespace into Note instances
    """
    if pitch_context is None:
        pitch_context = PITCH_CONTEXT_11LIMIT
    return base_parser(text, beat_duration, initial_pitch, extra_intervals, extra_chords, pitch_context, parse_interval, CHORDS_11LIMIT)
