# Krita Comic Guides

A small Krita Python plugin that:

1. Creates a new document: **11" × 17", @ 600 PPI**
2. Adds bleed, trim and safe guides.
3. Creates a 9-panel vector grid.

## Install

1. Download [`comic-guides.zip`](https://github.com/ngafar/krita-comic-guides/releases/latest/download/comic-guides.zip).
2. In Krita: **Tools → Scripts → Import Python Plugin from File** and choose the zip.
3. Restart Krita.

## Usage 

**Tools → Scripts → New US Comic Page (11×17)**.

If you do not see the script, you might need to enable the plugin: **Settings → Configure Krita → Python Plugin Manager** → enable **Comic Page Guides**.


## Layout

The guides are based on these dimensions:

![Comic page dimensions](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/articles_artdimensions1.jpg?1924)

Source: [Blambot](https://blambot.com/pages/original-art-dimensions-for-american-standard-comics)

## Development Notes

To quickly install from this repo:

```bash
uv run python scripts/install.py --force
```
