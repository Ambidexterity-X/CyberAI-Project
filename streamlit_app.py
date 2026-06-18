from __future__ import annotations

import requests
import streamlit as st


st.set_page_config(page_title="CyberAI Face Search", layout="wide")
BACKEND_URL = st.sidebar.text_input("Backend URL", value="http://localhost:8000")


def api_get(path: str):
    return requests.get(f"{BACKEND_URL}{path}", timeout=30)


def api_post(path: str, files=None, data=None):
    return requests.post(f"{BACKEND_URL}{path}", files=files, data=data, timeout=120)


st.title("CyberAI Face Search")
st.caption("Enroll faces, search images, and track timestamped sightings.")

tab_enroll, tab_search, tab_history = st.tabs(["Enroll", "Search", "History"])

with tab_enroll:
    st.subheader("Enroll a person")
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
    st.subheader("Search for matches")
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
    st.subheader("Sighting history")
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
                            for sighting in sightings:
                                spotted_at = sighting["spotted_at"]
                                st.write(
                                    f"{spotted_at} | {sighting['location'] or 'Unknown location'} | confidence={sighting['confidence']:.3f}"
                                )
                    else:
                        st.error(sightings_response.text)
