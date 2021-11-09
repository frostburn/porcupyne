from numpy import array, dot
from parser_5limit import parse_pitch, parse_interval


def test_parse_pitch():
    assert (parse_pitch("A4") == array([0, 0, 0])).all()
    assert (parse_pitch("A3") == array([-1, 0, 0])).all()
    assert (parse_pitch("A5") == array([1, 0, 0])).all()
    assert (parse_pitch("A4u") == array([(-4, 4, -1)])).all()
    assert (parse_pitch("A4d") == array([(4, -4, 1)])).all()
    assert (parse_pitch("A4d2") == array([(8, -8, 2)])).all()

    assert (parse_pitch("E4") == array([-2, 1, 0])).all()
    assert (parse_pitch("D4") == array([1, -1, 0])).all()

    assert (parse_pitch("F#3d2") == array([13, -5, 2])).all()


def test_parse_interval():
    mapping = array([12, 19, 28])
    scale = ["P1", "m2", "M2", "m3u", "M3d", "P4", "A4", "P5", "m6u", "M6d", "m7u", "M7d", "P8", "m9", "M9"]
    edo12 = [dot(mapping, parse_interval(s)) for s in scale]
    assert edo12 == list(range(15))

    assert (parse_interval("M3d") == array([-2, 0, 1])).all()
    assert (parse_interval("d7u2") == array([7, -1, -2])).all()


if __name__ == '__main__':
    test_parse_pitch()
    test_parse_interval()
