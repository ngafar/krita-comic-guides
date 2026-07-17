try:
    from krita import Krita
except ImportError:
    pass
else:
    from .comic_guides import ComicGuidesExtension

    app = Krita.instance()
    app.addExtension(ComicGuidesExtension(app))
