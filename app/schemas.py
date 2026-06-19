from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class PersonRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class MatchRead(BaseModel):
    person_id: int
    person_name: str
    score: float
    face_index: int
    sample_id: int


class SearchResultRead(BaseModel):
    face_index: int
    matches: list[MatchRead]


class SightingRead(BaseModel):
    id: int
    person_id: int | None
    person_name: str | None
    image_path: str | None
    location: str | None
    spotted_at: datetime
    confidence: float
    face_index: int
    notes: str | None


class EnrollResponse(BaseModel):
    person: PersonRead
    sample_id: int
    image_path: str | None
    face_index: int
    message: str


class DeletePersonResponse(BaseModel):
    deleted_sample_count: int
    deleted_sighting_count: int
    message: str


class SearchResponse(BaseModel):
    results: list[SearchResultRead]
    sightings_created: list[int]


class ClearSightingsResponse(BaseModel):
    deleted_count: int


class HealthResponse(BaseModel):
    status: str
