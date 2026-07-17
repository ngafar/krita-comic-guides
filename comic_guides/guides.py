"""Apply comic presets to a Krita document via GuidesConfig.

This module imports ``krita`` and is only meant to run inside Krita.
Preset math lives in ``presets.py``.
"""

from __future__ import annotations

from .panel_grid import apply_nine_panel_grid
from .presets import (
    DEFAULT_PRESET,
    ComicPreset,
    guide_pixels,
    merge_guides,
    page_matches_preset,
    page_size_inches,
)


class GuideError(Exception):
    """Raised when guides cannot be applied."""


def _document_ppi(document) -> tuple[float, float]:
    """Return (x_ppi, y_ppi). Prefer xRes/yRes; fall back to resolution()."""
    x_ppi = float(document.xRes())
    y_ppi = float(document.yRes())
    if x_ppi <= 0 or y_ppi <= 0:
        res = float(document.resolution())
        if res <= 0:
            raise GuideError("Document resolution is not set (PPI must be > 0).")
        return res, res
    return x_ppi, y_ppi


def apply_comic_guides(
    document,
    preset: ComicPreset = DEFAULT_PRESET,
    *,
    replace: bool = True,
    visible: bool = True,
    locked: bool = True,
    snap: bool = True,
    nine_panel: bool = False,
    require_page_size: bool = False,
) -> str:
    """Place comic guides on *document*.

    Returns a short status message. Raises ``GuideError`` on failure.
    """
    from krita import GuidesConfig

    if document is None:
        raise GuideError("No active document. Open an 11×17 in comic page first.")

    x_ppi, y_ppi = _document_ppi(document)
    width_px = float(document.width())
    height_px = float(document.height())

    matches = page_matches_preset(preset, width_px, height_px, x_ppi, y_ppi)
    if require_page_size and not matches:
        width_in, height_in = page_size_inches(width_px, height_px, x_ppi, y_ppi)
        raise GuideError(
            f"Document is {width_in:.3f}×{height_in:.3f} in, "
            f"but preset expects {preset.page_width_in}×{preset.page_height_in} in."
        )

    vertical_px, horizontal_px = guide_pixels(preset, x_ppi, y_ppi)

    guides = document.guidesConfig()
    if guides is None:
        guides = GuidesConfig()

    existing_v = list(guides.verticalGuides() or [])
    existing_h = list(guides.horizontalGuides() or [])

    guides.setVerticalGuides(merge_guides(existing_v, vertical_px, replace=replace))
    guides.setHorizontalGuides(merge_guides(existing_h, horizontal_px, replace=replace))
    guides.setVisible(visible)
    guides.setLocked(locked)
    guides.setSnap(snap)

    document.setGuidesConfig(guides)

    parts = [
        f"Applied “{preset.name}” guides at {x_ppi:.0f}×{y_ppi:.0f} PPI."
    ]

    if nine_panel:
        try:
            parts.append(
                apply_nine_panel_grid(
                    document, preset, x_ppi, y_ppi, replace=replace
                )
            )
        except Exception as exc:  # noqa: BLE001 — surface Krita API failures
            raise GuideError(f"Guides applied, but 9-panel grid failed: {exc}") from exc

    document.refreshProjection()
    document.setModified(True)

    if not matches:
        width_in, height_in = page_size_inches(width_px, height_px, x_ppi, y_ppi)
        parts.append(
            f"Note: page is {width_in:.3f}×{height_in:.3f} in "
            f"(preset is {preset.page_width_in}×{preset.page_height_in} in)."
        )
    return " ".join(parts)
