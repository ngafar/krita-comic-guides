"""Nine-panel layout grid as a colored vector layer.

Krita document guides all share one color, so the 3×3 panel reference is drawn
on its own vector layer (distinct stroke) that artists can hide before export.

SVG coordinates are in **document pixels** (not points). Using points made the
grid appear tiny in the corner on high-DPI pages (e.g. 11×17 @ 600 PPI).
"""

from __future__ import annotations

from .presets import (
    ComicPreset,
    inches_to_pixels,
    nine_panel_gutter_lines_in,
    safe_rect_in,
)

NINE_PANEL_LAYER_NAME = "Comic 9-Panel Grid"
# Warm orange — distinct from Krita’s usual guide teal/cyan.
NINE_PANEL_COLOR = "#E67E22"
NINE_PANEL_OPACITY = 160  # 0–255


def nine_panel_svg(
    preset: ComicPreset,
    x_ppi: float,
    y_ppi: float,
    *,
    color: str = NINE_PANEL_COLOR,
) -> str:
    """Build an SVG 3×3 grid over the safe area in document pixel coordinates."""
    left, top, right, bottom = safe_rect_in(preset)
    v_lines, h_lines = nine_panel_gutter_lines_in(preset)

    def x_px(inches: float) -> float:
        return inches_to_pixels(inches, x_ppi)

    def y_px(inches: float) -> float:
        return inches_to_pixels(inches, y_ppi)

    page_w = x_px(preset.page_width_in)
    page_h = y_px(preset.page_height_in)
    x0, y0 = x_px(left), y_px(top)
    x1, y1 = x_px(right), y_px(bottom)
    # ~1 pt stroke, readable at 600 PPI
    stroke = max(2.0, x_ppi / 72.0)

    parts = [
        f'<rect x="{x0:.4f}" y="{y0:.4f}" '
        f'width="{x1 - x0:.4f}" height="{y1 - y0:.4f}" />'
    ]
    for vx in v_lines:
        px = x_px(vx)
        parts.append(
            f'<line x1="{px:.4f}" y1="{y0:.4f}" x2="{px:.4f}" y2="{y1:.4f}" />'
        )
    for hy in h_lines:
        py = y_px(hy)
        parts.append(
            f'<line x1="{x0:.4f}" y1="{py:.4f}" x2="{x1:.4f}" y2="{py:.4f}" />'
        )
    body = "\n    ".join(parts)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{page_w:.4f}px" height="{page_h:.4f}px"
     viewBox="0 0 {page_w:.4f} {page_h:.4f}">
  <g id="comic-nine-panel" fill="none" stroke="{color}" stroke-width="{stroke:.4f}">
    {body}
  </g>
</svg>
"""


def _find_layer_by_name(document, name: str):
    node = document.rootNode()
    if node is None:
        return None
    for child in node.childNodes() or []:
        if child.name() == name:
            return child
    return None


def apply_nine_panel_grid(
    document,
    preset: ComicPreset,
    x_ppi: float,
    y_ppi: float,
    *,
    replace: bool = True,
    color: str = NINE_PANEL_COLOR,
) -> str:
    """Create or replace the nine-panel vector layer. Returns a short status."""
    existing = _find_layer_by_name(document, NINE_PANEL_LAYER_NAME)
    if existing is not None:
        if not replace:
            return f"Left existing “{NINE_PANEL_LAYER_NAME}” layer unchanged."
        parent = existing.parentNode()
        if parent is not None:
            parent.removeChildNode(existing)

    layer = document.createVectorLayer(NINE_PANEL_LAYER_NAME)
    if layer is None:
        raise RuntimeError("Could not create a vector layer for the 9-panel grid.")

    root = document.rootNode()
    root.addChildNode(layer, None)

    svg = nine_panel_svg(preset, x_ppi, y_ppi, color=color)
    shapes = layer.addShapesFromSvg(svg)
    if not shapes:
        raise RuntimeError("Failed to add 9-panel SVG shapes to the vector layer.")

    layer.setLocked(True)
    if hasattr(layer, "setOpacity"):
        layer.setOpacity(NINE_PANEL_OPACITY)

    document.refreshProjection()
    document.setModified(True)
    gutter = preset.panel_gutter_in
    return (
        f"Added “{NINE_PANEL_LAYER_NAME}” "
        f"({preset.panel_cols}×{preset.panel_rows}, {gutter}\" gutters, {color}). "
        f"Hide or delete it before export."
    )
