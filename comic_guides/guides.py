from .panel_grid import apply_nine_panel_grid
from .presets import (
    DEFAULT_PRESET,
    DOCUMENT_PPI,
    ComicPreset,
    guide_pixels,
    inches_to_pixels,
    merge_guides,
    page_matches_preset,
    page_size_inches,
)

# SVG/CSS named color — pale blue for bleed/trim/safe guides.
GUIDE_COLOR_NAME = "powderblue"


class GuideError(Exception):
    pass


def create_comic_document(preset: ComicPreset = DEFAULT_PRESET, ppi: int = DOCUMENT_PPI):
    from krita import Krita

    app = Krita.instance()
    width_px = int(round(inches_to_pixels(preset.page_width_in, ppi)))
    height_px = int(round(inches_to_pixels(preset.page_height_in, ppi)))

    document = app.createDocument(
        width_px,
        height_px,
        "US Comic Page",
        "RGBA",
        "U8",
        "",
        ppi,
    )
    if document is None:
        raise GuideError("Could not create a new Krita document.")

    window = app.activeWindow()
    if window is None:
        document.close()
        raise GuideError("No active Krita window to open the new page in.")

    window.addView(document)
    return document


def _document_ppi(document) -> tuple[float, float]:
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
    from krita import GuidesConfig

    try:
        from PyQt6.QtGui import QColor
    except ImportError:
        from PyQt5.QtGui import QColor

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
    guides.setColor(QColor(GUIDE_COLOR_NAME))
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
        except Exception as exc:
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
