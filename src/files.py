"""Handles scanning, renaming, extracting RARs, and other file operations."""

import importlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENDORED_UNRAR_DIR = PROJECT_ROOT / ".deps" / "unrar"
DEBIAN_UNRAR_LIB_PACKAGES = ("libunrar5t64", "libunrar5")


def _run(command: list[str], *, cwd: Path | None = None, quiet: bool = False) -> bool:
    kwargs = {}
    if quiet:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL

    try:
        subprocess.check_call(command, cwd=cwd, **kwargs)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def _clear_unrar_import_cache() -> None:
    for module_name in list(sys.modules):
        if module_name == "unrar" or module_name.startswith("unrar."):
            del sys.modules[module_name]
    importlib.invalidate_caches()


def _find_vendored_unrar_library() -> Path | None:
    if not VENDORED_UNRAR_DIR.exists():
        return None

    candidates = sorted(VENDORED_UNRAR_DIR.glob("**/libunrar.so*"))
    return candidates[0] if candidates else None


def _activate_vendored_unrar_library() -> bool:
    lib_path = _find_vendored_unrar_library()
    if not lib_path:
        return False

    os.environ["UNRAR_LIB_PATH"] = str(lib_path)
    return True


def _install_python_unrar() -> bool:
    return _run([sys.executable, "-m", "pip", "install", "unrar"])


def _install_unrar_library_from_apt_package() -> bool:
    if not shutil.which("apt-get") or not shutil.which("dpkg-deb"):
        return False

    VENDORED_UNRAR_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for package in DEBIAN_UNRAR_LIB_PACKAGES:
            if not _run(["apt-get", "download", package], cwd=tmp_path):
                continue

            packages = sorted(tmp_path.glob(f"{package}_*.deb"))
            if not packages:
                continue

            if _run(["dpkg-deb", "-x", str(packages[-1]), str(VENDORED_UNRAR_DIR)]):
                return _activate_vendored_unrar_library()

    return False


def _install_unrar_library_with_package_manager() -> bool:
    if not shutil.which("apt-get"):
        return False

    if hasattr(os, "geteuid") and os.geteuid() == 0:
        command_prefix = []
    elif shutil.which("sudo") and _run(["sudo", "-n", "true"], quiet=True):
        command_prefix = ["sudo", "-n"]
    else:
        return False

    for package in DEBIAN_UNRAR_LIB_PACKAGES:
        if _run(command_prefix + ["apt-get", "install", "-y", package]):
            return True

    return False


def _install_unrar_library() -> bool:
    return (
        _activate_vendored_unrar_library()
        or _install_unrar_library_from_apt_package()
        or _install_unrar_library_with_package_manager()
    )


def get_rarfile_module(*, auto_install: bool = True):
    """Return ``unrar.rarfile``, installing missing dependencies when possible."""

    for _ in range(3):
        try:
            return importlib.import_module("unrar.rarfile")
        except ModuleNotFoundError as exc:
            if exc.name != "unrar" or not auto_install or not _install_python_unrar():
                raise RuntimeError(
                    "Missing Python package 'unrar'. Install it with "
                    f"'{sys.executable} -m pip install unrar'."
                ) from exc
            _clear_unrar_import_cache()
        except LookupError as exc:
            if not auto_install or not _install_unrar_library():
                raise RuntimeError(
                    "Missing libunrar shared library. On Debian/Ubuntu install "
                    "libunrar5t64 or libunrar5, or set UNRAR_LIB_PATH to libunrar.so."
                ) from exc
            _clear_unrar_import_cache()

    raise RuntimeError("Unable to load unrar after installing dependencies.")


def open_rar(path: str | Path, *, auto_install: bool = True):
    rarfile = get_rarfile_module(auto_install=auto_install)
    return rarfile.RarFile(str(path))


class Scanner:
    def __init__(self, path: Path):
        pass
