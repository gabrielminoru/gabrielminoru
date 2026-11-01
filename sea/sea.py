import datetime
import math
import random
import sys

cols = 64
rows = 20
cell = 8
frames = 48
frame_time = 0.12
sea_level = 6
max_crest = rows - 6  # keep the top rows for the sun and clouds
cloud_step_time = 0.5
rain_step = 20

# colors blend from calm to storm as the intensity rises
calm = {
    "sky_top": (0x2E, 0x7F, 0xD6),
    "sky_horizon": (0xA8, 0xDB, 0xFF),
    "cloud": (0xFF, 0xFF, 0xFF),
    "surface": (0x3C, 0xB0, 0xE6),
    "deep": (0x00, 0x1A, 0x3D),
}
storm = {
    "sky_top": (0x16, 0x1A, 0x21),
    "sky_horizon": (0x55, 0x5F, 0x6B),
    "cloud": (0x3A, 0x40, 0x4A),
    "surface": (0x4F, 0x7C, 0x94),
    "deep": (0x04, 0x0E, 0x1A),
}
sun_color = "#FFE07A"
foam_color = "#EAF8FF"
rain_color = "#A9BCCF"
label_color = "#EAF8FF"
states = ["glassy", "calm", "choppy", "rough", "stormy"]

today = datetime.date.today().isoformat()
rng = random.Random(today)  # same sea all day, new sea tomorrow
intensity = float(sys.argv[1]) if len(sys.argv) > 1 else rng.random()


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def to_hex(color):
    return "#" + "".join(f"{c:02X}" for c in color)


def palette(name):
    return mix(calm[name], storm[name], intensity)


def make_waves():
    # (wavelength in cells, amplitude in cells, loops per animation, phase)
    # loops are whole numbers so the last frame flows back into the first
    swell = (rng.uniform(30, 50), 0.6 + 3.0 * intensity, 1, rng.uniform(0, 2 * math.pi))
    middle = (rng.uniform(12, 20), 0.3 + 1.5 * intensity, 2, rng.uniform(0, 2 * math.pi))
    chop = (rng.uniform(4, 8), 0.1 + 1.0 * intensity, rng.choice([-4, -3, 3, 4]), rng.uniform(0, 2 * math.pi))
    return [swell, middle, chop]


def surface(waves, x, frame):
    height = sea_level
    for length, amplitude, loops, phase in waves:
        height += amplitude * math.sin(2 * math.pi * (x / length - loops * frame / frames) + phase)
    return min(max(round(height), 2), max_crest)


def foam(heights, x):
    crest = heights[x] - sea_level
    left = heights[max(x - 1, 0)]
    right = heights[min(x + 1, cols - 1)]
    if intensity < 0.25 or crest < 1 or heights[x] < max(left, right):
        return 0
    return 2 if crest >= 3 and intensity > 0.6 else 1


def banded_gradient(name, top, bottom, first_row, last_row):
    stops = []
    bands = last_row - first_row + 1
    for r in range(bands):
        color = to_hex(mix(top, bottom, r / (bands - 1)))
        stops.append(f'<stop offset="{r / bands:.4f}" stop-color="{color}"/>')
        stops.append(f'<stop offset="{(r + 1) / bands:.4f}" stop-color="{color}"/>')
    return (
        f'<linearGradient id="{name}" gradientUnits="userSpaceOnUse" '
        f'x1="0" y1="{first_row * cell}" x2="0" y2="{(last_row + 1) * cell}">' + "".join(stops) + "</linearGradient>"
    )


def animate(attribute, values, duration=frames * frame_time):
    return (
        f'<animate attributeName="{attribute}" values="{";".join(map(str, values))}" '
        f'dur="{duration:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'
    )


def block(x, y, color, w=1, h=1):
    return f'<rect x="{x * cell}" y="{y * cell}" width="{w * cell}" height="{h * cell}" fill="{color}"/>'


def sun():
    if intensity >= 0.6:
        return []
    cx, cy, radius = cols - 10, 3, 2.5
    return [
        block(x, y, sun_color)
        for y in range(rows)
        for x in range(cols)
        if (x - cx) ** 2 + (y - cy) ** 2 <= radius**2
    ]


def make_cloud(x0, y0, color, underside):
    width = rng.randint(5, 10)
    height = rng.randint(2, 3)
    parts = []
    for r in range(height):
        inset = min((height - 1 - r) * rng.randint(1, 2), width // 2 - 1)  # rounder on top
        shade = underside if r == height - 1 else color
        parts.append(block(x0 + inset, y0 + r, shade, w=width - 2 * inset))
    return parts


def clouds():
    color = palette("cloud")
    underside = to_hex(mix(color, (0, 0, 0), 0.15))
    shapes = []
    for i in range(1 + round(intensity * 7)):
        x, y = rng.randrange(cols), rng.randint(0, 4)
        # drawn twice, one screen apart, so the drift wraps around seamlessly
        shapes += make_cloud(x, y, to_hex(color), underside)
        shapes += make_cloud(x + cols, y, to_hex(color), underside)
    offsets = [f"{-i * cell} 0" for i in range(cols)]
    duration = cols * cloud_step_time * (1 - 0.6 * intensity)
    return (
        ["<g>"]
        + shapes
        + [
            f'<animateTransform attributeName="transform" type="translate" values="{";".join(offsets)}" '
            f'dur="{duration:.2f}s" calcMode="discrete" repeatCount="indefinite"/>',
            "</g>",
        ]
    )


def rain():
    if intensity <= 0.55:
        return []
    drops = []
    for i in range(round((intensity - 0.55) * 80)):
        x = rng.randrange(cols) * cell + 3
        start = rng.randrange(rows * cell)
        ys = [(start + f * rain_step) % (rows * cell) for f in range(frames)]
        drops.append(
            f'<rect x="{x}" y="{ys[0]}" width="2" height="6" fill="{rain_color}" opacity="0.7">'
            + animate("y", ys)
            + "</rect>"
        )
    return drops


def lightning():
    if intensity <= 0.8:
        return []
    flash = [0] * frames
    strike = rng.randrange(frames - 3)
    flash[strike], flash[strike + 2] = 0.6, 0.3
    return [
        f'<rect width="{cols * cell}" height="{rows * cell}" fill="#FFFFFF" opacity="0">'
        + animate("opacity", flash)
        + "</rect>"
    ]


def water(heights):
    parts = []
    for x in range(cols):
        tops = [(rows - heights[f][x]) * cell for f in range(frames)]
        foams = [foam(heights[f], x) * cell for f in range(frames)]
        parts.append(
            f'<rect x="{x * cell}" y="{tops[0]}" width="{cell}" height="{rows * cell}" fill="url(#depth)">'
            + animate("y", tops)
            + "</rect>"
        )
        if any(foams):
            parts.append(
                f'<rect x="{x * cell}" y="{tops[0]}" width="{cell}" height="{foams[0]}" fill="{foam_color}">'
                + animate("y", tops)
                + animate("height", foams)
                + "</rect>"
            )
    return parts


def render():
    waves = make_waves()
    heights = [[surface(waves, x, f) for x in range(cols)] for f in range(frames)]
    width = cols * cell
    height = rows * cell
    state = states[min(int(intensity * len(states)), len(states) - 1)]
    sky = banded_gradient("sky", palette("sky_top"), palette("sky_horizon"), 0, rows - 1)
    depth = banded_gradient("depth", palette("surface"), palette("deep"), rows - sea_level - 2, rows - 1)

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" shape-rendering="crispEdges">',
            f"<defs>{sky}{depth}</defs>",
            f'<rect width="{width}" height="{height}" fill="url(#sky)"/>',
        ]
        + sun()
        + rain()
        + clouds()
        + lightning()
        + water(heights)
        + [
            f'<text x="4" y="{height - 4}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
            f'font-size="9" fill="{label_color}" opacity="0.8">sea state: {state} · {today}</text>',
            "</svg>",
        ]
    )


with open("sea.svg", "w") as f:
    f.write(render())
