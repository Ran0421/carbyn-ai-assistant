import os
import base64
import io
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_PATH = "vectorstore/chroma_db"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_model)


def retrieve_context(query: str, k: int = 2) -> str:
    docs = vectordb.similarity_search(query, k=k)
    if not docs:
        return "No relevant manual context found."
    chunks = []
    for i, doc in enumerate(docs, 1):
        text   = doc.page_content.strip()
        source = doc.metadata.get("source", "manual")
        page   = doc.metadata.get("page", "?")
        if len(text) > 80:
            chunks.append(f"[Ref {i} — {source}, p.{page}]\n{text[:300]}")
    return "\n\n---\n\n".join(chunks) if chunks else "No useful context retrieved."


SYSTEM_PROMPT = """You are an expert industrial maintenance AI assistant.
A technician is showing you equipment and asking for help.

When given an image, you MUST:
1. Describe exactly what you see (equipment type, visible condition, any anomalies)
2. Identify the most likely fault or concern based on the visual
3. Give numbered, actionable repair steps — specific to what you see
4. Cite any relevant section from the provided manual context

Format your response EXACTLY as:
**What I see:** (visual description)
**Diagnosis:** (likely fault)
**Action steps:**
1. (first step)
2. (second step)
3. (continue as needed)
**Manual reference:** (cite the relevant retrieved context if applicable)

Never give generic advice. Every step must relate to what you actually see in the image."""


def generate_assistant_response(image_path: str, user_query: str) -> dict:
    # Step 1: RAG retrieval
    rag_context = retrieve_context(user_query)

    # Step 2: Load + encode image as base64
    try:
        img = Image.open(image_path).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        return {
            "status": "error",
            "error": f"Could not open image: {e}",
            "query": user_query,
            "vision_analysis": None,
            "retrieved_context": rag_context,
            "recommendations": [],
        }

    # Step 3: Build prompt
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"RELEVANT MANUAL EXCERPTS:\n"
        f"{'─'*50}\n"
        f"{rag_context}\n"
        f"{'─'*50}\n\n"
        f"TECHNICIAN'S QUESTION: {user_query}"
    )

    # Step 4: Call Groq vision
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                }
            ],
            max_tokens=1024,
            temperature=0.2,
        )
        full_response = response.choices[0].message.content

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": user_query,
            "vision_analysis": None,
            "retrieved_context": rag_context,
            "recommendations": [],
            "raw_response": None,
        }

    # Step 5: Parse structured sections
    def _extract(text, header):
        marker = f"**{header}**"
        if marker not in text:
            return ""
        start = text.index(marker) + len(marker)
        headers = ["What I see:", "Diagnosis:", "Action steps:", "Manual reference:"]
        nexts = [text.index(f"**{h}**") for h in headers
                 if f"**{h}**" in text and text.index(f"**{h}**") > start]
        return text[start:min(nexts) if nexts else len(text)].strip()

    steps_text = _extract(full_response, "Action steps:")
    recommendations = []
    for line in steps_text.splitlines():
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            clean = line.lstrip("0123456789.-) ").strip()
            if clean:
                recommendations.append(clean)
    if not recommendations and steps_text:
        recommendations = [steps_text]

    return {
        "status": "success",
        "query": user_query,
        "vision_analysis": _extract(full_response, "What I see:") or full_response,
        "diagnosis": _extract(full_response, "Diagnosis:"),
        "retrieved_context": rag_context,
        "recommendations": recommendations,
        "manual_reference": _extract(full_response, "Manual reference:"),
        "raw_response": full_response,
    }
