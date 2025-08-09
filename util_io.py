from __future__ import annotations

import io
import json
import os
from dataclasses import dataclass
from typing import Any, List, Optional

from PIL import Image
import orjson


def read_env_api_key() -> Optional[str]:
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_APIKEY") or os.environ.get("GEMINI_API_KEY")


def read_creds_fallback() -> Optional[str]:
    try:
        from creds import GOOGLE_API_KEY  # type: ignore

        key = str(GOOGLE_API_KEY).strip()
        return key if key else None
    except Exception:
        return None


def get_api_key() -> Optional[str]:
    return read_env_api_key() or read_creds_fallback()


def to_json(obj: Any) -> str:
    try:
        return orjson.dumps(obj).decode("utf-8")
    except Exception:
        return json.dumps(obj, ensure_ascii=False)


def pil_image_to_png_bytes(image: Image.Image) -> bytes:
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()


@dataclass
class SlideContent:
    slide_index: int
    text: str
    images: List[Image.Image]


