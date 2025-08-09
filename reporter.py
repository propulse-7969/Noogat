from __future__ import annotations

from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from util_io import to_json
import re


def print_summary(issues: List[Dict[str, Any]]) -> None:
    console = Console()
    if not issues:
        console.print("[bold green]No inconsistencies detected across slides.[/bold green]")
        return

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for issue in issues:
        grouped.setdefault(issue["type"], []).append(issue)

    for itype, items in grouped.items():
        console.rule(f"{itype} ({len(items)})")
        table = Table(show_lines=False)
        table.add_column("S. No.", no_wrap=True, width=6)
        table.add_column("Error Type", no_wrap=True, width=16)
        table.add_column("Slides", no_wrap=False, width=20)
        table.add_column("Message", no_wrap=False)
        for idx, it in enumerate(items, 1):
            slides = ", ".join(str(s) for s in sorted(set(it.get("slides", []))))
            msg = it.get("message", "")
            # Classify error type
            error_type = "other"
            lower_msg = msg.lower()
            if "sum" in lower_msg or "total" in lower_msg:
                error_type = "sum/total"
            elif "contradict" in lower_msg or "conflict" in lower_msg:
                error_type = "contradiction"
            elif "timeline" in lower_msg or "date" in lower_msg or "year" in lower_msg:
                error_type = "timeline/date"
            elif "percent" in lower_msg or "%" in lower_msg:
                error_type = "percent"
            elif "duplicate" in lower_msg or "same value" in lower_msg:
                error_type = "duplicate"
            elif "numeric" in lower_msg or re.search(r'\d', lower_msg):
                error_type = "numeric"
            elif "text" in lower_msg:
                error_type = "text"
            # Show full message without trimming; table will line-wrap as needed
            table.add_row(str(idx), error_type, slides, msg)
        console.print(table)


def to_json_report(issues: List[Dict[str, Any]]) -> str:
    return to_json({"issues": issues})


