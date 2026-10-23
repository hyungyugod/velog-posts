# -*- coding: utf-8 -*-
"""표식 승계 — 줄머리 ★★/★ + (08-30처럼) 소제목 줄에 단 ★를 그 소제목 아래 줄에 승계."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "src_index.json"), encoding="utf-8"))
COMBINED = "/mnt/user-data/uploads/velog-posts/_시험엔진/anki/_work/특판_원천_2026-10-23.md"

HEADSTAR = {}
_note = None
_cur = ""
for raw in open(COMBINED, encoding="utf-8"):
    m = re.match(r"^==== \[(\d\d)-(\d\d)\]", raw)
    if m:
        _note = m.group(1) + m.group(2)
        _cur = ""
        continue
    m = re.match(r"^(?:  |⛔)L(\d+)\| ?(.*)$", raw.rstrip("\n"))
    if not m or _note is None:
        continue
    ln, text = int(m.group(1)), m.group(2)
    if re.match(r"^#{1,2}\s", text):
        _cur = ""
        continue
    h = re.match(r"^###\s+(?:\d+\)\s*)?(★★|★)", text)
    if text.startswith("### "):
        _cur = h.group(1) if h else ""
        continue
    if _cur:
        HEADSTAR[f"{_note}:{ln}"] = _cur


def line_star(k):
    t = SRC[k]["text"]
    m = re.match(r"^\s*(?:[-*]|\d+\.)?\s*(★★|★)", t)
    return m.group(1) if m else ""


def star_of(k):
    s = line_star(k)
    if s:
        return s
    return HEADSTAR.get(k, "")


def item_star(it):
    st = [star_of(k) for k in it.src if k in SRC]
    return "★★" if "★★" in st else ("★" if "★" in st else "")
