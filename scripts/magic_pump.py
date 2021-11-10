#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
from pylab import *
from parser_5limit import parse
from temperament import COMMA_BY_HOROGRAM, minimax, temper #, canonize
from note import PitchContext
from instrument import Strings, Ping, render_notes
from audio import write, merge_stereo
# from lattice_visualizer import visualize_progression, make_picture_frame


def main(filename):
    horogram = "magic"
    comma = COMMA_BY_HOROGRAM[horogram]
    mapping = minimax(temper([comma]))
    generator = (-2, 0, 1)
    # temperament = lambda t, f: canonize(t, f, horogram)
    context = PitchContext(mapping, comma)

    extra_intervals = {"G": generator, "G2": (-4, 0, 2), "g": (3, 0, -1), "g2": (5, 0, -2)}

    g_pump = """
    -P5(M7) +G(+7_3) -g2(M7+) +G2(7_2)
    """

    g_pump_melody = """
    -P5 +G +m3u +G
    -P5 +G +G[2]
    -g[2] +G[2]
    +m3u +M3d -m3u -G
    """

    repetitions = 2

    harmony = parse(g_pump*repetitions, extra_intervals=extra_intervals, pitch_context=context)
    melody = parse(g_pump_melody*repetitions, "1/4", extra_intervals=extra_intervals, pitch_context=context)

    strings = Strings(attack=0.2)
    harmony_audio = render_notes(harmony, strings)

    ping = Ping(attack=0.004, decay=0.3)
    melody_audio = render_notes(melody, ping) * 0.7

    result = merge_stereo((harmony_audio, 0), (melody_audio, 0))

    if not filename.endswith(".wav"):
        print("No output filename given or unrecognized file extension")
        return
    print("Storing song under {}".format(filename))
    write(filename, result * 0.25)


if __name__ == "__main__":
    main(sys.argv[-1])
