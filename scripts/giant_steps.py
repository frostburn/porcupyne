#pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin
import sys
from pylab import *
from audio import *
from parser_5limit import parse


def main(filename):
    #pylint: disable=invalid-name
    # Only defines root motion in terms of pitch classes
    chord_progression = """
    -P5(M) +m3u(dom) -P5(M) +m3u(dom) -P5(M)[2] +A4d(m7) -P5(dom)
    -P5(M) +m3u(dom) -P5(M) +m3u(dom) -P5(M)[2] +A4d(m7) -P5(dom)
    -P5(M)[2] +A4d(m7) -P5(dom) -P5(M)[2] +A4d(m7) -P5(dom)
    -P5(M)[2] +A4d(m7) -P5(dom) -P5(M)[2] +m7u(m7) -P5(dom)
    """

    melody = """
    +P1[4] -M3d[4] -m3u[4] -M3d[7/2] +m3u[17/2] +A1d[3] -M2[5]
    +P4[4] -M3d[4] -m3u[4] -M3d[7/2] +m3u[17/2] +A1d[4] -M2[7/2] +P4[17/2]
    +A1d[4] -M2[7/2] +P4[17/2] +A1d[4] -M2[7/2] +P4[17/2]
    +A1d[4] -M2[7/2] +P4[17/2] -M3d[3] +P1[5]
    """

    melody = parse(melody)

    # Move chord tones under the melody
    progression = parse(chord_progression)
    for melody_notes, notes in zip(melody, progression):
        melody_note = melody_notes[0]
        for note in notes:
            note.pitch = array(note.pitch)
            while note < melody_note:
                note.pitch += array([1, 0, 0])
            while note > melody_note:
                note.pitch -= array([1, 0, 0])

    result = empty()

    for notes in melody:
        note = notes[0]
        freq = 1.5 * note.freq
        dur = float(note.duration/8)
        t = trange(dur)
        signal = tanh(100*t)*tanh(10*(dur-t))*softsaw(freq*t, 0.25+exp(-15*t)*0.6)
        signal = [signal]*2
        result = merge_stereo((result, 0), (signal, float(note.time/8)))

    for notes in progression:
        chord = empty()
        for note in notes:
            freq = 1.5 * note.freq
            dur = float(note.duration/2)
            t = trange(dur)
            signal = tanh(50*t)*tanh(10*(dur-t))*softsaw(freq*t, 0.2+exp(-5*t)*0.5)
            signal = [signal]*2
            chord = merge_stereo((chord, 0), (signal, 0))
        result = merge_stereo((result, 0), (chord*0.5, float(note.time/2)))


    if not filename.endswith(".wav"):
        print("No output filename given or unrecognized file extension")
        return
    print("Storing song under {}".format(filename))
    write(filename, result * 0.25)


if __name__ == "__main__":
    main(sys.argv[-1])
