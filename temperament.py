# coding: utf-8
"""
Tools for tempering out commas from musical tunings, particularly 5-limit just intonation.
"""
from collections import defaultdict
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from numpy import log, dot, array, cross, absolute, sign, prod, arange
from numpy.linalg import norm
from util import gcd

# Prime limit mappings
JI_5LIMIT = log(array([2, 3, 5]))
JI_7LIMIT = log(array([2, 3, 5, 7]))
JI_11LIMIT = log(array([2, 3, 5, 7, 11]))

# Subgroups
JI_3_7 = log(array([2, 3, 7]))
JI_ISLAND = log(array([2, 3, 13/5]))


# 5-limit
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
    "miracle": (-25, 7, 6),

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
    "miracle": "ampersand",
}


PERGEN_BY_HOROGRAM = {
    "father": ((1, 0, 0), (2, -1, 0)),
    "bug": ((1, 0, 0), (1, 1, -1)),
    "dicot": ((1, 0, 0), (-2, 0, 1)),
    "meantone": ((1, 0, 0), (2, -1, 0)),
    "augmented": ((-2, 0, 1), (4, -1, -1)),
    "mavila": ((1, 0, 0), (2, -1, 0)),
    "porcupine": ((1, 0, 0), (1, -2, 1)),
    "blackwood": ((-3, 2, 0), (12, -6, -1)),
    "dimipent": ((1, 1, -1), (-3, -1, 2)),
    "stural": ((-5, 2, 1), (4, -1, -1)),
    "magic": ((1, 0, 0), (-2, 0, 1)),
    "ripple": ((1, 0, 0), (0, 3, -2)),
    "hanson": ((1, 0, 0), (1, 1, -1)),
    "negripent": ((1, 0, 0), (4, -1, -1)),
    "tetracot": ((1, 0, 0), (1, -2, 1)),
    "superpyth": ((1, 0, 0), (2, -1, 0)),
    "helmholtz": ((1, 0, 0), (2, -1, 0)),
    "sensipent": ((1, 0, 0), (1, 4, -3)),
    "passion": ((1, 0, 0), (4, -1, -1)),
    "würschmidt": ((1, 0, 0), (-2, 0, 1)),
    "compton": ((8, -5, 0), (-61, 40, -1)),
    "amity": ((1, 0, 0), (-3, 5, -2)),
    "orson": ((1, 0, 0), (-6, 1, 2)),
    "vishnu": ((-11, -3, 7), (-3, -1, 2)),
    "luna": ((1, 0, 0), (18, -1, -7)),
    "shibboleth": ((1, 0, 0), (1, 1, -1)),
    "quinbigu": ((1, 0, 0), (1, 1, -1)),
    "quintriyo": ((3, 4, -4), (-16, -25, 24)),
    "doublewide": ((-4, -3, 4), (4, 2, -3)),
    "unicorn": ((1, 0, 0), (1, -5, 3)),
    "fifive": ((0, -7, 5), (0, 3, -2)),
    "nusecond": ((1, 0, 0), (-2, -6, 5)),
    "parakleismic": ((1, 0, 0), (1, 1, -1)),
    "valentine": ((1, 0, 0), (-3, -1, 2)),
    "sevond": ((1, -2, 1), (-5, 9, -4)),
    "bohpieric": ((1, 0, 0), (0, 3, -2)),
    "wronecki": ((1, -2, 1), (-4, 7, -3)),
    "miracle": ((1, 0, 0), (4, -1, -1)),
}


ISLAND_COMMA_BY_HOROGRAM = {
    "barbados": (2, -3, 2),
}


ISLAND_COMMA_NAME_BY_HOROGRAM = {
    "barbados": "parizeksma",
}


ISLAND_PERGEN_BY_HOROGRAM = {
    "barbados": ((1, 0, 0), (0, 1, -1)),
}

# 7-limit
COMMA_LIST_BY_HOROGRAM = {
    "srutal": ((11, -4, -2, 0), (-1, -7, 4, 1)),
    "miracle": ((-10, 1, 0, 3), (-5, 2, 2, -1)),
}

PERGEN_7LIMIT_BY_HOROGRAM = {
    "srutal": ((-5, 2, 1, 0), (4, -1, -1, 0)),
    "miracle": ((1, 0, 0, 0), (0, -1, -1, 0)),
}

# 2.3.7 subgroup
COMMA_3_7_BY_HOROGRAM = {
    "archy": (6, -2, -1),
    "slendric": (-10, 1, 3),
    "eric": (7, 8, -7),
    "ennealimmal": (-11, -9, 9),
    "buzzardismic": (16, -3, -4),
    "cloudy": (-14, 0, 5),
}


PERGEN_3_7_BY_HOROGRAM = {
    "archy": ((1, 0, 0), (2, -1, 0)),
    "slendric": ((1, 0, 0), (3, 0, -1)),
    "eric": ((1, 0, 0), (-1, -1, 1)),
    "ennealimmal": ((5, 4, -4), (-26, -19, 20)),
    "buzzardismic": ((1, 0, 0), (-4, 1, 1)),
    "cloudy": ((3, 0, -1), (-4, -1, 2)),
}


# 11-limit
COMMA_LIST_11LIMIT_BY_HOROGRAM = {
    # Minimax error less than 1 cent
    "slendric_unimarv": ((-7, -1, 1, 1, 1), (-10, 1, 0, 3, 0), (-5, 2, 2, -1, 0)),
    "keen_slendric": ((-7, -1, 1, 1, 1), (-10, 1, 0, 3, 0), (-12, 1, 3, 0, 1)),
    "slendric_marvel": ((-10, 1, 0, 3, 0), (-5, 2, 2, -1, 0), (-12, 1, 3, 0, 1)),
}

PERGEN_11LIMIT_BY_HOROGRAM = {
    "slendric_unimarv": ((1, 0, 0, 0, 0), (0, -1, -1, 0, 0)),
    "keen_slendric": ((1, 0, 0, 0, 0), (0, -1, -1, 0, 0)),
    "slendric_marvel": ((1, 0, 0, 0, 0), (0, -1, -1, 0, 0)),
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


def guess_pergen(comma_list, mapping, search_depth=10, generation_depth=None, tolerance=1e-6):
    if generation_depth is None:
        generation_depth = search_depth
    sub_edos = []
    for comma in comma_list:
        sub_edos.append(abs(reduce(gcd, comma[1:])))
    edo = prod(sub_edos) // reduce(gcd, sub_edos)

    comma_list = [array(comma) for comma in comma_list]

    search_space = arange(-search_depth, search_depth+1)

    period = None
    for candidate in product(search_space, repeat=len(mapping)):
        candidate = array(candidate)
        if abs(dot(candidate*edo, mapping) - mapping[0]) < tolerance:
            if period is None or abs(candidate).sum() < abs(period).sum():
                period = candidate

    modulus = mapping[0] / edo
    generator = None
    for candidate in product(search_space, repeat=len(mapping)):
        candidate = array(candidate)
        generates = array([False] * (len(mapping)-1))
        for multiplier in range(-generation_depth, generation_depth+1):  # pylint: disable=invalid-unary-operand-type
            for i, coord in enumerate(mapping[1:]):
                if abs(dot(candidate*multiplier, mapping)%modulus - coord%modulus) < tolerance:
                    generates[i] = True
        if generates.all() and (generator is None or abs(candidate).sum() < abs(generator).sum()):
            generator = candidate

    return period, generator


def canonize(threes, fives, horogram="JI"):
    """
    Reduce a pitch class given in powers of three and five into a canonical form that has the same frequency class based on the temperament.
    """
    # pylint: disable=invalid-name
    if horogram == "father":
        return (threes - fives, 0)

    if horogram == "bug":
        m = fives - ((fives+1)//2)*2
        return (threes + 3*(fives - m)//2, m)

    if horogram == "dicot":
        return (0, fives + 2*threes)

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
        return (threes - ((threes + 2)//5)*5, fives)

    if horogram == "dimipent":
        f = (fives+2)//4
        return (threes + f*4, fives - f*4)

    if horogram == "srutal":
        if fives % 2:
            return (threes - 2*(fives-1), 1)
        return (threes - 2*fives, 0)

    if horogram == "magic":
        return (0, fives + 5*threes)

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
        return (0, fives + 8*threes)

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

    if horogram == "miracle":
        m = fives - ((fives + 3)//6)*6
        return (threes - 7*(fives - m)//6, m)

    if horogram == "JI":
        return (threes, fives)

    raise ValueError("Unrecognized temperament")


def canonize2(twos, threes, fives, horogram="JI"):
    """
    Reduce a pitch given in powers of two, three and five into a canonical form that has the same frequency based on the temperament.
    """
    # pylint: disable=invalid-name
    if horogram == "meantone":
        return (twos - 4*fives, threes + 4*fives, 0)

    if horogram == "augmented":
        return (twos + ((fives+1)//3)*7, threes, fives - ((fives+1)//3)*3)

    if horogram == "porcupine":
        m = fives - ((fives + 1)//3)*3
        return (twos - (fives - m)//3, threes + 5*(fives - m)//3, m)

    if horogram == "JI":
        return (twos, threes, fives)

    raise ValueError("Unrecognized temperament")


def canonize_7limit(threes, fives, sevens, horogram="JI"):
    if horogram == "srutal":
        threes += 7*sevens
        fives -= 4*sevens
        if fives % 2:
            return (threes - 2*(fives-1), 1, 0)
        return (threes - 2*fives, 0, 0)

    if horogram == "JI":
        return (threes, fives, sevens)

    raise ValueError("Unrecognized temperament")


def canonize_3_7(threes, sevens, horogram="JI"):
    # pylint: disable=invalid-name
    if horogram == "archy":
        return (threes - 2*sevens, 0)

    if horogram == "slendric":
        return (0, sevens - 3*threes)

    if horogram == "eric":
        m = sevens - ((sevens + 3)//7)*7
        return (threes + 8*(sevens - m)//7, m)

    if horogram == "ennealimmal":
        index = sevens - threes
        ortho = threes + sevens
        index -= ((index + 4)//9)*9
        return (ortho - index, index + ortho)

    if horogram == "buzzardismic":
        m = sevens - ((sevens + 2)//4)*4
        return (threes - 3*(sevens - m)//4, m)

    if horogram == "cloudy":
        return (threes, sevens - ((sevens+2)//5)*5)

    if horogram == "JI":
        return (threes, sevens)

    raise ValueError("Unrecognized temperament")


def canonize2_3_7(twos, threes, sevens, horogram="JI"):
    # pylint: disable=invalid-name
    if horogram == "slendric":
        return (twos + 10*threes, 0, sevens - 3*threes)

    if horogram == "JI":
        return (twos, threes, sevens)

    raise ValueError("Unrecognized temperament")


def canonize_11limit(threes, fives, sevens, elevens, horogram="JI"):
    if horogram == "slendric_unimarv":
        sevens -= elevens
        fives += 2*sevens - elevens
        threes += 2*sevens + elevens
        m = fives - ((fives + 3)//6)*6
        return (threes - 7*(fives - m)//6, m, 0, 0)
    if horogram == "JI":
        return (threes, fives, sevens, elevens)

    raise ValueError("Unrecognized temperament")


def mod_comma(pitch, comma):
    """
    Calculate pitch modulo comma

    Result not canonized, but unique
    """
    pitch = array(pitch)
    comma = array(comma)

    if comma[-1] == 0:
        if comma[-2] == 0:
            raise NotImplementedError("Generic reduction not implemented")
        if comma[-2] < 0:
            comma = -comma
        while pitch[-2] > 0:
            pitch -= comma
        while pitch[-2] < 0:
            pitch += comma
    else:
        if comma[-1] < 0:
            comma = -comma

        while pitch[-1] > 0:
            pitch -= comma
        while pitch[-1] < 0:
            pitch += comma

    return pitch


# TODO: def comma_equals(pitch_a, pitch_b, comma_list, persistence=10):


def find_subset_commas(max_complexity, factors, threshold=Fraction(10, 9)):
    """
    Find intervals smaller than a given threshold between factors less complex than the given limit
    """
    factors = [Fraction(f) for f in factors]
    result = []
    def search(num_remaining, exponents):
        if num_remaining:
            for exponent in range(-max_complexity, max_complexity+1):
                search(num_remaining - 1, exponents + [exponent])
        else:
            if reduce(gcd, exponents) not in (-1, 1):
                return
            comma = Fraction(1)
            for factor, exponent in zip(factors, exponents):
                comma *= factor**exponent
            if 1 < comma < threshold:
                result.append((comma, array(exponents)))
    search(len(factors), [])
    return result


def find_subset_commas_manhattan(max_complexity, factors, threshold=Fraction(10, 9), period=2):
    period = Fraction(2)
    factors = [Fraction(f) for f in factors]
    result = []
    search_space = arange(-max_complexity, max_complexity+1)
    def search(num_remaining, exponents):
        if absolute(exponents).sum() > max_complexity:
            return
        if num_remaining:
            for exponent in search_space:
                search(num_remaining - 1, exponents + [exponent])
        else:
            if reduce(gcd, exponents) not in (-1, 1):
                return
            comma = Fraction(1)
            for factor, exponent in zip(factors, exponents):
                comma *= factor**exponent
            num_periods = 0
            while comma >= 1:
                comma /= period
                num_periods -= 1
            while comma < 1:
                comma *= period
                num_periods += 1
            if comma < threshold:
                result.append((comma, array([num_periods] + exponents)))
    search(len(factors), [])
    return result


def tabulate_meets(commas):
    """
    Tabulate rank 1 meets between commas
    """
    meets_by_edo = defaultdict(list)
    for i, comma_a in enumerate(commas):
        if len(comma_a) != 3:
            raise NotImplementedError("Only rank 3 to rank 1 reduction supported")
        for comma_b in commas[i+1:]:
            mapping = cross(comma_a, comma_b)
            if mapping[0] < 0:
                mapping = -mapping
            mapping //= reduce(gcd, mapping)
            meets_by_edo[mapping[0]].append((mapping, comma_a, comma_b))
    return meets_by_edo
