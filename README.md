# Krita Comic Guides

A small Krita Python plugin that:

1. Creates a new **11 × 17 in @ 600 PPI** document 
2. Adds bleed, trim and safe guides.
3. Creates a 9-panel vector grid.


## Layout 

The guides are based on these dimensions:

![Comic page dimensions](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/articles_artdimensions1.jpg?1924)

Source: [Blambot](https://blambot.com/pages/original-art-dimensions-for-american-standard-comics)

## Install

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
