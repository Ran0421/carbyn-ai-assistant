import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Load model
model = genai.GenerativeModel(
    "models/gemini-2.0-flash"
)


def analyze_equipment_image(image_path):

    image = Image.open(image_path)

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

    response = model.generate_content(
        [prompt, image],
        request_options={"timeout": 10}
    )

    return response.text