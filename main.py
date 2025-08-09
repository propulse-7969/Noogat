from __future__ import annotations

import argparse
import os

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

    # DEBUG: show brief preview of slides sent to Gemini
    # if slides:
    #     print("\n===== SLIDES SENT TO GEMINI (PREVIEW) =====\n")
    #     import json
    #     preview = {sc.slide_index: (sc.text[:300] + ('...' if len(sc.text) > 300 else '')) for sc in slides[:5]}
    #     print(json.dumps(preview, indent=2, ensure_ascii=False))
    #     print("\n==========================================\n")

    # Use Gemini to find anomalies across the slides (text + images)
    anomalies = find_slide_anomalies_with_gemini(args.model, slides)

    # Normalize Gemini output for reporter compatibility
    for issue in anomalies:
        # Keep message simple and human-friendly: use Gemini's description as-is
        if "message" not in issue and "description" in issue:
            issue["message"] = issue["description"]
        if "type" not in issue:
            issue["type"] = "anomaly"

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


