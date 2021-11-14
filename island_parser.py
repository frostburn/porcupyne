"""
Parsing tools for turning strings into 2.3.13/5 subgroup pitch vectors
"""

from fractions import Fraction
from numpy import array
from parser_5limit import parse as base_parser
from note import ISLAND_PITCH_CONTEXT


BASIC_INTERVALS = {
    "d2": (19, -12, 0),
    "d6": (18, -11, 0),
    "d3": (16, -10, 0),
    "d7": (15, -9, 0),
    "d4": (13, -8, 0),
    "d1": (11, -7, 0),
    "d5": (10, -6, 0),
    "m2": (8, -5, 0),
    "m6": (7, -4, 0),
    "m3": (5, -3, 0),
    "m7": (4, -2, 0),
    "P4": (2, -1, 0),
    "P1": (0, 0, 0),
    "P5": (-1, 1, 0),
    "M2": (-3, 2, 0),
    "M6": (-4, 3, 0),
    "M3": (-6, 4, 0),
    "M7": (-7, 5, 0),
    "A4": (-9, 6, 0),
    "A1": (-11, 7, 0),
    "A5": (-12, 8, 0),
    "A2": (-14, 9, 0),
    "A6": (-15, 10, 0),
    "A3": (-17, 11, 0),
    "A7": (-18, 12, 0),

    "wm2": (24, -16, 1),
    "wm6": (23, -15, 1),
    "wm3": (21, -14, 1),
    "wm7": (20, -13, 1),
    "w4": (18, -12, 1),
    "w1": (16, -11, 1),
    "w5": (15, -10, 1),
    "@2": (13, -9, 1),
    "@6": (12, -8, 1),
    "@3": (10, -7, 1),
    "@7": (9, -6, 1),
    "^4": (7, -5, 1),
    "^1": (5, -4, 1),
    "^5": (4, -3, 1),
    "^M2": (2, -2, 1),
    "^M6": (1, -1, 1),
    "^M3": (-1, 0, 1),
    "^M7": (-2, 1, 1),
    "^A4": (-4, 2, 1),
    "^A1": (-6, 3, 1),
    "^A5": (-7, 4, 1),
    "^A2": (-9, 5, 1),
    "^A6": (-10, 6, 1),
    "^A3": (-12, 7, 1),
    "^A7": (-13, 8, 1),
    "*5": (-15, 9, 1),
    "*2": (-17, 10, 1),
    "*6": (-18, 11, 1),
    "*3": (-20, 12, 1),
    "*7": (-21, 13, 1),

    "vd2": (14, -8, -1),
    "vd6": (13, -7, -1),
    "vd3": (11, -6, -1),
    "vd7": (10, -5, -1),
    "vd4": (8, -4, -1),
    "vd1": (6, -3, -1),
    "vd5": (5, -2, -1),
    "vm2": (3, -1, -1),
    "vm6": (2, 0, -1),
    "vm3": (0, 1, -1),
    "vm7": (-1, 2, -1),
    "v4": (-3, 3, -1),
    "v1": (-5, 4, -1),
    "v5": (-6, 5, -1),
    "~2": (-8, 6, -1),
    "~6": (-9, 7, -1),
    "~3": (-11, 8, -1),
    "~7": (-12, 9, -1),
}


def parse_interval(token):
    """
    Parse an interval like ^M7d2 given in terms of size and island commas into a relative pitch vector
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

    result = array(BASIC_INTERVALS["{}{}".format(quality, basic_class)]) + array([octave, 0, 0])

    return result + arrows * array([2, -3, 2])


ISLAND_CHORDS = {
    "U": ("P1",),

    "sus2": ("P1", "M2", "P5"),
    "sus4": ("P1", "P4", "P5"),
    "quartal": ("P1", "P4", "m7"),
    "quintal": ("P1", "P5", "M9"),
    "sus2add6": ("P1", "M2", "P5", "M6"),

    "^M": ("P1", "^M3", "P5"),
    "^M7": ("P1", "^M3", "P5", "^M7"),

    "vm": ("P1", "vm3", "P5"),
    "vm7": ("P1", "vm3", "P5", "vm7"),

    "^v7": ("P1", "^M3", "P5", "vm7"),
    "^dom": ("P1", "^M3", "P5", "m7"),
}


def parse(text, beat_duration=Fraction(1), initial_pitch=(0, 0, 0), extra_intervals=None, extra_chords=None, pitch_context=None):
    """
    Parse a string of intervals separated by whitespace into Note instances
    """
    if pitch_context is None:
        pitch_context = ISLAND_PITCH_CONTEXT
    return base_parser(text, beat_duration, initial_pitch, extra_intervals, extra_chords, pitch_context, parse_interval, ISLAND_CHORDS)
