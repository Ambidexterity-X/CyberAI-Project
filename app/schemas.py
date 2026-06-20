from __future__ import annotations

from pydantic import BaseModel, Field


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class PersonRead(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
    sample_count: int


class ImageMatchRead(BaseModel):
    person_id: int
    person_name: str
    score: float
    face_index: int
    sample_id: int


class ImageResultRead(BaseModel):
    image_path: str
    captured_at: str
    latitude: float | None
    longitude: float | None
    matches: list[ImageMatchRead]


class EnrollResponse(BaseModel):
    person: PersonRead
    sample_id: int
    image_path: str | None
    face_index: int
    message: str


class DeletePersonResponse(BaseModel):
    deleted_sample_count: int
    message: str


class ScanResponse(BaseModel):
    images_scanned: int
    images_matched: int
    results: list[ImageResultRead]
    shared_dir: str


class HealthResponse(BaseModel):
    status: str
