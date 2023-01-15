#!/usr/bin/env python3

# force_16_palette
# this script generates a 256 palette based on the terminal's 16 colors
# this forces terminal apps to respect my theme

import os
import random
import math
import sys

BLACK         = 0
RED           = 1
GREEN         = 2
YELLOW        = 3
BLUE          = 4
PURPLE        = 5
CYAN          = 6
WHITE         = 7
BRIGHT_BLACK  = 8
BRIGHT_RED    = 9
BRIGHT_GREEN  = 10
BRIGHT_YELLOW = 11
BRIGHT_BLUE   = 12
BRIGHT_PURPLE = 13
BRIGHT_CYAN   = 14
BRIGHT_WHITE  = 15

def hexToRgb(hex):
    return (
        (hex & 0xff0000) >> 16,
        (hex & 0x00ff00) >> 8,
        (hex & 0x0000ff)
    )

class Color:
    def ansiBg(self):
        raise NotImplementedError()

    def ansiFg(self):
        raise NotImplementedError()

class ColorRGB(Color):
    def __init__(self, *args):
        if len(args) == 3:
            self.rgb = tuple(int(a) for a in args)
            return
        if len(args) != 1:
            raise ValueError()
        val = args[0]
        if isinstance(val, int):
            self.rgb = hexToRgb(val)
        elif isinstance(val, str):
            if val.startswith("#"):
                val = val[1:]
            self.rgb = hexToRgb(int(val, base=16))
        elif isinstance(val, tuple) or isinstance(val, list):
            self.rgb = (val[0], val[1], val[2])
        else:
            raise ValueError()

    def ansiBg(self):
        return "\x1b[48;2;%d;%d;%dm" % self.rgb

    def ansiFg(self):
        return "\x1b[38;2;%d;%d;%dm" % self.rgb

    def toHexString(self):
        return '#%02x%02x%02x' % self.rgb

    def mix(self, color, p):
        p2 = 1.0 - p
        return ColorRGB(
            int(self.rgb[0] * p2 + color.rgb[0] * p),
            int(self.rgb[1] * p2 + color.rgb[1] * p),
            int(self.rgb[2] * p2 + color.rgb[2] * p)
        )

class Color256(Color):
    def __init__(self, idx):
        self.idx = idx

    def ansiBg(self):
        return "\x1b[48;5;%dm" % self.idx

    def ansiFg(self):
        return "\x1b[38;5;%dm" % self.idx

def baseline256ToRgb(n):
    if n > 255:
        raise ValueError("Out of bounds")

    if n < 16:
        return BASELINE_COLORS[n]

    if n >= 232:
        n -= 232
        val = 8 + n * 10 if n else 8
        return ColorRGB(val, val, val)

    n -= 16
    rgb = (n // 36, (n // 6) % 6, n % 6)
    rgb = tuple((55 + v * 40 if v else 0) for v in rgb)
    return ColorRGB(rgb)


def custom256ToRgb(n):
    if n > 255:
        raise ValueError("Out of bounds")

    if n < 16:
        return COLORS[n]

    if n >= 232:
        color = BG.mix(COLORS[BRIGHT_WHITE], (n - 232) / 24)
        return ColorRGB(tuple(
            min(255, int(color.rgb[i] * GADIENT_HUE_SHIFT[i]))
            for i in range(3)
        ))

    n -= 16
    r, g, b = (n // 36, (n // 6) % 6, n % 6)

    cyan = min(g, b)
    purple = min(r, b)
    yellow = min(r, g)
    red = r - max(purple, yellow)
    blue = b - max(purple, cyan)
    green = g - max(cyan, yellow)

    vals = [0, red, green, yellow, blue, purple, cyan]
    closestColor = WHITE
    for color in [RED, GREEN, YELLOW, BLUE, PURPLE, CYAN]:
        if max(vals) == vals[color] and vals.count(vals[color]) <= 2:
            closestColor = color
            break
    return COLORS[closestColor + 8 if (max(vals) > 3) else closestColor]

def print256Cell(idx, method):
    color = method(idx)
    print(color.ansiBg() + str(idx).rjust(4) + " ", end="")

def preview256Base16(approaches):
    for approach, method in approaches.items():
        print("%s:" % approach)
        for i in range(2):
            for j in range(8):
                print256Cell(i * 8 + j, method)
            print("\x1b[0m")
        print()

def preview256RGB(approaches):
    for approach in approaches:
        print(("%s:" % approach).ljust(34), end="")

    print()

    for i in range(36):
        for j, method in enumerate(approaches.values()):
            for k in range(6):
                print256Cell(16 + i * 6 + k, method)
            if j == len(approaches) - 1:
                print("\x1b[0m")
            else:
                print("\x1b[0m    ", end="")

def preview256GreyGradient(approaches):
    for approach, method in approaches.items():
        print("\n%s:" % approach)
        for i in range(24):
            print256Cell(232 + i, method)
        print("\x1b[0m")

def preview256Colors():
    approaches = {
        "Current": Color256,
        "Baseline": baseline256ToRgb,
        "Custom": custom256ToRgb
    }
    preview256Base16(approaches)
    preview256RGB(approaches)
    preview256GreyGradient(approaches)

def generateKitty():
    for i in range(16, 256):
        color = custom256ToRgb(i)
        print("color%d %s" % (i, color.toHexString()))

def usage(name):
    print("%s OPTION" % name)
    print()
    print("OPTIONS:")
    print("    --generate-kitty")
    print("    --preview")


# terminal background color
# this is used for the 24 grey gradient
BG = ColorRGB(0x252932)

# color shift for the 24 grey gradient
# i perfer my greys slightly blue, so it is shifted 10% on the blue
GADIENT_HUE_SHIFT = (1.0, 1.0, 1.1)

# terminal color palette which the 256 is built from
# bright white is used for the end of the 24 grey gradient
COLORS = [
    ColorRGB(0x000000),  # black
    ColorRGB(0xe06c75),  # red
    ColorRGB(0x88B369),  # green
    ColorRGB(0xD19A66),  # yellow
    ColorRGB(0x61afef),  # blue
    ColorRGB(0xB663CC),  # purple
    ColorRGB(0x56b6c2),  # cyan
    ColorRGB(0xb3b3c3),  # white
    ColorRGB(0x000000),  # bright black
    ColorRGB(0xe0878e),  # bright red
    ColorRGB(0x8dc464),  # bright green
    ColorRGB(0xe5c07b),  # bright yellow
    ColorRGB(0xa0c8ff),  # bright blue
    ColorRGB(0xd58ee8),  # bright purple
    ColorRGB(0x77d5e0),  # bright cyan
    ColorRGB(0xf1f1ef)   # bright white
]

# generic baseline colors for comparison
BASELINE_COLORS = [
    ColorRGB(0x000000),  # black
    ColorRGB(0xcc2222),  # red
    ColorRGB(0x22cc22),  # green
    ColorRGB(0xcccc22),  # yellow
    ColorRGB(0x2222cc),  # blue
    ColorRGB(0xcc22cc),  # purple
    ColorRGB(0x22cccc),  # cyan
    ColorRGB(0xcccccc),  # white
    ColorRGB(0x404040),  # bright black
    ColorRGB(0xee1111),  # bright red
    ColorRGB(0x11ee11),  # bright green
    ColorRGB(0xeeee11),  # bright yellow
    ColorRGB(0x1111ee),  # bright blue
    ColorRGB(0xee11ee),  # bright purple
    ColorRGB(0x11eeee),  # bright cyan
    ColorRGB(0xeeeeee),  # bright white
]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage(sys.argv[0])
        exit(1)

    if (sys.argv[1]) == "--preview":
        preview256Colors()
    elif (sys.argv[1] == "--generate-kitty"):
        generateKitty()
    else:
        usage(sys.argv[0])
        exit(1)
