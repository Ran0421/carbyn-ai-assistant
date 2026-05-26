import os
import io
import base64
from dotenv import load_dotenv
from groq import Groq
from PIL import Image

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_equipment_image(image_path: str) -> str:
    img = Image.open(image_path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt = """
    You are an industrial maintenance assistant.
    Analyze this electrical equipment image.
    Identify:
    1. Equipment type
    2. Visible abnormalities
    3. Possible issues
    4. Safety hazards
    5. Recommended next action
    Keep the response technical and concise.
    """

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
        max_tokens=512,
        temperature=0.2,
    )
    return response.choices[0].message.content