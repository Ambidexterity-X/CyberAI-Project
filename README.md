# CyberAI Face Search

Streamlit front end plus a FastAPI backend for:

- enrolling people from images
- scanning a shared directory to find images containing enrolled faces
- viewing a per-person sighting timeline with capture timestamps and GPS location

## Stack

- `Streamlit` for the UI
- `FastAPI` for the backend API
- `Pillow` for face embedding extraction and EXIF metadata parsing
- `face_recognition` for face detection and 128-dim embedding generation
- JSON file (`data/registry.json`) for persistence — no database required

## Prerequisites

- Python `3.11.9`
- Git
- On Windows, the Microsoft Visual C++ Build Tools

The project uses `face_recognition`, which depends on native build tooling on Windows. If pip needs to compile packages, install the Visual Studio C++ build tools first so the environment can build those wheels successfully.

## Setup

1. On Windows, install a package manager if you do not already have one. `winget` is included with recent versions of Windows; if you prefer, you can use `Chocolatey` instead.
2. Install Python `3.11` on Windows:

```bash
winget install Python.Python.3.11
```

3. Install the Microsoft Visual C++ Build Tools on Windows if you do not already have them.
4. Create a virtual environment named `.venv`:

```bash
py -3.11 -m venv .venv
```

5. Activate the virtual environment:

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Command Prompt:

```bat
.venv\Scripts\activate.bat
```

6. Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

7. Copy `.env.example` to `.env` if you want to override defaults.
8. Run the backend:

```bash
uvicorn app.api.main:app --reload
```

9. Run the UI:

```bash
streamlit run streamlit_app.py
```

## Configuration

All settings are read from `.env`. The defaults work out of the box:

| Variable          | Default        | Description                                              |
|-------------------|----------------|----------------------------------------------------------|
| `DATA_DIR`        | `data`         | Root directory for uploads and the registry file         |
| `SHARED_DIR`      | `data/shared`  | Directory scanned for images to match against            |
| `MATCH_THRESHOLD` | `0.6`          | Minimum cosine similarity score to count as a match      |

## Usage

### Enroll a person
Upload a portrait containing exactly one face. The face embedding is stored in `data/registry.json`.

### Scan shared directory
Place images into `SHARED_DIR` (default `data/shared`). Select an enrolled person from the dropdown (or "All enrolled people") and click **Scan**. Each matched image is shown as a thumbnail alongside the person name and confidence score.

### Timeline
Select an enrolled person and click **Build Timeline**. The app scans the shared directory and displays every matched image in chronological order, grouped by day. Each entry shows:

- Capture timestamp — from EXIF `DateTimeOriginal` when present, otherwise file modification time
- GPS coordinates — from EXIF GPS tags when present, otherwise "Unknown location"
- Confidence score and bar
- Image thumbnail

### Data Management
Remove enrolled people and their face samples from the registry.

## Directory layout

```
data/
  registry.json       # enrolled people and face embeddings
  uploads/            # enrollment images saved on enroll
  shared/             # images to scan (place your files here)
app/
  api/main.py         # FastAPI endpoints
  services/
    face.py           # face detection and embedding extraction
    search.py         # shared directory scan and matching
    metadata.py       # EXIF timestamp and GPS extraction
    storage.py        # file upload helper
  store.py            # JSON registry read/write
  config.py           # settings from .env
  schemas.py          # Pydantic request/response models
streamlit_app.py      # Streamlit UI
```

## Windows Notes

If installation fails while building `face_recognition` or one of its dependencies, install the Visual C++ Build Tools from Microsoft and retry the `pip install -r requirements.txt` step inside `.venv`.

The repository was last verified with Python `3.11.9` in `.venv`.

## Notes

- Face matching uses 128-dimensional cosine similarity embeddings (dlib ResNet via `face_recognition`).
- The registry is a plain JSON file — no database server required.
- Images in `SHARED_DIR` are never modified or moved by the application.
- Enrollment images are saved to `data/uploads` with UUID filenames.
