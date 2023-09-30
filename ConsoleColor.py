def set_fg_color(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"


def set_bg_color(r, g, b):
    return f"\x1b[48;2;{r};{g};{b}m"


def gradient(sr, sg, sb, er, eg, eb, steps, n):
    dr = (er - sr) / steps
    dg = (eg - sg) / steps
    db = (eb - sb) / steps
    return (sr + int(dr * n), sg + int(dg * n), sb + int(db * n))


def gradient2d(sr, sg, sb, exr, exg, exb, eyr, eyg, eyb, steps_x, steps_y, x, y):
    dxr = (exr - sr) // steps_x
    dxg = (exg - sg) // steps_x
    dxb = (exb - sb) // steps_x
    dyr = (eyr - sr) // steps_y
    dyg = (eyg - sg) // steps_y
    dyb = (eyb - sb) // steps_y

    return (
        sr + ((dxr * x) + (dyr * y)) // 2,
        sg + ((dxg * x) + (dyg * y)) // 2,
        sb + ((dxb * x) + (dyb * y)) // 2,
    )


def test():
    steps = 100
    black_color_code = set_bg_color(0, 0, 0)
    for i in range(steps):
        color = gradient(255, 0, 0, 0, 0, 255, steps, i)
        color_code = set_bg_color(color[0], color[1], color[2])
        print(f"{color_code} ", end="")
    print(f"{black_color_code}")


def test2d():
    xsteps = 200
    ysteps = 30
    black_color_code = set_bg_color(0, 0, 0)
    for y in range(ysteps):
        for x in range(xsteps):
            color = gradient2d(255, 0, 0, 0, 255, 0, 0, 0, 255, xsteps, ysteps, x, y)
            color_code = set_bg_color(color[0], color[1], color[2])
            print(f"{color_code} ", end="")
        print(f"{black_color_code}")


if __name__ == "__main__":
    test()
    #test2d()
