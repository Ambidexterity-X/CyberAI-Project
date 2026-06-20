from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class FaceSampleRecord(TypedDict):
    sample_id: int
    image_path: str | None
    embedding: list[float]
    face_index: int
    created_at: str


class PersonRecord(TypedDict):
    id: int
    name: str
    created_at: str
    updated_at: str
    samples: list[FaceSampleRecord]


class Registry(TypedDict):
    next_person_id: int
    next_sample_id: int
    people: list[PersonRecord]


_lock = threading.Lock()


def _load(path: Path) -> Registry:
    if path.exists():
        with open(path) as fh:
            return json.load(fh)
    return {"next_person_id": 1, "next_sample_id": 1, "people": []}


def _save(path: Path, data: Registry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def get_all_people(registry_path: Path) -> list[PersonRecord]:
    with _lock:
        data = _load(registry_path)
    return sorted(data["people"], key=lambda p: p["name"])


def get_person_by_id(registry_path: Path, person_id: int) -> PersonRecord | None:
    with _lock:
        data = _load(registry_path)
    for person in data["people"]:
        if person["id"] == person_id:
            return person
    return None


def get_person_by_name(registry_path: Path, name: str) -> PersonRecord | None:
    with _lock:
        data = _load(registry_path)
    for person in data["people"]:
        if person["name"] == name:
            return person
    return None


def upsert_person_with_sample(
    registry_path: Path,
    name: str,
    embedding: list[float],
    face_index: int,
    image_path: str | None,
) -> tuple[PersonRecord, FaceSampleRecord]:
    with _lock:
        data = _load(registry_path)

        person: PersonRecord | None = None
        for p in data["people"]:
            if p["name"] == name:
                person = p
                break

        if person is None:
            person = {
                "id": data["next_person_id"],
                "name": name,
                "created_at": _utcnow(),
                "updated_at": _utcnow(),
                "samples": [],
            }
            data["next_person_id"] += 1
            data["people"].append(person)
        else:
            person["updated_at"] = _utcnow()

        sample: FaceSampleRecord = {
            "sample_id": data["next_sample_id"],
            "image_path": image_path,
            "embedding": embedding,
            "face_index": face_index,
            "created_at": _utcnow(),
        }
        data["next_sample_id"] += 1
        person["samples"].append(sample)

        _save(registry_path, data)
        return person, sample


def delete_person(registry_path: Path, person_id: int) -> PersonRecord | None:
    with _lock:
        data = _load(registry_path)
        for i, p in enumerate(data["people"]):
            if p["id"] == person_id:
                removed = data["people"].pop(i)
                _save(registry_path, data)
                return removed
    return None
