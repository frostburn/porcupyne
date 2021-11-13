from pylab import log


LYDIAN = ("F", "C", "G", "D", "A", "E", "B")


def gcd(a, b):
    # pylint: disable=invalid-name
    if b == 0:
        return a
    return gcd(b, a % b)


def rtoi(ratio, division=12):
    return log(ratio) / log(2**(1/division))


def itor(interval, division=12):
    return 2**(interval/division)


def note_name(index, flats=False):
    if flats:
        return ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"][index%12]
    return ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][index%12]


def note_unicode_5limit(threes, fives, twos=None, reference_letter="A", reference_octave=4, first_letter_of_the_octave="C"):
    index = LYDIAN.index(reference_letter) + threes + fives*4
    sharps = index // len(LYDIAN)
    letter = LYDIAN[index % len(LYDIAN)]
    if sharps == 0:
        accidental = chr(0x266E)
        if fives > 0:
            accidental = chr(0x1D12F)
        elif fives < 0:
            accidental = chr(0x1D12E)
    elif sharps == 1:
        accidental = chr(0x266F)
        if fives > 0:
            accidental = chr(0x1D131)
        elif fives < 0:
            accidental = chr(0x1D130)
    elif sharps == -1:
        accidental = chr(0x266D)
        if fives > 0:
            accidental = chr(0x1D12D)
        elif fives < 0:
            accidental = chr(0x1D12C)
    elif sharps >= 2:
        accidental = chr(0x1D12A)
    elif sharps <= -2:
        accidental = chr(0x1D12B)

    if abs(sharps) >= 2:
        while sharps > 2:
            if sharps > 3:
                accidental += chr(0x1D12A)
                sharps -= 2
            else:
                accidental = chr(0x266F) + accidental
                sharps -= 1
        while sharps < -2:
            if sharps < -3:
                accidental += chr(0x1D12B)
                sharps += 2
            else:
                accidental = chr(0x266D) + accidental
                sharps += 1
        if fives > 0:
            accidental += chr(0x1F813)
        elif fives < 0:
            accidental += chr(0x1F811)

    if twos is None:
        result = letter + accidental
    else:
        if reference_letter != "A" or first_letter_of_the_octave != "C":
            raise NotImplementedError("Dynamic reference not implemented")
        edo12 = twos*12 + threes*19 + fives*28
        octaves = reference_octave + (edo12 + 9)//12
        result = letter + str(octaves) + accidental

    if abs(fives) > 1:
        result += str(abs(fives))
    return result


def interval_name(semitones):
    semitones = abs(semitones)
    quality = ["P", "m", "M", "m", "M", "P", "A", "P", "m", "M", "m", "M"][semitones%12]
    number = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7][semitones%12]
    number += (semitones // 12)*7
    return quality + str(number)
