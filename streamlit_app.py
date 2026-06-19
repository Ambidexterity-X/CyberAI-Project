from __future__ import annotations

import html
from collections import defaultdict
from datetime import datetime, timezone

import requests
import streamlit as st


st.set_page_config(page_title="CyberAI Face Search", layout="wide")
BACKEND_URL = st.sidebar.text_input("Backend URL", value="http://localhost:8000")

st.markdown(
    """
    <style>
    :root {
        --bg: #081120;
        --panel: rgba(12, 18, 33, 0.72);
        --panel-strong: rgba(15, 23, 42, 0.9);
        --panel-soft: rgba(148, 163, 184, 0.08);
        --border: rgba(148, 163, 184, 0.18);
        --text: #e5eefb;
        --muted: rgba(203, 213, 225, 0.82);
        --accent: #67e8f9;
        --accent-2: #8b5cf6;
        --accent-3: #22c55e;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(139, 92, 246, 0.22), transparent 32%),
            radial-gradient(circle at top right, rgba(34, 197, 94, 0.16), transparent 24%),
            linear-gradient(180deg, #050816 0%, #081120 45%, #0b1426 100%);
        color: var(--text);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .app-hero {
        position: relative;
        overflow: hidden;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.1rem;
        border: 1px solid var(--border);
        border-radius: 1.4rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.58));
        box-shadow: 0 24px 60px rgba(2, 6, 23, 0.36);
    }
    .app-hero::after {
        content: "";
        position: absolute;
        inset: -30% auto auto 62%;
        width: 18rem;
        height: 18rem;
        background: radial-gradient(circle, rgba(103, 232, 249, 0.2) 0%, rgba(103, 232, 249, 0) 68%);
        pointer-events: none;
    }
    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: rgba(103, 232, 249, 0.12);
        color: var(--accent);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .app-title {
        margin: 0.65rem 0 0.35rem;
        font-size: 2.35rem;
        line-height: 1.05;
        color: var(--text);
        font-weight: 800;
        letter-spacing: -0.04em;
    }
    .app-subtitle {
        max-width: 60rem;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin-top: 1rem;
    }
    .feature-card {
        padding: 0.95rem 1rem;
        border: 1px solid var(--border);
        border-radius: 1rem;
        background: rgba(8, 17, 32, 0.5);
        backdrop-filter: blur(16px);
    }
    .feature-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.25rem;
        height: 2.25rem;
        border-radius: 0.7rem;
        margin-bottom: 0.65rem;
        font-size: 1.1rem;
        background: linear-gradient(135deg, rgba(103, 232, 249, 0.2), rgba(139, 92, 246, 0.18));
    }
    .feature-title {
        color: var(--text);
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .feature-copy {
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.45;
    }
    .section-card {
        padding: 1rem 1.1rem;
        border: 1px solid var(--border);
        border-radius: 1.15rem;
        background: rgba(15, 23, 42, 0.75);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.24);
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.8rem;
    }
    .section-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: 0.65rem;
        background: rgba(103, 232, 249, 0.12);
        color: var(--accent);
        font-size: 1rem;
    }
    .section-title {
        color: var(--text);
        font-size: 1.1rem;
        font-weight: 750;
    }
    .section-copy {
        color: var(--muted);
        margin-bottom: 0.9rem;
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: rgba(15, 23, 42, 0.38);
        padding: 0.35rem;
        border-radius: 999px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.65rem 1rem;
        color: var(--muted);
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(103, 232, 249, 0.18), rgba(139, 92, 246, 0.16)) !important;
        color: var(--text) !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stMultiSelect div {
        border-radius: 0.8rem !important;
    }
    .stButton > button {
        border-radius: 0.85rem;
        border: 1px solid rgba(103, 232, 249, 0.2);
        background: linear-gradient(135deg, rgba(103, 232, 249, 0.18), rgba(139, 92, 246, 0.22));
        color: white;
        padding: 0.65rem 1.05rem;
        font-weight: 700;
    }
    .stButton > button:hover {
        border-color: rgba(103, 232, 249, 0.44);
        transform: translateY(-1px);
    }
    .timeline-shell {
        position: relative;
        margin-top: 0.75rem;
        padding-left: 1.1rem;
        border-left: 1px solid rgba(148, 163, 184, 0.32);
    }
    .timeline-day {
        margin: 1.2rem 0 0.75rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(203, 213, 225, 0.88);
    }
    .timeline-item {
        position: relative;
        margin: 0 0 0.9rem;
        padding: 0.9rem 1rem 0.9rem 1rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 0.95rem;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.72));
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.22);
    }
    .timeline-item::before {
        content: "";
        position: absolute;
        left: -1.52rem;
        top: 1.15rem;
        width: 0.7rem;
        height: 0.7rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #4f46e5, #06b6d4);
        border: 3px solid #081120;
        box-shadow: 0 0 0 1px rgba(79, 70, 229, 0.16);
    }
    .timeline-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 0.75rem;
        align-items: center;
        color: rgba(226, 232, 240, 0.92);
        font-size: 0.92rem;
    }
    .timeline-time {
        font-weight: 700;
        color: rgba(255, 255, 255, 0.96);
    }
    .timeline-pill {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.18rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(103, 232, 249, 0.12);
        color: var(--accent);
    }
    .timeline-note {
        margin-top: 0.45rem;
        color: rgba(203, 213, 225, 0.88);
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str):
    return requests.get(f"{BACKEND_URL}{path}", timeout=30)


def api_post(path: str, files=None, data=None):
    return requests.post(f"{BACKEND_URL}{path}", files=files, data=data, timeout=120)


def api_delete(path: str):
    return requests.delete(f"{BACKEND_URL}{path}", timeout=30)


def parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def humanize_timestamp(value: str) -> tuple[str, str, str]:
    dt = parse_timestamp(value).astimezone()
    now = datetime.now(dt.tzinfo)
    delta = now - dt
    seconds = int(delta.total_seconds())
    if seconds < 0:
        human = "just now"
    elif seconds < 60:
        human = "just now" if seconds < 10 else f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        human = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400 and dt.date() == now.date():
        hours = seconds // 3600
        human = f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 172800 and (now.date() - dt.date()).days == 1:
        human = "yesterday"
    elif seconds < 604800:
        days = (now.date() - dt.date()).days
        human = f"{days} days ago"
    else:
        human = dt.strftime("%b %d, %Y")
    date_key = dt.strftime("%Y-%m-%d")
    date_label = dt.strftime("%A, %b %d, %Y")
    time_label = dt.strftime("%I:%M %p").lstrip("0")
    return date_key, date_label, f"{human} · {time_label}"


st.markdown(
    """
    <div class="app-hero">
        <span class="eyebrow">CyberAI operations hub</span>
        <h1 class="app-title">Face search, enrollment, and sightings in one control plane</h1>
        <div class="app-subtitle">
            Store a person once, match probe images quickly, and keep a clean activity trail with location-aware sightings.
        </div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🪪</div>
                <div class="feature-title">Enroll identities</div>
                <div class="feature-copy">Register a person from a single image and persist their face embedding.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔎</div>
                <div class="feature-title">Match probe images</div>
                <div class="feature-copy">Search against stored records and tune the confidence threshold.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📍</div>
                <div class="feature-title">Track sightings</div>
                <div class="feature-copy">Review history by person with timestamps, locations, and confidence scores.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_enroll, tab_search, tab_history = st.tabs(["🪪 Enroll", "🔎 Search", "📍 History"])

with tab_enroll:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">🪪</span>
            <div class="section-title">Enroll a person</div>
        </div>
        <div class="section-copy">Add a new identity to the database so future matches and sightings can be linked to a person.</div>
        """,
        unsafe_allow_html=True,
    )
    name = st.text_input("Person name")
    image = st.file_uploader("Enrollment image", type=["jpg", "jpeg", "png"], key="enroll_image")

    if st.button("Enroll", type="primary"):
        if not name or image is None:
            st.error("Provide a name and an image.")
        else:
            with st.spinner("Uploading and extracting face embedding..."):
                try:
                    response = api_post(
                        "/enroll",
                        files={"image": (image.name, image.getvalue(), image.type or "image/jpeg")},
                        data={"name": name},
                    )
                except requests.RequestException as exc:
                    st.error(f"Could not reach backend: {exc}")
                else:
                    if response.ok:
                        st.success(response.json()["message"])
                    else:
                        st.error(response.text)

with tab_search:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">🔎</span>
            <div class="section-title">Search for matches</div>
        </div>
        <div class="section-copy">Upload a probe image, set a threshold, and decide whether confident matches should be recorded automatically.</div>
        """,
        unsafe_allow_html=True,
    )
    search_image = st.file_uploader("Probe image", type=["jpg", "jpeg", "png"], key="search_image")
    search_location = st.text_input("Spotted location", placeholder="Optional", key="search_location")
    record = st.checkbox("Record sightings for confident matches", value=True)
    threshold = st.slider("Match threshold", min_value=0.0, max_value=1.0, value=0.6, step=0.01)

    if st.button("Search", type="primary"):
        if search_image is None:
            st.error("Upload a probe image first.")
        else:
            with st.spinner("Searching..."):
                try:
                    response = api_post(
                        "/search",
                        files={"image": (search_image.name, search_image.getvalue(), search_image.type or "image/jpeg")},
                        data={
                            "location": search_location,
                            "record_sightings": str(record).lower(),
                            "threshold": str(threshold),
                        },
                    )
                except requests.RequestException as exc:
                    st.error(f"Could not reach backend: {exc}")
                else:
                    if response.ok:
                        payload = response.json()
                        st.success(f"Created sightings: {payload['sightings_created']}")
                        for face_result in payload["results"]:
                            st.markdown(f"### Detected face {face_result['face_index']}")
                            if not face_result["matches"]:
                                st.info("No stored faces matched this detection.")
                                continue
                            for match in face_result["matches"]:
                                st.write(
                                    f"{match['person_name']} | score={match['score']:.3f} | sample={match['sample_id']}"
                                )
                    else:
                        st.error(response.text)

with tab_history:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">📍</span>
            <div class="section-title">Sighting history</div>
        </div>
        <div class="section-copy">Browse sightings per person and clear history when you need a clean audit trail.</div>
        """,
        unsafe_allow_html=True,
    )
    try:
        people_response = api_get("/people")
    except requests.RequestException as exc:
        st.error(f"Could not reach backend: {exc}")
    else:
        if not people_response.ok:
            st.error(people_response.text)
        else:
            people = people_response.json()
            if not people:
                st.info("No enrolled people yet.")
            else:
                selected = st.selectbox("Select person", options=people, format_func=lambda item: item["name"])

                st.divider()
                st.subheader("Remove enrolled user")
                st.warning(
                    "This permanently deletes the person, their face samples, and their associated sightings."
                )
                confirm_remove = st.checkbox(
                    f"I understand this will remove {selected['name']} from enrollment.",
                    key=f"confirm_remove_{selected['id']}",
                )
                if st.button(
                    "Remove enrolled user",
                    type="secondary",
                    disabled=not confirm_remove,
                    key=f"remove_person_{selected['id']}",
                ):
                    try:
                        delete_response = api_delete(f"/people/{selected['id']}")
                    except requests.RequestException as exc:
                        st.error(f"Could not reach backend: {exc}")
                    else:
                        if delete_response.ok:
                            payload = delete_response.json()
                            st.success(payload["message"])
                            st.info(
                                "Deleted "
                                f"{payload['deleted_sample_count']} face sample"
                                f"{'s' if payload['deleted_sample_count'] != 1 else ''} and "
                                f"{payload['deleted_sighting_count']} sighting"
                                f"{'s' if payload['deleted_sighting_count'] != 1 else ''}."
                            )
                            st.rerun()
                        else:
                            st.error(delete_response.text)

                try:
                    sightings_response = api_get(f"/people/{selected['id']}/sightings")
                except requests.RequestException as exc:
                    st.error(f"Could not reach backend: {exc}")
                else:
                    if sightings_response.ok:
                        sightings = sightings_response.json()
                        if not sightings:
                            st.info("No sightings recorded for this person.")
                        else:
                            grouped_sightings: dict[str, list[dict]] = defaultdict(list)
                            date_labels: dict[str, str] = {}
                            for sighting in sightings:
                                date_key, date_label, human_label = humanize_timestamp(sighting["spotted_at"])
                                grouped_sightings[date_key].append({**sighting, "human_label": human_label})
                                date_labels[date_key] = date_label

                            st.markdown('<div class="timeline-shell">', unsafe_allow_html=True)
                            for date_key in sorted(grouped_sightings.keys(), reverse=True):
                                st.markdown(
                                    f'<div class="timeline-day">{html.escape(date_labels[date_key])}</div>',
                                    unsafe_allow_html=True,
                                )
                                for sighting in grouped_sightings[date_key]:
                                    location = html.escape(sighting["location"] or "Unknown location")
                                    human_label = html.escape(sighting["human_label"])
                                    notes = html.escape(sighting["notes"]) if sighting["notes"] else ""
                                    st.markdown(
                                        f"""
                                        <div class="timeline-item">
                                            <div class="timeline-meta">
                                                <span class="timeline-time">{human_label}</span>
                                                <span class="timeline-pill">Face #{sighting["face_index"]}</span>
                                                <span>{location}</span>
                                                <span>Confidence {sighting["confidence"]:.3f}</span>
                                            </div>
                                            {f'<div class="timeline-note">{notes}</div>' if notes else ""}
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                            st.markdown("</div>", unsafe_allow_html=True)

                            st.divider()
                            st.subheader("Clear history")
                            st.warning("This deletes all sightings for the selected person. It cannot be undone.")
                            confirm_clear = st.checkbox(
                                f"I understand this will delete {selected['name']}'s sightings.",
                                key=f"confirm_clear_{selected['id']}",
                            )
                            if st.button(
                                "Clear selected history",
                                type="secondary",
                                disabled=not confirm_clear,
                                key=f"clear_history_{selected['id']}",
                            ):
                                try:
                                    delete_response = api_delete(f"/people/{selected['id']}/sightings")
                                except requests.RequestException as exc:
                                    st.error(f"Could not reach backend: {exc}")
                                else:
                                    if delete_response.ok:
                                        deleted_count = delete_response.json().get("deleted_count", 0)
                                        st.success(f"Deleted {deleted_count} sighting{'s' if deleted_count != 1 else ''}.")
                                        st.rerun()
                                    else:
                                        st.error(delete_response.text)
                    else:
                        st.error(sightings_response.text)
