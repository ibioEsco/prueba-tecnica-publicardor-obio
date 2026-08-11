import os
import base64
import asyncio
import logging
from pathlib import Path
from google import genai

log = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
MODEL = "gemini-3.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"


def _load_voice_prompt(language: str) -> str:
    lang = "es" if language == "es" else "en"
    path = PROMPTS_DIR / f"voice_jlb_{lang}.txt"
    return path.read_text(encoding="utf-8")


def _chat(system: str, user: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=user,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
        ),
    )
    return response.text.strip()


async def generate_post_text(topic: str, language: str) -> str:
    voice_prompt = _load_voice_prompt(language)
    lang_label = "Spanish" if language == "es" else "English"

    user_msg = f"TOPIC: {topic}\nLANGUAGE: Write exclusively in {lang_label}.\n\nGenerate the LinkedIn post now."

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _chat(voice_prompt, user_msg))


async def generate_image_prompt(post_text: str, language: str) -> str:
    system = """You are creating an image generation prompt for a LinkedIn post about COBOL/mainframe technology.

Create a concise, vivid image generation prompt (max 80 words) that:
- Visually represents the core argument of the post
- References mainframe/COBOL aesthetics when relevant (green phosphor screens, punch cards, IBM z-series hardware, data center racks, terminal interfaces)
- Avoids generic stock photo clichés (no handshakes, no vague "technology" imagery)
- Has a specific, concrete visual that reinforces the post's thesis

Respond in English regardless of the post language.
Return only the image prompt text, nothing else."""

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _chat(system, post_text))


async def generate_image_base64(image_prompt: str) -> str | None:
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, lambda: _generate_image(image_prompt))
        if result:
            return result
    except Exception as exc:
        log.warning("Image generation failed, using placeholder: %s", exc)
    return _placeholder_image(image_prompt)


def _generate_image(prompt: str) -> str | None:
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=f"Generate an image: {prompt}",
        config=genai.types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            mime = part.inline_data.mime_type or "image/png"
            b64 = base64.b64encode(part.inline_data.data).decode()
            return f"data:{mime};base64,{b64}"
    return None


def _placeholder_image(prompt: str) -> str:
    short = (prompt[:80] + "...") if len(prompt) > 80 else prompt
    short_escaped = short.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#0a0a0a"/>
  <rect x="20" y="20" width="360" height="360" fill="none" stroke="#00ff41" stroke-width="1" stroke-dasharray="4 2"/>
  <text x="200" y="60" font-family="monospace" font-size="11" fill="#00ff41" text-anchor="middle">[ IMAGE GENERATION PENDING ]</text>
  <text x="200" y="85" font-family="monospace" font-size="10" fill="#00cc33" text-anchor="middle">Imagen API required</text>
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
