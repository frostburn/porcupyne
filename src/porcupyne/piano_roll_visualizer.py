from numpy import linspace, meshgrid, logical_and, logical_or
from .graphics import RESOLUTIONS, note_symbol, number_symbol


GM_LETTERS = ["C", "C", "D", "D", "E", "F", "F", "G", "G", "A", "A", "B"]
GM_SHARPS = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
GM_C4 = 60


def gm_labels(index):
    index -= GM_C4
    octaves = index // 12
    index -= octaves * 12
    octaves += 4
    letter = GM_LETTERS[index]
    sharps = GM_SHARPS[index]
    return sharps, letter, sharps, 0, octaves


def _roll_coords(resolution, start, end, low, high):
    if resolution in RESOLUTIONS:
        width, height = RESOLUTIONS[resolution]
    else:
        width, height = resolution

    x = linspace(start, end, width)
    y = linspace(high + 1, low, height)

    x, y = meshgrid(x, y)
    aspect = width / height
    screen_ratio = (high + 1 - low) * aspect / (end - start)
    screen_x = (x - start) * screen_ratio

    return x, y, screen_x, screen_ratio


def piano_roll(resolution, start, end, low, high, labels=None):
    if labels is None:
        labels = gm_labels

    x, y, screen_x, _ = _roll_coords(resolution, start, end, low, high)

    grid = x*0 + 1

    for index in range(low, high+1):
        palette_index, letter, sharps, arrows, octaves = labels(index)
        grid_line = logical_and(y > index, y < index + 1)
        grid -= 0.1 * palette_index * grid_line
        symbol = note_symbol(4*(screen_x - 0.5), 4*(y - index - 0.5), letter, sharps, arrows)
        if octaves is not None:
            symbol = logical_or(symbol, number_symbol(4*(screen_x - 1.5), 4*(y - index - 0.5), octaves, centered=True))
        grid -= symbol

    return grid


def piano_holes(resolution, start, end, low, high, notes, border=0.1):
    x, y, _, screen_ratio = _roll_coords(resolution, start, end, low, high)
    holes = 0*x
    for note in notes:
        holes += logical_and(
            logical_and(x > note.time, x < note.off_time),
            logical_and(y > note.pitch, y < note.pitch + 1)
        ) * 0.5
        holes += logical_and(
            logical_and(x > note.time + border / screen_ratio, x < note.off_time - border / screen_ratio),
            logical_and(y > note.pitch + border, y < note.pitch + 1 - border)
        ) * 0.5

    return holes
