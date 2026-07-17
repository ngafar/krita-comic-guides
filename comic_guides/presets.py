"""Comic page guide presets.

Guide positions are defined in inches relative to an 11×17 in page.
Krita stores guides in document pixels, so callers convert with
``inches_to_pixels`` using the active document's resolution.

The Standard US Comic preset matches Photoshop Guide Layout exports:
``TrimLine.gds`` (0.625″ margins) and ``SafeArea.gds`` (1″ margins,
3×3 with 0.125″ gutters), plus a 0.5″ bleed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComicPreset:
    """A named set of vertical and horizontal guide positions in inches."""

    name: str
    page_width_in: float
    page_height_in: float
    # Left → right (bleed, trim, safe, safe, trim, bleed)
    vertical_in: tuple[float, ...]
    # Top → bottom (bleed, trim, safe, safe, trim, bleed)
    horizontal_in: tuple[float, ...]
    # 9-panel grid inside the safe area (from SafeArea.gds)
    panel_cols: int = 3
    panel_rows: int = 3
    panel_gutter_in: float = 0.125
    description: str = ""


# 11×17 board @ typically 600 PPI:
#   Bleed: 0.5″ margins  → 10″ × 16″
#   Trim:  0.625″ margins → 9.75″ × 15.75″  (TrimLine.gds)
#   Safe:  1.0″ margins  → 9″ × 15″         (SafeArea.gds)
STANDARD_US_COMIC = ComicPreset(
    name="Standard US Comic — 11 × 17 in",
    page_width_in=11.0,
    page_height_in=17.0,
    vertical_in=(0.500, 0.625, 1.000, 10.000, 10.375, 10.500),
    horizontal_in=(0.500, 0.625, 1.000, 16.000, 16.375, 16.500),
    panel_cols=3,
    panel_rows=3,
    panel_gutter_in=0.125,
    description="Bleed 0.5″, trim 0.625″, safe 1″; 3×3 panels with 0.125″ gutters",
)

PRESETS: dict[str, ComicPreset] = {
    STANDARD_US_COMIC.name: STANDARD_US_COMIC,
}

DEFAULT_PRESET = STANDARD_US_COMIC


def inches_to_pixels(inches: float, ppi: float) -> float:
    """Convert an inch measurement to document pixels at the given PPI."""
    return inches * ppi


def guide_pixels(
    preset: ComicPreset, x_ppi: float, y_ppi: float
) -> tuple[list[float], list[float]]:
    """Return (vertical_px, horizontal_px) for *preset* at the given resolutions."""
    vertical = [inches_to_pixels(v, x_ppi) for v in preset.vertical_in]
    horizontal = [inches_to_pixels(h, y_ppi) for h in preset.horizontal_in]
    return vertical, horizontal


def page_size_inches(width_px: float, height_px: float, x_ppi: float, y_ppi: float) -> tuple[float, float]:
    """Document size in inches from pixel size and resolution."""
    if x_ppi <= 0 or y_ppi <= 0:
        raise ValueError("Resolution (PPI) must be positive")
    return width_px / x_ppi, height_px / y_ppi


def page_matches_preset(
    preset: ComicPreset,
    width_px: float,
    height_px: float,
    x_ppi: float,
    y_ppi: float,
    tolerance_in: float = 0.02,
) -> bool:
    """True if the document page size matches the preset within *tolerance_in* inches."""
    width_in, height_in = page_size_inches(width_px, height_px, x_ppi, y_ppi)
    return (
        abs(width_in - preset.page_width_in) <= tolerance_in
        and abs(height_in - preset.page_height_in) <= tolerance_in
    )


def merge_guides(
    existing: list[float], new: list[float], *, replace: bool, epsilon: float = 0.5
) -> list[float]:
    """Merge guide lists. When *replace* is True, return *new* only."""
    if replace:
        return sorted(new)
    merged = list(existing)
    for value in new:
        if not any(abs(value - e) <= epsilon for e in merged):
            merged.append(value)
    return sorted(merged)


def safe_rect_in(preset: ComicPreset) -> tuple[float, float, float, float]:
    """Return (left, top, right, bottom) of the safe area in inches.

    Presets store guides as bleed, trim, safe, safe, trim, bleed.
    """
    _, _, safe_left, safe_right, _, _ = preset.vertical_in
    _, _, safe_top, safe_bottom, _, _ = preset.horizontal_in
    return safe_left, safe_top, safe_right, safe_bottom


def nine_panel_rects_in(
    preset: ComicPreset,
) -> list[tuple[float, float, float, float]]:
    """Return each panel as ``(left, top, right, bottom)`` in inches.

    Reading order is left-to-right, top-to-bottom (comic page order).
    """
    left, top, right, bottom = safe_rect_in(preset)
    width = right - left
    height = bottom - top
    cols = preset.panel_cols
    rows = preset.panel_rows
    gutter = preset.panel_gutter_in

    panel_w = (width - (cols - 1) * gutter) / cols
    panel_h = (height - (rows - 1) * gutter) / rows

    rects: list[tuple[float, float, float, float]] = []
    for row in range(rows):
        for col in range(cols):
            x0 = left + col * (panel_w + gutter)
            y0 = top + row * (panel_h + gutter)
            rects.append((x0, y0, x0 + panel_w, y0 + panel_h))
    return rects


def nine_panel_gutter_lines_in(
    preset: ComicPreset,
) -> tuple[list[float], list[float]]:
    """Return vertical and horizontal gutter-edge lines inside the safe area.

    Matches Photoshop Guide Layout: ``colCount`` / ``rowCount`` panels with
    ``panel_gutter_in`` gaps. Each gutter contributes two lines (both edges).
    """
    left, top, right, bottom = safe_rect_in(preset)
    width = right - left
    height = bottom - top
    cols = preset.panel_cols
    rows = preset.panel_rows
    gutter = preset.panel_gutter_in

    panel_w = (width - (cols - 1) * gutter) / cols
    panel_h = (height - (rows - 1) * gutter) / rows

    vertical: list[float] = []
    x = left
    for _ in range(cols - 1):
        x += panel_w
        vertical.append(x)
        vertical.append(x + gutter)
        x += gutter

    horizontal: list[float] = []
    y = top
    for _ in range(rows - 1):
        y += panel_h
        horizontal.append(y)
        horizontal.append(y + gutter)
        y += gutter

    return vertical, horizontal
