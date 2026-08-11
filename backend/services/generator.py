import os
import re
import json
import base64
import asyncio
from pathlib import Path
import google.generativeai as genai

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

text_model = genai.GenerativeModel("gemini-1.5-flash")
image_model = genai.GenerativeModel("gemini-1.5-flash")


def _load_voice_prompt(language: str) -> str:
    lang = "es" if language == "es" else "en"
    path = PROMPTS_DIR / f"voice_jlb_{lang}.txt"
    return path.read_text(encoding="utf-8")


async def generate_post_text(topic: str, language: str) -> str:
    voice_prompt = _load_voice_prompt(language)
    lang_label = "Spanish" if language == "es" else "English"

    prompt = f"""{voice_prompt}

---
TOPIC: {topic}
LANGUAGE: Write exclusively in {lang_label}.

Generate the LinkedIn post now."""

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: text_model.generate_content(prompt)
    )
    return response.text.strip()


async def generate_image_prompt(post_text: str, language: str) -> str:
    lang_instruction = "Respond in English regardless of the post language."
    prompt = f"""You are creating an image generation prompt for a LinkedIn post about COBOL/mainframe technology.

Post text:
{post_text}

Create a concise, vivid image generation prompt (max 80 words) that:
- Visually represents the core argument of the post
- References mainframe/COBOL aesthetics when relevant (green phosphor screens, punch cards, IBM z-series hardware, data center racks, terminal interfaces)
- Avoids generic stock photo clichés (no handshakes, no vague "technology" imagery)
- Has a specific, concrete visual that reinforces the post's thesis

{lang_instruction}
Return only the image prompt text, nothing else."""

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: text_model.generate_content(prompt)
    )
    return response.text.strip()


async def generate_image_base64(image_prompt: str) -> str | None:
    """
    Attempts to generate image via Gemini. Returns base64 data URI or None.
    Falls back gracefully — the post is still valuable without the image.
    """
    try:
        from google.generativeai import types as gtypes
        imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: imagen_model.generate_images(
                prompt=image_prompt,
                number_of_images=1,
                aspect_ratio="1:1",
            )
        )
        if result.images:
            img_bytes = result.images[0]._image_bytes
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"[image gen] Imagen failed: {e} — using placeholder")

    return _placeholder_image(image_prompt)


def _placeholder_image(prompt: str) -> str:
    """
    Returns a deterministic SVG placeholder that references the image prompt.
    Honest: shows what would be generated, with the prompt visible.
    """
    short = (prompt[:80] + "...") if len(prompt) > 80 else prompt
    short_escaped = short.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#0a0a0a"/>
  <rect x="20" y="20" width="360" height="360" fill="none" stroke="#00ff41" stroke-width="1" stroke-dasharray="4 2"/>
  <text x="200" y="60" font-family="monospace" font-size="11" fill="#00ff41" text-anchor="middle">[ IMAGE GENERATION PENDING ]</text>
  <text x="200" y="85" font-family="monospace" font-size="10" fill="#00cc33" text-anchor="middle">Imagen API key required</text>
  <line x1="40" y1="105" x2="360" y2="105" stroke="#00ff41" stroke-width="0.5" opacity="0.4"/>
  <text x="200" y="130" font-family="monospace" font-size="9" fill="#009922" text-anchor="middle">PROMPT:</text>
  <foreignObject x="40" y="140" width="320" height="200">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:monospace;font-size:10px;color:#00cc33;line-height:1.5;word-wrap:break-word;">
      {short_escaped}
    </div>
  </foreignObject>
  <text x="200" y="370" font-family="monospace" font-size="9" fill="#005511" text-anchor="middle">linkedin-cobol-engine v0.1</text>
</svg>"""

    svg_b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{svg_b64}"
