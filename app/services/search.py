from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import FaceSample, Person, Sighting
from app.services.face import FaceEncoding, cosine_similarity, embedding_from_json


@dataclass
class MatchCandidate:
    person_id: int
    person_name: str
    score: float
    face_index: int
    sample_id: int


def find_best_matches(session: Session, probe: FaceEncoding, limit: int = 5) -> list[MatchCandidate]:
    sample_rows = session.execute(
        select(FaceSample, Person).join(Person, FaceSample.person_id == Person.id)
    ).all()

    candidates: list[MatchCandidate] = []
    for sample, person in sample_rows:
        score = cosine_similarity(probe.embedding, embedding_from_json(sample.embedding_json))
        candidates.append(
            MatchCandidate(
                person_id=person.id,
                person_name=person.name,
                score=score,
                face_index=probe.face_index,
                sample_id=sample.id,
            )
        )

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates[:limit]


def record_sighting(
    session: Session,
    *,
    person_id: int | None,
    confidence: float,
    image_path: str | None,
    location: str | None,
    face_index: int,
    notes: str | None = None,
) -> Sighting:
    sighting = Sighting(
        person_id=person_id,
        confidence=confidence,
        image_path=image_path,
        location=location,
        face_index=face_index,
        notes=notes,
    )
    session.add(sighting)
    session.flush()
    return sighting


def search_and_optionally_record(
    session: Session,
    embeddings: list[FaceEncoding],
    *,
    image_path: str | None,
    location: str | None,
    record_sightings: bool = True,
    threshold: float | None = None,
) -> tuple[list[dict], list[int]]:
    settings = get_settings()
    cutoff = threshold if threshold is not None else settings.match_threshold
    results: list[dict] = []
    created_sightings: list[int] = []

    for probe in embeddings:
        matches = find_best_matches(session, probe)
        results.append(
            {
                "face_index": probe.face_index,
                "matches": [match.__dict__ for match in matches],
            }
        )

        if not record_sightings or not matches:
            continue

        best = matches[0]
        if best.score < cutoff:
            continue

        sighting = record_sighting(
            session,
            person_id=best.person_id,
            confidence=best.score,
            image_path=image_path,
            location=location,
            face_index=probe.face_index,
            notes="Auto-recorded from search",
        )
        created_sightings.append(sighting.id)

    return results, created_sightings
