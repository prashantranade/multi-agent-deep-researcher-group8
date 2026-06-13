# infrastructure/image_analyser.py
import base64
from openai import OpenAI
import config

def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyse_image(image_path: str) -> str:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    b64 = _encode_image(image_path)
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = f"image/{ext}" if ext in ("png", "jpg", "jpeg", "gif", "webp") else "image/png"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": "Describe the content of this image in detail for use as research context."},
            ],
        }],
        max_tokens=500,
    )
    return response.choices[0].message.content
