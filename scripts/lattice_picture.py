# pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pylab import *
from lattice_visualizer import hex_grid, square_grid, hex_highlight, square_highlight, make_picture_frame, square_pergen_grid
from temperament import COMMA_BY_HOROGRAM, PERGEN_BY_HOROGRAM, ISLAND_COMMA_BY_HOROGRAM, ISLAND_PERGEN_BY_HOROGRAM, COMMA_3_7_BY_HOROGRAM, PERGEN_3_7_BY_HOROGRAM
from note import notate, notate_island, notate_3_7


def main():
    # pylint: disable=invalid-name, redefined-outer-name
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--temperament', type=str, default="JI", help='Temperament to use')
    parser.add_argument('--pergen', action='store_true')
    parser.add_argument('--period', nargs='+', type=int)
    parser.add_argument('--generator', nargs='+', type=int)
    parser.add_argument('--hex', action='store_true')
    parser.add_argument('--island', action='store_true')
    parser.add_argument('--za', action='store_true')
    parser.add_argument('--zoom-out', type=float, default=1.0)
    parser.add_argument('--anti-alias', type=int, default=1)
    args = parser.parse_args()

    comma = None
    period = args.period
    generator = args.generator

    if args.temperament != "JI":
        if args.island:
            comma = ISLAND_COMMA_BY_HOROGRAM[args.temperament]
        elif args.za:
            comma = COMMA_3_7_BY_HOROGRAM[args.temperament]
        else:
            comma = COMMA_BY_HOROGRAM[args.temperament]
    if args.pergen:
        if period is not None or generator is not None:
            raise ValueError("Custom period or generator provided when canonical was requested")
        if args.island:
            period, generator = ISLAND_PERGEN_BY_HOROGRAM[args.temperament]
        elif args.za:
            period, generator = PERGEN_3_7_BY_HOROGRAM[args.temperament]
        else:
            period, generator = PERGEN_BY_HOROGRAM[args.temperament]

    if period is None and generator is None:
        if args.island:
            notation = lambda threes, supermajors: notate_island(threes, supermajors, horogram=args.temperament)
        elif args.za:
            notation = lambda threes, sevens: notate_3_7(threes, sevens, horogram=args.temperament)
        else:
            notation = lambda threes, fives: notate(threes, fives, horogram=args.temperament)

        if args.hex:
            x = linspace(-10*args.zoom_out, 10*args.zoom_out, 1080)
        else:
            x = linspace(-5*args.zoom_out, 5*args.zoom_out, 1080)
        dx = x[1]-x[0]
        x, y = meshgrid(x, -x)  # pylint: disable=invalid-unary-operand-type

        image = array([0*x, 0*x, 0*x])
        for i in range(args.anti_alias):
            x_ = x + i*dx / args.anti_alias
            for j in range(args.anti_alias):
                y_ = y + j*dx/args.anti_alias
                if args.hex:
                    grid = hex_grid(x_, y_, notation=notation)*1.0
                else:
                    grid = square_grid(x_, y_, notation=notation)*1.0

                highlight = hex_highlight if args.hex else square_highlight

                if comma is None:
                    highlights = highlight(x_, y_, 0, 0)
                else:
                    highlights = 0*x_
                    for n in range(-10, 11):
                        highlights += highlight(x_, y_, n*comma[1], n*comma[2])
                image = image + array([grid - highlights*0.5, grid - highlights, grid])
    else:
        if args.island:
            notation = lambda pitch: notate_island(pitch[1], pitch[2], twos=pitch[0], horogram=args.temperament)
        elif args.za:
            notation = lambda pitch: notate_3_7(pitch[1], pitch[2], twos=pitch[0], horogram=args.temperament)
        else:
            notation = lambda pitch: notate(pitch[1], pitch[2], twos=pitch[0], horogram=args.temperament)

        period = array(period)
        generator = array(generator)

        x = linspace(-5*args.zoom_out, 5*args.zoom_out, 1080)
        dx = x[1]-x[0]
        x, y = meshgrid(x, -x)  # pylint: disable=invalid-unary-operand-type

        image = array([0*x, 0*x, 0*x])
        for i in range(args.anti_alias):
            x_ = x + i*dx / args.anti_alias
            for j in range(args.anti_alias):
                y_ = y + j*dx/args.anti_alias
                grid = square_pergen_grid(x_, y_, period, generator, notation=notation)
                image = image + array([grid, grid, grid])

    image = image/(args.anti_alias**2)
    fname = args.outfile
    print("Saving", fname)
    imsave(fname, make_picture_frame(image))


if __name__ == "__main__":
    main()
