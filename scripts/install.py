import argparse
import os
import platform
import shutil
from pathlib import Path

PLUGIN_NAME = "comic_guides"
DESKTOP_NAME = f"{PLUGIN_NAME}.desktop"


def krita_pykrita_dir() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library/Application Support/krita/pykrita"
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise SystemExit("APPDATA is not set; cannot locate Krita resources.")
        return Path(appdata) / "krita" / "pykrita"
    xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))
    return Path(xdg) / "krita" / "pykrita"


def repo_plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def install(*, force: bool = False) -> None:
    src_root = repo_plugin_root()
    src_pkg = src_root / PLUGIN_NAME
    src_desktop = src_root / DESKTOP_NAME
    if not src_pkg.is_dir() or not src_desktop.is_file():
        raise SystemExit(f"Plugin sources not found under {src_root}")

    dest_root = krita_pykrita_dir()
    dest_root.mkdir(parents=True, exist_ok=True)
    dest_pkg = dest_root / PLUGIN_NAME
    dest_desktop = dest_root / DESKTOP_NAME

    if dest_pkg.exists() or dest_desktop.exists():
        if not force:
            raise SystemExit(
                f"Already installed at {dest_root}. Re-run with --force to replace."
            )
        _remove_path(dest_pkg)
        _remove_path(dest_desktop)

    shutil.copytree(src_pkg, dest_pkg)
    shutil.copy2(src_desktop, dest_desktop)
    print(f"Installed {PLUGIN_NAME} → {dest_root}")
    print("Restart Krita, then enable the plugin under:")
    print("  Settings → Configure Krita → Python Plugin Manager")


def uninstall() -> None:
    dest_root = krita_pykrita_dir()
    dest_pkg = dest_root / PLUGIN_NAME
    dest_desktop = dest_root / DESKTOP_NAME
    removed = False
    for path in (dest_pkg, dest_desktop):
        if path.exists() or path.is_symlink():
            _remove_path(path)
            removed = True
    if removed:
        print(f"Removed {PLUGIN_NAME} from {dest_root}")
    else:
        print(f"Nothing to remove under {dest_root}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Install or uninstall the Comic Page Guides plugin into Krita."
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove the plugin from Krita's pykrita folder",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing install",
    )
    parser.add_argument(
        "--print-target",
        action="store_true",
        help="Print the Krita pykrita directory and exit",
    )
    args = parser.parse_args(argv)

    if args.print_target:
        print(krita_pykrita_dir())
        return
    if args.uninstall:
        uninstall()
        return
    install(force=args.force)


if __name__ == "__main__":
    main()
