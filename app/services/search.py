from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.services.face import FaceEncoding, FaceDetectionError, cosine_similarity, extract_embeddings
from app.services.metadata import extract_captured_at, extract_gps
from app.store import PersonRecord


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass
class ImageMatch:
    person_id: int
    person_name: str
    score: float
    face_index: int
    sample_id: int


@dataclass
class ImageResult:
    image_path: str
    captured_at: str                        # ISO-8601 UTC string
    latitude: float | None                  # EXIF GPS latitude, or None
    longitude: float | None                 # EXIF GPS longitude, or None
    matches: list[ImageMatch]


def _find_best_match(
    people: list[PersonRecord],
    probe: FaceEncoding,
    limit: int = 5,
) -> list[ImageMatch]:
    candidates: list[ImageMatch] = []
    for person in people:
        for sample in person["samples"]:
            score = cosine_similarity(probe.embedding, sample["embedding"])
            candidates.append(
                ImageMatch(
                    person_id=person["id"],
                    person_name=person["name"],
                    score=score,
                    face_index=probe.face_index,
                    sample_id=sample["sample_id"],
                )
            )
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:limit]


def scan_shared_directory(
    shared_dir: Path,
    people: list[PersonRecord],
    threshold: float,
) -> list[ImageResult]:
    """Scan every image in shared_dir and return which enrolled people appear in them."""
    results: list[ImageResult] = []

    image_paths = [
        p for p in sorted(shared_dir.iterdir())
        if p.is_file() and p.suffix.lower() in _IMAGE_EXTENSIONS
    ]

    for image_path in image_paths:
        try:
            content = image_path.read_bytes()
            embeddings = extract_embeddings(content)
        except (FaceDetectionError, Exception):
            continue

        top_matches: list[ImageMatch] = []
        for probe in embeddings:
            candidates = _find_best_match(people, probe)
            if candidates and candidates[0].score >= threshold:
                top_matches.append(candidates[0])

        if top_matches:
            captured_at = extract_captured_at(image_path).isoformat()
            gps = extract_gps(image_path)
            results.append(
                ImageResult(
                    image_path=str(image_path),
                    captured_at=captured_at,
                    latitude=gps[0] if gps else None,
                    longitude=gps[1] if gps else None,
                    matches=top_matches,
                )
            )

    return results
