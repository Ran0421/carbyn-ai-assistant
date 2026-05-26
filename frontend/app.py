import os
import tempfile
import streamlit as st
import requests
from gtts import gTTS

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="Industrial AI Assistant", layout="wide")
st.title("Industrial AI Maintenance Assistant")
st.write("Upload an equipment image and ask a troubleshooting question.")

uploaded_file = st.file_uploader("Upload Equipment Image", type=["jpg", "jpeg", "png"])
query = st.text_input("Enter your question", placeholder="Why is this breaker overheating?")

if st.button("Analyze Equipment"):
    if uploaded_file is None or not query.strip():
        st.warning("Please upload an image and enter a query.")
        st.stop()

    with st.spinner("Analyzing equipment..."):
        try:
            response = requests.post(
                API_URL,
                files={"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                data={"query": query},
                timeout=180,
            )
            response.raise_for_status()
            result = response.json()

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach backend. Is uvicorn running on port 8000?")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("Request timed out. Try again.")
            st.stop()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    # ── Error state ───────────────────────────────────────────────────────────
    if result.get("status") == "error":
        st.error(f"Backend error: {result.get('error', 'unknown')}")
        with st.expander("Pipeline Details (retrieved context + raw response)"):
            st.json(result)
        st.stop()

    st.success("Analysis Complete")

    # ── Vision analysis ───────────────────────────────────────────────────────
    st.subheader("Vision Analysis")
    vision = result.get("vision_analysis") or result.get("raw_response") or ""
    if vision:
        st.write(vision)
    else:
        st.warning("Vision analysis unavailable.")
        with st.expander("Raw LLM Response"):
            st.code(result.get("raw_response", "empty"))

    # ── Diagnosis ─────────────────────────────────────────────────────────────
    diagnosis = result.get("diagnosis", "")
    if diagnosis:
        st.subheader("Diagnosis")
        st.info(diagnosis)

    # ── Recommendations ───────────────────────────────────────────────────────
    st.subheader("Recommendations")
    recommendations = result.get("recommendations", [])
    if recommendations:
        for item in recommendations:
            st.success(item)
    else:
        st.warning("No recommendations parsed.")
        with st.expander("Raw LLM Response"):
            st.code(result.get("raw_response", "empty"))

    # ── Manual reference ──────────────────────────────────────────────────────
    manual_ref = result.get("manual_reference", "")
    if manual_ref:
        st.subheader("Manual Reference")
        st.caption(manual_ref)

    # ── Retrieved context ─────────────────────────────────────────────────────
    with st.expander(" Retrieved Manual Context"):
        st.write(result.get("retrieved_context", "None"))

    # ── Full pipeline details ─────────────────────────────────────────────────
    with st.expander(" Pipeline Details (retrieved context + raw response)"):
        st.json(result)

    if st.checkbox("Show full LLM response", value=False):
        st.code(result.get("raw_response", ""), language="markdown")

    # ── Text-to-Speech ────────────────────────────────────────────────────────
    tts_parts = []
    if diagnosis:
        tts_parts.append(f"Diagnosis: {diagnosis}")
    if recommendations:
        tts_parts.append("Recommended steps: " + ". ".join(recommendations))

    summary_text = " ".join(tts_parts).strip()

    if summary_text:
        try:
            tts = gTTS(text=summary_text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
            os.unlink(tmp_path)
        except Exception as e:
            st.warning(f"Text-to-speech failed: {e}")
    else:
        st.info("No text available for audio playback.")
