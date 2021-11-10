# pylint: disable=invalid-name, missing-function-docstring
from numpy import logical_and, logical_or, logical_xor, sqrt, stack, clip, maximum, sign, floor, linspace, meshgrid
from numpy.random import random


def make_picture_frame(rgb, dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return frame


SQ3 = sqrt(3)


def hexagon(x, y):
    return logical_and(abs(y) < 1, abs(abs(x)*SQ3 + abs(y)) < 2)


def letter_C(x, y, thickness=0.1):
    r = sqrt(x*x + y*y)
    return logical_and(
        abs(r - 1) < thickness,
        logical_or(x+y < 0, x-y < 0)
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
    result = logical_and(abs(r - 1) < thickness, logical_or(2*x+y < 0, 2*x-y < 0))
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
    "E": -0.1,
    "F": -0.1,
    "G": 0.1,
    "A": -0.1,
}


def note_symbol(x, y, letter, sharps=0, arrows=0, thickness=0.1):
    bg = 0*x

    # TODO: Further improve the bounds a little bit
    if sharps > 2:
        x_offset = 0.4*((sharps+1)//2)
    elif sharps < 0:
        x_offset = 0.2*(-sharps-1)
    else:
        x_offset = 0

    if sharps > 0:
        accidental_space = 1.75 + 1.5 * ((sharps+1)//2 - 1)
    elif sharps < 0:
        accidental_space = 1.25 + 0.75 * (-1-sharps)
    else:
        accidental_space = 1.25

    x_min = -1 - x_offset - thickness
    x_max = 1 - x_offset + thickness + accidental_space
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

    x = x + x_offset

    letter_offset = LETTER_OFFSETS.get(letter, 0.0)
    result = LETTERS[letter](x-letter_offset, y, thickness)

    if sharps == 0:
        result = logical_or(result, natural(x-1.5, y, arrows, thickness))
        arrows = 0

    elif sharps > 0:
        arrows_per_sign, extra_arrows = divmod(abs(arrows), (sharps+1)//2)
        offset = 1.75
        if sharps % 2:
            result = logical_or(result, sharp(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
            extra_arrows -= 1
            offset += 1.5
            sharps -= 1
        while sharps > 0:
            result = logical_or(result, double_sharp(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
            extra_arrows -= 1
            offset += 1.5
            sharps -= 2

    elif sharps < 0:
        arrows_per_sign, extra_arrows = divmod(abs(arrows), -sharps)
        offset = 1.25
        while sharps < 0:
            result = logical_or(result, flat(x-offset, y, (arrows_per_sign + (extra_arrows > 0))*sign(arrows), thickness))
            extra_arrows -= 1
            offset += 0.75
            sharps += 1

    bg[bbox] = result
    return bg


def note_symbol_5limit(x, y, threes, fives, thickness=0.1):
    lydian = ["F", "C", "G", "D", "A", "E", "B"]
    index = 1 + threes + fives*4
    sharps = index // len(lydian)
    letter = lydian[index % len(lydian)]
    return note_symbol(x, y, letter, sharps, -fives, thickness)


def square_grid(x, y, spacing=0.2, line_thickness=0.1, temperament=None):
    gx = x - floor((x + 1)/(2 + spacing))*(2 + spacing)
    gy = y - floor((y + 1)/(2 + spacing))*(2 + spacing)

    grid = maximum(abs(gx), abs(gy)) < 1

    min_x = x.min()
    max_x = x.max()

    min_y = y.min()
    max_y = y.max()

    result = grid
    for threes in range(int(min_y) - 1, int(max_y) + 1):
        for fives in range(int(min_x) - 1, int(max_x) + 1):
            loc_x = fives * (2 + spacing)
            loc_y = threes * (2 + spacing)
            if min_x - 1 < loc_x < max_x + 1 and min_y - 1 < loc_y < max_y + 1:
                if temperament is not None:
                    t, f = temperament(threes, fives)
                else:
                    t, f = (threes, fives)
                result = logical_xor(result, note_symbol_5limit(2.6*(x - loc_x + 0.28), 2.6*(y - loc_y), t, f, line_thickness))

    return result


def square_highlight(x, y, threes, fives, spacing=0.2):
    loc_x = fives * (2 + spacing)
    loc_y = threes * (2 + spacing)
    return maximum(abs(x - loc_x), abs(y - loc_y)) < 1


def hex_grid(x, y, spacing=0.2, line_thickness=0.1, temperament=None):
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
                if temperament is not None:
                    t, f = temperament(threes, fives)
                else:
                    t, f = (threes, fives)
                result = logical_xor(result, note_symbol_5limit(2.75*(x - loc_x + 0.25), 2.75*(y - loc_y), t, f, line_thickness))

    return result


def hex_highlight(x, y, threes, fives, spacing=0.2):
    loc_x = 0.5*(2*SQ3 + spacing)*fives
    loc_y = (2 + 0.5*spacing*SQ3)*threes + (1 + spacing*0.25*SQ3)*fives

    return hexagon((x - loc_x)*(1-0.2*spacing), (y - loc_y)*(1-0.2*spacing))


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


# TODO: Anti-aliasing
def visualize_progression(resolution, x0, y0, scale, notess, temperament=None, comma=None):
    width, height = RESOLUTIONS[resolution]
    aspect = width / height
    x = linspace(-scale*aspect, scale*aspect, width) + x0
    y = linspace(scale, -scale, height) + y0

    x, y = meshgrid(x, y)

    grid = hex_grid(x, y, temperament=temperament)*1.0
    for notes in notess:
        highlights = 0*x
        root_highlights = 0*x
        if comma is None:
            for note in notes:
                highlights += hex_highlight(x, y, note.pitch[1], note.pitch[2])
            root_highlights = hex_highlight(x, y, notes[0].pitch[1], notes[0].pitch[2])
        else:
            for k in range(-6, 7):
                for note in notes:
                    highlights += hex_highlight(x, y, note.pitch[1] + k*comma[1], note.pitch[2] + k*comma[2])
                root_highlights += hex_highlight(x, y, notes[0].pitch[1] + k*comma[1], notes[0].pitch[2] + k*comma[2])

        image = [grid - highlights, grid - highlights*0.1, grid - root_highlights]
        yield image
