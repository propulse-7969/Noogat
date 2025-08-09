from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from util_io import get_api_key, to_json


DEFAULT_MODEL = "gemini-2.5-flash"


def configure_gemini(api_key: Optional[str] = None, model: str = DEFAULT_MODEL) -> None:
    key = api_key or get_api_key()
    if not key:
        raise RuntimeError("Missing Google Gemini API key. Set env var GOOGLE_API_KEY or define GOOGLE_API_KEY in creds.py")
    genai.configure(api_key=key)


EXTRACTION_SYSTEM_PROMPT = (
    "You are a precise analyst extracting structured claims from slide content. "
    "Return STRICT JSON with this schema: {\n"
    "  'claims': [\n"
    "    { 'type': 'numeric'|'text'|'timeline', 'subject': str, 'predicate': str, 'object': str,\n"
    "      'value': number|null, 'unit': str|null, 'date': str|null, 'year': int|null, 'evidence': str }\n"
    "  ]\n"
    "}.\n"
    "- type=numeric: use 'value' and 'unit' (e.g., %, $, M, K).\n"
    "- type=timeline: use 'date' (ISO if possible) or 'year'.\n"
    "- evidence: short quote from input.\n"
    "If images are provided, read them carefully (OCR) and include those claims too."
)


CONTRADICTION_SYSTEM_PROMPT = (
    "You are judging if two claims contradict each other. Return JSON: { 'contradict': bool, 'reason': str }.\n"
    "Consider semantic meaning and units. If uncertain, set contradict=false with reason."
)


def _strip_json(text: str) -> str:
    # Try to extract the first JSON object/array from the text
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    return match.group(1) if match else text


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def extract_claims(model_name: str, slide_text: str, images: Optional[List[bytes]] = None) -> Dict[str, Any]:
    model = genai.GenerativeModel(model_name, system_instruction=EXTRACTION_SYSTEM_PROMPT)
    contents: List[Any] = [{"text": slide_text or ""}]
    if images:
        for png_bytes in images:
            contents.append({"inline_data": {"mime_type": "image/png", "data": png_bytes}})

    resp = model.generate_content(contents)
    text = (resp.text or "{}").strip()
    try:
        return json_loads_safe(_strip_json(text))
    except Exception:
        # Attempt one retry path: ask to restate strictly JSON
        repair = model.generate_content([{"text": "Return STRICT JSON only, no prose. Reformat this strictly as JSON without commentary:"}, {"text": text}])
        return json_loads_safe(_strip_json((repair.text or "{}").strip()))


def json_loads_safe(text: str) -> Dict[str, Any]:
    import json

    try:
        return json.loads(text)
    except Exception:
        # Last resort minimal object
        return {"claims": []}


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def judge_contradiction(model_name: str, claim_a: str, claim_b: str) -> Dict[str, Any]:
    model = genai.GenerativeModel(model_name, system_instruction=CONTRADICTION_SYSTEM_PROMPT)
    prompt = f"Claim A: {claim_a}\nClaim B: {claim_b}\nReturn JSON: {{ 'contradict': bool, 'reason': str }}"
    resp = model.generate_content([{"text": prompt}])
    text = (resp.text or "{}").strip()
    try:
        return json_loads_safe(_strip_json(text))
    except Exception:
        return {"contradict": False, "reason": "Parse error"}


def find_slide_anomalies_with_gemini(model_name: str, slide_dict: dict[int, str]) -> list[dict[str, any]]:
    """
    Given a dictionary of slides {slide_number: content}, ask Gemini to find anomalies across slides.
    Returns a list of dicts: { 'slides': [slide numbers], 'description': str }
    """
    import json
    model = genai.GenerativeModel(model_name)
    # Clean slide content: remove \n, \t, and extra whitespace
    import re as _re
    clean_slide_dict = {k: _re.sub(r'[\n\t]+', ' ', v).strip() for k, v in slide_dict.items()}
    slides_json = json.dumps(clean_slide_dict, ensure_ascii=False, indent=2)
    prompt = (
        "Here is a presentation as a JSON dictionary where keys are slide numbers and values are the slide content. "
        "Identify all inconsistencies, contradictions, or anomalies in the data or claims. "
        "For each, return STRICT JSON: { 'slides': [slide numbers], 'description': str }. "
        "In each description, first give a crisp, data-focused flag (e.g., numeric or factual), then add a brief, clear explanation for context. "
        "Format: 'flag: ... Explanation: ...'. If none, return an empty list [].\n\n" + slides_json
    )
    resp = model.generate_content([{"text": prompt}], generation_config={"temperature": 1.7})
    text = (resp.text or "[]").strip()
    # DEBUG:
    print("\n===== RAW GEMINI RESPONSE =====\n")
    print(text)
    print("\n==============================\n")
    try:
        import re
        # Remove Markdown code block markers if present
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
        # Now extract the first JSON array
        match = re.search(r'(\[.*\])', text, re.DOTALL)
        if match:
            text = match.group(1)
        return json.loads(text)
    except Exception:
        return []


