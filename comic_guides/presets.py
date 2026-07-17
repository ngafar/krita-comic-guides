from dataclasses import dataclass


@dataclass(frozen=True)
class ComicPreset:
    name: str
    page_width_in: float
    page_height_in: float
    # Left → right (bleed, trim, safe, safe, trim, bleed)
    vertical_in: tuple[float, ...]
    # Top → bottom (bleed, trim, safe, safe, trim, bleed)
    horizontal_in: tuple[float, ...]
    panel_cols: int = 3
    panel_rows: int = 3
    panel_gutter_in: float = 0.125
    description: str = ""


# 11×17 Bristol board — Standard USA comic dimensions:
#   Full bleed: 10″ × 15⅜″   (½″ sides, 13/16″ top/bottom)
#   Trim line:  9¾″ × 15″    (⅝″ sides, 1″ top/bottom)
#   Safe area:  9″ × 14¼″    (1″ sides, 1⅜″ top/bottom)
STANDARD_US_COMIC = ComicPreset(
    name="Standard US Comic — 11 × 17 in",
    page_width_in=11.0,
    page_height_in=17.0,
    vertical_in=(0.500, 0.625, 1.000, 10.000, 10.375, 10.500),
    horizontal_in=(0.8125, 1.000, 1.375, 15.625, 16.000, 16.1875),
    panel_cols=3,
    panel_rows=3,
    panel_gutter_in=0.125,
    description="Bleed 10×15⅜, trim 9¾×15, safe 9×14¼; 3×3 panels with 0.125″ gutters",
)

DEFAULT_PRESET = STANDARD_US_COMIC
DOCUMENT_PPI = 600


def inches_to_pixels(inches: float, ppi: float) -> float:
    return inches * ppi


def guide_pixels(
    preset: ComicPreset, x_ppi: float, y_ppi: float
) -> tuple[list[float], list[float]]:
    vertical = [inches_to_pixels(v, x_ppi) for v in preset.vertical_in]
    horizontal = [inches_to_pixels(h, y_ppi) for h in preset.horizontal_in]
    return vertical, horizontal


def page_size_inches(
    width_px: float, height_px: float, x_ppi: float, y_ppi: float
) -> tuple[float, float]:
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
    width_in, height_in = page_size_inches(width_px, height_px, x_ppi, y_ppi)
    return (
        abs(width_in - preset.page_width_in) <= tolerance_in
        and abs(height_in - preset.page_height_in) <= tolerance_in
    )


def merge_guides(
    existing: list[float], new: list[float], *, replace: bool, epsilon: float = 0.5
) -> list[float]:
    if replace:
        return sorted(new)
    merged = list(existing)
    for value in new:
        if not any(abs(value - e) <= epsilon for e in merged):
            merged.append(value)
    return sorted(merged)


def safe_rect_in(preset: ComicPreset) -> tuple[float, float, float, float]:
    _, _, safe_left, safe_right, _, _ = preset.vertical_in
    _, _, safe_top, safe_bottom, _, _ = preset.horizontal_in
    return safe_left, safe_top, safe_right, safe_bottom


def nine_panel_rects_in(
    preset: ComicPreset,
) -> list[tuple[float, float, float, float]]:
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
