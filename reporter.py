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
        table.add_column("Slides", no_wrap=False, width=20)
        table.add_column("Message", no_wrap=False)
        for it in items:
            slides = ", ".join(str(s) for s in sorted(set(it.get("slides", []))))
            msg = it.get("message", "")
            # Make message as data-focused as possible, but do not truncate
            flag = None
            eq_match = re.search(r'(\d+\s*[+\-*/]\s*\d+(?:\s*[+\-*/]\s*\d+)*\s*=*\s*\d+)', msg)
            if eq_match:
                flag = eq_match.group(1)
            else:
                sum_match = re.search(r'sum.*?is only [^\.]+', msg)
                if sum_match:
                    flag = sum_match.group(0)
                else:
                    nums = re.findall(r'([\w\s\'\"]*?\d+[\w\s\'\"]*)', msg)
                    nums = [n.strip() for n in nums if len(n.strip()) > 0]
                    if nums:
                        flag = '; '.join(nums)
            if not flag:
                num_phrase = re.search(r'([^.]*\d+[^.]*)', msg)
                if num_phrase:
                    flag = num_phrase.group(1)
                else:
                    flag = msg
            # Do NOT truncate the flag/message
            table.add_row(slides, flag)
        console.print(table)


def to_json_report(issues: List[Dict[str, Any]]) -> str:
    return to_json({"issues": issues})


