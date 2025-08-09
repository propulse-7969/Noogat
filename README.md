## Noogat Deck Consistency Checker

A command-line tool that analyzes PowerPoint decks for inconsistencies using Google Gemini. It processes slide text and embedded pictures, detects cross-slide issues, and outputs a machine-readable JSON report and/or a readable console summary.

### Capabilities
- Detects contradictions and duplicated/conflicting statements across slides
- Flags numeric issues (e.g., sums/totals, percentage inconsistencies)
- Highlights timeline/date mismatches
- Processes embedded pictures on slides and sends them for multimodal analysis

### How it works
- `pptx_loader.py` extracts slide text (including tables) and embedded pictures (`PICTURE` shapes only)
- `gemini_client.py` sends per-slide text and inline PNG images to Gemini with concise instructions
- `reporter.py` formats the model response into a console table and JSON report

## Prerequisites
- Python 3.10+
- A Google Gemini API key
  - Obtain a key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Installation
```bash
python -m venv .venv
./.venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

## Configuration
The tool reads the API key in this order:
- Environment variables: `GOOGLE_API_KEY`, `GOOGLE_APIKEY`, or `GEMINI_API_KEY`
- Fallback module `creds.py` with `GOOGLE_API_KEY = "..."`

Examples:
```powershell
setx GOOGLE_API_KEY "YOUR_KEY"   # Windows (restart the shell)
```
```python
# creds.py
GOOGLE_API_KEY = "YOUR_KEY"
```

## Usage
Basic command:
```bash
python main.py --pptx place_ppt_here/NoogatAssignment.pptx --pretty
```

CLI options:
- `--pptx PATH` (string): Path to a `.pptx` file. Default: `place_ppt_here/NoogatAssignment.pptx`
- `--max-slides N` (int): Limit the number of slides analyzed (0 = all). Default: 0
- `--output FILE` (string): Write the JSON report to this path
- `--pretty` (flag): Print a formatted console summary instead of raw JSON
- `--model NAME` (string): Gemini model (e.g., `gemini-2.5-pro`, `gemini-2.5-flash`). Default: `gemini-2.5-pro`

Examples:
```bash
# Pretty console summary
python main.py --pptx your_deck.pptx --pretty

# Raw JSON to stdout
python main.py --pptx your_deck.pptx

# Save JSON to file
python main.py --pptx your_deck.pptx --output report.json

# Analyze only first 10 slides using Gemini Flash
python main.py --pptx your_deck.pptx --max-slides 10 --model gemini-2.5-flash
```

## Output
- Console summary: grouped by inferred error type (sum/total, contradiction, timeline/date, percent, duplicate, numeric, text)
- JSON report: `{"issues": [...]}` where each issue contains `slides`, `message`, and `type`

## Notes and limitations
- Only embedded pictures (`PICTURE` shapes) are extracted. Charts, SmartArt, vector shapes, and slide backgrounds are not rasterized.
- The tool does not render slide thumbnails; content is limited to extracted text + images.
- Gemini response is expected to be a strict JSON array of issues; unexpected formats are handled conservatively.

## Troubleshooting
- Missing API key: ensure `GOOGLE_API_KEY` is set or create `creds.py` with `GOOGLE_API_KEY`.
- PPTX not found: verify the `--pptx` path.
- Empty output: try `--model gemini-2.5-pro`, reduce to a smaller deck, or ensure textual content is actually extractable.

## License
MIT