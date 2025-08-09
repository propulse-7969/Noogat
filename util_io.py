from __future__ import annotations

import base64
import io
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

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


def from_json(text: str) -> Any:
    try:
        return orjson.loads(text)
    except Exception:
        return json.loads(text)


def pil_image_to_png_bytes(image: Image.Image) -> bytes:
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()


def load_images_from_dir(images_dir: str) -> List[Image.Image]:
    images: List[Image.Image] = []
    if not images_dir:
        return images
    if not os.path.isdir(images_dir):
        return images

    supported = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
    for name in sorted(os.listdir(images_dir)):
        ext = os.path.splitext(name)[1].lower()
        if ext in supported:
            path = os.path.join(images_dir, name)
            try:
                images.append(Image.open(path).convert("RGB"))
            except Exception:
                continue
    return images


@dataclass
class SlideContent:
    slide_index: int
    text: str
    images: List[Image.Image]


