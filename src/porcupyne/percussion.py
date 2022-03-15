from numpy import tanh, sqrt
from numpy.random import RandomState
from .audio import sinepings, tlike

class Percussion:
    def play(self, velocity):
        pass


class SplashCymbal:
    def __init__(self, base_freq=650, num_partials=7000, freq_spread=150, decay_spread=5, amplitude_spread=5, seed=4):
        self.rstate = RandomState()
        self.num_partials = num_partials
        self.base_freq = base_freq
        self.num_partials
        self.freq_spread = freq_spread
        self.decay_spread = decay_spread
        self.amplitude_spread = amplitude_spread
        self.seed = seed

    def play(self, velocity):
        self.rstate.seed(self.seed)
        n = self.num_partials

        ratios = 1 + self.freq_spread * self.rstate.random(n)
        pings = sinepings(
            self.base_freq * ratios,
            2 + ratios + self.rstate.random(n)*self.decay_spread,
            1 / (5 + ratios + self.rstate.random(n)*self.amplitude_spread)
        )
        t = tlike(pings)
        result = tanh(sqrt(t+0.000001)*pings*velocity)
        return [result, result]


if __name__ == '__main__':
    from .audio import write
    splash = SplashCymbal().play(1)
    write("/tmp/splash.wav", splash[0])
