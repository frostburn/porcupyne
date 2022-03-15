from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    "void sineping(double *samples, size_t num_samples, double delta, double gamma, double amplitude, double phase);"
    "void sinepings(double *samples, size_t num_samples, double *deltas, double *gammas, double *amplitudes, double *phases, size_t num_pings);"
)

ffibuilder.set_source(
    "_routines",
    """
    void sineping(double *samples, size_t num_samples, double delta, double gamma, double amplitude, double phase) {
        double a1 = 2*cos(delta)*gamma;
        double a2 = -gamma*gamma;
        samples[0] = sin(phase) * amplitude;
        samples[1] = sin(phase + delta) * amplitude * gamma;

        for (size_t i = 2; i < num_samples; ++i) {
            samples[i] = a1*samples[i-1] + a2*samples[i-2];
        }
    }

    void sinepings(double *samples, size_t num_samples, double *deltas, double *gammas, double *amplitudes, double *phases, size_t num_pings) {
        double a1, a2, y0, y1, y2;
        for (size_t i = 0; i < num_pings; ++i) {
            a1 = 2*cos(deltas[i])*gammas[i];
            a2 = -gammas[i]*gammas[i];
            y2 = sin(phases[i]) * amplitudes[i];
            y1 = sin(phases[i] + deltas[i]) * amplitudes[i] * gammas[i];
            samples[0] += y2;
            samples[1] += y1;
            for (size_t j = 2; j < num_samples; ++j) {
                y0 = a1*y1 + a2*y2;
                y2 = y1;
                y1 = y0;
                samples[j] += y1;
            }
        }
    }
    """
)

if __name__ == '__main__':
    from pathlib import Path
    path = Path(__file__)
    fpath = path.parent.parent / "src" / "porcupyne" / "_routines.*"
    ffibuilder.compile(target=str(fpath.absolute()), tmpdir="/tmp/", verbose=True)
