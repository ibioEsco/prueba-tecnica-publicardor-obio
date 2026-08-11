"""
LinkedIn publishing service.

Two modes:
- REAL: Uses LinkedIn API v2 (ugcPosts endpoint) with OAuth token.
  Requires: LINKEDIN_ACCESS_TOKEN env var.
- SIMULATED: Shows exactly what would be sent, marks post as 'simulated'.
  A simulated post is NEVER presented as a real publication.
"""

import os
import aiohttp
import base64
from dataclasses import dataclass

LINKEDIN_API = "https://api.linkedin.com/v2"


@dataclass
class PublishResult:
    success: bool
    simulated: bool
    post_url: str | None
    payload_preview: dict
    error: str | None = None
    required_scopes: list[str] = None
    setup_instructions: str | None = None


async def publish_to_linkedin(
    post_text: str,
    image_data_uri: str | None,
    author_urn: str | None = None,
) -> PublishResult:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")

    if not token:
        return await _simulate_publish(post_text, image_data_uri)

    return await _real_publish(token, post_text, image_data_uri, author_urn)


async def _real_publish(
    token: str,
    post_text: str,
    image_data_uri: str | None,
    author_urn: str | None,
) -> PublishResult:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    async with aiohttp.ClientSession() as session:
        # 1. Get author URN if not provided
        if not author_urn:
            async with session.get(f"{LINKEDIN_API}/userinfo", headers=headers) as r:
                if r.status != 200:
                    return PublishResult(
                        success=False, simulated=False, post_url=None,
                        payload_preview={},
                        error=f"Failed to get LinkedIn profile: HTTP {r.status}"
                    )
                profile = await r.json()
                author_urn = f"urn:li:person:{profile['sub']}"

        # 2. Upload image if present
        media_asset = None
        if image_data_uri and not image_data_uri.startswith("data:image/svg"):
            media_asset = await _upload_image(session, headers, author_urn, image_data_uri)

        # 3. Build post payload
        payload = _build_payload(author_urn, post_text, media_asset)

        # 4. Post
        async with session.post(
            f"{LINKEDIN_API}/ugcPosts", headers=headers, json=payload
        ) as r:
            if r.status in (200, 201):
                data = await r.json()
                post_id = data.get("id", "")
                return PublishResult(
                    success=True, simulated=False,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}/",
                    payload_preview=payload,
                )
            else:
                body = await r.text()
                return PublishResult(
                    success=False, simulated=False, post_url=None,
                    payload_preview=payload,
                    error=f"LinkedIn API error {r.status}: {body}"
                )


async def _upload_image(session, headers, author_urn, data_uri) -> str | None:
    try:
        # Register upload
        register_payload = {
            "registerUploadRequest": {
                "owner": author_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {"identifier": "urn:li:userGeneratedContent",
                     "relationshipType": "OWNER"}
                ],
                "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"],
            }
        }
        async with session.post(
            f"{LINKEDIN_API}/assets?action=registerUpload",
            headers=headers, json=register_payload
        ) as r:
            if r.status != 200:
                return None
            reg_data = await r.json()

        upload_url = reg_data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset = reg_data["value"]["asset"]

        # Upload bytes
        header, encoded = data_uri.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        upload_headers = {**headers, "Content-Type": "image/png"}
        async with session.put(upload_url, headers=upload_headers, data=img_bytes) as r:
            if r.status not in (200, 201):
                return None

        return asset
    except Exception as e:
        print(f"[image upload] {e}")
        return None


def _build_payload(author_urn: str, text: str, media_asset: str | None) -> dict:
    if media_asset:
        return {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "media": media_asset,
                    }],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
    return {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }


async def _simulate_publish(post_text: str, image_data_uri: str | None) -> PublishResult:
    example_urn = "urn:li:person:EXAMPLE_ID"
    payload = _build_payload(example_urn, post_text, None)

    return PublishResult(
        success=True,
        simulated=True,
        post_url=None,
        payload_preview=payload,
        required_scopes=["r_liteprofile", "w_member_social"],
        setup_instructions=(
            "To enable real publishing:\n"
            "1. Create a LinkedIn App at https://www.linkedin.com/developers/\n"
            "2. Request 'Share on LinkedIn' and 'Sign In with LinkedIn' products\n"
            "3. Generate an OAuth 2.0 access token with scopes: r_liteprofile, w_member_social\n"
            "4. Set LINKEDIN_ACCESS_TOKEN=<token> in your .env file\n"
            "5. Optionally set LINKEDIN_AUTHOR_URN=urn:li:person:<your_id>"
        ),
    )
