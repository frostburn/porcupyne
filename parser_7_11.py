"""
Parsing tools for turning strings into 2.7.11 subgroup pitch vectors
"""

from fractions import Fraction
from numpy import array
from parser_5limit import parse as base_parser
from note import PITCH_CONTEXT_7_11


BASIC_INTERVALS = {
    "n2": (52, 0, -15),
    "d6": (49, 0, -14),
    "d2": (45, 0, -13),
    "d5": (42, 0, -12),
    "d1": (38, 0, -11),
    "n4": (35, 0, -10),
    "n7": (32, 0, -9),
    "M3": (28, 0, -8),
    "s7": (25, 0, -7),
    "m3": (21, 0, -6),
    "n6": (18, 0, -5),  # n6u = 128/77
    "m2": (14, 0, -4),  # m2u = 8/7
    "s6": (11, 0, -3),  # s6u = 11/7
    "s2": (7, 0, -2),  # s2u = 121/112
    "s5": (4, 0, -1),  # = 16/11
    "P1": (0, 0, 0),  # = 1/1
    "S4": (-3, 0, 1),  # = 11/8
    "M7": (-6, 0, 2),  # M7d = 224/121
    "S3": (-10, 0, 3),  # S3d = 14/11
    "m7": (-13, 0, 4),  # m7d = 7/4
    "N3": (-17, 0, 5),  # N3d = 77/64
    "M6": (-20, 0, 6),
    "S2": (-24, 0, 7),
    "m6": (-27, 0, 8),
    "N2": (-31, 0, 9),
    "N5": (-34, 0, 10),
    "A1": (-38, 0, 11),
    "A4": (-41, 0, 12),
    "S7": (-44, 0, 13),
    "A3": (-48, 0, 14),
    "N7": (-51, 0, 15),
}


def parse_interval(token):
    """
    Parse an interval like N3u2 given in terms of size and frostburn commas into a relative pitch vector
    """

    quality, token = token[0], token[1:]
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

    return result + arrows * array([-11, -1, 4])


CHORDS_7_11 = {
    "U": ("P1",),

    "Sq": ("P1", "S4", "M7"),
    "sq": ("P1", "s5", "s9"),

    "S-": ("P1", "S3d", "S4"),
    "N-": ("P1", "N3d", "S4"),
    "M6-": ("P1", "M6d", "S4"),
    "m-": ("P1", "m3u", "S4"),
    "m2-": ("P1", "m2u", "S4"),
    "n6-": ("P1", "n6u", "S4"),

    "S+": ("P1", "S3d", "s5"),
    "N+": ("P1", "N3d", "s5"),
    "M6+": ("P1", "M6d", "s5"),
    "m+": ("P1", "m3u", "s5"),
    "m2+": ("P1", "m2u", "s5"),
    "n6+": ("P1", "n6u", "s5"),

    "M7+": ("P1", "S3d", "s5", "M7d"),
    "m7+": ("P1", "N3d", "s5", "m7d"),
    "m7-": ("P1", "S3d", "S4", "m7d"),
    "s7+": ("P1", "m3u", "s5", "s7u"),
}


def parse(text, beat_duration=Fraction(1), initial_pitch=(0, 0, 0), extra_intervals=None, extra_chords=None, pitch_context=None):
    """
    Parse a string of intervals separated by whitespace into Note instances
    """
    if pitch_context is None:
        pitch_context = PITCH_CONTEXT_7_11
    return base_parser(text, beat_duration, initial_pitch, extra_intervals, extra_chords, pitch_context, parse_interval, CHORDS_7_11)
