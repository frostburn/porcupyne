# pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pylab import *
from lattice_visualizer import hex_grid, square_grid, hex_highlight, square_highlight, make_picture_frame, square_pergen_grid
from temperament import COMMA_BY_HOROGRAM, PERGEN_BY_HOROGRAM
from note import notate


def main():
    # pylint: disable=invalid-name, redefined-outer-name
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--temperament', type=str, default="JI", help='Temperament to use')
    parser.add_argument('--pergen', action='store_true')
    parser.add_argument('--period', nargs='+', type=int)
    parser.add_argument('--generator', nargs='+', type=int)
    parser.add_argument('--hex', action='store_true')
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
        notation = lambda threes, fives: notate(threes, fives, horogram=args.temperament)

        if args.hex:
            x = linspace(-10, 10, 1080)
        else:
            x = linspace(-5, 5, 1080)
        x, y = meshgrid(x, -x)  # pylint: disable=invalid-unary-operand-type


        if args.hex:
            grid = hex_grid(x, y, notation=notation)*1.0
        else:
            grid = square_grid(x, y, notation=notation)*1.0

        highlight = hex_highlight if args.hex else square_highlight

        if comma is None:
            highlights = highlight(x, y, 0, 0)
        else:
            highlights = 0*x
            for n in range(-10, 11):
                highlights += highlight(x, y, n*comma[1], n*comma[2])
        image = [grid - highlights*0.5, grid - highlights, grid]
    else:
        notation = lambda pitch: notate(pitch[1], pitch[2], twos=pitch[0], horogram=args.temperament)

        period = array(period)
        generator = array(generator)

        x = linspace(-5, 5, 1080)
        x, y = meshgrid(x, -x)  # pylint: disable=invalid-unary-operand-type

        grid = square_pergen_grid(x, y, period, generator, notation=notation)
        image = [grid, grid, grid]

    fname = args.outfile
    print("Saving", fname)
    imsave(fname, make_picture_frame(image))


if __name__ == "__main__":
    main()
