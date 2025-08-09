from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from util_io import get_api_key, pil_image_to_png_bytes, SlideContent


def configure_gemini(api_key: Optional[str] = None) -> None:
    key = api_key or get_api_key()
    if not key:
        raise RuntimeError("Missing Google Gemini API key. Set env var GOOGLE_API_KEY or define GOOGLE_API_KEY in creds.py")
    genai.configure(api_key=key)


def find_slide_anomalies_with_gemini(model_name: str, slides: List[SlideContent]) -> List[Dict[str, Any]]:
    """
    Ask Gemini to find anomalies across slides using BOTH text and images.
    Expect a JSON array: [{ 'slides': [slide numbers], 'description': str }].
    """
    import json
    import re as _re

    model = genai.GenerativeModel(model_name)

    # Build a multimodal content list: header instructions, then per-slide text and images
    contents: List[Dict[str, Any]] = []
    header = (
        "You are given a presentation slide-by-slide. Each slide includes text and may include one or more images. "
        "Analyze the entire deck for inconsistencies, contradictions, numeric sum issues, timeline/date mismatches, "
        "and duplicated/conflicting statements across slides.\n\n"
        "Return STRICT JSON only (no prose): a JSON array where each element has exactly: "
        "{ 'slides': [slide numbers], 'description': str }.\n"
        "The 'description' must be a concise, data-focused flag followed by a brief explanation (unaltered). "
        "If there are no issues, return []."
    )
    contents.append({"text": header})

    for sc in slides:
        clean_text = _re.sub(r'[\n\t]+', ' ', (sc.text or '')).strip()
        contents.append({"text": f"Slide {sc.slide_index}:\n{clean_text}"})
        for img in sc.images:
            try:
                png_bytes = pil_image_to_png_bytes(img)
                contents.append({"inline_data": {"mime_type": "image/png", "data": png_bytes}})
            except Exception:
                continue

    resp = model.generate_content(contents, generation_config={"temperature": 1.0})
    text = (resp.text or "[]").strip()
    # DEBUG:
    # print("\n===== RAW GEMINI RESPONSE =====\n")
    # print(text)
    # print("\n==============================\n")
    try:
        # Remove Markdown code block markers if present
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
        # Extract the first JSON array
        match = re.search(r'(\[.*\])', text, re.DOTALL)
        if match:
            text = match.group(1)
        return json.loads(text)
    except Exception:
        return []


