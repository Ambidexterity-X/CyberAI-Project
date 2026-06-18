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

## Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` if you want to override defaults.
4. Set the database URL if you want PostgreSQL:

```bash
set DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/cyberai
```

5. Run the backend:

```bash
uvicorn app.api.main:app --reload
```

6. Run the UI:

```bash
streamlit run streamlit_app.py
```

## Notes

- Face matching uses stored embeddings and similarity scoring.
- Sightings are stored with a UTC timestamp and a free-form location string.
- The image store is local under `data/uploads` by default.
