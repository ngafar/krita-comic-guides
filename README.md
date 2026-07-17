# Krita Comic Guides

A small Krita Python plugin that places **bleed**, **trim**, and **safe-area** guides on comic pages. Guides are real Krita guides (not painted lines), so they stay out of exports.

Intended document: **11 × 17 in at 600 PPI** (works at other PPI; guides scale with resolution).

## Standard US Comic preset

Matches Photoshop Guide Layout exports (`TrimLine.gds`, `SafeArea.gds`):

| Zone | Margins | Size on 11×17 |
|------|---------|----------------|
| Full bleed | 0.500″ | 10″ × 16″ |
| Trim | 0.625″ | 9.75″ × 15.75″ |
| Safe area | 1.000″ | 9″ × 15″ |

Guide positions (inches):

```text
Vertical:   0.500, 0.625, 1.000, 10.000, 10.375, 10.500
Horizontal: 0.500, 0.625, 1.000, 16.000, 16.375, 16.500
```

Optional **9-panel grid**: nine separate orange vector rectangles (`Panel 1`–`Panel 9`) inside the safe area with **0.125″ gutters**, on layer `Comic 9-Panel Grid`. Drag or delete each with **Select Shapes**; hide the layer before export.

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

The menu entries only appear after this step:

- **Tools → Scripts → Comic Page Guides**
- **Tools → Scripts → Add Standard US Comic Guides**

### Uninstall

```bash
uv run python scripts/install.py --uninstall
```

## Usage

1. Create or open an **11 × 17 in** document at **600 PPI** (or any PPI).
2. Choose one of:
   - **Tools → Scripts → Comic Page Guides** — dialog with options
   - **Tools → Scripts → Add Standard US Comic Guides** — one-click defaults

Default options: replace existing guides, show, lock, snap, and the 9-panel grid.

## Layout

```text
comic_guides.desktop
comic_guides/
├── __init__.py          # registers the Extension
├── comic_guides.py      # menu actions + dialog
├── guides.py            # applies GuidesConfig
├── panel_grid.py        # 9-panel vector overlay
└── presets.py           # inch presets + pixel conversion
scripts/
└── install.py           # copy into Krita’s pykrita folder
```
