import argparse
from pylab import *
import scipy.io.wavfile
from porcupyne.graphics import RESOLUTIONS, make_video_frame
import imageio

parser = argparse.ArgumentParser(description='Render a video of the spectrogram of an audio file')
parser.add_argument('infile', type=str, help='Audio input file name')
parser.add_argument('outfile', type=str, help='Video output file name')
parser.add_argument('--resolution', type=str, default='240p', help='Video resolution')
parser.add_argument('--low', type=float, default=10.0, help='Lowest frequency to plot')
parser.add_argument('--high', type=float, default=3000.0, help='Highest frequency to plot')
parser.add_argument('--increment', type=int, default=4, help='Number of pixels to advance each frame')
parser.add_argument('--framerate', type=int, default=24, help='Video frame rate')
parser.add_argument('--video-quality', type=int, default=10, help='Video quality factor')
parser.add_argument('--exposure', type=float, default=20.0)
args = parser.parse_args()

width, height = RESOLUTIONS[args.resolution]

sample_rate, data = scipy.io.wavfile.read(args.infile)

if len(data.shape) > 1:
    num_channels = data.shape[1]
    if num_channels != 2:
        raise ValueError("Only stereo audio supported")
    left = data[:, 0]
    right = data[:, 1]
else:
    left = data
    right = data

norm = abs(data).max()
left = left / norm
right = right / norm

# Solve for windowing limits
EPSILON = 1e-5
# exp(-tlow**2 * sqrt(args.low)) < EPSILON
# -tlow**2 * sqrt(args.low) < log(EPSILON)
# tlow <> -+sqrt(-log(EPSILON) / sqrt(args.low))
# tlow = -sqrt(-log(EPSILON) / sqrt(args.low))

fspace = linspace(args.low, args.high, height)

windows = []
for f in fspace:
    t_high = sqrt(-log(EPSILON) / sqrt(f))
    n_high = ceil(t_high * sample_rate)
    x = (arange(2*n_high) - n_high) / sample_rate *2*pi
    envelope = exp(-x*x*sqrt(f))
    c = cos(x*f)
    real = c * envelope
    norm = (real * c).sum()
    real /= norm
    imag = sin(x*f) * envelope / norm

    windows.append((real, imag))

delta_t = 1 / args.framerate / args.increment

t_start = -width / 2 * delta_t
window_padding = int(ceil(sqrt(-log(EPSILON) / sqrt(args.low)) * sample_rate))
padding = int(ceil(-t_start * sample_rate)) + window_padding

left = concatenate((zeros(padding, dtype=float), left, zeros(window_padding, dtype=float)))
right = concatenate((zeros(padding, dtype=float), right, zeros(window_padding, dtype=float)))

def columns(data):
    t = t_start

    while True:
        n = int(ceil(t * sample_rate) + padding)
        if n + window_padding >= len(left):
            break
        column = []
        for window in windows:
            l = len(window[0]) // 2
            current_data = data[n - l: n + l]
            real = current_data * window[0]
            imag = current_data * window[1]
            column.append(hypot(real.sum(), imag.sum()))
        yield array(column[::-1])

        t += delta_t

gen_left = columns(left)
gen_right = columns(right)

cols_left = []
cols_right = []

while len(cols_left) + len(cols_right) < width:
    cols_left.append(next(gen_left))
    cols_right.append(next(gen_right))

writer = imageio.get_writer(args.outfile, fps=args.framerate, quality=args.video_quality, macro_block_size=1)
n = 0
while n < float("inf"):
    for _ in range(args.increment):
        try:
            col = next(gen_left)
            cols_left.pop(0)
            cols_left.append(col)
            col = next(gen_right)
            cols_right.pop(0)
            cols_right.append(col)
        except StopIteration:
            n = float("inf")

    frame = transpose(cols_left + cols_right[::-1]) * args.exposure
    fmin = frame.min()
    fmax = frame.max()
    frame = make_video_frame([tanh(sqrt(frame)), tanh(0.9*frame), tanh(0.4*frame**2)])
    writer.append_data(frame)
    n += 1
    print(n, fmin, fmax, frame.max())

writer.close()
