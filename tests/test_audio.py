from numpy import isclose
from porcupyne.audio import sineping, sinepings, ffi


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


if __name__ == '__main__':
    test_sineping()
    test_sinepings()
