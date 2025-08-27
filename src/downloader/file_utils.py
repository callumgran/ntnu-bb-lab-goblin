import re
import time
from pathlib import Path


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w.\-]+", "", name)
    return name


def split_extension(filename: str):
    p = Path(filename)
    if len(p.suffixes) > 1:
        ext = "".join(p.suffixes)
        stem = p.name[: -len(ext)]
    else:
        ext = p.suffix
        stem = p.stem
    return stem, ext


def on_downloads_complete(download_dir, idle_seconds=2):
    last_active = time.time()
    while True:
        partials = list(Path(download_dir).glob("*.part"))
        if partials:
            last_active = time.time()
        else:
            if time.time() - last_active >= idle_seconds:
                return
        time.sleep(0.5)
