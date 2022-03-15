from numpy import tanh, sqrt, exp, sinh, sin, log, arcsin
from numpy.random import RandomState
from .audio import sinepings, tlike, trange, sine
from .noise import pink_noise, white_noise


class Percussion:
    def play(self, velocity):
        pass


class SplashCymbal(Percussion):
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


class Snare(Percussion):
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


class HiHat(Percussion):
    # TODO: Better noise spectra
    def __init__(self, omega0=2100, omega1=4768, omega2=2880, mod1=4.3, mod2=40.5, mod_decay=10, metal_decay=30, metal_amp=0.9, pink_decay=25, pink_amp=0.3, white_decay=45, white_amp=1.2):
        self.omega0 = omega0
        self.omega1 = omega1
        self.omega2 = omega2
        self.mod1 = mod1
        self.mod2 = mod2
        self.mod_decay = mod_decay
        self.metal_decay = metal_decay
        self.metal_amp = metal_amp
        self.pink_decay = pink_decay
        self.pink_amp = pink_amp
        self.white_decay = white_decay
        self.white_amp = white_amp

    def play(self, velocity):
        t = trange(1)
        metal = sin(t*self.omega0 + self.mod1*sin(t*self.omega1 + self.mod2*sin(t*self.omega2))*exp(-t*self.mod_decay))
        wn = white_noise(1)
        pn = pink_noise(1)
        signal = (
            metal*exp(-t*self.metal_decay)*self.metal_amp +
            pn*exp(-t*self.pink_decay)*self.pink_amp +
            wn*t*exp(-t*self.white_decay)*self.white_amp
        )
        result = tanh(signal*velocity)*tanh(t*400)*0.5
        result[1:] += result[:-1]  # Minor low-pass
        return [result, result]


class Kick(Percussion):
    def __init__(self, base_freq=30, freq_decay=60, a=1.8, b=1.2, decay1=5, decay2=3):
        self.base_freq = base_freq
        self.freq_decay = freq_decay
        self.a = a
        self.b = b
        self.decay1 = decay1
        self.decay2 = decay2

    def play(self, velocity):
        t = trange(1.5)
        a = self.a
        b = self.b + velocity * 0.5
        theta = arcsin((1-a) / b)
        signal = -log(a + sin(theta + (exp(-t*self.freq_decay)-1)*self.base_freq)*exp(-t*self.decay1)*b) * exp(-t*self.decay2)
        signal /= -log(a - b)
        signal *= velocity * 0.9
        return [signal, signal]


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

    if name is None or name == "hihat":
        hihat = HiHat().play(1)
        write(path / "hihat.wav", hihat[0])

    if name is None or name == "kick":
        kick = Kick().play(1)
        write(path / "kick.wav", kick[0])
