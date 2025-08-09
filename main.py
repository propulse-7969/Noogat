from __future__ import annotations

import argparse
import os
from typing import Any

from pptx_loader import load_pptx
from gemini_client import configure_gemini, find_slide_anomalies_with_gemini
from reporter import print_summary, to_json_report

DEFAULT_MODEL = "gemini-2.5-pro"

def main() -> None:
    parser = argparse.ArgumentParser(description="Deck consistency checker using Gemini 2.5 Pro")
    parser.add_argument("--pptx", type=str, default="place_ppt_here/NoogatAssignment.pptx", help="Path to pptx file")
    parser.add_argument("--max-slides", type=int, default=0, help="Limit number of slides to analyze (0 = all)")
    parser.add_argument("--output", type=str, default="", help="Write JSON report to this path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print console summary")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Gemini model name")
    args = parser.parse_args()

    configure_gemini()

    slides = []
    if args.pptx and os.path.isfile(args.pptx):
        slides = load_pptx(args.pptx)
    else:
        print(f"Warning: pptx not found at {args.pptx}")

    if args.max_slides and args.max_slides > 0:
        slides = slides[: args.max_slides]

    # Build a dictionary: {slide_number: raw_text}
    slide_dict = {idx: sc.text for idx, sc in enumerate(slides, 1)}

    # DEBUG: 
    # print("\n===== SLIDE DICTIONARY SENT TO GEMINI =====\n")
    # import json
    # print(json.dumps(slide_dict, indent=2, ensure_ascii=False))
    # print("\n==========================================\n")

    # Use Gemini to find anomalies across the slide dictionary
    anomalies = find_slide_anomalies_with_gemini(args.model, slide_dict)

    # Normalize Gemini output for reporter compatibility
    for issue in anomalies:
        if "type" not in issue:
            issue["type"] = "anomaly"
        if "message" not in issue and "description" in issue:
            issue["message"] = issue["description"]

    # Output
    if args.pretty:
        print_summary(anomalies)
    else:
        print(to_json_report(anomalies))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(to_json_report(anomalies))

if __name__ == "__main__":
    main()


