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
horizon = rows - sea_level
cloud_step_time = 0.5
rain_step = 20
lunar_month = 29.530588
new_moon = datetime.datetime(2000, 1, 6, 18, 14, tzinfo=datetime.timezone.utc)

# clear-weather sky through the day, as (hour, top color, horizon color)
night = ((0x0A, 0x0F, 0x24), (0x1C, 0x27, 0x4A))
dawn = ((0x3B, 0x4C, 0x8F), (0xF4, 0xA7, 0x6A))
day = ((0x2E, 0x7F, 0xD6), (0xA8, 0xDB, 0xFF))
dusk = ((0x2D, 0x2A, 0x6B), (0xF0, 0x7B, 0x4F))
sky_by_hour = [(0, *night), (4.5, *night), (6, *dawn), (7.5, *day), (16.5, *day), (18, *dusk), (19.5, *night), (24, *night)]
storm_day = ((0x16, 0x1A, 0x21), (0x55, 0x5F, 0x6B))
storm_night = ((0x06, 0x08, 0x0D), (0x18, 0x1C, 0x24))

# colors blend from calm to storm as the intensity rises
calm = {
    "cloud": (0xFF, 0xFF, 0xFF),
    "surface": (0x3C, 0xB0, 0xE6),
    "deep": (0x00, 0x1A, 0x3D),
}
storm = {
    "cloud": (0x3A, 0x40, 0x4A),
    "surface": (0x4F, 0x7C, 0x94),
    "deep": (0x04, 0x0E, 0x1A),
}
sun_color = (0xFF, 0xE0, 0x7A)
low_sun_color = (0xFF, 0x8A, 0x3D)
moon_color = "#E9E6D3"
foam_color = (0xEA, 0xF8, 0xFF)
rain_color = "#A9BCCF"
label_color = "#EAF8FF"
states = ["glassy", "calm", "choppy", "rough", "stormy"]

brt = datetime.timezone(datetime.timedelta(hours=-3), "BRT")
now = datetime.datetime.now(brt)
today = now.date().isoformat()
rng = random.Random(today)  # same sea all day, new sea tomorrow
intensity = float(sys.argv[1]) if len(sys.argv) > 1 else rng.random()
hour = float(sys.argv[2]) if len(sys.argv) > 2 else now.hour + now.minute / 60


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def to_hex(color):
    return "#" + "".join(f"{c:02X}" for c in color)


def palette(name):
    return mix(calm[name], storm[name], intensity)


def elevation(h):
    # 1 at the top of its arc, 0 on the horizon, negative below it
    return math.sin(math.pi * (h - 6) / 12)


daylight = min(max((elevation(hour) + 0.15) / 0.45, 0), 1)
light = 0.3 + 0.7 * daylight


def sky_colors():
    for (h0, top0, bottom0), (h1, top1, bottom1) in zip(sky_by_hour, sky_by_hour[1:]):
        if h0 <= hour <= h1:
            t = (hour - h0) / (h1 - h0)
            top, bottom = mix(top0, top1, t), mix(bottom0, bottom1, t)
            break
    storm_top = mix(storm_night[0], storm_day[0], daylight)
    storm_bottom = mix(storm_night[1], storm_day[1], daylight)
    return mix(top, storm_top, intensity), mix(bottom, storm_bottom, intensity)


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


def disc(cx, cy, color, lit=lambda nx, ny: True, radius=2.5):
    cx, cy = round(cx), round(cy)  # centered on a cell so the disc stays round
    return [
        block(x, y, color)
        for y in range(round(cy - radius), round(cy + radius) + 1)
        for x in range(round(cx - radius), round(cx + radius) + 1)
        if (x - cx) ** 2 + (y - cy) ** 2 <= radius**2 and lit((x - cx) / radius, (y - cy) / radius)
    ]


def arc(h):
    # crosses the sky left to right in 12 hours, rising from and setting into the sea
    return cols * (h % 24 - 6) / 12, horizon - (horizon - 3) * elevation(h)


def sun():
    if intensity >= 0.6 or elevation(hour) < -0.15:
        return []
    color = mix(low_sun_color, sun_color, min(max(elevation(hour) * 3, 0), 1))
    return disc(*arc(hour), to_hex(color))


def moon():
    moon_hour = hour + 12  # rises around sunset, sets around sunrise
    if intensity >= 0.6 or elevation(moon_hour) < -0.15:
        return []
    phase = (now - new_moon).total_seconds() / 86400 % lunar_month / lunar_month

    def lit(nx, ny):
        terminator = math.cos(2 * math.pi * phase) * math.sqrt(max(1 - ny**2, 0))
        side = -nx  # seen from the southern hemisphere, the moon waxes on the left
        return side > terminator if phase < 0.5 else side < -terminator

    return disc(*arc(moon_hour), moon_color, lit)


def stars():
    if daylight >= 0.6:
        return []
    star_rng = random.Random(today + "stars")  # own generator so the hour doesn't move the clouds
    brightness = (1 - daylight / 0.6) * (1 - intensity)
    parts = []
    for i in range(round(50 * (1 - intensity))):
        x = star_rng.randrange(cols * cell)
        y = star_rng.randrange((horizon - 1) * cell)
        twinkle = [round(brightness, 2)] * frames
        twinkle[star_rng.randrange(frames)] = round(brightness * 0.3, 2)
        parts.append(
            f'<rect x="{x}" y="{y}" width="2" height="2" fill="#FFFFFF" opacity="{twinkle[0]}">'
            + animate("opacity", twinkle)
            + "</rect>"
        )
    return parts


def make_cloud(x0, y0, color, underside):
    width = rng.randint(5, 10)
    height = rng.randint(2, 3)
    parts = []
    for r in range(height):
        inset = min((height - 1 - r) * rng.randint(1, 2), width // 2 - 1)  # rounder on top
        shade = underside if r == height - 1 else color
        parts.append(block(x0 + inset, y0 + r, shade, w=width - 2 * inset))
    return parts


def clouds(sky_horizon):
    color = mix(mix((0, 0, 0), palette("cloud"), light), sky_horizon, 0.25)
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
    crest_color = to_hex(mix((0, 0, 0), foam_color, 0.5 + 0.5 * daylight))
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
                f'<rect x="{x * cell}" y="{tops[0]}" width="{cell}" height="{foams[0]}" fill="{crest_color}">'
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
    clock = f"{int(hour) % 24:02d}:{int(hour % 1 * 60):02d}"
    sky_top, sky_horizon = sky_colors()
    sky = banded_gradient("sky", sky_top, sky_horizon, 0, rows - 1)
    surface_color = mix((0, 0, 0), palette("surface"), light)
    deep_color = mix((0, 0, 0), palette("deep"), light)
    depth = banded_gradient("depth", surface_color, deep_color, horizon - 2, rows - 1)

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" shape-rendering="crispEdges">',
            f"<defs>{sky}{depth}</defs>",
            f'<rect width="{width}" height="{height}" fill="url(#sky)"/>',
        ]
        + stars()
        + sun()
        + moon()
        + rain()
        + clouds(sky_horizon)
        + lightning()
        + water(heights)
        + [
            f'<text x="4" y="{height - 4}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
            f'font-size="9" fill="{label_color}" opacity="0.8">sea state: {state} · {today} {clock} BRT</text>',
            "</svg>",
        ]
    )


with open("sea.svg", "w") as f:
    f.write(render())
