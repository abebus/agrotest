from pathlib import Path
import cchardet


def detect_encoding(path: str | Path) -> str:
    with open(path, "rb") as f:
        raw = f.read(10000)
    detected = cchardet.detect(raw)
    return detected["encoding"] or "utf-8"
