# coding: utf-8
"""
Tools for tempering out commas from musical tunings, particularly 5-limit just intonation.
"""

from functools import reduce
from itertools import combinations
from numpy import log, dot, array, cross, absolute, sign
from numpy.linalg import norm
from util import gcd

JI_5LIMIT = log(array([2, 3, 5]))
EPSILON = 1e-12

COMMA_BY_HOROGRAM = {
    # Exotemperaments
    "father": (4, -1, -1),
    "bug": (0, 3, -2),
    # Main sequence
    "dicot": (-3, -1, 2),
    "meantone": (-4, 4, -1),
    "augmented": (7, 0, -3),
    "mavila": (-7, 3, 1),
    "porcupine": (1, -5, 3),
    "blackwood": (8, -5, 0),
    "dimipent": (3, 4, -4),
    "srutal": (11, -4, -2),
    "magic": (-10, -1, 5),
    "ripple": (-1, 8, -5),
    "hanson": (-6, -5, 6),
    "negripent": (-14, 3, 4),
    "tetracot": (5, -9, 4),
    "superpyth": (12, -9, 1),
    "helmholtz": (-15, 8, 1),
    "sensipent": (2, 9, -7),
    "passion": (18, -4, -5),
    "würschmidt": (17, 1, -8),
    "compton": (-19, 12, 0),
    "amity": (9, -13, 5),
    "orson": (-21, 3, 7),
    # Bonus
    "vishnu": (23, 6, -14),
    "luna": (38, -2, -15),

    # Additional coverage
    "shibboleth": (-5, -10, 9),
    "quinbigu": (9, 9, -10),
    "quintriyo": (-11, -15, 15),
    "doublewide": (-9, -6, 8),
    "unicorn": (-2, 13, -8),
    "fifive": (-1, -14, 10),
    "nusecond": (5, 13, -11),
    "parakleismic": (8, 14, -13),
    "valentine": (13, 5, -9),
    "sevond": (6, -14, 7),

    # Special
    "bohpieric": (0, -19, 13),
    "wronecki": (-5, 12, -6),
}


COMMA_NAME_BY_HOROGRAM = {
    "bug": "large limma",
    "father": "just diatonic semitone",
    "dicot": "classic chromatic semitone",
    "meantone": "syntonic",
    "augmented": "diesis",
    "dimipent": "major diesis",
    "srutal": "diaschisma",
    "hanson": "kleisma",
    "negripent": "negri",
    "vishnu": "vishnuzma",
    "parakleismic": "parakleisma",
    "bohpieric": "bohpier",
}


def temper(comma_list, just_mapping=JI_5LIMIT, num_iterations=1000):
    """
    Temper out a given list of commas.

    The magnitude of the resulting mapping is arbitrary.
    """
    if len(just_mapping) == 3:
        if len(comma_list) == 2:
            mapping = cross(comma_list[0], comma_list[1])
            if mapping[0] < 0:
                mapping = -mapping
            mapping //= reduce(gcd, mapping)
            return mapping
        if len(comma_list) == 1:
            comma = comma_list[0]
            pseudo_comma = cross(just_mapping, comma)
            mapping = cross(comma, pseudo_comma)
            if mapping[0] < 0:
                mapping = -mapping
            mapping *= just_mapping[0] / mapping[0]
            return mapping
    mapping = array(just_mapping)
    normalized_comma_list = [array(comma) / norm(comma) for comma in comma_list]
    for _ in range(num_iterations):
        for comma in normalized_comma_list:
            mapping = mapping - dot(mapping, comma)*comma
    return mapping


def minimax(mapping, just_mapping=JI_5LIMIT):
    """
    Scale the mapping to minimize the maximum error from just intonation.
    """
    least_error = float("inf")
    best_mapping = mapping
    for i, j in combinations(list(range(len(just_mapping))), 2):
        candidate = mapping / (mapping[i] + mapping[j]) * (just_mapping[i] + just_mapping[j])
        error = abs(just_mapping - candidate).max()
        if error < least_error:
            least_error = error
            best_mapping = candidate
    return best_mapping


def rank2_pergen(comma, mapping=None, search_depth=10):
    """
    Work out the period and generator of a temperament eliminating a given comma.
    """
    if len(comma) != 3:
        raise NotImplementedError("Only rank 3 to rank 2 reduction implemented")
    comma = array(comma)
    edo = abs(gcd(comma[1], comma[2]))
    period = None
    for i in range(-search_depth, search_depth+1):
        two = comma*i + array([1, 0, 0])
        if two[0] % edo == 0:
            if period is None or absolute(two // edo).sum() < absolute(period).sum():
                period = two // edo
    if period is None:
        period = array([1, 0, 0])
    if comma[1] == 0:
        generator = array([0, 1, 0])
    elif comma[2] == 0:
        generator = array([0, 0, 1])
    else:
        generator = None
        for i in range(-search_depth, search_depth+1):
            for j in range(-search_depth, search_depth+1):
                gen = array([0, i, j])
                generates_second = False
                generates_third = False
                for order in range(-search_depth, search_depth+1):
                    for octave in range(edo):
                        generated = order*gen + octave*period
                        while generated[2] < 0:
                            generated += comma*sign(comma[2])
                        while generated[2] > 0:
                            generated -= comma*sign(comma[2])
                        if generated[1] == 1 and generated[2] == 0:
                            generates_second = True

                        while generated[1] < 0:
                            generated += comma*sign(comma[1])
                        while generated[1] > 0:
                            generated -= comma*sign(comma[1])
                        if generated[2] == 1 and generated[1] == 0:
                            generates_third = True
                if generates_second and generates_third:
                    if generator is None or absolute(gen).sum() < absolute(generator).sum():
                        generator = gen
    if generator is None:
        return period, generator  # Partial failure
    if mapping is not None:
        while dot(generator, mapping) >= 0:
            generator[0] -= 1
        while dot(generator, mapping) <= 0:
            generator[0] += 1
        inverted = -generator  # pylint: disable=invalid-unary-operand-type
        while dot(inverted, mapping) >= 0:
            inverted[0] -= 1
        while dot(inverted, mapping) <= 0:
            inverted[0] += 1
        while dot(generator, mapping) >= dot(period, mapping):
            generator -= period
        while dot(inverted, mapping) >= dot(period, mapping):
            inverted -= period
        if dot(inverted, mapping) < dot(generator, mapping):
            generator = inverted
    return period, generator


def canonize(threes, fives, horogram="JI"):
    """
    Reduce a pitch class given in powers of three and five into a canonical form based on the temperament.
    """
    # pylint: disable=invalid-name
    if horogram == "father":
        return (threes - fives, 0)

    if horogram == "bug":
        m = fives - ((fives+1)//2)*2
        return (threes + 3*(fives - m)//2, m)

    if horogram == "dicot":
        permutation = [0, 4, 1, 5, 2, 6, 3]
        num = fives + 2*threes
        return ((num//len(permutation))*len(permutation) + permutation[num % len(permutation)], 0)

    if horogram == "meantone":
        return (threes + 4*fives, 0)

    if horogram == "augmented":
        return (threes, fives - ((fives+1)//3)*3)

    if horogram == "mavila":
        return (threes - 3*fives, 0)

    if horogram == "porcupine":
        m = fives - ((fives + 1)//3)*3
        return (threes + 5*(fives - m)//3, m)

    if horogram == "blackwood":
        threes = threes - ((threes + 1)//5)*5
        if threes == 3:
            return (threes + 4*fives + 4, -1)
        return (threes + 4*fives, 0)

    if horogram == "dimipent":
        f = (fives+2)//4
        return (threes + f*4, fives - f*4)

    if horogram == "srutal":
        if fives % 2:
            return (threes - 2*(fives-1), 1)
        return (threes - 2*fives, 0)

    if horogram == "magic":
        fifths_19edo = [0, 7, 14, 2, 9, 16, 4, 11, 18, 6, 13, 1, 8, 15, 3, 10, 17, 5, 12]
        index = fives + 5*threes
        edo19 = (threes*30 + fives*44) % 19
        meantone = (fifths_19edo[edo19] + 8) % 19 - 8
        arrows = index // 19
        return (meantone + arrows*4, -arrows)

    if horogram == "ripple":
        m = fives - ((fives+2)//5)*5
        return (threes + 8*(fives - m)//5, m)

    if horogram == "hanson":
        m = fives - ((fives+3)//6)*6
        return (threes + 5*(fives - m)//6, m)

    if horogram == "negripent":
        m = fives - ((fives+2)//4)*4
        return (threes - 3*(fives - m)//4, m)

    if horogram == "tetracot":
        m = fives - ((fives+2)//4)*4
        return (threes + 9*(fives - m)//4, m)

    if horogram == "superpyth":
        return (threes + 9*fives, 0)

    if horogram == "helmholtz":
        return (threes - 8*fives, 0)

    if horogram == "passion":
        m = fives - ((fives + 2)//5)*5
        return (threes - 4*(fives - m)//5, m)

    if horogram == "würschmidt":
        fifths_31edo = [0, 19, 7, 26, 14, 2, 21, 9, 28, 16, 4, 23, 11, 30, 18, 6, 25, 13, 1, 20, 8, 27, 15, 3, 22, 10, 29, 17, 5, 24, 12]
        index = fives + 8*threes
        edo31 = (threes*49 + fives*72) % 31
        meantone = (fifths_31edo[edo31] + 11) % 31 - 11
        arrows = index // 31
        return (meantone + arrows*4, -arrows)

    if horogram == "compton":
        arrows = -fives
        meantone = threes + 4*fives
        return (meantone - ((meantone + 3)//12)*12 + arrows*4, -arrows)

    if horogram == "quintriyo":
        f = (fives + 7)//15
        return (threes + f*15, fives - f*15)

    if horogram == "doublewide":
        m = fives - ((fives + 4)//8)*8
        return (threes + 3*(fives-m)//4, m)

    if horogram == "wronecki":
        m = fives - ((fives + 3)//6)*6
        return (threes + 2*(fives-m), m)

    return (threes, fives)
