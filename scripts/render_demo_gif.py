#!/usr/bin/env python3
"""Render a lightweight animated GIF preview for the README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1200
HEIGHT = 760
BG = "#0b1220"
PANEL = "#111827"
PANEL_ALT = "#0f172a"
TEXT = "#e5eef8"
MUTED = "#93a4b8"
ACCENT = "#f97316"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#f59e0b"
BLUE = "#38bdf8"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = font(44, bold=True)
FONT_SUB = font(22)
FONT_MONO = font(24)
FONT_SMALL = font(18)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str | None = None) -> None:
    draw.rounded_rectangle(box, radius=22, fill=fill, outline=outline, width=2 if outline else 0)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, fill: str = TEXT, fnt=FONT_MONO) -> None:
    draw.text(xy, value, font=fnt, fill=fill)


def sensor_bar(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: float, color: str) -> None:
    text(draw, (x, y), label, MUTED, FONT_SMALL)
    rounded(draw, (x, y + 28, x + 260, y + 52), "#1f2937")
    rounded(draw, (x, y + 28, x + int(260 * max(0.08, min(value, 1.0))), y + 52), color)


def hero_frame() -> Image.Image:
    image = Image.new("P", (WIDTH, HEIGHT), 0)
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BG)

    text(draw, (72, 54), "fleet-monitor", ACCENT, FONT_TITLE)
    text(draw, (74, 114), "Predictive maintenance dashboard for IoT fleets", TEXT, FONT_SUB)
    text(draw, (74, 150), "ML scoring, telemetry simulation, SQLite history, Telegram alerts", MUTED, FONT_SUB)

    rounded(draw, (64, 212, 1136, 664), PANEL, "#1f2937")
    rounded(draw, (92, 246, 1108, 630), PANEL_ALT)
    text(draw, (122, 274), "$ python scripts/seed_history.py", GREEN)
    text(draw, (122, 314), "Seeded 14400 telemetry rows into data/fleet_monitor.db", TEXT, FONT_SMALL)
    text(draw, (122, 350), "$ streamlit run src/fleet_monitor/dashboard/app.py", GREEN)
    text(draw, (122, 398), "Fleet Overview", ACCENT, FONT_SUB)
    sensor_bar(draw, 122, 448, "Average fleet health", 0.74, GREEN)
    sensor_bar(draw, 122, 528, "Critical devices", 0.22, RED)
    sensor_bar(draw, 432, 448, "Average failure risk", 0.38, YELLOW)
    sensor_bar(draw, 432, 528, "Alerts last 24h", 0.41, BLUE)
    text(draw, (780, 446), "20 devices", TEXT, FONT_SUB)
    text(draw, (780, 494), "5 dashboard pages", TEXT, FONT_SUB)
    text(draw, (780, 542), "AI4I + XGBoost", TEXT, FONT_SUB)
    text(draw, (780, 590), "Telegram-ready", TEXT, FONT_SUB)
    return image.convert("P", palette=Image.ADAPTIVE)


def device_frame() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    text(draw, (72, 54), "Device Detail", ACCENT, FONT_TITLE)
    text(draw, (74, 114), "Lodwar Community Borehole • Heat dissipation failure", MUTED, FONT_SUB)
    rounded(draw, (64, 190, 370, 654), PANEL, "#1f2937")
    text(draw, (96, 228), "Health score", MUTED, FONT_SMALL)
    text(draw, (96, 266), "28%", RED, FONT_TITLE)
    text(draw, (96, 350), "Failure risk", MUTED, FONT_SMALL)
    text(draw, (96, 388), "86%", YELLOW, FONT_TITLE)
    text(draw, (96, 472), "Tool wear", MUTED, FONT_SMALL)
    text(draw, (96, 510), "311 min", TEXT, FONT_SUB)
    rounded(draw, (402, 190, 1136, 654), PANEL, "#1f2937")
    text(draw, (436, 226), "24h sensor trend", TEXT, FONT_SUB)
    for idx, color in enumerate([BLUE, GREEN, YELLOW, RED]):
        y = 290 + idx * 74
        sensor_bar(draw, 436, y, ["temperature", "vibration", "power_draw", "tool_wear"][idx], [0.82, 0.73, 0.66, 0.91][idx], color)
    text(draw, (436, 594), "Top risk driver: temp_x_torque", MUTED, FONT_SMALL)
    return image.convert("P", palette=Image.ADAPTIVE)


def predictions_frame() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    text(draw, (72, 54), "ML Predictions", ACCENT, FONT_TITLE)
    text(draw, (74, 114), "Failure forecast table, risk matrix, and estimated RUL", MUTED, FONT_SUB)
    rounded(draw, (64, 190, 1136, 654), PANEL, "#1f2937")
    rows = [
        ("dev_016", "Lodwar Community Borehole", "86%", "2.6", RED),
        ("dev_010", "Garissa Solar Pump", "77%", "4.1", YELLOW),
        ("dev_004", "Nakuru Compressor", "69%", "5.3", YELLOW),
        ("dev_003", "Kisumu Water Pump 1", "61%", "6.0", BLUE),
    ]
    text(draw, (96, 234), "Device", MUTED, FONT_SMALL)
    text(draw, (630, 234), "Risk", MUTED, FONT_SMALL)
    text(draw, (760, 234), "Est. RUL (days)", MUTED, FONT_SMALL)
    for idx, row in enumerate(rows):
        y = 286 + idx * 82
        rounded(draw, (88, y - 16, 1112, y + 42), PANEL_ALT)
        text(draw, (108, y), f"{row[0]}  {row[1]}", TEXT, FONT_SMALL)
        text(draw, (648, y), row[2], row[4], FONT_SMALL)
        text(draw, (798, y), row[3], TEXT, FONT_SMALL)
    text(draw, (96, 598), "Primary model: xgboost", TEXT, FONT_SMALL)
    text(draw, (320, 598), "ROC AUC: 0.96", GREEN, FONT_SMALL)
    text(draw, (486, 598), "F1: 0.71", GREEN, FONT_SMALL)
    return image.convert("P", palette=Image.ADAPTIVE)


def alerts_frame() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    text(draw, (72, 54), "Alerts + Delivery", ACCENT, FONT_TITLE)
    text(draw, (74, 114), "Critical alerts can be pushed to Telegram when credentials are set", MUTED, FONT_SUB)
    rounded(draw, (64, 190, 1136, 654), PANEL, "#1f2937")
    text(draw, (100, 232), "[CRITICAL] Immediate maintenance required", RED, FONT_SUB)
    text(draw, (100, 278), "dev_016 is at 28% health with 86% failure risk.", TEXT, FONT_SMALL)
    text(draw, (100, 308), "Probable mode: Heat dissipation failure.", TEXT, FONT_SMALL)
    text(draw, (100, 382), "[WARNING] Degradation detected", YELLOW, FONT_SUB)
    text(draw, (100, 428), "dev_010 is degrading. Top driver: power_estimate.", TEXT, FONT_SMALL)
    text(draw, (100, 502), "[INFO] Maintenance window due", BLUE, FONT_SUB)
    text(draw, (100, 548), "dev_004 has elevated tool wear and should be serviced.", TEXT, FONT_SMALL)
    text(draw, (100, 606), "Optional mode: works without Telegram configured", MUTED, FONT_SMALL)
    return image.convert("P", palette=Image.ADAPTIVE)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = [hero_frame(), device_frame(), predictions_frame(), alerts_frame()]
    frames[0].save(
        out_dir / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[1400, 1400, 1400, 1600],
        loop=0,
        optimize=False,
    )
    print(out_dir / "demo.gif")


if __name__ == "__main__":
    main()
