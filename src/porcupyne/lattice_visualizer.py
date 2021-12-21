# pylint: disable=invalid-name, missing-function-docstring
from numpy import logical_and, logical_or, logical_xor, sqrt, maximum, floor
from .note import notate
from .graphics import number_symbol, note_symbol, screen_coords


SQ3 = sqrt(3)


def hexagon(x, y):
    return logical_and(abs(y) < 1, abs(abs(x)*SQ3 + abs(y)) < 2)


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
            if letter.isdigit():
                result = logical_xor(result, number_symbol(6*(x - fives - 0.1), 6*(y - threes), letter, line_thickness, centered=True))
            else:
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
        elif len(comma_list) == 2:
            for k in range(-comma_range, comma_range):
                for l in range(-comma_range, comma_range):
                    for note in notes:
                        highlights += hex_highlight(
                            x, y,
                            note.pitch[i] + k*comma_list[0][i] + l*comma_list[1][i],
                            note.pitch[j] + k*comma_list[0][j] + l*comma_list[1][j]
                        )
        else:
            raise NotImplementedError("TODO")
        highlightss.append((time, highlights))

    return grid, highlightss


def animate_notes(x, y, delta_t, decay, notes, indices=(1, 2), tolerance=1e-6, highlighter=hex_highlight):
    decay = decay**delta_t
    i, j = indices
    highlights = 0.0*x
    t = 0.0
    notes = list(sorted(notes, key=lambda n: n.time))
    while True:
        while notes and notes[0].time <= t + tolerance:
            note = notes.pop(0)
            highlights += highlighter(x, y, note.pitch[i], note.pitch[j])
        highlights = highlights * decay
        yield highlights
        t += delta_t
