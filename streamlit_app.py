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
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.9rem 0 1rem;
    }
    .summary-card {
        padding: 0.9rem 1rem;
        border: 1px solid var(--border);
        border-radius: 1rem;
        background: linear-gradient(180deg, rgba(8, 17, 32, 0.82), rgba(15, 23, 42, 0.6));
    }
    .summary-label {
        color: rgba(203, 213, 225, 0.8);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .summary-value {
        margin-top: 0.35rem;
        color: var(--text);
        font-size: 1.15rem;
        font-weight: 800;
    }
    .summary-note {
        margin-top: 0.2rem;
        color: var(--muted);
        font-size: 0.86rem;
    }
    .match-list {
        display: grid;
        gap: 0.8rem;
    }
    .match-card {
        padding: 0.95rem 1rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 1rem;
        background: rgba(8, 17, 32, 0.54);
    }
    .match-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin-bottom: 0.8rem;
    }
    .match-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.18rem 0.6rem;
        font-size: 0.74rem;
        font-weight: 800;
        background: rgba(103, 232, 249, 0.12);
        color: var(--accent);
    }
    .match-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem 0.6rem;
        align-items: center;
        margin-bottom: 0.35rem;
        color: rgba(226, 232, 240, 0.94);
        font-size: 0.88rem;
    }
    .match-name {
        font-weight: 750;
        color: var(--text);
    }
    .match-path {
        color: var(--muted);
        font-size: 0.8rem;
        font-family: monospace;
        word-break: break-all;
        margin-top: 0.3rem;
    }
    .confidence-track {
        height: 0.45rem;
        margin-top: 0.55rem;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.16);
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #22c55e, #67e8f9 55%, #8b5cf6);
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
        padding: 0.9rem 1rem;
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
    }
    .timeline-time {
        font-weight: 700;
        color: rgba(255, 255, 255, 0.96);
    }
    .timeline-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 0.75rem;
        align-items: center;
        color: rgba(226, 232, 240, 0.92);
        font-size: 0.92rem;
        margin-bottom: 0.4rem;
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
    .timeline-location {
        margin-top: 0.3rem;
        color: rgba(203, 213, 225, 0.8);
        font-size: 0.88rem;
    }
    .timeline-file {
        margin-top: 0.25rem;
        color: var(--muted);
        font-size: 0.78rem;
        font-family: monospace;
        word-break: break-all;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str):
    return requests.get(f"{BACKEND_URL}{path}", timeout=30)


def api_post(path: str, files=None, data=None):
    return requests.post(f"{BACKEND_URL}{path}", files=files, data=data, timeout=300)


def api_delete(path: str):
    return requests.delete(f"{BACKEND_URL}{path}", timeout=30)


def humanize_timestamp(iso_value: str) -> tuple[str, str, str]:
    """Return (day_key, day_label, human_label) for an ISO-8601 UTC string."""
    dt = datetime.fromisoformat(iso_value.replace("Z", "+00:00")).astimezone()
    now = datetime.now(dt.tzinfo)
    delta = now - dt
    seconds = int(delta.total_seconds())
    if seconds < 0:
        human = "just now"
    elif seconds < 60:
        human = "just now" if seconds < 10 else f"{seconds} seconds ago"
    elif seconds < 3600:
        m = seconds // 60
        human = f"{m} minute{'s' if m != 1 else ''} ago"
    elif seconds < 86400 and dt.date() == now.date():
        h = seconds // 3600
        human = f"{h} hour{'s' if h != 1 else ''} ago"
    elif seconds < 172800 and (now.date() - dt.date()).days == 1:
        human = "yesterday"
    elif seconds < 604800:
        d = (now.date() - dt.date()).days
        human = f"{d} days ago"
    else:
        human = dt.strftime("%b %d, %Y")
    time_label = dt.strftime("%I:%M %p").lstrip("0")
    return dt.strftime("%Y-%m-%d"), dt.strftime("%A, %b %d, %Y"), f"{human} · {time_label}"


st.markdown(
    """
    <div class="app-hero">
        <span class="eyebrow">CyberAI operations hub</span>
        <h1 class="app-title">Face search, enrollment, and shared directory scanning</h1>
        <div class="app-subtitle">
            Enroll a person once, then scan a shared directory to find every image they appear in.
        </div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🪪</div>
                <div class="feature-title">Enroll identities</div>
                <div class="feature-copy">Register a person from a single image and persist their face embedding.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📂</div>
                <div class="feature-title">Scan shared directory</div>
                <div class="feature-copy">Search every image in the shared folder and match against enrolled faces.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🗂️</div>
                <div class="feature-title">Manage enrollments</div>
                <div class="feature-copy">View enrolled people and remove them when no longer needed.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_enroll, tab_scan, tab_timeline, tab_data_management = st.tabs(
    ["🪪 Enroll", "📂 Scan Directory", "📍 Timeline", "🗂️ Data Management"]
)

with tab_enroll:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">🪪</span>
            <div class="section-title">Enroll a person</div>
        </div>
        <div class="section-copy">Add a new identity so future scans can match images against this person.</div>
        """,
        unsafe_allow_html=True,
    )
    name = st.text_input("Person name")
    image = st.file_uploader("Enrollment image (must contain exactly one face)", type=["jpg", "jpeg", "png"], key="enroll_image")

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

with tab_scan:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">📂</span>
            <div class="section-title">Scan shared directory</div>
        </div>
        <div class="section-copy">
            Select an enrolled person to filter results, set a confidence threshold, and scan.
            Place the images you want to search in the shared directory before running the scan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        scan_people_resp = api_get("/people")
        scan_people = scan_people_resp.json() if scan_people_resp.ok else []
    except requests.RequestException:
        scan_people = []

    _ALL_SENTINEL = {"id": None, "name": "All enrolled people"}
    scan_person_options = [_ALL_SENTINEL] + scan_people
    scan_selected = st.selectbox(
        "Filter by person",
        options=scan_person_options,
        format_func=lambda p: p["name"],
        key="scan_person",
    )
    threshold = st.slider("Match threshold", min_value=0.0, max_value=1.0, value=0.6, step=0.01)

    if st.button("Scan", type="primary"):
        if scan_people and scan_selected["id"] is None and not scan_people:
            st.error("No enrolled people to match against.")
        else:
            with st.spinner("Scanning shared directory..."):
                try:
                    response = api_post(
                        "/scan",
                        data={"threshold": str(threshold)},
                    )
                except requests.RequestException as exc:
                    st.error(f"Could not reach backend: {exc}")
                else:
                    if response.ok:
                        payload = response.json()

                        # Filter to the selected person when not "All"
                        target_id = scan_selected["id"]
                        if target_id is not None:
                            filtered_results = []
                            for img_result in payload["results"]:
                                person_matches = [
                                    m for m in img_result["matches"]
                                    if m["person_id"] == target_id
                                ]
                                if person_matches:
                                    filtered_results.append({
                                        **img_result,
                                        "matches": person_matches,
                                    })
                        else:
                            filtered_results = payload["results"]

                        st.markdown(
                            f"""
                            <div class="section-card">
                                <div class="summary-grid">
                                    <div class="summary-card">
                                        <div class="summary-label">Images scanned</div>
                                        <div class="summary-value">{payload['images_scanned']}</div>
                                        <div class="summary-note">Total images found in the shared directory.</div>
                                    </div>
                                    <div class="summary-card">
                                        <div class="summary-label">Images with matches</div>
                                        <div class="summary-value">{len(filtered_results)}</div>
                                        <div class="summary-note">
                                            {'For ' + html.escape(scan_selected['name']) + '.' if target_id else 'Across all enrolled people.'}
                                        </div>
                                    </div>
                                    <div class="summary-card">
                                        <div class="summary-label">Threshold</div>
                                        <div class="summary-value">{threshold:.2f}</div>
                                        <div class="summary-note">Shared dir: {html.escape(payload['shared_dir'])}</div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if not filtered_results:
                            st.info(
                                f"No matches found for **{html.escape(scan_selected['name'])}**."
                                if target_id else "No matches found in the shared directory."
                            )
                        else:
                            for image_result in filtered_results:
                                image_filename = html.escape(image_result["image_path"].split("/")[-1])
                                full_path = html.escape(image_result["image_path"])

                                thumb_col, info_col = st.columns([1, 2], gap="medium")
                                with thumb_col:
                                    try:
                                        st.image(
                                            image_result["image_path"],
                                            use_container_width=True,
                                            caption=image_filename,
                                        )
                                    except Exception:
                                        st.caption(f"Could not load: {image_filename}")

                                with info_col:
                                    st.markdown(
                                        f"""
                                        <div class="match-card" style="height: 100%;">
                                            <div class="match-header">
                                                <span class="match-badge">{len(image_result["matches"])} match{'es' if len(image_result['matches']) != 1 else ''}</span>
                                            </div>
                                            <div class="match-path">{full_path}</div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    for match in image_result["matches"]:
                                        score = max(0.0, min(float(match["score"]), 1.0))
                                        st.markdown(
                                            f"""
                                            <div class="match-meta" style="margin-top: 0.7rem;">
                                                <span class="match-name">{html.escape(match['person_name'])}</span>
                                                <span>Score {score:.3f}</span>
                                                <span style="color: var(--muted); font-size: 0.8rem;">face #{match['face_index']}</span>
                                            </div>
                                            <div class="confidence-track">
                                                <div class="confidence-fill" style="width: {score * 100:.1f}%;"></div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                                    st.markdown("</div>", unsafe_allow_html=True)

                                st.divider()
                    else:
                        st.error(response.text)

with tab_timeline:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">📍</span>
            <div class="section-title">Sighting timeline</div>
        </div>
        <div class="section-copy">
            Select an enrolled person, set a confidence threshold, and build a chronological
            timeline of every image in the shared directory where they appear — with capture
            time and GPS location extracted from image EXIF metadata.
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        people_resp = api_get("/people")
    except requests.RequestException as exc:
        st.error(f"Could not reach backend: {exc}")
        people_resp = None

    if people_resp is not None:
        if not people_resp.ok:
            st.error(people_resp.text)
        else:
            people = people_resp.json()
            if not people:
                st.info("No enrolled people yet. Enroll someone first.")
            else:
                selected = st.selectbox(
                    "Select person",
                    options=people,
                    format_func=lambda p: p["name"],
                    key="timeline_person",
                )
                tl_threshold = st.slider(
                    "Match threshold",
                    min_value=0.0, max_value=1.0, value=0.6, step=0.01,
                    key="timeline_threshold",
                )

                if st.button("Build Timeline", type="primary", key="timeline_build"):
                    with st.spinner("Scanning shared directory…"):
                        try:
                            scan_resp = api_post(
                                "/scan",
                                data={"threshold": str(tl_threshold)},
                            )
                        except requests.RequestException as exc:
                            st.error(f"Could not reach backend: {exc}")
                            scan_resp = None

                    if scan_resp is not None:
                        if not scan_resp.ok:
                            st.error(scan_resp.text)
                        else:
                            payload = scan_resp.json()
                            target_id = selected["id"]

                            # Filter to images where the selected person appears
                            person_results = []
                            for img_result in payload["results"]:
                                person_matches = [
                                    m for m in img_result["matches"]
                                    if m["person_id"] == target_id
                                ]
                                if person_matches:
                                    best = max(person_matches, key=lambda m: m["score"])
                                    person_results.append({
                                        **img_result,
                                        "best_match": best,
                                    })

                            if not person_results:
                                st.info(
                                    f"No sightings found for **{html.escape(selected['name'])}** "
                                    f"at threshold {tl_threshold:.2f}."
                                )
                            else:
                                # Group by local date
                                grouped: dict[str, list[dict]] = defaultdict(list)
                                day_labels: dict[str, str] = {}
                                for item in person_results:
                                    day_key, day_label, human_label = humanize_timestamp(
                                        item["captured_at"]
                                    )
                                    grouped[day_key].append({**item, "human_label": human_label})
                                    day_labels[day_key] = day_label

                                st.markdown(
                                    f"""
                                    <div class="summary-grid" style="margin-bottom: 1rem;">
                                        <div class="summary-card">
                                            <div class="summary-label">Sightings found</div>
                                            <div class="summary-value">{len(person_results)}</div>
                                            <div class="summary-note">Images featuring {html.escape(selected['name'])}.</div>
                                        </div>
                                        <div class="summary-card">
                                            <div class="summary-label">Days spanned</div>
                                            <div class="summary-value">{len(grouped)}</div>
                                            <div class="summary-note">Distinct calendar days.</div>
                                        </div>
                                        <div class="summary-card">
                                            <div class="summary-label">Threshold</div>
                                            <div class="summary-value">{tl_threshold:.2f}</div>
                                            <div class="summary-note">Min confidence to count as a match.</div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                                st.markdown('<div class="timeline-shell">', unsafe_allow_html=True)
                                for day_key in sorted(grouped.keys(), reverse=True):
                                    st.markdown(
                                        f'<div class="timeline-day">{html.escape(day_labels[day_key])}</div>',
                                        unsafe_allow_html=True,
                                    )
                                    day_items = sorted(
                                        grouped[day_key],
                                        key=lambda i: i["captured_at"],
                                        reverse=True,
                                    )
                                    for item in day_items:
                                        score = max(0.0, min(float(item["best_match"]["score"]), 1.0))
                                        filename = item["image_path"].split("/")[-1]
                                        human_label = html.escape(item["human_label"])

                                        lat = item.get("latitude")
                                        lon = item.get("longitude")
                                        location_str = f"📍 {lat:.5f}, {lon:.5f}" if lat is not None and lon is not None else "📍 Unknown location"

                                        tl_thumb_col, tl_info_col = st.columns([1, 2], gap="medium")
                                        with tl_thumb_col:
                                            try:
                                                st.image(
                                                    item["image_path"],
                                                    use_container_width=True,
                                                    caption=html.escape(filename),
                                                )
                                            except Exception:
                                                st.caption(f"Could not load: {html.escape(filename)}")

                                        with tl_info_col:
                                            st.markdown(
                                                f"""
                                                <div class="timeline-item">
                                                    <div class="timeline-meta">
                                                        <span class="timeline-time">{human_label}</span>
                                                        <span class="timeline-pill">Score {score:.3f}</span>
                                                    </div>
                                                    <div class="timeline-location">{location_str}</div>
                                                    <div class="timeline-file">{html.escape(item['image_path'])}</div>
                                                    <div class="confidence-track" style="margin-top: 0.6rem;">
                                                        <div class="confidence-fill" style="width: {score * 100:.1f}%;"></div>
                                                    </div>
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )
                                st.markdown("</div>", unsafe_allow_html=True)

with tab_data_management:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-icon">🗂️</span>
            <div class="section-title">Data management</div>
        </div>
        <div class="section-copy">View enrolled people and remove them from the registry.</div>
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
                selected = st.selectbox("Select person to manage", options=people, format_func=lambda item: item["name"])

                st.markdown(
                    f"""
                    <div class="section-card">
                        <div class="section-copy" style="margin-bottom: 0;">
                            <strong>{html.escape(selected['name'])}</strong> — {selected['sample_count']} face sample{'s' if selected['sample_count'] != 1 else ''} enrolled.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.divider()
                st.markdown(
                    """
                    <div class="section-card">
                        <div class="section-header">
                            <span class="section-icon">⛔</span>
                            <div class="section-title">Remove enrolled user</div>
                        </div>
                        <div class="section-copy">Permanently deletes the person and all their face samples from the registry.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
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
                                f"Deleted {payload['deleted_sample_count']} face sample"
                                f"{'s' if payload['deleted_sample_count'] != 1 else ''}."
                            )
                            st.rerun()
                        else:
                            st.error(delete_response.text)
