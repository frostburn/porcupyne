from numpy import isclose, array, around
from porcupyne.audio import sineping, sinepings, delayedpings, ffi, get_sample_rate


def test_sineping():
    assert ffi is not None
    y0 = sineping(100, 100, 0.8, 0.3)
    y1 = sineping(100, 100, 0.8, 0.3, force_fallback=True)
    assert isclose(y0, y1).all()


def test_sinepings():
    assert ffi is not None
    y0 = sinepings([100, 111, 222, 333], [100, 200, 300, 400], [1, 0.9, 0.8, 0.5], [0, 0.2, 0.3, 0.4])
    y1 = sinepings([100, 111, 222, 333], [100, 200, 300, 400], [1, 0.9, 0.8, 0.5], [0, 0.2, 0.3, 0.4], force_fallback=True)
    assert isclose(y0, y1).all()


def test_delayedpings():
    assert ffi is not None
    srate = get_sample_rate()
    delays = around(array([0.01, 0.02]) * srate) / srate
    y0 = delayedpings([100, 111], [100, 200], [0.9, 0.7], [0.01, 0.02], delays, [0.1, 0.2])
    y1 = delayedpings([100, 111], [100, 200], [0.9, 0.7], [0.01, 0.02], delays, [0.1, 0.2], force_fallback=True)
    assert isclose(y0, y1).all()

if __name__ == '__main__':
    test_sineping()
    test_sinepings()
    test_delayedpings()
