from numpy import tanh, sqrt, exp, sinh
from numpy.random import RandomState
from .audio import sinepings, tlike, trange, sine
from .noise import pink_noise


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
            1 / (5 + ratios + self.rstate.random(n)*self.amplitude_spread),
            self.rstate.random(n)
        )
        t = tlike(pings)
        result = tanh(sqrt(t+0.000001)*pings*velocity)
        return [result, result]


class Snare:
    def __init__(self, base_freq=173, mod_amount=0.12, mod_freq=222, partials=((274, 3, 0.1), (1000, 1, 0.025)), noise_decay=10, noise_amp=1.0, decay=20):
        self.base_freq = base_freq
        self.mod_amount = mod_amount
        self.mod_freq = mod_freq
        self.partials = partials
        self.noise_decay = noise_decay
        self.noise_amp = noise_amp
        self.decay = decay

    def play(self, velocity):
        t = trange(1)
        env = exp(-t)
        signal = sinh(
            (4+velocity)*sine(
                t*self.base_freq + self.mod_amount*sine(t*self.mod_freq)
            )*env
        )/sinh(4 + velocity)

        for freq, sharpness, amp in self.partials:
            signal += sinh(sharpness*sine(t*freq)*env)/sinh(sharpness)*amp

        signal += pink_noise(1) * t*exp(-t*self.noise_decay)*(10 + 5*velocity)*self.noise_amp

        result = tanh(signal)*exp(-t*self.decay)*0.7*velocity
        return [result, result]


if __name__ == '__main__':
    import sys
    from pathlib import Path
    from .audio import write

    name = None
    if len(sys.argv) > 1:
        name = sys.argv[1]

    path = Path("/tmp/")

    if name is None or name == "splash":
        splash = SplashCymbal().play(1)
        write(path / "splash.wav", splash[0])

    if name is None or name == "snare":
        snare = Snare().play(1)
        write(path / "snare.wav", snare[0])
