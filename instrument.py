from numpy import tanh, arange, interp, log, exp, array, sin, arcsin, pi
from numpy.random import rand
from audio import trange, softsaw, merge_stereo, integrate, EPSILON
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


class Instrument:
    def __init__(self):
        pass

    def play(self, note):
        pass


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
        env = tanh(t/self.attack)*tanh((dur-t)/self.decay) / self.voice_stacking
        channels = []
        for _ in range(2):
            result = 0
            for _ in range(self.voice_stacking):
                phase = vary_frequency(note.freq, dur, self.freq_spread, self.var_freq)
                result = result + softsaw(phase, self.sharpness)
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


def render_notes(notess, instrument):
    samples = []
    for notes in notess:
        if not isinstance(notes, list):
            notes = [notes]
        for note in notes:
            samples.append((instrument.play(note), note.time))
    return merge_stereo(*samples)
