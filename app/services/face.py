from __future__ import annotations

import io
import json
from dataclasses import dataclass

import numpy as np
from PIL import Image


class FaceDetectionError(RuntimeError):
    pass


@dataclass
class FaceEncoding:
    embedding: list[float]
    face_index: int


def _load_face_recognition():
    try:
        import face_recognition  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency issue
        raise RuntimeError(
            "face_recognition is required. Install project dependencies first."
        ) from exc
    return face_recognition


def image_bytes_to_array(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.asarray(image)


def extract_embeddings(image_bytes: bytes) -> list[FaceEncoding]:
    face_recognition = _load_face_recognition()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_array = np.asarray(image)

    locations = face_recognition.face_locations(image_array, model="hog")
    if not locations:
        raise FaceDetectionError("No face detected in the uploaded image.")

    encodings = face_recognition.face_encodings(image_array, known_face_locations=locations)
    results: list[FaceEncoding] = []
    for index, encoding in enumerate(encodings):
        results.append(FaceEncoding(embedding=encoding.astype(float).tolist(), face_index=index))
    return results


def cosine_similarity(left: list[float], right: list[float]) -> float:
    left_vec = np.asarray(left, dtype=np.float32)
    right_vec = np.asarray(right, dtype=np.float32)
    denom = float(np.linalg.norm(left_vec) * np.linalg.norm(right_vec))
    if denom == 0:
        return 0.0
    return float(np.dot(left_vec, right_vec) / denom)


def euclidean_distance(left: list[float], right: list[float]) -> float:
    left_vec = np.asarray(left, dtype=np.float32)
    right_vec = np.asarray(right, dtype=np.float32)
    return float(np.linalg.norm(left_vec - right_vec))


def embedding_to_json(embedding: list[float]) -> str:
    return json.dumps(embedding)


def embedding_from_json(payload: str) -> list[float]:
    return [float(value) for value in json.loads(payload)]
