#!/usr/bin/env python3
"""Scan prose for common AI-writing tells.

The script flags patterns for human review. It does not prove AI use.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


BANNED_PHRASES = [
    "let's dive in",
    "dive into",
    "let's explore",
    "let's break down",
    "game-changer",
    "groundbreaking",
    "revolutionary",
    "cutting-edge",
    "leverage",
    "utilize",
    "facilitate",
    "streamline",
    "in today's fast-paced world",
    "in the world of",
    "whether you're a beginner or expert",
    "without further ado",
    "it's worth noting that",
    "interestingly",
    "happy coding",
]

AI_VOCAB = [
    "additionally",
    "align with",
    "boasts",
    "bolstered",
    "crucial",
    "delve",
    "emphasizing",
    "enduring",
    "enhance",
    "fostering",
    "garner",
    "highlight",
    "interplay",
    "intricate",
    "intricacies",
    "key",
    "landscape",
    "meticulous",
    "meticulously",
    "pivotal",
    "robust",
    "showcase",
    "tapestry",
    "testament",
    "underscore",
    "valuable",
    "vibrant",
]

COPULATIVE_AVOIDANCE = [
    "serves as",
    "stands as",
    "marks a",
    "marks an",
    "represents a",
    "represents an",
    "holds the distinction",
]

NEGATIVE_PARALLELISM_PATTERNS = [
    re.compile(r"\bnot\s+only\b.+\bbut\s+also\b", re.IGNORECASE),
    re.compile(r"\bnot\s+just\b.+\bbut\b", re.IGNORECASE),
    re.compile(r"\bit\s+is\s+not\b.+\bit\s+is\b", re.IGNORECASE),
    re.compile(r"\bit's\s+not\b.+\bit's\b", re.IGNORECASE),
    re.compile(r"\bno\b.+,\s*\bno\b.+,\s*\bjust\b", re.IGNORECASE),
]

RULE_OF_THREE = re.compile(
    r"\b([A-Za-z][A-Za-z-]+),\s+([A-Za-z][A-Za-z-]+),\s+(and|or)\s+([A-Za-z][A-Za-z-]+)\b"
)

INLINE_HEADER_LIST = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*]{2,80}\*\*:\s+\S")
TITLE_CASE_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
THEMATIC_BREAK = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")


def is_title_case_heading(text: str) -> bool:
    words = [w.strip("`*_[]()") for w in re.split(r"\s+", text)]
    words = [w for w in words if w and any(c.isalpha() for c in w)]
    if len(words) < 3:
        return False
    capped = 0
    for word in words:
        first = next((c for c in word if c.isalpha()), "")
        if first and first.isupper():
            capped += 1
    return capped >= max(3, len(words) - 1)


def find_column(line: str, needle: str) -> int:
    idx = line.lower().find(needle.lower())
    return idx + 1 if idx >= 0 else 1


def emit(findings: list[tuple[str, int, int, str, str]], path: str, line_no: int, col: int, code: str, message: str) -> None:
    findings.append((path, line_no, col, code, message))


def scan_text(path_label: str, text: str) -> list[tuple[str, int, int, str, str]]:
    findings: list[tuple[str, int, int, str, str]] = []
    lines = text.splitlines()
    previous_was_break = False
    previous_heading_level = 0

    for line_no, line in enumerate(lines, start=1):
        lower = line.lower()

        for phrase in BANNED_PHRASES:
            if phrase in lower:
                emit(findings, path_label, line_no, find_column(line, phrase), "phrase", f"stock AI phrase: {phrase}")

        for word in AI_VOCAB:
            pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, lower):
                emit(findings, path_label, line_no, find_column(line, word), "vocab", f"AI-vocabulary word to review: {word}")

        for phrase in COPULATIVE_AVOIDANCE:
            if phrase in lower:
                emit(findings, path_label, line_no, find_column(line, phrase), "copula", f"plain 'is' or 'has' may work better than '{phrase}'")

        em_dash = "\u2014"
        if em_dash in line:
            emit(findings, path_label, line_no, line.index(em_dash) + 1, "dash", "em dash")

        for char, label in [
            ("\u201c", "curly opening quote"),
            ("\u201d", "curly closing quote"),
            ("\u2018", "curly opening apostrophe"),
            ("\u2019", "curly apostrophe"),
        ]:
            if char in line:
                emit(findings, path_label, line_no, line.index(char) + 1, "curly", label)

        for pattern in NEGATIVE_PARALLELISM_PATTERNS:
            match = pattern.search(line)
            if match:
                emit(findings, path_label, line_no, match.start() + 1, "negative-parallelism", "corrective construction")

        match = RULE_OF_THREE.search(line)
        if match:
            emit(findings, path_label, line_no, match.start() + 1, "rule-of-three", "possible padding by three-part list")

        if INLINE_HEADER_LIST.search(line):
            emit(findings, path_label, line_no, 1, "inline-header-list", "bold inline header list item")

        heading = TITLE_CASE_HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            heading_text = heading.group(2)
            if previous_heading_level and level > previous_heading_level + 1:
                emit(findings, path_label, line_no, 1, "heading-level", "skipped markdown heading level")
            if is_title_case_heading(heading_text):
                emit(findings, path_label, line_no, 1, "title-case-heading", "title-case heading")
            if previous_was_break:
                emit(findings, path_label, line_no, 1, "break-before-heading", "thematic break before heading")
            previous_heading_level = level

        previous_was_break = bool(THEMATIC_BREAK.match(line))

    return findings


def read_inputs(paths: list[str]) -> list[tuple[str, str]]:
    if not paths:
        data = sys.stdin.buffer.read()
        try:
            return [("<stdin>", data.decode("utf-8-sig"))]
        except UnicodeDecodeError:
            return [("<stdin>", data.decode("cp1252"))]

    inputs: list[tuple[str, str]] = []
    for raw_path in paths:
        path = Path(raw_path)
        try:
            inputs.append((str(path), path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            inputs.append((str(path), path.read_text(encoding="utf-8-sig")))
    return inputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan prose for common AI-writing tells.")
    parser.add_argument("paths", nargs="*", help="Text or markdown files to scan. Reads stdin when omitted.")
    parser.add_argument("--fail-on-findings", action="store_true", help="Return exit code 1 when findings exist.")
    args = parser.parse_args()

    all_findings: list[tuple[str, int, int, str, str]] = []
    for path_label, text in read_inputs(args.paths):
        all_findings.extend(scan_text(path_label, text))

    if not all_findings:
        print("No AI-writing tells found.")
        return 0

    for path, line_no, col, code, message in all_findings:
        print(f"{path}:{line_no}:{col}: {code}: {message}")

    return 1 if args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
