from pylab import log


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


def note_unicode(letter, sharps, arrows, octaves=None):
    if sharps == 0:
        accidental = chr(0x266E)
        if arrows < 0:
            accidental = chr(0x1D12F)
        elif arrows > 0:
            accidental = chr(0x1D12E)
    elif sharps == 1:
        accidental = chr(0x266F)
        if arrows < 0:
            accidental = chr(0x1D131)
        elif arrows > 0:
            accidental = chr(0x1D130)
    elif sharps == -1:
        accidental = chr(0x266D)
        if arrows < 0:
            accidental = chr(0x1D12D)
        elif arrows > 0:
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
        if arrows < 0:
            accidental += chr(0x1F813)
        elif arrows > 0:
            accidental += chr(0x1F811)

    if octaves is None:
        result = letter + accidental
    else:
        result = letter + str(octaves) + accidental

    if abs(arrows) > 1:
        result += str(abs(arrows))
    return result


def interval_name(semitones):
    semitones = abs(semitones)
    quality = ["P", "m", "M", "m", "M", "P", "A", "P", "m", "M", "m", "M"][semitones%12]
    number = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7][semitones%12]
    number += (semitones // 12)*7
    return quality + str(number)


def rwh_primes1(n):
    # https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
    """ Returns  a list of primes < n """
    sieve = [True] * (n//2)
    for i in range(3, int(n**0.5)+1, 2):
        if sieve[i//2]:
            sieve[i*i//2::i] = [False] * ((n-i*i-1)//(2*i)+1)
    return [2] + [2*i+1 for i in range(1,n//2) if sieve[i]]


def append_prime(primes):
    if not primes:
        primes.append(2)
    if len(primes) == 1:
        primes.append(3)
    n = primes[-1]
    while True:
        n += 2
        limit = int(n**0.5)
        for p in primes:
            if p > limit:
                primes.append(n)
                return
            if n % p == 0:
                break

def rindex(lst, value):
    lst = list(lst)
    return len(lst) - lst[::-1].index(value) - 1
