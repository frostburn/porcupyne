import warnings
from numpy import arange, cumsum, arctan, arcsin, sin, cos, log, exp, array, imag, tanh, pi, sqrt, clip, zeros, ceil, ndarray, empty as nempty, zeros_like
from numpy.random import rand
import scipy.io.wavfile
try:
    from ._routines import ffi, lib
except ImportError:
    warnings.warn("Unable to import _routines.* Run scripts/build_routines.py to speed up computation.")
    ffi = None
    lib = None
# pylint: disable=invalid-name


EPSILON = 1e-5
SAMPLE_RATE = 48000

PHI = (sqrt(5)+1)/2


def set_sample_rate(value):
    global SAMPLE_RATE
    SAMPLE_RATE = value


def tempty(duration):
    return nempty(int(round(duration * SAMPLE_RATE)))


def tzeros(duration):
    return zeros(int(round(duration * SAMPLE_RATE)))


def tlike(arr):
    return arange(len(arr)) / SAMPLE_RATE


def trange(duration):
    return arange(int(round(duration * SAMPLE_RATE))) / SAMPLE_RATE


def integrate(signal):
    return cumsum(signal) / SAMPLE_RATE


def sine(phase):
    return sin(2*pi*phase)


def cosine(phase):
    return cos(2*pi*phase)


def softsaw(phase, sharpness):
    sharpness = clip(sharpness, EPSILON, 1.0 - EPSILON)
    return arctan(
        sharpness * sin(2*pi*phase) / (1.0 + sharpness * cos(2*pi*phase))
    ) / arcsin(sharpness)


def ping(freq, carrier_index=1, modulation_index=2, decay=0.4, sharpness1=0.99, sharpness2=1.2, separation=6):
    """
    Decent FM string pluck or bell depending on the modulation indices.
    """
    dur = -log(EPSILON) / decay
    t = trange(dur)
    envelope = exp(-t*decay) * tanh(t*1000)

    modulator = arcsin(sin(2*pi*freq*t*modulation_index + t*separation) * exp(-t*2) * sharpness1) * sharpness2
    left = sin(2*pi*freq*t*carrier_index + modulator) * envelope

    modulator = arcsin(sin(2*pi*freq*t*modulation_index - t*separation) * exp(-t*2) * sharpness1) * sharpness2
    right = sin(2*pi*freq*t*carrier_index + modulator) * envelope

    return array((left, right))


def organ(freq, duration):
    t = trange(duration)
    theta = 2j * pi * freq * t
    zl = exp(theta + 2j*t + 2j*pi*rand()) * 0.93
    zr = exp(theta - 2j*t + 2j*pi*rand()) * 0.93
    resultl = imag(zl)
    resultr = imag(zr)
    f = freq
    for _ in range(9):
        f *= 2
        if 2*f > SAMPLE_RATE:
            break
        zl = zl**2
        zr = zr**2
        resultl += imag(zl)
        resultr += imag(zr)
    env = 0.3 * tanh((duration - t)*60) * tanh(t*150)
    return array((resultl * env, resultr * env))


def kick():
    t = trange(1)
    a = 1.8
    b = 1.2
    theta = arcsin((1-a) / b)
    k = -log(a + sin(theta + (exp(-t*50)-1)*30)*exp(-t*5)*b) * exp(-t*3)
    return k


def snare():
    t = trange(1.5)
    res = 0
    for k in [7, 11, 13, 17, 29]:
        res += tanh(0.2 + 2*sin(t*120*k) * exp(-t*(2*k + 3*cos(k))))
    noise = rand(len(t)+1) - 0.5
    noise = noise[1:] + noise[:-1]
    return tanh(0.2*res + 0.3 * noise * exp(-40*t))*3


def merge(*samples):
    """
    Add samples together at specified locations.
    """
    length = 0
    for sample, location in samples:
        length = max(length, len(sample) + float(location) * SAMPLE_RATE)
    x = zeros(int(ceil(length)))
    for sample, location in samples:
        loc = int(location * SAMPLE_RATE)
        x[loc:loc+len(sample)] += sample
    return x


def merge_stereo(*samples):
    left = [(s[0][0], s[1]) for s in samples]
    right = [(s[0][1], s[1]) for s in samples]
    return array([merge(*left), merge(*right)])


def write(filename, data):
    if not isinstance(data, ndarray):
        data = array(data, dtype=float)

    # Figure out the number of channels
    shape = data.shape
    if len(shape) > 3:
        raise ValueError("Data shape not understood. Not single or multi-channel.")
    if len(data.shape) > 1 and shape[0] < shape[1]:
        data = data.T

    if data.dtype == float:
        data = (data * (0.99 * 2.0 ** 15)).astype("int16")
    scipy.io.wavfile.write(filename, SAMPLE_RATE, data)


def empty():
    return array([[], []])


def sineping(frequency, decay, amplitude=1, phase=0, duration=None, force_fallback=False):
    if duration is None:
        if decay <= EPSILON:
            raise ValueError("Non-decaying sine ping and no duration given")
        duration = -log(EPSILON) / decay
    if ffi is None or force_fallback:
        t = trange(duration)
        return sine(phase + frequency*t) * exp(-t*decay) * amplitude
    result = tempty(duration)
    result_buf = ffi.cast("double*", result.ctypes.data)
    lib.sineping(result_buf, len(result), 2*pi*frequency/SAMPLE_RATE, exp(-decay/SAMPLE_RATE), amplitude, 2*pi*phase)
    return result


def sinepings(frequencies, decays, amplitudes, phases=None, duration=None, force_fallback=False):
    if phases is None:
        phases = zeros_like(frequencies)
    fs = []
    ds = []
    amps = []
    ps = []
    nyquist = SAMPLE_RATE / 2
    for f, d, a, p in zip(frequencies, decays, amplitudes, phases):
        if abs(f) < nyquist:
            fs.append(f)
            ds.append(d)
            amps.append(a)
            ps.append(p)
    frequencies, decays, amplitudes, phases = fs, ds, amps, ps
    if duration is None:
        min_decay = float("inf")
        for decay in decays:
            if decay <= EPSILON:
                raise ValueError("Non-decaying mode and no duration given")
            if decay < min_decay:
                min_decay = decay
        duration = -log(EPSILON) / min_decay
    if ffi is None or force_fallback:
        t = trange(duration)
        result = tzeros(duration)
        for frequency, decay, amplitude, phase in zip(frequencies, decays, amplitudes, phases):
            result += sine(phase + frequency*t) * exp(-t*decay) * amplitude
        return result
    result = tzeros(duration)
    result_buf = ffi.cast("double*", result.ctypes.data)
    deltas = 2*pi*array(frequencies)/SAMPLE_RATE
    deltas_buf = ffi.cast("double*", deltas.ctypes.data)
    gammas = exp(-array(decays)/SAMPLE_RATE)
    gammas_buf = ffi.cast("double*", gammas.ctypes.data)
    amplitudes = array(amplitudes)
    amplitudes_buf = ffi.cast("double*", amplitudes.ctypes.data)
    phases = 2*pi*array(phases)
    phases_buf = ffi.cast("double*", phases.ctypes.data)
    lib.sinepings(
        result_buf, len(result),
        deltas_buf, gammas_buf, amplitudes_buf, phases_buf,
        len(deltas)
    )
    return result
