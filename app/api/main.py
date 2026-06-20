from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import (
    DeletePersonResponse,
    EnrollResponse,
    HealthResponse,
    ImageMatchRead,
    ImageResultRead,
    PersonRead,
    ScanResponse,
)
from app.services.face import FaceDetectionError, extract_embeddings
from app.services.search import scan_shared_directory
from app.services.storage import save_upload
from app.store import (
    delete_person,
    get_all_people,
    get_person_by_id,
    upsert_person_with_sample,
)

settings = get_settings()
app = FastAPI(title=settings.api_title)


def _person_read(person) -> PersonRead:
    return PersonRead(
        id=person["id"],
        name=person["name"],
        created_at=person["created_at"],
        updated_at=person["updated_at"],
        sample_count=len(person["samples"]),
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/enroll", response_model=EnrollResponse)
async def enroll_person(
    name: str = Form(...),
    image: UploadFile = File(...),
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

    enc = embeddings[0]
    person, sample = upsert_person_with_sample(
        settings.registry_path,
        name=name,
        embedding=enc.embedding,
        face_index=enc.face_index,
        image_path=stored_path,
    )

    return EnrollResponse(
        person=_person_read(person),
        sample_id=sample["sample_id"],
        image_path=stored_path,
        face_index=enc.face_index,
        message="Person enrolled successfully.",
    )


@app.post("/scan", response_model=ScanResponse)
def scan_faces(
    threshold: float | None = Form(default=None),
) -> ScanResponse:
    cutoff = threshold if threshold is not None else settings.match_threshold
    people = get_all_people(settings.registry_path)

    if not people:
        raise HTTPException(status_code=400, detail="No enrolled people to match against.")

    all_images = [
        p for p in sorted(settings.shared_dir.iterdir())
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    ]

    results = scan_shared_directory(settings.shared_dir, people, cutoff)

    return ScanResponse(
        images_scanned=len(all_images),
        images_matched=len(results),
        shared_dir=str(settings.shared_dir),
        results=[
            ImageResultRead(
                image_path=r.image_path,
                captured_at=r.captured_at,
                latitude=r.latitude,
                longitude=r.longitude,
                matches=[
                    ImageMatchRead(
                        person_id=m.person_id,
                        person_name=m.person_name,
                        score=m.score,
                        face_index=m.face_index,
                        sample_id=m.sample_id,
                    )
                    for m in r.matches
                ],
            )
            for r in results
        ],
    )


@app.get("/people", response_model=list[PersonRead])
def list_people() -> list[PersonRead]:
    return [_person_read(p) for p in get_all_people(settings.registry_path)]


@app.delete("/people/{person_id}", response_model=DeletePersonResponse)
def remove_person(person_id: int) -> DeletePersonResponse:
    person = get_person_by_id(settings.registry_path, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found.")

    sample_count = len(person["samples"])
    delete_person(settings.registry_path, person_id)

    return DeletePersonResponse(
        deleted_sample_count=sample_count,
        message=f"Removed enrolled user '{person['name']}'.",
    )
