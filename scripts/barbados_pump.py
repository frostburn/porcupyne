#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pathlib import Path
from pylab import *
from island_parser import parse
from temperament import ISLAND_COMMA_BY_HOROGRAM, minimax, temper, JI_ISLAND, ISLAND_PERGEN_BY_HOROGRAM
from note import PitchContext, notate_island
from instrument import Strings, Ping, render_notes
from audio import write, merge_stereo
from lattice_visualizer import visualize_progression, make_picture_frame


def main():
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--outdir', type=str, help='Image output folder')
    args = parser.parse_args()

    horogram = "barbados"
    comma = ISLAND_COMMA_BY_HOROGRAM[horogram]
    mapping = minimax(temper([comma], JI_ISLAND), JI_ISLAND)
    _, generator = ISLAND_PERGEN_BY_HOROGRAM[horogram]
    context = PitchContext(mapping, comma)

    extra_intervals = {"G": generator, "g": (1, -1, 1)}

    g_pump = """
    -P5(^M7) +g(vm7_2) -G(^v7_3)
    """

    g_pump_melody = """
    +P4 +^M3 +vm3 +^M3
    -P5[2] -^M3 -vm3
    +^M3 -vm3 -^M3[2]
    """

    repetitions = 4

    harmony = parse(g_pump*repetitions, extra_intervals=extra_intervals, pitch_context=context)
    melody = parse(g_pump_melody*repetitions, "1/4", extra_intervals=extra_intervals, pitch_context=context)

    if args.outdir:
        outpath = Path(args.outdir)
        notation = lambda threes, supermajors: notate_island(threes, supermajors, horogram=horogram)
        for i, image in enumerate(visualize_progression("720p", 0, 0, 10, harmony, notation=notation, comma=comma)):
            fname = outpath / "harmony{:02d}.png".format(i)
            print("Saving", fname)
            imsave(fname, make_picture_frame(image))

        for i, image in enumerate(visualize_progression("720p", 0, 0, 10, melody, notation=notation, comma=comma)):
            fname = outpath / "melody{:02d}.png".format(i)
            print("Saving", fname)
            imsave(fname, make_picture_frame(image))


    strings = Strings(attack=0.2)
    harmony_audio = render_notes(harmony, strings)

    ping = Ping(attack=0.004, decay=0.3, modulation_index=5, mod_sharpness=1.0)
    melody_audio = render_notes(melody, ping) * 0.7

    result = merge_stereo((harmony_audio, 0), (melody_audio, 0))

    filename = args.outfile
    print("Storing song under {}".format(filename))
    write(filename, result * 0.25)


if __name__ == "__main__":
    main()
