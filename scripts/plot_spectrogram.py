import argparse
from pylab import *
import scipy.io.wavfile

parser = argparse.ArgumentParser(description='Plot the spectrogram of an audio file')
parser.add_argument('infile', type=str, help='Audio input file name')
parser.add_argument('--xres', type=int, default=200)
parser.add_argument('--yres', type=int, default=200)
parser.add_argument('--low', type=float, default=15.0)
parser.add_argument('--high', type=float, default=1000.0)
args = parser.parse_args()

sample_rate, data = scipy.io.wavfile.read(args.infile)

data = data / abs(data).max()

t = arange(len(data)) / sample_rate

columns = []

fspace = linspace(args.low, args.high, args.yres)

tmin = -0.025
tmax = t.max() + 0.25
for t0 in linspace(tmin, tmax, args.xres):
    column = []
    x = (t-t0)*2*pi
    for f in fspace:
        env = exp(-x*x*sqrt(f))
        real = (cos(x*f) * env * data).sum()
        imag = (sin(x*f) * env * data).sum()
        mag = sqrt(real*real + imag*imag) * f / args.low / args.xres
        column.append(mag)
    columns.append(column)

imshow(array(columns).T[::-1], extent=(tmin, tmax, args.low, args.high), aspect='auto')
show()
