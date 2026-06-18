from __future__ import annotations

import uuid
from pathlib import Path


def save_upload(target_dir: Path, filename: str | None, content: bytes) -> str:
    suffix = ""
    if filename:
        suffix = Path(filename).suffix
    target_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    path = target_dir / stored_name
    path.write_bytes(content)
    return str(path)
