#!/usr/bin/env python3
"""Export termite's built-in calm set (modes 38-67) as standalone
marketplace shaders — each becomes a user-shader .metal implementing
termite_main, forkable and hot-reloadable.

Usage: tools/export-calm-set.py <path-to-term64>/Renderer/Sources/TermiteGPU/Shaders.metal
Writes shaders/termite/<stem>.metal and prints registry entries JSON.
"""
import json
import re
import sys
from pathlib import Path

# mode -> (stem, Name, description) — descriptions mirror the in-file catalog.
CALM = {
    38: ("drift", "Drift", "a dual-tone color field slowly folding over itself"),
    39: ("breath", "Breath", "the background inhales on an 8s cycle; idling deepens it"),
    40: ("lagoon", "Lagoon", "teal caustic light webs, pool-floor slow"),
    41: ("silk", "Silk", "translucent ribbons swaying, dusty violet"),
    42: ("ember", "Ember", "sparse warm motes rising and winking out"),
    43: ("fireflies", "Fireflies", "wandering green-gold points, soft blinking"),
    44: ("clouds", "Clouds", "a pale cloud bank crossing at stratus pace"),
    45: ("mist", "Mist", "ground fog breathing along the bottom"),
    46: ("deep", "Deep", "abyssal gradient; a faint sonar ring every nine seconds"),
    47: ("tide", "Tide", "a waterline breathing at two-thirds height, foam whisper"),
    48: ("zen", "Zen", "raked sand rings around two slowly orbiting stones"),
    49: ("lanterns", "Lanterns", "five paper lanterns climbing on staggered loops"),
    50: ("snowfall", "Snowfall", "three parallax layers of unhurried flakes"),
    51: ("petals", "Petals", "pink petals drifting down-wind with a sway"),
    52: ("koi", "Koi", "three blurred koi gliding under frosted ice"),
    53: ("moss", "Moss", "green mottle creeping at lichen speed"),
    54: ("dunes", "Dunes", "layered dune silhouettes, crest light, sand haze"),
    55: ("horizon", "Horizon", "a dawn gradient whose mood shifts over three minutes"),
    56: ("rainfall", "Rainfall", "rain trails sliding down window glass"),
    57: ("nebula", "Nebula", "slow-turning gas in magenta and indigo, dim stars"),
    58: ("comet", "Comet", "every ~17s one soft comet crosses the upper sky"),
    59: ("meadow", "Meadow", "green ground glow + pollen adrift"),
    60: ("ink", "Ink", "ink blots blooming and dissolving in water"),
    61: ("marble", "Marble", "fine veins wandering through warped stone"),
    62: ("prism", "Prism", "one faint light shaft, spectrum-fringed, slowly swinging"),
    63: ("halo", "Halo", "a breathing glow that follows the cursor"),
    64: ("waterline", "Waterline", "the scene reflects in water along the bottom edge"),
    65: ("slowscan", "Slowscan", "a luminous band sweeps down every twelve seconds"),
    66: ("voronoi", "Voronoi", "drifting cells, edges barely glowing"),
    67: ("eclipse", "Eclipse", "a dark disc with a breathing corona, upper right"),
}

NOISE_HELPERS = """\
// Value noise + 3-octave fbm (the built-in helpers cover hash/palette/mask;
// organic fields bring their own noise).
static float termite_vnoise(float2 p) {
    float2 i = floor(p), f = fract(p);
    float2 s = f * f * (3.0 - 2.0 * f);
    float a = termite_hash(i);
    float b = termite_hash(i + float2(1.0, 0.0));
    float c = termite_hash(i + float2(0.0, 1.0));
    float d = termite_hash(i + float2(1.0, 1.0));
    return mix(mix(a, b, s.x), mix(c, d, s.x), s.y);
}
static float termite_fbm(float2 p) {
    float v = 0.0, amp = 0.5;
    for (int i = 0; i < 3; i++) {
        v += termite_vnoise(p) * amp;
        p = p * 2.03 + 17.31;
        amp *= 0.5;
    }
    return v;
}

"""

TEMPLATE = """\
// {name} — {desc}.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/{stem}

{helpers}float4 termite_main(float2 uv, float4 sceneColor,
                    constant TermiteUniforms &u,
                    texture2d<float> scene, sampler smp) {{
    float3 rgb = sceneColor.rgb;
    float aspect = u.resolution.x / u.resolution.y;
    float2 sq = (uv - 0.5) * float2(aspect, 1.0);
    float2 pp = uv * u.resolution;
    float mask = termite_textMask(rgb, u.background.rgb);
    float3 fx = float3(0.0);
    (void)pp;

{body}
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}}
"""


def extract_mode_blocks(source: str) -> dict:
    """Pull the body of every `if (mode == N) { ... }` via brace matching."""
    blocks = {}
    for m in re.finditer(r"if \(mode == (\d+)\) \{", source):
        mode = int(m.group(1))
        if mode not in CALM:
            continue
        depth = 1
        i = m.end()
        while depth > 0:
            if source[i] == "{":
                depth += 1
            elif source[i] == "}":
                depth -= 1
            i += 1
        blocks[mode] = source[m.end():i - 1].rstrip()
    return blocks


def main():
    metal_path = Path(sys.argv[1])
    source = metal_path.read_text()
    out_dir = Path(__file__).resolve().parent.parent / "shaders" / "termite"
    out_dir.mkdir(parents=True, exist_ok=True)

    blocks = extract_mode_blocks(source)
    entries = []
    for mode, (stem, name, desc) in sorted(CALM.items()):
        body = blocks[mode]
        # De-indent from the pack's nesting (12 spaces) to function level (4).
        lines = [l[8:] if l.startswith(" " * 8) else l for l in body.splitlines()]
        body = "\n".join(lines)
        # Built-in helper names -> user-shader helper names.
        body = body.replace("t64_hash", "termite_hash")
        body = body.replace("t64_palette", "termite_palette")
        body = body.replace("t64_fbm", "termite_fbm")
        body = body.replace("t64_vnoise", "termite_vnoise")
        # The built-in sampler is `s`; the user-shader contract names it `smp`.
        body = body.replace("scene.sample(s,", "scene.sample(smp,")
        helpers = NOISE_HELPERS if "termite_fbm" in body or "termite_vnoise" in body else ""
        out = TEMPLATE.format(name=name, desc=desc, stem=stem, helpers=helpers, body=body)
        (out_dir / f"{stem}.metal").write_text(out)
        entries.append({
            "kind": "shader", "id": f"termite/{stem}", "name": name,
            "description": desc, "author": "termite", "license": "MIT",
            "version": "1.0.0", "file": f"shaders/termite/{stem}.metal",
        })
    print(json.dumps(entries, indent=2))
    print(f"\nwrote {len(entries)} shaders to {out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
