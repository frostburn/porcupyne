# pylint: disable=invalid-name, missing-function-docstring
from numpy import logical_and, logical_or, logical_xor, sqrt, stack, clip, maximum, sign, floor, linspace, meshgrid, minimum, copysign
from numpy.random import random
from .note import notate


def make_picture_frame(rgb, dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return frame


SQ3 = sqrt(3)


def hexagon(x, y):
    return logical_and(abs(y) < 1, abs(abs(x)*SQ3 + abs(y)) < 2)


def digit_minus(x, y, thickness=0.1):
    return logical_and(abs(y) < thickness, abs(x) < 0.25 + thickness)


def digit_dot(x, y, thickness=0.1):
    r = sqrt(x*x + (y+1-thickness)**2)
    return r < 2*thickness


def digit_0(x, y, thickness=0.1):
    r = sqrt(2.2*x*x + y*y)
    return abs(r - 1) < thickness


def digit_1(x, y, thickness=0.1):
    return logical_and(
        logical_and(x < thickness, abs(y) < 1 + thickness),
        logical_or(
            -x < thickness,
            logical_and(y-x < 1 + 2*thickness, y > 1-thickness)
        )
    )


def _digit_2(x, y, thickness):
    r = sqrt(x*x + y*y)
    return logical_or(
        logical_and(maximum(x+y, x + 2*y) > 0, abs(r - 1) < thickness),
        logical_and(
            logical_and(abs(x) < 1 + thickness, y > -2.5-thickness),
            logical_or(
                y < -2.5 + thickness,
                logical_and(x+y <= 0, abs(x-y-sqrt(2)) < sqrt(2)*thickness)
            )
        )
    )


def digit_2(x, y, thickness=0.1):
    return _digit_2(x*1.75, (y-0.425)*1.75, thickness*1.75)


def _digit_3(x, y, thickness):
    r = sqrt(x*x + (abs(y)-1)**2)
    return logical_and(
        logical_or(x + abs(y) > 0.5, x > -0.15),
        abs(r - 1) < thickness,
    )


def digit_3(x, y, thickness=0.1):
    return _digit_3(x*2, y*2, thickness*2)


def digit_4(x, y, thickness=0.1):
    return logical_and(
        logical_and(abs(y) < 1 + thickness, abs(x+0.19+thickness) < 0.6+thickness),
        logical_or(
            minimum(abs(x), abs(y+thickness)) < thickness,
            logical_and(abs(1.25*x-y+1+thickness) < 1.25*thickness, y > -thickness)
        )
    )


def _digit_5(x, y, thickness):
    r = sqrt(x*x + y*y)
    result = logical_or(
        logical_and(abs(r - 1) < thickness, logical_or(x > 0, 3*x - 2*y > 0)),
        logical_and(
            abs(maximum(0.5+thickness-x, y-1)-1) < thickness,
            maximum(x-1-thickness, 1-thickness-y) < 0
        )
    )
    return logical_or(
        result,
        logical_and(
            logical_and(x < 0, x > -0.5), abs(y-1) < thickness
        )
    )


def digit_5(x, y, thickness=0.1):
    return _digit_5(1.5*x, 1.5*(y+0.333333), 1.5*thickness)


def _digit_6(x, y, thickness):
    r = sqrt(x*x + y*y)
    return logical_or(
        logical_and(abs(2*x - y + sqrt(5)) < sqrt(5)*thickness, abs(2*y + x - 1.75*sqrt(5)) < 3.5),
        abs(r-1) < thickness
    )


def digit_6(x, y, thickness=0.1):
    return _digit_6(2*x, 2*(y+0.5), 2*thickness)


def digit_7(x, y, thickness=0.1):
    result = logical_and(
        abs(x-0.15) < 0.57 + thickness,
        logical_or(y > 1 - thickness, abs(3*x - y - 1.2) < sqrt(10)*thickness)
    )
    return logical_and(result, abs(y) < 1 + thickness)


def _digit_8(x, y, thickness):
    r = sqrt(x*x + (abs(y)-1)**2)
    return abs(r - 1) < thickness


def digit_8(x, y, thickness=0.1):
    return _digit_8(x*2, y*2, thickness*2)


def digit_9(x, y, thickness=0.1):
    return digit_6(-x, -y, thickness)


def letter_C(x, y, thickness=0.1):
    r = sqrt(x*x + y*y)
    return logical_and(
        abs(r - 1) < thickness,
        x - abs(y) < 0,
    )


def letter_D(x, y, thickness=0.1):
    r = sqrt(x*x + y*y)
    return logical_or(
        logical_and(abs(r - 1) < thickness, x > 0),
        logical_and(abs(y) < 1+thickness, abs(x + thickness) < thickness)
    )


def letter_E(x, y, thickness=0.1):
    result = logical_and(abs(y) < 1+thickness, abs(x) < thickness)
    for offset in range(-1, 2):
        result = logical_or(
            result,
            logical_and(abs(2*x - 1) < 1, abs(y + offset) < thickness)
        )
    return result


def letter_F(x, y, thickness=0.1):
    result = logical_and(abs(y) < 1+thickness, abs(x) < thickness)
    result = logical_or(result, logical_and(abs(2*x-1) < 1, abs(y-1) < thickness))
    result = logical_or(result, logical_and(abs(2.2*x-1) < 1, abs(y) < thickness))
    return result


def letter_G(x, y, thickness=0.1):
    r = sqrt(x*x + y*y)
    result = logical_and(abs(r - 1) < thickness, 2*x - abs(y) < 0)
    result = logical_or(result, logical_and(r < 1 + thickness, logical_and(abs(x-0.5) < thickness, y < 0)))
    result = logical_or(result, logical_and(abs(x-0.25) < 0.25+thickness, abs(y) < thickness))
    return result


def letter_A(x, y, thickness=0.1):
    z = maximum(2.5*x+y-1, y-1-2.5*x)
    result = logical_and(abs(y) < 1+thickness, abs(z) < 2.5*thickness)
    result = logical_or(result, logical_and(abs(y) < thickness, z < 2.5*thickness))
    return result


def letter_B(x, y, thickness=0.1):
    result = logical_and(abs(y) < 1 + thickness, abs(x) < thickness)
    r = sqrt((x-0.25)**2 + (abs(y)-0.5)**2)
    result = logical_or(result, logical_and(x > 0, abs(r-0.5) < thickness))
    result = logical_or(result, logical_and(abs(abs(y)-1) < thickness, abs(x-0.125) < 0.125-thickness))
    return result


def letter_M(x, y, thickness=0.1):
    result = logical_or(abs(abs(x)-1) < thickness, abs(y-abs(x)*(1+2*thickness)) < sqrt(2)*thickness)
    result = logical_and(result, abs(y) < 1+thickness)
    return result


def arrow(x, y):
    return logical_and(y < 0, maximum(2*x-y, -2*x-y) < 1)


def natural(x, y, arrows=0, thickness=0.1):
    result = logical_and(abs(x+0.4) < 0.5*thickness, abs(y-0.2) < 0.8)
    result = logical_or(result, logical_and(abs(x-0.4) < 0.5*thickness, abs(y+0.2) < 0.8))
    result = logical_or(result, logical_and(abs(-0.35+abs(y-0.5*x)) < thickness, abs(x) < 0.4+thickness*0.5))
    if arrows > 0:
        for i in range(arrows):
            result = logical_or(result, arrow(2*(x+0.4), -2*(y-1+0.3*i)))
    elif arrows < 0:
        for i in range(-arrows):
            result = logical_or(result, arrow(2*(x-0.4), 2*(y+1-0.3*i)))
    return result


def dark_natural(x, y, arrows=0, thickness=0.1):
    result = logical_and(abs(x+0.4) < 0.5*thickness, abs(y-0.2) < 0.8)
    result = logical_or(result, logical_and(abs(x-0.4) < 0.5*thickness, abs(y+0.2) < 0.8))
    result = logical_or(result, logical_and(abs(y-0.5*x) < 0.4+thickness, abs(x) < 0.4+thickness*0.5))
    if arrows > 0:
        for i in range(arrows):
            result = logical_or(result, arrow(2*(x+0.4), -2*(y-1+0.3*i)))
    elif arrows < 0:
        for i in range(-arrows):
            result = logical_or(result, arrow(2*(x-0.4), 2*(y+1-0.3*i)))
    return result


def sharp(x, y, arrows=0, thickness=0.1):
    result = logical_and(abs(abs(x)-0.4) < 0.5*thickness, abs(y) < 1)
    result = logical_or(result, logical_and(abs(-0.35+abs(y-0.5*x)) < thickness, abs(x) < 0.6+thickness*0.5))
    if arrows > 0:
        for i in range(arrows):
            result = logical_or(result, arrow(2*(x+0.4), -2*(y-1+0.3*i)))
    elif arrows < 0:
        for i in range(-arrows):
            result = logical_or(result, arrow(2*(x-0.4), 2*(y+1-0.3*i)))
    return result


def flat(x, y, arrows=0, thickness=0.1):
    result = logical_and(abs(x) < 0.5*thickness, abs(y) < 1 + thickness)
    if arrows > 0:
        for i in range(arrows):
            result = logical_or(result, arrow(2*x, -2*(y-1-thickness+0.3*i)))
    elif arrows < 0:
        result = logical_or(result, logical_and(abs(x) < 0.5*thickness, abs(y+1) < 0.5))
        for i in range(-arrows):
            result = logical_or(result, arrow(2*x, 2*(y+1.25+thickness+0.3*i)))
    y = y - 0.3*x
    r = sqrt((x-0.0)**2 + (y+0.5)**2)
    result = logical_or(result, logical_and(x > 0, abs(r-0.5) < thickness))
    return result


def double_sharp_(x, y, thickness):
    result = abs((1+thickness)*abs(x)-abs(y)) < thickness
    result = logical_or(result, abs(-abs(x)+(1+thickness)*abs(y)) < thickness)
    result = logical_and(result, maximum(abs(x), abs(y)) < 1)
    return result


def double_sharp(x, y, arrows=0, thickness=0.1):
    result = double_sharp_(1.5*x, 1.5*y, thickness*2)
    if abs(arrows) > 0:
        y = -sign(arrows)*y
        result = logical_or(result, logical_and(abs(x) < 0.5*thickness, abs(y+0.4) < 0.4))
        for i in range(abs(arrows)):
            result = logical_or(result, arrow(2*x, 2*(y+0.7+0.3*i)))
    return result


def one_and_a_half_sharp(x, y, arrows=0, thickness=0.1):
    result = logical_and(
        logical_or(abs(x) < 0.5*thickness, abs(abs(x)-0.4) < 0.5*thickness),
        abs(y) < 1
    )
    result = logical_or(result, logical_and(abs(-0.35+abs(y-0.5*x)) < thickness, abs(x) < 0.6+thickness*0.5))
    if arrows > 0:
        for i in range(arrows):
            result = logical_or(result, arrow(2*(x+0.4), -2*(y-1+0.3*i)))
    elif arrows < 0:
        for i in range(-arrows):
            result = logical_or(result, arrow(2*(x-0.4), 2*(y+1-0.3*i)))
    return result


def half_sharp(x, y, arrows=0, thickness=0.1):
    result = logical_and(
        abs(x) < 0.5*thickness,
        abs(y) < 1
    )
    result = logical_or(result, logical_and(abs(-0.35+abs(y-0.5*x)) < thickness, abs(x) < 0.4+thickness*0.5))
    if arrows > 0:
        for i in range(arrows):
            result = logical_or(result, arrow(2*x, -2*(y-1+0.3*i)))
    elif arrows < 0:
        for i in range(-arrows):
            result = logical_or(result, arrow(2*x, 2*(y+1-0.3*i)))
    return result


# TODO: Full sagittal notation
def sagittal7(x, y, thickness=0.1):
    return logical_or(
        logical_and(abs(x) < 0.5*thickness, abs(y) < 1 + thickness),
        logical_and(abs(x-0.5) < 0.5, abs(1.25*x**6+y-1) < thickness)
    )


def double_sagittal7(x, y, thickness=0.1):
    arc = 1.25*x**6 + y - 1
    return logical_or(
        logical_and(
            abs(abs(x-0.3)-0.3) < 0.5*thickness,
            logical_and(y > -1 - thickness, arc < thickness)
        ),
        logical_and(abs(x-0.5) < 0.5, abs(arc) < thickness)
    )


def triple_sagittal7(x, y, thickness=0.1):
    arc = 1.25*x**6 + y - 1
    return logical_or(
        logical_and(
            logical_or(abs(abs(x-0.3)-0.3) < 0.5*thickness, abs(x-0.3) < 0.5*thickness),
            logical_and(y > -1 - thickness, arc < thickness)
        ),
        logical_and(abs(x-0.5) < 0.5, abs(arc) < thickness)
    )


def quadruple_sagittal7(x, y, thickness=0.1):
    arc = 1.25*x**6 + y - 1
    return logical_or(
        logical_and(
            abs(abs(abs(x-0.33)-0.22)-0.11) < 0.5*thickness,
            logical_and(y > -1 - thickness, arc < thickness)
        ),
        logical_and(abs(x-0.5) < 0.5, abs(arc) < thickness)
    )


LETTERS = {
    "F": letter_F,
    "C": letter_C,
    "G": letter_G,
    "D": letter_D,
    "A": letter_A,
    "E": letter_E,
    "B": letter_B,

    "M": letter_M,
}


LETTER_OFFSETS = {
    "D": -0.25,
    "E": -0.15,
    "F": -0.1,
    "G": 0.1,
    "A": -0.1,
}


DIGITS = {
    "-": digit_minus,
    ".": digit_dot,
    "0": digit_0,
    "1": digit_1,
    "2": digit_2,
    "3": digit_3,
    "4": digit_4,
    "5": digit_5,
    "6": digit_6,
    "7": digit_7,
    "8": digit_8,
    "9": digit_9,
}

DIGIT_OFFSETS = {
    ".": 0.2,
    "4": 0.3,
    "5": -0.1,
}


def number_symbol(x, y, number, thickness, centered=False):
    digits = str(number)
    offset = 0
    if centered:
        offset -= 0.75*len(digits)
    result = DIGITS[digits[0]](x - DIGIT_OFFSETS.get(digits[0], 0) - offset, y, thickness)
    offset += 1.5
    for digit in digits[1:]:
        result = logical_or(result, DIGITS[digit](x - DIGIT_OFFSETS.get(digit, 0) - offset, y, thickness))
        offset += 1.5
    return result


def accidental_symbol(x, y, sharps, arrows, thickness):
    bg = 0*x

    has_dark_natural = False
    if copysign(1, sharps) < 0 and sharps == 0.0:
        has_dark_natural = True

    has_half_sharp = False
    has_one_and_a_half_sharp = False
    has_half_flat = False
    # Note: Floating point numbers are exact for multiples of 0.5 so this shouldn't cause issues.
    if sharps > 0 and sharps == int(sharps) + 0.5:
        if int(sharps) % 2:
            has_one_and_a_half_sharp = True
        else:
            has_half_sharp = True
    if sharps < 0 and sharps == int(sharps) - 0.5:
        has_half_flat = True

    sharps = int(sharps)

    if sharps > 0:
        accidental_space = 0.75 + 1.5 * ((sharps+1)//2 - 1)
        if has_half_sharp:
            accidental_space += 1.3
    elif sharps < 0:
        accidental_space = 0.25 + 0.75 * (-1-sharps)
        if has_half_flat:
            accidental_space += 0.75
    else:
        accidental_space = 0.4

    x_min = -0.1 - thickness
    x_max = 0.75 + thickness + accidental_space
    if sharps < 0 and arrows < 0:
        y_min = -1.5 - thickness - max(0, -0.3*arrows)
    else:
        y_min = -1.3 - thickness - max(0, -0.3*arrows)
    y_max = 1.3 + thickness + max(0, 0.3*arrows)

    # TODO: Use index slices when the coordinates are orthogonal
    bbox = logical_and(
        logical_and(
            x > x_min,
            x < x_max
        ), logical_and(
            y > y_min,
            y < y_max
        )
    )
    x = x[bbox]
    y = y[bbox]

    if sharps == 0 and not (has_half_flat or has_half_sharp):
        if has_dark_natural:
            result = dark_natural(x-0.5, y, arrows, thickness)
        else:
            result = natural(x-0.5, y, arrows, thickness)
        arrows = 0

    elif sharps > 0 or has_half_sharp:
        arrows_per_sign, extra_arrows = divmod(abs(arrows), (sharps+1)//2 + has_half_sharp)
        offset = 0.75
        if has_half_sharp:
            result = half_sharp(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness)
            extra_arrows -= 1
            offset += 1.3
        else:
            result = 0*x
        if sharps % 2:
            if has_one_and_a_half_sharp:
                result = logical_or(result, one_and_a_half_sharp(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
                has_one_and_a_half_sharp = False
            else:
                result = logical_or(result, sharp(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
            extra_arrows -= 1
            offset += 1.5
            sharps -= 1
        while sharps > 0:
            result = logical_or(result, double_sharp(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
            extra_arrows -= 1
            offset += 1.5
            sharps -= 2

    elif sharps < 0 or has_half_flat:
        arrows_per_sign, extra_arrows = divmod(abs(arrows), -sharps + has_half_flat)
        offset = 0.25
        if has_half_flat:
            result = flat(offset-x+0.3, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness)
            extra_arrows -= 1
            offset += 0.55
        else:
            result = 0*x
        while sharps < 0:
            result = logical_or(result, flat(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
            extra_arrows -= 1
            offset += 0.75
            sharps += 1

    bg[bbox] = result
    return bg


def note_symbol(x, y, letter, sharps=0, arrows=0, octaves=None, thickness=0.1):
    if sharps > 2:
        x_offset = 0.4*((sharps+1)//2)
    elif sharps < 0:
        x_offset = 0.2*(-sharps-1)
    else:
        x_offset = 0

    x = x + x_offset

    letter_offset = LETTER_OFFSETS.get(letter, 0.0)
    result = LETTERS[letter](x-letter_offset, y, thickness)

    if octaves is None:
        return logical_or(result, accidental_symbol(x-1, y, sharps, arrows, thickness))

    result = logical_or(result, accidental_symbol((x-1)*1.75, (y-0.95)*1.75, sharps, arrows, thickness))
    result = logical_or(result, number_symbol((x-1.3)*2, (y+0.75)*2, octaves, thickness))
    return result


def _square_grid(x, y, padding):
    gx = x - floor(x + 0.5)
    gy = y - floor(y + 0.5)

    return maximum(abs(gx), abs(gy)) < 0.5 - padding


def square_grid(x, y, padding=0.05, line_thickness=0.1, notation=None):
    grid = _square_grid(x, y, padding)

    min_x = x.min()
    max_x = x.max()

    min_y = y.min()
    max_y = y.max()

    result = grid
    for threes in range(int(min_y) - 1, int(max_y) + 2):
        for fives in range(int(min_x) - 1, int(max_x) + 2):
            if notation is None:
                letter, sharps, arrows = notate(threes, fives, horogram="JI")
            else:
                letter, sharps, arrows = notation(threes, fives)
            result = logical_xor(
                result,
                note_symbol(6*(x - fives + 0.1), 6*(y - threes), letter, sharps, arrows, None, line_thickness)
            )

    return result


def square_highlight(x, y, threes, fives, padding=0.05, border=0.02):
    return maximum(abs(x - fives), abs(y - threes)) < 0.5 - padding + border


def square_pergen_grid(x, y, period, generator, padding=0.05, line_thickness=0.1, notation=None):
    grid = _square_grid(x, y, padding)

    min_x = x.min()
    max_x = x.max()

    min_y = y.min()
    max_y = y.max()

    result = grid
    for m in range(int(min_y) - 1, int(max_y) + 2):
        for n in range(int(min_x) - 1, int(max_x) + 2):
            pitch = period*n + generator*m
            if notation is None:
                letter, sharps, arrows, octaves = notate(pitch[1], pitch[2], twos=pitch[0], horogram="JI")
            else:
                letter, sharps, arrows, octaves = notation(pitch)
            result = logical_xor(
                result,
                note_symbol(6*(x - n + 0.1), 6*(y - m), letter, sharps, arrows, octaves, line_thickness)
            )

    return result


def hex_grid(x, y, spacing=0.2, line_thickness=0.1, notation=None):
    def grid_coords(x, y, spacing=0.2):
        gx = x - floor((x + SQ3 + 0.5*spacing)/(2*SQ3 + spacing))*(2*SQ3 + spacing)
        spacing *= 0.5*SQ3
        gy = y - floor((y + 1 + 0.5*spacing)/(2 + spacing))*(2 + spacing)
        return gx, gy

    gx, gy = grid_coords(x, y, spacing)
    sgx, sgy = grid_coords(x + SQ3 + 0.5*spacing, y + 1 + 0.5*spacing, spacing)

    grid = logical_or(hexagon(gx, gy), hexagon(sgx, sgy))

    min_x = x.min()
    max_x = x.max()

    min_y = y.min()
    max_y = y.max()

    result = grid
    # TODO: Calculate the limits correctly
    for threes in range(int(min_y) - 2, int(max_y) + 2):
        for fives in range(int(min_x) - 2, int(max_x) + 2):
            loc_x = 0.5*(2*SQ3 + spacing)*fives
            loc_y = (2 + 0.5*spacing*SQ3)*threes + (1 + spacing*0.25*SQ3)*fives
            if min_x - 1 < loc_x < max_x + 1 and min_y - 1 < loc_y < max_y + 1:
                if notation is None:
                    letter, sharps, arrows = notate(threes, fives, horogram="JI")
                else:
                    letter, sharps, arrows = notation(threes, fives)
                if letter.isdigit():
                    result = logical_xor(result, number_symbol(2.75*(x - loc_x - 0.25), 2.75*(y - loc_y), letter, line_thickness, centered=True))
                else:
                    result = logical_xor(result, note_symbol(2.75*(x - loc_x + 0.25), 2.75*(y - loc_y), letter, sharps, arrows, None, line_thickness))

    return result


def hex_highlight(x, y, threes, fives, spacing=0.2, padding=0.5):
    loc_x = 0.5*(2*SQ3 + spacing)*fives
    loc_y = (2 + 0.5*spacing*SQ3)*threes + (1 + spacing*0.25*SQ3)*fives

    return hexagon((x - loc_x)*(1-padding*spacing), (y - loc_y)*(1-padding*spacing))


RESOLUTIONS = {
    "2160p": (3840, 2160),
    "1440p": (2560, 1440),
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "480p": (854, 480),
    "360p": (640, 360),
    "240p": (426, 240),
    "160p": (284, 160),
    "80p": (142, 80),
    "40p": (71, 40),
}


def screen_coords(resolution, x0, y0, scale):
    width, height = RESOLUTIONS[resolution]
    aspect = width / height
    x = linspace(-scale*aspect, scale*aspect, width) + x0
    y = linspace(scale, -scale, height) + y0

    return meshgrid(x, y)


def visualize_sonorities(resolution, x0, y0, scale, sonorities, notation=None, comma_list=None, indices=(1, 2), comma_range=7):
    x, y = screen_coords(resolution, x0, y0, scale)

    grid = hex_grid(x, y, notation=notation)*1.0
    i, j = indices
    highlightss = []
    for time, notes in sonorities:
        highlights = 0.0*x
        if not comma_list:
            for note in notes:
                highlights += hex_highlight(x, y, note.pitch[i], note.pitch[j])
        elif len(comma_list) == 1:
            comma = comma_list[0]
            for k in range(-comma_range, comma_range):
                for note in notes:
                    highlights += hex_highlight(x, y, note.pitch[i] + k*comma[i], note.pitch[j] + k*comma[j])
        else:
            raise NotImplementedError("TODO")
        highlightss.append((time, highlights))

    return grid, highlightss


def animate_notes(x, y, delta_t, decay, notes, indices=(1, 2), tolerance=1e-6):
    decay = decay**delta_t
    i, j = indices
    highlights = 0.0*x
    t = 0.0
    notes = list(sorted(notes, key=lambda n: n.time))
    while True:
        while notes and notes[0].time <= t + tolerance:
            note = notes.pop(0)
            highlights += hex_highlight(x, y, note.pitch[i], note.pitch[j])
        highlights = highlights * decay
        yield highlights
        t += delta_t
