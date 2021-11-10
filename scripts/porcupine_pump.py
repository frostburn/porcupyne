#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
from pylab import *
from parser_5limit import parse
from temperament import COMMA_BY_HOROGRAM, minimax, temper
from note import PitchContext
from instrument import Strings, Ping, render_notes
from audio import write, merge_stereo


def main(filename):
    horogram = "porcupine"
    comma = COMMA_BY_HOROGRAM[horogram]
    mapping = minimax(temper([comma]))
    generator = (1, -2, 1)
    # temperament = lambda t, f: canonize(t, f, horogram)
    context = PitchContext(mapping, comma)

    extra_intervals = {"G": generator, "g": (0, 2, -1)}

    g_pump = """
    +P4(m7_2) -G(m7_3) -G(m7) -G(7)
    """

    g_pump_melody = """
    +P4 +m3u +M3d +m3u
    -G -G[1/2] -G[1/2] -M3d -m3u
    -G +m3u +M3d +G[1/2] +G[1/2]
    -G -m3u -G[1/2] -G[1/2] -M3d
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
