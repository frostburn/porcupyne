from numpy import tanh, arange, interp, log, exp, array, sin, arcsin, pi, ceil, sqrt, maximum
from numpy.random import rand
from .audio import trange, softsaw, merge_stereo, integrate, EPSILON, sine, cosine
#pylint: disable=invalid-name, too-few-public-methods


def vary_frequency(freq, duration, cents, var_freq, lattice_variation=0.15):
    """
    Create a wavering phase signal
    """
    num_ctrl_points = int(round(duration / var_freq)) + 2
    xp = arange(num_ctrl_points) + (rand(num_ctrl_points)*2-1)*lattice_variation
    fp = rand(num_ctrl_points)*2-1

    t = trange(duration)
    pitch_bend = interp(t, xp, fp) * cents / 1200 * log(2)
    return integrate(freq*exp(pitch_bend))


def ar_tanh(t, duration, attack, decay):
    return tanh(t/attack)*tanh((duration - t)/decay)


class Instrument:
    def __init__(self):
        pass

    def play(self, note):
        pass


class AROsc(Instrument):
    def __init__(self, waveform=cosine, attack=0.1, decay=0.2):
        self.waveform = waveform
        self.attack = attack
        self.decay = decay

    def play(self, note):
        dur = float(note.duration)
        t = trange(dur)
        env = ar_tanh(t, dur, self.attack, self.decay) * note.velocity
        signal = self.waveform(t*note.freq + note.rads/(2*pi))
        result = env*signal
        return array([result, result])  # Convert to stereo


class Strings(Instrument):
    def __init__(self, sharpness=0.7, freq_spread=10, var_freq=1, attack=0.5, decay=0.5, voice_stacking=5):
        super().__init__()
        self.sharpness = sharpness
        self.freq_spread = freq_spread
        self.var_freq = var_freq
        self.attack = attack
        self.decay = decay
        self.voice_stacking = voice_stacking

    def play(self, note):
        dur = float(note.duration)
        t = trange(dur)
        env = ar_tanh(t, dur, self.attack, self.decay) / self.voice_stacking * note.velocity
        channels = []
        for _ in range(2):
            result = 0
            for _ in range(self.voice_stacking):
                phase = vary_frequency(note.freq, dur, self.freq_spread, self.var_freq)
                result = result + softsaw(phase, self.sharpness*(1 - note.velocity*0.1))
            channels.append(env*result)
        return array(channels)


class Ping(Instrument):
    """
    Decent FM string pluck or bell depending on the modulation indices.
    """

    def __init__(self, carrier_index=1, modulation_index=2, attack=0.002, decay=0.5, tri_decay=0.5, tri_sharpness=0.99, mod_sharpness=1.2, separation=6):
        super().__init__()
        self.carrier_index = carrier_index
        self.modulation_index = modulation_index
        self.attack = attack
        self.decay = decay
        self.tri_decay = tri_decay
        self.tri_sharpness = tri_sharpness
        self.mod_sharpness = mod_sharpness
        self.separation = separation

    def play(self, note):
        dur = -log(EPSILON) * self.decay
        t = trange(dur)
        envelope = exp(-t/self.decay) * tanh(t/self.attack)

        tri_envelope = exp(-t/self.tri_decay) * self.tri_sharpness

        phase = 2*pi*note.freq*t
        mod_phase = phase*self.modulation_index
        carrier_phase = phase*self.carrier_index

        separator = t*self.separation

        modulator = arcsin(sin(mod_phase + separator) * tri_envelope) * self.mod_sharpness
        left = sin(carrier_phase + modulator) * envelope

        modulator = arcsin(sin(mod_phase - separator) * tri_envelope) * self.mod_sharpness
        right = sin(carrier_phase + modulator) * envelope

        return array((left, right))


class Shepard(Instrument):
    """
    Shepard tones with gaussian octave envelope.
    """

    def __init__(self, waveform=sine, falloff=0.5, base_freq=440, attack=0.05, decay=0.05):
        super().__init__()
        self.waveform = sine
        self.falloff = falloff
        self.base_freq = base_freq
        self.attack = attack
        self.decay = decay

        norm = 0
        for i in self.component_range():
            norm += exp(-(i*self.falloff)**2)
        self.i_norm = 1 / norm

    def component_range(self):
        limit = int(ceil(sqrt(-log(EPSILON))/self.falloff))
        return range(-limit, limit+1)

    def play(self, note):
        duration = float(note.duration)
        dur = duration - log(EPSILON) * self.decay
        t = trange(dur)
        envelope = tanh(t/self.attack) * exp(-maximum(0, t - duration)/self.decay)

        freq = exp(log(float(note.freq) / self.base_freq)%log(2)) * self.base_freq
        wave = 0
        for i in self.component_range():
            phase = t * freq * 2**i
            wave += exp(-(i*self.falloff)**2) * self.waveform(phase)
        signal = envelope * wave * self.i_norm * float(note.velocity)
        return array((signal, signal))


def render_notes(notes, instrument):
    samples = []
    for note in notes:
        samples.append((instrument.play(note), float(note.time)))
    return merge_stereo(*samples)
