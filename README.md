## Noogat Deck Consistency Checker

AI-enabled CLI tool that analyzes multi-slide PowerPoint decks (and/or slide images) to flag factual and logical inconsistencies across slides using Gemini 2.5 Flash.

### Features
- Extracts text and embedded images per slide from `.pptx` decks
- Uses Gemini 2.5 Flash to extract structured claims (numeric/text/timeline) from slide text/images
- Cross-slide checks:
  - Numeric conflicts (same metric, different values)
  - Percentage sum issues (>100% or implausible totals)
  - Contradictory textual claims (e.g., “highly competitive” vs “few competitors”)
  - Timeline/date mismatches
- Clear, structured report referencing slide numbers and evidence

### Requirements
- Python 3.10+
- Google Gemini API key (free): `https://aistudio.google.com/app/apikey`

### Setup
```bash
python -m venv .venv
./.venv/Scripts/Activate.ps1  # on Windows PowerShell
# Windows (recommended):
pip install -r requirements-win.txt

# If that fails, try minimal core first (no PPTX/image), then add PPTX libs:
pip install -r requirements-core.txt
pip install python-pptx Pillow==9.5.0
```

Provide your API key via environment variable or `creds.py`:
- Environment variable (recommended):
  - PowerShell: `setx GOOGLE_API_KEY "YOUR_KEY_HERE"`
  - Then restart your shell
- Or edit `creds.py` and set `GOOGLE_API_KEY = "YOUR_KEY_HERE"`

### Usage
Place your deck at `place_ppt_here/NoogatAssignment.pptx` or supply a path.

```bash
python main.py --pptx place_ppt_here/NoogatAssignment.pptx --pretty
```

Optional: analyze a folder of slide images (PNG/JPG). Images will be treated as additional slides:

```bash
python main.py --images-dir path/to/images --pretty
```

Full CLI:
```bash
python main.py \
  [--pptx PATH_TO_PPTX] \
  [--images-dir PATH_TO_DIR] \
  [--model gemini-2.5-flash] \
  [--max-slides N] \
  [--output report.json] \
  [--pretty] \
  [--no-vision]  # disable sending images to Gemini
```

### Output
- Console summary highlighting issues by type
- Optional JSON file with full structured report, including cross-references to slides and evidence snippets

### How it works (high level)
1. Parse `.pptx` to get per-slide text, tables, and embedded images
2. For each slide, call Gemini 2.5 Flash to extract structured claims (strict JSON)
3. Normalize and cluster claims across slides
4. Run rule-based checks for numeric conflicts, percentage sums, and timelines; use Gemini to judge borderline textual contradictions
5. Emit a structured report

### Limitations
- LLM extraction quality impacts downstream checks; malformed JSON is heuristically repaired but may miss edge cases
- Numeric normalization and entity canonicalization are heuristic; different phrasings may not cluster perfectly
- Percentage sum checks are conservative; domain-specific aggregation logic is not included
- Timeline reasoning is basic; complex dependencies may require bespoke logic

### Development
Run on the provided sample:
```bash
python main.py --pptx place_ppt_here/NoogatAssignment.pptx --pretty --output sample_report.json
```

### License
MIT


