# pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pylab import *
from lattice_visualizer import hex_grid, hex_highlight, make_picture_frame
from temperament import COMMA_BY_HOROGRAM, canonize


def main():
    # pylint: disable=invalid-name, redefined-outer-name
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--temperament', type=str, default="JI", help='Temperament to use')
    args = parser.parse_args()

    comma = None
    if args.temperament != "JI":
        comma = COMMA_BY_HOROGRAM[args.temperament]
    temperament = lambda threes, fives: canonize(threes, fives, args.temperament)

    x = linspace(-10, 10, 1080)
    x, y = meshgrid(x, -x)  # pylint: disable=invalid-unary-operand-type

    grid = hex_grid(x, y, temperament=temperament)*1.0

    if comma is None:
        highlights = hex_highlight(x, y, 0, 0)
    else:
        highlights = 0*x
        for n in range(-10, 11):
            highlights += hex_highlight(x, y, n*comma[1], n*comma[2])
    image = [grid - highlights*0.5, grid - highlights, grid]
    fname = args.outfile
    print("Saving", fname)
    imsave(fname, make_picture_frame(image))


if __name__ == "__main__":
    main()
