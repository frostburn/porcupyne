# pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pylab import *
from lattice_visualizer import hex_grid, hex_highlight, make_picture_frame, square_pergen_grid
from temperament import COMMA_BY_HOROGRAM, PERGEN_BY_HOROGRAM, canonize, canonize2


def main():
    # pylint: disable=invalid-name, redefined-outer-name
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--temperament', type=str, default="JI", help='Temperament to use')
    parser.add_argument('--pergen', action='store_true')
    parser.add_argument('--period', nargs='+', type=int)
    parser.add_argument('--generator', nargs='+', type=int)
    args = parser.parse_args()

    comma = None
    period = args.period
    generator = args.generator

    if args.temperament != "JI":
        comma = COMMA_BY_HOROGRAM[args.temperament]
    if args.pergen:
        if period is not None or generator is not None:
            raise ValueError("Custom period or generator provided when canonical was requested")
        period, generator = PERGEN_BY_HOROGRAM[args.temperament]

    if period is None and generator is None:
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
    else:
        temperament = lambda twos, threes, fives: canonize2(twos, threes, fives, args.temperament)

        period = array(period)
        generator = array(generator)

        x = linspace(-5, 5, 1080)
        x, y = meshgrid(x, -x)  # pylint: disable=invalid-unary-operand-type

        grid = square_pergen_grid(x, y, period, generator, temperament=temperament)
        image = [grid, grid, grid]

    fname = args.outfile
    print("Saving", fname)
    imsave(fname, make_picture_frame(image))


if __name__ == "__main__":
    main()
