# CyberAI Face Search

Streamlit front end plus a FastAPI backend for:

- enrolling people from images
- searching probe images against stored face records
- recording timestamped sightings with location metadata

## Stack

- `Streamlit` for the UI
- `FastAPI` for the backend API
- `SQLAlchemy` for persistence
- `PostgreSQL` recommended for deployment
- `SQLite` supported by default for local development

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
8. Set the database URL if you want PostgreSQL:

```bash
set DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/cyberai
```

9. Run the backend:

```bash
uvicorn app.api.main:app --reload
```

10. Run the UI:

```bash
streamlit run streamlit_app.py
```

## Windows Notes

If installation fails while building `face_recognition` or one of its dependencies, install the Visual C++ Build Tools from Microsoft and retry the `pip install -r requirements.txt` step inside `.venv`.

The repository was last verified with Python `3.11.9` in `.venv`.

## Notes

- Face matching uses stored embeddings and similarity scoring.
- Sightings are stored with a UTC timestamp and a free-form location string.
- The image store is local under `data/uploads` by default.
