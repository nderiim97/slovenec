"""Generate local abstract SVG covers for demo articles (no external assets)."""

from __future__ import annotations

import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "covers"
OUT.mkdir(parents=True, exist_ok=True)

PALETTES = [
    ("#7f1d1d", "#e01b22", "#fecaca"),
    ("#0c1e4a", "#2563eb", "#bfdbfe"),
    ("#052e1b", "#16a34a", "#bbf7d0"),
    ("#3b0764", "#8b5cf6", "#ddd6fe"),
    ("#7c2d12", "#f97316", "#fed7aa"),
    ("#0f172a", "#0ea5e9", "#bae6fd"),
    ("#4a044e", "#db2777", "#fbcfe8"),
    ("#134e4a", "#14b8a6", "#ccfbf1"),
    ("#422006", "#eab308", "#fef08a"),
    ("#1e1b4b", "#6366f1", "#c7d2fe"),
    ("#500724", "#be123c", "#fecdd3"),
    ("#0b3b2e", "#059669", "#a7f3d0"),
]


def svg(index: int, palette: tuple[str, str, str]) -> str:
    dark, mid, light = palette
    rnd = random.Random(index * 977 + 13)
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" '
        f'width="1200" height="675" role="img" aria-label="Ilustracija {index}">'
    )
    parts.append(
        f'<defs><linearGradient id="g{index}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{dark}"/>'
        f'<stop offset="0.55" stop-color="{mid}"/>'
        f'<stop offset="1" stop-color="{dark}"/>'
        f"</linearGradient>"
        f'<linearGradient id="s{index}" x1="0" y1="1" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{light}" stop-opacity="0.85"/>'
        f'<stop offset="1" stop-color="{light}" stop-opacity="0"/>'
        f"</linearGradient></defs>"
    )
    parts.append(f'<rect width="1200" height="675" fill="url(#g{index})"/>')

    # Soft large circles.
    for i in range(3):
        cx = rnd.randint(-100, 1300)
        cy = rnd.randint(-100, 780)
        r = rnd.randint(160, 420)
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{light}" opacity="{rnd.choice([0.05, 0.08, 0.12])}"/>'
        )

    # Diagonal bands.
    for i in range(4):
        x = -300 + i * 380 + rnd.randint(-60, 60)
        w = rnd.randint(50, 140)
        parts.append(
            f'<rect x="{x}" y="-100" width="{w}" height="900" fill="{light}" '
            f'opacity="{rnd.choice([0.04, 0.07])}" transform="rotate(18 600 337)"/>'
        )

    # Editorial grid lines.
    for x in range(0, 1200, 100):
        parts.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="675" stroke="{light}" stroke-opacity="0.05"/>'
        )
    for y in range(0, 675, 75):
        parts.append(
            f'<line x1="0" y1="{y}" x2="1200" y2="{y}" stroke="{light}" stroke-opacity="0.05"/>'
        )

    # Foreground shapes.
    shape = index % 4
    if shape == 0:
        pts = []
        for i in range(7):
            x = 80 + i * 170
            y = 420 - int(180 * math.sin(i / 2.1 + index))
            pts.append(f"{x},{y}")
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{light}" '
            f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>'
        )
        parts.append(
            f'<polygon points="{" ".join(pts)} 1120,675 80,675" fill="{light}" opacity="0.10"/>'
        )
    elif shape == 1:
        for i in range(5):
            parts.append(
                f'<rect x="{110 + i * 190}" y="{210 + (i % 3) * 60}" width="120" height="260" '
                f'rx="10" fill="{light}" opacity="{0.08 + i * 0.05}"/>'
            )
        parts.append(
            f'<circle cx="930" cy="190" r="120" fill="none" stroke="{light}" stroke-width="18" opacity="0.55"/>'
        )
    elif shape == 2:
        for i in range(9):
            r = 40 + i * 28
            parts.append(
                f'<circle cx="600" cy="337" r="{r}" fill="none" stroke="{light}" '
                f'stroke-width="3" opacity="{0.55 - i * 0.05}"/>'
            )
        parts.append(
            f'<path d="M0 560 Q300 400 600 560 T1200 560 V675 H0 Z" fill="{light}" opacity="0.14"/>'
        )
    else:
        parts.append(
            f'<path d="M0 675 L320 300 L520 470 L760 180 L1200 675 Z" fill="{light}" opacity="0.12"/>'
        )
        parts.append(
            f'<path d="M0 675 L320 300 L520 470 L760 180 L1200 675" fill="none" stroke="{light}" '
            f'stroke-width="8" opacity="0.5"/>'
        )
        parts.append(
            f'<circle cx="{rnd.randint(850, 1000)}" cy="{rnd.randint(120, 220)}" r="70" fill="{light}" opacity="0.6"/>'
        )

    # Bottom fade for text overlays.
    parts.append(
        f'<rect y="400" width="1200" height="275" fill="url(#s{index})" opacity="0.35"/>'
    )
    parts.append("</svg>")
    return "".join(parts)


for i, palette in enumerate(PALETTES, start=1):
    (OUT / f"cover-{i}.svg").write_text(svg(i, palette), encoding="utf-8")

print(f"Wrote {len(PALETTES)} covers to {OUT}")
