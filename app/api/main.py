from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db_session, init_db
from app.models import FaceSample, Person, Sighting
from app.schemas import (
    EnrollResponse,
    HealthResponse,
    MatchRead,
    PersonRead,
    SearchResponse,
    SearchResultRead,
    SightingRead,
)
from app.services.face import FaceDetectionError, embedding_to_json, extract_embeddings
from app.services.search import search_and_optionally_record
from app.services.storage import save_upload

settings = get_settings()
app = FastAPI(title=settings.api_title)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def db_session():
    with get_db_session() as session:
        yield session


def person_to_read(person: Person) -> PersonRead:
    return PersonRead(
        id=person.id,
        name=person.name,
        created_at=person.created_at,
        updated_at=person.updated_at,
    )


def sighting_to_read(sighting: Sighting) -> SightingRead:
    person_name = sighting.person.name if sighting.person else None
    return SightingRead(
        id=sighting.id,
        person_id=sighting.person_id,
        person_name=person_name,
        image_path=sighting.image_path,
        location=sighting.location,
        spotted_at=sighting.spotted_at,
        confidence=sighting.confidence,
        face_index=sighting.face_index,
        notes=sighting.notes,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/enroll", response_model=EnrollResponse)
async def enroll_person(
    name: str = Form(...),
    image: UploadFile = File(...),
    session: Session = Depends(db_session),
) -> EnrollResponse:
    content = await image.read()
    stored_path = save_upload(settings.uploads_dir, image.filename, content)

    try:
        embeddings = extract_embeddings(content)
    except FaceDetectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if len(embeddings) != 1:
        raise HTTPException(
            status_code=400,
            detail="Enrollment images must contain exactly one clear face.",
        )

    person = session.scalar(select(Person).where(Person.name == name))
    if person is None:
        person = Person(name=name)
        session.add(person)
        session.flush()

    sample = FaceSample(
        person_id=person.id,
        image_path=stored_path,
        embedding_json=embedding_to_json(embeddings[0].embedding),
        face_index=embeddings[0].face_index,
    )
    session.add(sample)
    session.flush()

    return EnrollResponse(
        person=person_to_read(person),
        sample_id=sample.id,
        image_path=stored_path,
        face_index=embeddings[0].face_index,
        message="Person enrolled successfully.",
    )


@app.post("/search", response_model=SearchResponse)
async def search_faces(
    image: UploadFile = File(...),
    location: str | None = Form(default=None),
    record_sightings: bool = Form(default=True),
    threshold: float | None = Form(default=None),
    session: Session = Depends(db_session),
) -> SearchResponse:
    content = await image.read()
    stored_path = save_upload(settings.uploads_dir, image.filename, content)

    try:
        embeddings = extract_embeddings(content)
    except FaceDetectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results, sighting_ids = search_and_optionally_record(
        session,
        embeddings,
        image_path=stored_path,
        location=location,
        record_sightings=record_sightings,
        threshold=threshold,
    )

    return SearchResponse(
        results=[
            SearchResultRead(
                face_index=item["face_index"],
                matches=[MatchRead(**match) for match in item["matches"]],
            )
            for item in results
        ],
        sightings_created=sighting_ids,
    )


@app.get("/people", response_model=list[PersonRead])
def list_people(session: Session = Depends(db_session)) -> list[PersonRead]:
    people = session.scalars(select(Person).order_by(Person.name.asc())).all()
    return [person_to_read(person) for person in people]


@app.get("/people/{person_id}/sightings", response_model=list[SightingRead])
def list_person_sightings(person_id: int, session: Session = Depends(db_session)) -> list[SightingRead]:
    sightings = (
        session.scalars(
            select(Sighting)
            .where(Sighting.person_id == person_id)
            .order_by(Sighting.spotted_at.desc())
        )
        .unique()
        .all()
    )
    return [sighting_to_read(sighting) for sighting in sightings]
