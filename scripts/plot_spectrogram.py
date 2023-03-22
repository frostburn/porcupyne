import argparse
from pylab import *
import scipy.io.wavfile

parser = argparse.ArgumentParser(description='Plot the spectrogram of an audio file')
parser.add_argument('infile', type=str, help='Audio input file name')
parser.add_argument('--xres', type=int, default=200)
parser.add_argument('--yres', type=int, default=200)
parser.add_argument('--low', type=float, default=15.0)
parser.add_argument('--high', type=float, default=1000.0)
parser.add_argument('--tlow', type=float, default=-0.05)
parser.add_argument('--thigh', type=float)
parser.add_argument('--channel', type=str, default="mixed")
args = parser.parse_args()

sample_rate, data = scipy.io.wavfile.read(args.infile)

if len(data.shape) > 1:
    if args.channel != "mixed":
        raise ValueError("Unsupported channel mode")
    data = data.sum(axis=1)

data = data / abs(data).max()

t = arange(len(data)) / sample_rate

columns = []

fspace = linspace(args.low, args.high, args.yres)

tmin = args.tlow
if args.thigh is None:
    tmax = t.max() + 0.05
else:
    tmax = args.thigh
for t0 in linspace(tmin, tmax, args.xres):
    column = []
    x = (t-t0)*2*pi
    for f in fspace:
        windowed = exp(-x*x*sqrt(f)) * data
        real = (cos(x*f) * windowed).sum()
        imag = (sin(x*f) * windowed).sum()
        mag = sqrt(real*real + imag*imag) / args.low / args.xres
        column.append(mag)
    columns.append(column)

imshow(array(columns).T[::-1], extent=(tmin, tmax, args.low, args.high), aspect='auto')
show()
