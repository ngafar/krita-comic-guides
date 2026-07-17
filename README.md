# Krita Comic Guides

A small Krita Python plugin that creates a ready-to-draw **US comic page** in one click: an **11 × 17 in @ 600 PPI** document with bleed / trim / safe guides and a 9-panel vector grid.

## What one click does

**Tools → Scripts → New US Comic Page (11×17)**

1. Creates a new RGBA document: 11 × 17 in at 600 PPI (6600 × 10200 px)
2. Places bleed, trim, and safe-area guides
3. Adds nine editable orange panel rectangles on layer `Comic 9-Panel Grid`

## Layout (from Photoshop Guide Layout exports)

| Zone | Margins | Size on 11×17 |
|------|---------|----------------|
| Full bleed | 0.500″ | 10″ × 16″ |
| Trim | 0.625″ | 9.75″ × 15.75″ |
| Safe area | 1.000″ | 9″ × 15″ |

```text
Vertical:   0.500, 0.625, 1.000, 10.000, 10.375, 10.500
Horizontal: 0.500, 0.625, 1.000, 16.000, 16.375, 16.500
```

9-panel grid: `Panel 1`–`Panel 9` (left→right, top→bottom) with **0.125″ gutters**. Drag or delete each with **Select Shapes**; hide that layer before export. Guides do not appear in exports.

## Requirements

- Krita 5.3+ (guide scripting API)

## Install into Krita

### Option A — copy into resources (from this repo)

```bash
uv run python scripts/install.py
```

This copies `comic_guides/` and `comic_guides.desktop` into Krita’s `pykrita` resources folder (on macOS: `~/Library/Application Support/krita/pykrita`).

Re-copy after changes with `uv run python scripts/install.py --force`.

### Option B — zip importer

Zip `comic_guides/` and `comic_guides.desktop` at the archive top level, then in Krita use **Tools → Scripts → Import Python Plugin…**.

### Enable the plugin (required)

Installing alone is not enough — Krita leaves new Python plugins disabled until you turn them on:

1. Restart Krita after installing
2. **Settings → Configure Krita → Python Plugin Manager**
3. Check **Comic Page Guides** to enable it
4. Restart Krita again

Then use **Tools → Scripts → New US Comic Page (11×17)**.

### Uninstall

```bash
uv run python scripts/install.py --uninstall
```

## Layout

```text
comic_guides.desktop
comic_guides/
├── __init__.py          # registers the Extension
├── comic_guides.py      # one-click menu action
├── guides.py            # new document + GuidesConfig
├── panel_grid.py        # 9-panel vector shapes
└── presets.py           # inch presets + pixel conversion
scripts/
└── install.py           # copy into Krita’s pykrita folder
```
