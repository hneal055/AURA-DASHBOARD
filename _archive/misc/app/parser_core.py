"""
parser_core.py — Intelligent Budget + Contract Parser
"""

import re
import json
from typing import Dict, Any, List


# ---------- HELPERS ----------
money_regex = re.compile(
    r"""
    (?:\$|USD\s*)?                     # optional currency symbol
    (\d{1,3}(?:[,\.]\d{3})*|\d+)       # number with thousands or just digits
    (?:\s*(k|K|m|M))?                  # optional suffix (k, m)
    """,
    re.VERBOSE,
)

percent_regex = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")

date_regex = re.compile(
    r"\b("
    r"\d{1,2}/\d{1,2}/\d{2,4}|"
    r"\d{4}-\d{2}-\d{2}|"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},\s+\d{4}"
    r")\b"
)


# Convert $4.2M or $5k to numeric
def normalize_money(value: str) -> float:
    value = value.replace(",", "").replace("$", "").replace("USD", "").strip()
    multiplier = 1

    if value.lower().endswith("k"):
        multiplier = 1_000
        value = value[:-1]
    elif value.lower().endswith("m"):
        multiplier = 1_000_000
        value = value[:-1]

    try:
        return float(value) * multiplier
    except:
        return None


# ---------- CORE PARSER ----------
def process_input(text: str) -> Dict[str, Any]:
    """
    Main entry: extract summary, budget, and contract information.
    """

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full_text = " ".join(lines)

    return {
        "summary": extract_summary(full_text),
        "budget": extract_budget_items(lines),
        "contracts": extract_contract_data(full_text),
        "raw_text": text,
    }


# ---------- SUMMARY ----------
def extract_summary(text: str) -> List[str]:
    """
    Extract high-level summary sentences.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = [s for s in sentences if len(s.split()) > 3][:5]
    return summary


# ---------- BUDGET EXTRACTION ----------
def extract_budget_items(lines: List[str]) -> List[Dict[str, Any]]:
    results = []

    for line in lines:
        money_matches = list(money_regex.finditer(line))
        if not money_matches:
            continue

        description = line
        items = []

        for match in money_matches:
            amount_raw = match.group(0)
            amount_normalized = normalize_money(match.group(0))
            items.append({
                "raw": amount_raw,
                "normalized": amount_normalized
            })

        results.append({
            "line": line,
            "amounts": items
        })

    return results


# ---------- CONTRACT EXTRACTION ----------
def extract_contract_data(text: str) -> Dict[str, Any]:
    """
    Extract useful contract elements.
    """

    dates = date_regex.findall(text)
    percentages = percent_regex.findall(text)

    parties = []
    if "between" in text.lower():
        # crude party extraction
        try:
            segment = text.lower().split("between", 1)[1]
            segment = segment.split("and", 1)
            p1 = segment[0].strip(" ,.")
            p2 = segment[1].split(".")[0].strip(" ,.")
            parties = [p1.title(), p2.title()]
        except:
            pass

    payment_terms = []
    for line in text.splitlines():
        if any(word in line.lower() for word in ["payment", "fee", "compensation", "invoice"]):
            payment_terms.append(line.strip())

    return {
        "dates": dates,
        "percentages": percentages,
        "parties": parties,
        "payment_terms": payment_terms,
    }
