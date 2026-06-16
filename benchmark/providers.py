"""Thin API clients for stress tests (temperature=0)."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import List, Tuple


def _b64_path(path: str) -> Tuple[str, str]:
    p = Path(path)
    suf = p.suffix.lower()
    mt = "image/jpeg"
    if suf == ".png":
        mt = "image/png"
    elif suf == ".webp":
        mt = "image/webp"
    data = p.read_bytes()
    return base64.standard_b64encode(data).decode("ascii"), mt


def transcribe_anthropic(
    system: str,
    user_text: str,
    image_paths: List[str],
    model: str,
) -> str:
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic(api_key=key)
    content: list = [{"type": "text", "text": user_text}]
    for img in image_paths:
        b64, mt = _b64_path(img)
        content.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": mt, "data": b64},
            }
        )
    msg = client.messages.create(
        model=model,
        max_tokens=16384,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    parts = []
    for b in msg.content:
        if b.type == "text":
            parts.append(b.text)
    return "".join(parts)


def transcribe_openai(
    system: str,
    user_text: str,
    image_paths: List[str],
    model: str,
) -> str:
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=key)
    user_content: list = [{"type": "text", "text": user_text}]
    for img in image_paths:
        b64, mt = _b64_path(img)
        user_content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mt};base64,{b64}"},
            }
        )
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
    )
    return resp.choices[0].message.content or ""


def transcribe_gemini(
    system: str,
    user_text: str,
    image_paths: List[str],
    model: str,
) -> str:
    import mimetypes

    import google.genai as genai
    from google.genai import types as genai_types

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    client = genai.Client(api_key=api_key)

    contents: list = []
    for img in image_paths:
        mime, _ = mimetypes.guess_type(img)
        mime = mime or "image/jpeg"
        contents.append(
            genai_types.Part.from_bytes(data=Path(img).read_bytes(), mime_type=mime)
        )
    contents.append(f"{user_text}")

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
        ),
    )
    try:
        text = resp.text
    except (ValueError, AttributeError) as e:
        raise RuntimeError("Gemini returned no text (blocked or empty response)") from e
    return text or ""


def transcribe_mistral(
    system: str,
    user_text: str,
    image_paths: List[str],
    model: str,
) -> str:
    from mistralai import Mistral

    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        raise RuntimeError("MISTRAL_API_KEY is not set")
    client = Mistral(api_key=key)
    content: list = [{"type": "text", "text": f"{system}\n\n{user_text}"}]
    for img in image_paths:
        b64, mt = _b64_path(img)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mt};base64,{b64}"},
        })
    resp = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": content}],
    )
    return resp.choices[0].message.content or ""


PROVIDERS = {
    "anthropic": transcribe_anthropic,
    "openai": transcribe_openai,
    "gemini": transcribe_gemini,
    "mistral": transcribe_mistral,
}
