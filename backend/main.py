import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal

import db
from services.generator import generate_post_text, generate_image_prompt, generate_image_base64
from services.scorer import score_post
from services.linkedin import publish_to_linkedin

app = FastAPI(title="LinkedIn COBOL Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*", #para la prueba se habilita, en prod deben ser los puertos de vite/frontend
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type"],
)

db.init_db()

VALID_TRANSITIONS = {
    "draft": {"approved", "discarded"},
    "approved": {"draft", "published", "simulated"},
    "discarded": set(),
    "published": set(),
    "simulated": {"draft"},
}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal error: {type(exc).__name__}: {exc}"},
    )


# ── Schemas ─────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    topic: str
    language: Literal["en", "es"] = "en"


class UpdatePostRequest(BaseModel):
    status: Literal["approved", "discarded", "draft"]
    text: str | None = None


class PublishRequest(BaseModel):
    post_id: int


class RegenerateImageRequest(BaseModel):
    image_prompt: str | None = None


# ── Routes ───────────────────────────────────────────────────────────────────

@app.post("/generate")
async def generate(req: GenerateRequest):
    if not req.topic.strip():
        raise HTTPException(400, "Topic cannot be empty")

    # 1. Generate post text
    text = await generate_post_text(req.topic, req.language)

    # 2. Score the post
    score, reasons = score_post(text, req.language)

    # 3. Generate image prompt + image (parallel-ish)
    image_prompt = await generate_image_prompt(text, req.language)
    image_url = await generate_image_base64(image_prompt)

    # 4. Persist
    post_id = db.save_post(
        topic=req.topic,
        language=req.language,
        text=text,
        image_url=image_url,
        image_prompt=image_prompt,
        viral_score=score,
        viral_reasons=reasons,
    )

    post = db.get_post(post_id)
    if not post:
        raise HTTPException(500, "Failed to retrieve the generated post from database")
    return post


@app.get("/posts")
async def list_posts():
    return db.get_all_posts()


@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return post


@app.patch("/posts/{post_id}")
async def update_post(post_id: int, req: UpdatePostRequest):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    allowed = VALID_TRANSITIONS.get(post["status"], set())
    if req.status != post["status"] and req.status not in allowed:
        raise HTTPException(
            400,
            f"Cannot transition from '{post['status']}' to '{req.status}'"
        )
    db.update_post_status(post_id, req.status, req.text)
    return db.get_post(post_id)


@app.post("/posts/{post_id}/regenerate-image")
async def regenerate_image(post_id: int, req: RegenerateImageRequest):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    if post["status"] in ("published", "discarded"):
        raise HTTPException(400, f"Cannot regenerate the image of a '{post['status']}' post")

    custom = (req.image_prompt or "").strip()
    if custom:
        prompt = custom
    else:
        # No custom prompt: derive a fresh one from the post text so the new
        # image is a genuine alternative, not a re-roll of the same brief.
        prompt = await generate_image_prompt(post["text"], post["language"])

    image_url = await generate_image_base64(prompt)
    db.update_post_image(post_id, image_url, prompt)
    return db.get_post(post_id)


@app.post("/posts/{post_id}/publish")
async def publish_post(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    if post["status"] == "published":
        raise HTTPException(400, "Post already published")

    result = await publish_to_linkedin(
        post_text=post["text"],
        image_data_uri=post["image_url"],
        author_urn=os.environ.get("LINKEDIN_AUTHOR_URN"),
    )

    new_status = "published" if (result.success and not result.simulated) else "simulated"
    db.update_post_status(post_id, new_status)

    return {
        "status": new_status,
        "simulated": result.simulated,
        "post_url": result.post_url,
        "payload_preview": result.payload_preview,
        "error": result.error,
        "required_scopes": result.required_scopes,
        "setup_instructions": result.setup_instructions,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
