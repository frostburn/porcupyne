#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import argparse
from pathlib import Path
from pylab import *
from parser_5limit import CHORDS_5LIMIT, parse_interval
from lattice_visualizer import hex_grid, hex_highlight, make_picture_frame
from temperament import JI_5LIMIT, COMMA_BY_HOROGRAM, canonize, mod_comma, minimax, temper
from audio import empty, trange, softsaw, merge_stereo, write

def main():
    parser = argparse.ArgumentParser(description='Render lattice images and audio samples of chords')
    parser.add_argument('outfile', type=str, help='Audio output file name')
    parser.add_argument('outdir', type=str, help='Image output directory')
    parser.add_argument('--temperament', type=str, default="JI", help='Temperament to use')
    parser.add_argument('--no-images', action='store_true')
    parser.add_argument('--no-audio', action='store_true')
    args = parser.parse_args()

    imagedir = Path(args.outdir)

    comma = None
    if args.temperament != "JI":
        comma = COMMA_BY_HOROGRAM[args.temperament]
        mod = lambda p: mod_comma(p, comma)
    else:
        mod = lambda p: p
    temperament = lambda threes, fives: canonize(threes, fives, args.temperament)

    seen = set()
    chords = {}

    for name, tokens in sorted(CHORDS_5LIMIT.items()):
        chord = [parse_interval(token) for token in tokens]
        unique = frozenset([tuple(mod(tone)) for tone in chord])
        if unique not in seen:
            seen.add(unique)
            chords[name] = chord

    for name in sorted(chords.keys()):
        print(name)
    print("Total of {} chords".format(len(chords)))

    if not args.no_images:
        print("Saving images...")
        x = linspace(-10, 10, 1080)
        x, y = meshgrid(x, -x+2)

        grid = hex_grid(x, y, temperament=temperament)*1.0

        i = 0
        for name, tones in sorted(chords.items()):
            highlights = 0*x
            for tone in tones[1:]:
                highlights += hex_highlight(x, y, tone[1], tone[2])
            image = [grid - highlights*0.5, grid - highlights, grid - hex_highlight(x, y, tones[0][1], tones[0][2])]
            fname = imagedir / "out{:02d}.png".format(i)
            # print("Saving", fname)
            imsave(fname, make_picture_frame(image))
            i += 1
            # print()

    if not args.no_audio:
        if comma is None:
            mapping = JI_5LIMIT
        else:
            mapping = minimax(temper([comma]))
        print("Saving audio...")
        result = empty()
        beat_dur = 1.0

        t_ = 0
        for name, tones in sorted(chords.items()):
            chord_audio = empty()
            for tone in tones:
                freq = 300 * exp(dot(tone, mapping))
                dur = beat_dur
                t = trange(dur)
                signal = tanh(50*t)*tanh(10*(dur-t))*softsaw(freq*t, 0.2+exp(-5*t)*0.5)
                signal = [signal]*2
                chord_audio = merge_stereo((chord_audio, 0), (signal, 0))
            result = merge_stereo((result, 0), (chord_audio*0.5, t_))
            t_ += beat_dur

        filename = args.outfile
        print("Storing song under {}".format(filename))
        write(filename, result * 0.25)

if __name__ == "__main__":
    main()
