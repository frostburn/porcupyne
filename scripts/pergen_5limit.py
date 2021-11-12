from numpy import dot, log
from temperament import COMMA_BY_HOROGRAM, minimax, temper, rank2_pergen


for name, comma in COMMA_BY_HOROGRAM.items():
    mapping = minimax(temper([comma]))
    print(name, mapping)
    period, generator = rank2_pergen(comma, mapping, 20)
    print(period, "=", dot(mapping, period)/log(2) * 1200, "¢")
    if generator is not None:
        print(generator, "=", dot(mapping, generator)/log(2) * 1200, "¢")
    print()
