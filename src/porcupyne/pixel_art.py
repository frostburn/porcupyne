from numpy import sqrt, zeros, ones, arange, meshgrid
from numpy.random import RandomState

X_SCALE = 0.5*sqrt(3)


def offset_meshgrid(height, width):
    y = arange(height, dtype=float)
    x = arange(width, dtype=float) * X_SCALE

    x, y = meshgrid(x, y)
    y[:, 1::2] += 0.5
    return x, y


class OffsetPixels:
    """
    Pixel art that connects like a hex-grid
    """
    def __init__(self, values, size=8):
        self.values = values
        self.size_y = int(round(size))
        self.y_offset = self.size_y // 2
        self.size_x = int(round(X_SCALE*size))
        self.dx = 1.0 / self.size_x
        self.dy = 1.0 / self.size_y

        height, width = values.shape
        self.width = width*self.size_x
        self.height = height*self.size_y + self.y_offset

    def render(self):
        result = zeros((self.height, self.width))
        for j, row in enumerate(self.values):
            for i, value in enumerate(row):
                offset = (i%2) * self.y_offset
                result[
                    j*self.size_y + offset:(j+1)*self.size_y + offset,
                    i*self.size_x:(i+1)*self.size_x
                ] = value
        return result

    def add_to_pixel(self, x, y, value):
        i = int(x * self.dx)
        offset = (i%2) * self.y_offset
        j = int((y - offset) * self.dy)
        if 0 <= i < self.values.shape[1] and 0 <= j < self.values.shape[0]:
            self.values[j, i] += value


class Sparks:
    def __init__(self, num_particles, dt=1, seed=None):
        dims = 2
        self.locations = zeros((num_particles, dims))
        self.velocities = zeros((num_particles, dims))
        self.ages = ones(num_particles) * 1e10
        self.index = 0
        self.dt = dt
        self.drag = 0.95**dt
        self.gravity = -1
        self.random_state = RandomState(seed)

    def emit(self, x, y):
        i = self.index
        self.locations[i] = [x, y]
        self.velocities[i] = self.random_state.randn(2)*2
        self.ages[i] = 0
        self.index = (i + 1) % len(self.ages)

    def step(self):
        self.locations += self.velocities*self.dt
        self.velocities = self.velocities*self.drag
        self.velocities[:,1] += self.gravity*self.dt
        self.velocities += self.random_state.randn(*self.velocities.shape) * 0.05
        self.ages += self.dt


if __name__ == "__main__":
    from pylab import *

    x, y = offset_meshgrid(100, 200)
    x = (x-50)*0.1
    y = (y-50)*0.1
    pxls = OffsetPixels(exp(-x*x - y*y))
    res = pxls.render()
    imsave("/tmp/out.png", res, cmap='afmhot')

    if False:
        # res = OffsetPixels(rand(135, 275)).render()
        # imsave("/tmp/out.png", res[2:-2,2:-3])

        pxls = OffsetPixels(zeros((100, 200)))
        loc = array([700.0, 400.0])
        for _ in range(100000):
            loc += (rand(2) - 0.5)*5
            try:
                pxls.add_to_pixel(loc[0], loc[1], 0.1)
            except:
                break

        res = pxls.render()
        imsave("/tmp/out.png", res, cmap='afmhot')

    if False:
        sparks = Sparks(64)
        for i in range(30):
            for _ in range(3):
                sparks.emit()
            pxls = OffsetPixels(zeros((100, 200)))
            for (x, y), age in zip(sparks.locations, sparks.ages):
                pxls.add_to_pixel(x + 700, y + 400, exp(-0.1*age))
            im = pxls.render()
            imsave("/tmp/sparks/out{:03d}.png".format(i), im, cmap='afmhot')
            sparks.step()
