from .presets import ComicPreset, inches_to_pixels, nine_panel_rects_in

NINE_PANEL_LAYER_NAME = "Comic 9-Panel Grid"
NINE_PANEL_COLOR = "#E67E22"
NINE_PANEL_OPACITY = 255


def _panel_rect_svg(
    *,
    page_w: float,
    page_h: float,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    stroke: float,
    color: str,
    panel_id: str,
) -> str:
    # SVG strokes are centered on the path; inset by half the stroke so the
    # line sits fully inside the panel bounds.
    inset = stroke / 2.0
    ix0 = x0 + inset
    iy0 = y0 + inset
    ix1 = x1 - inset
    iy1 = y1 - inset
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{page_w:.4f}px" height="{page_h:.4f}px"
     viewBox="0 0 {page_w:.4f} {page_h:.4f}">
  <rect id="{panel_id}"
        x="{ix0:.4f}" y="{iy0:.4f}"
        width="{ix1 - ix0:.4f}" height="{iy1 - iy0:.4f}"
        fill="none" stroke="{color}" stroke-width="{stroke:.4f}" />
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


def _make_shapes_editable(shapes) -> None:
    for shape in shapes or []:
        if hasattr(shape, "setSelectable"):
            shape.setSelectable(True)
        if hasattr(shape, "setGeometryProtected"):
            shape.setGeometryProtected(False)
        if hasattr(shape, "update"):
            shape.update()


def apply_nine_panel_grid(
    document,
    preset: ComicPreset,
    x_ppi: float,
    y_ppi: float,
    *,
    replace: bool = True,
    color: str = NINE_PANEL_COLOR,
) -> str:
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

    page_w = inches_to_pixels(preset.page_width_in, x_ppi)
    page_h = inches_to_pixels(preset.page_height_in, y_ppi)
    stroke = max(2.0, x_ppi / 72.0)

    created = 0
    for index, (left, top, right, bottom) in enumerate(nine_panel_rects_in(preset), start=1):
        name = f"Panel {index}"
        svg = _panel_rect_svg(
            page_w=page_w,
            page_h=page_h,
            x0=inches_to_pixels(left, x_ppi),
            y0=inches_to_pixels(top, y_ppi),
            x1=inches_to_pixels(right, x_ppi),
            y1=inches_to_pixels(bottom, y_ppi),
            stroke=stroke,
            color=color,
            panel_id=f"panel-{index}",
        )
        shapes = layer.addShapesFromSvg(svg)
        if not shapes:
            raise RuntimeError(f"Failed to add vector shape for {name}.")
        for shape in shapes:
            if hasattr(shape, "setName"):
                shape.setName(name)
        _make_shapes_editable(shapes)
        created += len(shapes)

    if created == 0:
        raise RuntimeError("Failed to add panel shapes to the vector layer.")

    layer.setLocked(False)
    if hasattr(layer, "setOpacity"):
        layer.setOpacity(NINE_PANEL_OPACITY)

    document.setActiveNode(layer)
    document.refreshProjection()
    document.setModified(True)
    gutter = preset.panel_gutter_in
    return (
        f"Added “{NINE_PANEL_LAYER_NAME}” with {created} separate panel shapes "
        f"({preset.panel_cols}×{preset.panel_rows}, {gutter}\" gutters, {color}). "
        f"Use Select Shapes to drag or delete each panel; hide the layer before export."
    )
