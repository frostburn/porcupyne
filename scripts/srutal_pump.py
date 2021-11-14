#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pathlib import Path
from pylab import *
from parser_11limit import parse
from temperament import COMMA_LIST_BY_HOROGRAM, minimax, temper, JI_7LIMIT, canonize_7limit, COMMA_BY_HOROGRAM
from note import PitchContext, notate
from instrument import Strings, Ping, render_notes
from audio import write, merge_stereo
from lattice_visualizer import visualize_progression, make_picture_frame


def main():
    # pylint: disable=too-many-locals
    parser = argparse.ArgumentParser(description='Render image of the lattice for a given temperament')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('--outdir', type=str, help='Image output folder')
    args = parser.parse_args()

    horogram = "srutal"
    comma_list = COMMA_LIST_BY_HOROGRAM[horogram]
    mapping = minimax(temper(comma_list, JI_7LIMIT), JI_7LIMIT)
    mapping = array(list(mapping) + [log(11)/log(4)*2*mapping[0]])
    context = PitchContext(mapping)  # TODO: Comma list support for PitchContext

    extra_intervals = {}

    pump = """
    +P4(m7_2) -P5(m7) +m6u(h7_1) -P5(m7) +P4(m7_2) -M3d(h7_3)
    """

    pump_melody = """
    +P4 +m3u +M3d
    -P5 -M3d -m3u
    -M3d +M3d +m3u

    -M2 +m3u +M3d
    -P5 -M3d -m3u
    +m3u +M6d -M3d
    """

    repetitions = 4

    harmony = parse(pump*repetitions, extra_intervals=extra_intervals, pitch_context=context)
    melody = parse(pump_melody*repetitions, "1/3", extra_intervals=extra_intervals, pitch_context=context)

    if args.outdir:
        outpath = Path(args.outdir)
        notation = lambda threes, fives: notate(threes, fives, horogram=horogram)
        canonicals = []
        for notess in [harmony, melody]:
            result = []
            for notes in notess:
                notes = [note.copy() for note in notes]
                for note in notes:
                    # Hack down two dimensions to be able to visualize
                    note.pitch = [0] + list(canonize_7limit(*note.pitch[1:-1], horogram=horogram)[:-1])
                    note._context = None
                result.append(notes)
            canonicals.append(result)
        comma = COMMA_BY_HOROGRAM[horogram]
        for i, image in enumerate(visualize_progression("720p", 0, 0, 10, canonicals[0], notation=notation, comma=comma)):
            fname = outpath / "harmony{:02d}.png".format(i)
            print("Saving", fname)
            imsave(fname, make_picture_frame(image))

        for i, image in enumerate(visualize_progression("720p", 0, 0, 10, canonicals[1], notation=notation, comma=comma)):
            fname = outpath / "melody{:02d}.png".format(i)
            print("Saving", fname)
            imsave(fname, make_picture_frame(image))


    strings = Strings(attack=0.2)
    harmony_audio = render_notes(harmony, strings)

    ping = Ping(attack=0.004, decay=0.3, modulation_index=3, mod_sharpness=1.0)
    melody_audio = render_notes(melody, ping) * 0.7

    result = merge_stereo((harmony_audio, 0), (melody_audio, 0))

    filename = args.outfile
    print("Storing song under {}".format(filename))
    write(filename, result * 0.25)


if __name__ == "__main__":
    main()
