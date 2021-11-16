#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pathlib import Path
from pylab import *
from parser_7_11 import parse
from temperament import COMMA_7_11_BY_HOROGRAM, minimax, temper, JI_7_11, PERGEN_7_11_BY_HOROGRAM
from note import PitchContext, notate_7_11
from instrument import Strings, Ping, render_notes
from audio import write, merge_stereo
from lattice_visualizer import visualize_progression, make_picture_frame


def main():
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--outdir', type=str, help='Image output folder')
    args = parser.parse_args()

    horogram = "orgone"
    comma = COMMA_7_11_BY_HOROGRAM[horogram]
    mapping = minimax(temper([comma], JI_7_11), JI_7_11)
    _, generator = PERGEN_7_11_BY_HOROGRAM[horogram]
    context = PitchContext(mapping, comma)

    extra_intervals = {"G": generator, "g": (7, -1, -1)}

    g_pump = """
    -m7d(N-) G(N-_2) G(N-_1) G(m2+_1)
    """

    g_pump_melody = """
    -m7d N3d m2u -S4
    G N3d m2u -S4
    G N3d m2u -S4
    G -S4 s6u -m2u
    """

    repetitions = 4

    harmony = parse(g_pump*repetitions, extra_intervals=extra_intervals, pitch_context=context)
    melody = parse(g_pump_melody*repetitions, "1/4", extra_intervals=extra_intervals, pitch_context=context)

    if args.outdir:
        outpath = Path(args.outdir)
        notation = lambda sevens, elevens: notate_7_11(sevens, elevens, horogram=horogram)
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

    ping = Ping(attack=0.004, decay=0.3, modulation_index=7, mod_sharpness=0.5)
    melody_audio = render_notes(melody, ping) * 0.0

    result = merge_stereo((harmony_audio, 0), (melody_audio, 0))

    filename = args.outfile
    print("Storing song under {}".format(filename))
    write(filename, result * 0.25)


if __name__ == "__main__":
    main()
