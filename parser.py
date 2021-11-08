"""
Parsing tools for turning strings into 5-limit pitch vectors
"""
from numpy import array

LYDIAN = ("F", "C", "G", "D", "A", "E", "B")


def parse_pitch(token, reference_letter="A", reference_octave=4, first_letter_of_the_octave="C"):
    """
    Parse a pitch like F#3d2 given in terms of octaves and syntonic commas into a pitch vector
    """

    letter, token = token[0], token[1:]
    sharps = 0
    while token and token[0] in ("b", "#", "x"):
        if token[0] == "b":
            sharps -= 1
        elif token[0] == "#":
            sharps += 1
        else:
            sharps += 2
        token = token[1:]
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
    if token.isdigit():
        octave = int(token) - reference_octave
    else:
        octave = 0

    fifths = LYDIAN.index(letter) - LYDIAN.index(reference_letter) + sharps * len(LYDIAN)
    threes = fifths + 4*arrows
    fives = -arrows

    if reference_letter != "A" or first_letter_of_the_octave != "C":
        raise NotImplementedError("Dynamic reference not implemented")
    octave_correction = {
        "B": -3,
        "G": 3,
        "D": 1,
        "C": 4,
        "E": -2,
        "A": 0,
        "F": 6,
    }
    twos = -4*arrows + octave + octave_correction[letter]

    return array([twos, threes, fives])


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
}


def parse_interval(token):
    """
    Parse an interval like d7u2 given in terms of size and syntonic commas into a relative pitch vector
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

    return result + arrows * array([-4, 4, -1])
