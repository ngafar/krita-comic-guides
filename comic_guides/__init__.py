"""Comic Page Guides Krita plugin package.

When loaded inside Krita, registers the Extension. Outside Krita the package
still imports so modules like ``presets`` can be used on their own.
"""

try:
    from krita import Krita
except ImportError:
    pass
else:
    from .comic_guides import ComicGuidesExtension

    app = Krita.instance()
    app.addExtension(ComicGuidesExtension(app))
