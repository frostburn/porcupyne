from numpy import logical_and, logical_or, linspace, meshgrid


def meantone(L=2, s=1, octaves=1):
    L = (0,) + (1,) * (L - 1)
    s = (0,) + (1,) * (s - 1)
    return (L + L + s + L + L + L + s) * octaves


def mavila(L=2, s=1, octaves=1):
    L = (0,) + (1,) * (L - 1)
    s = (0,) + (1,) * (s - 1)
    return (s + s + L + s + s + s + L) * octaves


def orgone(L=2, s=1, octaves=1):
    L = (0,) + (1,) * (L - 1)
    s = (0,) + (1,) * (s - 1)
    return (L + s + L + s + L + s + L) * octaves


def keyboard_masks(key_indices, x, y):
    bounding_box = logical_and(y < 0, y > -1)
    black_bounding_box = logical_and(y < 0, y > -0.5)

    white_gaps = []

    num_covered = 0
    last_exposed = None
    for i in range(len(key_indices)-1):
        if key_indices[i] == 0 and key_indices[i+1] == 0:
            midpoint = 0.5*(i + i+1)
            white_gaps.append(midpoint)
            if last_exposed is not None:
                for j in range(num_covered):
                    white_gaps.append(last_exposed +  (j+1)*(midpoint - last_exposed) / (num_covered + 1))
                num_covered = 0
            elif num_covered:
                for j in range(num_covered):
                    white_gaps.append(midpoint - 2 - j)
                num_covered = 0
            last_exposed = midpoint
        elif key_indices[i] == 0:
            num_covered += 1
    white_gaps.sort()
    if num_covered:
        if white_gaps:
            last_gap = white_gaps[-1] - white_gaps[-2]
            for j in range(num_covered):
                white_gaps.append(last_exposed + (1+j) * last_gap)
        else:
            last = None
            for i, index in enumerate(key_indices):
                if index == 0:
                    if last is not None:
                        midpoint = 0.5*(i + last)
                        white_gaps.append(midpoint)
                    last = i

    white_gaps.append(2*white_gaps[-1] - white_gaps[-2])
    white_gaps.insert(0, white_gaps[1] - 2*white_gaps[0])

    white_masks = []
    for i in range(len(white_gaps) - 1):
        left = white_gaps[i]
        right = white_gaps[i+1]
        mask = logical_and(x > left + 0.1, x < right - 0.1)
        mask[~bounding_box] = 0
        white_masks.append(mask)

    black_gaps = []
    for i in range(len(key_indices)-1):
        if key_indices[i] == 1 and key_indices[i+1] == 1:
            midpoint = 0.5*(i + i+1)
            black_gaps.append(midpoint)

    black_anti_mask = (0*x > 1)
    for gap in black_gaps:
        mask = abs(x - gap) < 0.1
        black_anti_mask = logical_or(black_anti_mask, mask)

    black_mask = 0*x
    black_masks = []
    for i, index in enumerate(key_indices):
        if index == 1:
            mask = abs(x - i) < 0.5
            mask[~black_bounding_box] = 0
            mask[black_anti_mask] = 0
            black_masks.append(mask)
            black_mask = logical_or(black_mask, mask)

    for mask in white_masks:
        mask[black_mask] = 0

    result = []
    for index in key_indices:
        if index == 0:
            result.append(white_masks.pop(0))
        else:
            result.append(black_masks.pop(0))
    return result


def piano_holes(x, y, t, aspect, time_scale, notes, border=0.1, margin=0.1):
    holes = 0*x
    for note in notes:
        time = (note.time - t) * time_scale
        off_time = (note.off_time - t) * time_scale
        holes += logical_and(
            logical_and(x > note.pitch + margin - 0.5, x < note.pitch - margin + 0.5),
            logical_and(y > time, y < off_time)
        ) * 0.5
        holes += logical_and(
            logical_and(x > note.pitch + margin + border - 0.5, x < note.pitch - margin - border + 0.5),
            logical_and(y > time + border * aspect, y < off_time - border * aspect)
        ) * 0.5

    return holes


if __name__ == "__main__":
    from .graphics import make_picture_frame
    from pylab import imsave

    x = linspace(-1, 30, 1920)
    y = linspace(2, -1, 1080)
    x, y = meshgrid(x, y)

    indices = orgone(octaves=2)

    masks = keyboard_masks(indices, x, y)

    res = 0.3 + 0*x
    for index, mask in zip(indices, masks):
        if index == 0:
            res += mask*0.65
        else:
            res -= mask*0.25

    res = [res, res, res]
    im = make_picture_frame(res)
    imsave("/tmp/out.png", im)
