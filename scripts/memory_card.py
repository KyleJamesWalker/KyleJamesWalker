"""Render assets/memory-card.svg, a PS1-style memory card screen of featured repos."""

from pathlib import Path
from xml.sax.saxutils import escape

SAVES = [
    ("Palmcast", "Rust", 0, "Hand the room the mic: talks, polls and Q&A from phones."),
    ("keystones", "Python", 0, "Pin a review gate to an AST node, not a file path."),
    ("vscode-cc-agent-manager", "TypeScript", 7, "A live dashboard for Claude Code sessions in VSCode."),
    ("yamlsettings", "Python", 18, "Layered YAML settings with env var overrides."),
    ("AmberDAV", "Rust", 1, "One-binary WebDAV file server for handhelds and Steam Deck."),
    ("SimpleConfidenceMonitor", "Rust", 0, "A stage display for speakers, run from a phone."),
    ("cc-cmux-plugin", "Shell", 2, "Claude Code agent status and alerts inside cmux."),
    ("restraint-py", "Python", 0, "Composable rate limiting, sync or async."),
    ("pre-commit-hooks", "Python", 0, "Hooks incl. a Simplified Technical English linter."),
    ("pr-changes-matrix-builder", "Python", 20, "Build a CI matrix from the files a PR touched."),
    ("yaml-params", "Python", 1, "Export YAML into GitHub Actions env vars."),
    ("renogy_rover", "Python", 26, "MODBUS driver for Renogy Rover solar controllers."),
]

LANG_COLORS = {"Rust": "#dea584", "Python": "#3572a5", "TypeScript": "#3178c6", "Shell": "#89e051"}

W, H = 640, 360
ROW_H, ROWS_VISIBLE, LIST_TOP = 38, 5, 62
BOOT_END, FADE = 3.0, 0.5
FIRST_STEP, STEP, MOVE = 4.0, 0.8, 0.15
LAST_STEP = FIRST_STEP + STEP * (len(SAVES) - 1)
TOTAL = LAST_STEP + 1.2
BEGIN = 'begin="0s;hit.click" dur="%ss" fill="freeze"' % round(TOTAL, 3)


def kt(t):
    return round(t / TOTAL, 4)


def stepped(positions):
    """Values/keyTimes that hold each position, gliding to the next at each step."""
    times, values = [0.0], [positions[0]]
    for i in range(1, len(positions)):
        t = FIRST_STEP + STEP * i
        times += [t - MOVE, t]
        values += [positions[i - 1], positions[i]]
    times.append(TOTAL)
    values.append(positions[-1])
    return ";".join(str(kt(t)) for t in times), ";".join(str(v) for v in values)


def visible_window(i):
    """(cursor row, list scroll offset) when save i is selected."""
    row = min(i, ROWS_VISIBLE - 1)
    return row, i - row


def icon(name, lang, x, y):
    color = LANG_COLORS.get(lang, "#888")
    initials = escape(name.replace("_", "-").split("-")[0][:2].upper())
    return (
        f'<rect x="{x}" y="{y}" width="26" height="26" rx="3" fill="{color}"/>'
        f'<rect x="{x}" y="{y}" width="26" height="13" rx="3" fill="#fff" opacity=".18"/>'
        f'<text x="{x + 13}" y="{y + 18}" text-anchor="middle" font-size="12" font-weight="bold" fill="#10123a">{initials}</text>'
    )


def build():
    total_stars = sum(s[2] for s in SAVES)
    rows = []
    for i, (name, lang, stars, _) in enumerate(SAVES):
        y = LIST_TOP + i * ROW_H
        star = f'<text x="592" y="{y + 24}" text-anchor="end" fill="#f6c21c">★ {stars}</text>' if stars else ""
        rows.append(
            f'<rect x="32" y="{y + 2}" width="576" height="{ROW_H - 6}" rx="4" fill="#ffffff12"/>'
            + icon(name, lang, 42, y + 5)
            + f'<text x="80" y="{y + 24}">{escape(name)}</text>'
            + f'<text x="520" y="{y + 24}" text-anchor="end" font-size="12" fill="#9fd3ff">{lang.upper()}</text>'
            + star
        )

    windows = [visible_window(i) for i in range(len(SAVES))]
    cur_kt, cur_vals = stepped([LIST_TOP + r * ROW_H for r, _ in windows])
    scroll_kt, scroll_vals = stepped([-o * ROW_H for _, o in windows])

    infos = []
    for i, (name, _, _, blurb) in enumerate(SAVES):
        start = 0.0 if i == 0 else FIRST_STEP + STEP * i
        end = TOTAL if i == len(SAVES) - 1 else FIRST_STEP + STEP * (i + 1)
        if i == 0:
            keys, vals = f"0;{kt(end)};1", "1;0;0"
        elif end >= TOTAL:
            keys, vals = f"0;{kt(start)};1", "0;1;1"
        else:
            keys, vals = f"0;{kt(start)};{kt(end)};1", "0;1;0;0"
        infos.append(
            f'<g opacity="0"><animate attributeName="opacity" calcMode="discrete" keyTimes="{keys}" values="{vals}" {BEGIN}/>'
            f'<text x="44" y="290" font-size="16" fill="#f6c21c">{escape(name)}</text>'
            f'<text x="44" y="314" font-size="13" fill="#e8f1ff">{escape(blurb)}</text></g>'
        )

    boot_kt = f"0;{kt(BOOT_END)};{kt(BOOT_END + FADE)};1"
    end_kt = f"0;{kt(LAST_STEP + 0.4)};1"
    list_clip_h = ROWS_VISIBLE * ROW_H

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'Courier New', monospace">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1b1f6e"/>
      <stop offset="1" stop-color="#05061a"/>
    </linearGradient>
    <clipPath id="list"><rect x="0" y="{LIST_TOP}" width="{W}" height="{list_clip_h}"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" rx="12" fill="url(#sky)"/>

  <text x="32" y="44" font-size="18" fill="#9fd3ff" letter-spacing="3">MEMORY CARD 1</text>
  <text x="608" y="44" font-size="14" fill="#9fd3ff" text-anchor="end">{len(SAVES)} SAVES · ★ {total_stars}</text>

  <g clip-path="url(#list)">
    <g font-size="15" fill="#fff">
      <animateTransform attributeName="transform" type="translate" additive="replace" keyTimes="{scroll_kt}" values="{';'.join('0 ' + v for v in scroll_vals.split(';'))}" {BEGIN}/>
      {''.join(rows)}
    </g>
  </g>
  <rect x="30" y="{LIST_TOP}" width="580" height="{ROW_H - 2}" rx="5" fill="none" stroke="#f6c21c" stroke-width="2">
    <animate attributeName="y" keyTimes="{cur_kt}" values="{cur_vals}" {BEGIN}/>
  </rect>

  <rect x="32" y="{LIST_TOP + list_clip_h + 8}" width="576" height="64" rx="6" fill="#00000055" stroke="#9fd3ff55"/>
  {''.join(infos)}

  <text x="32" y="{H - 16}" font-size="13" fill="#9fd3ff">✕ LOAD   ○ COPY   △ DELETE (pls no)</text>
  <g opacity="0">
    <animate attributeName="opacity" calcMode="discrete" keyTimes="{end_kt}" values="0;1;1" {BEGIN}/>
    <text x="608" y="{H - 16}" font-size="13" fill="#fff" text-anchor="end">CLICK TO REPLAY<animate attributeName="opacity" values="1;0;1" dur="1.2s" calcMode="discrete" repeatCount="indefinite"/></text>
  </g>

  <g>
    <animate attributeName="opacity" keyTimes="{boot_kt}" values="1;1;0;0" {BEGIN}/>
    <animate attributeName="visibility" calcMode="discrete" keyTimes="0;{kt(BOOT_END + FADE)};1" values="visible;hidden;hidden" {BEGIN}/>
    <rect width="{W}" height="{H}" rx="12" fill="#fff"/>
    <g transform="translate(320 140)">
      <polygon points="-45,0 0,-45 0,0" fill="#e23b3b"/>
      <polygon points="0,-45 45,0 0,0" fill="#f6c21c"/>
      <polygon points="45,0 0,45 0,0" fill="#2e8bd8"/>
      <polygon points="0,45 -45,0 0,0" fill="#33b06b"/>
    </g>
    <text x="320" y="230" text-anchor="middle" font-size="26" font-weight="bold" fill="#222" letter-spacing="6">KJW</text>
    <text x="320" y="256" text-anchor="middle" font-size="13" fill="#555" letter-spacing="3">Licensed by Kyle James Walker</text>
  </g>

  <rect id="hit" width="{W}" height="{H}" fill="transparent" style="cursor:pointer"/>
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "memory-card.svg"
    out.write_text(build())
    print(f"wrote {out}")
