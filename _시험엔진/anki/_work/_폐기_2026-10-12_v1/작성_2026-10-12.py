# -*- coding: utf-8 -*-
"""2026-10-12 정규 덱 — 카드 문안 (디자인 v2.1 · 공인중개사만 → T1·T3·T4, 가족 노트 0).
스타일 블록은 참조 문서에서 정규식으로 읽는다. 실행: python3 작성_2026-10-12.py → ../카드_2026-10-12.tsv + 카드메타_2026-10-12.json
"""
import re, json, os, hashlib, glob
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
REF = open(f"{ROOT}/_시험엔진/spec/참조_카드디자인.md", encoding="utf-8").read()
CSS, RESTORE = re.findall(r"^(<style>.*?</style>)$", REF, re.M)[:2]
assert CSS.startswith("<style>.hg{") and RESTORE.startswith("<style>.hg .cloze-inactive{")
assert hashlib.md5(CSS.encode()).hexdigest() == "590d23d548cc89eff7885eeb94fdc4ea"

def one(pattern):
    fs = glob.glob(f"{ROOT}/공인중개사/{pattern}")
    assert len(fs) == 1, (pattern, fs)
    return os.path.basename(fs[0])
NOTES = {
    "M": (one("2026-10-05-민법-*.md"), "자격증::공인중개사::민법", "hg-o", "공인중개사 민법"),
    "G": (one("2026-10-06-부동산공법-*.md"), "자격증::공인중개사::부동산공법", "hg-b", "공인중개사 부동산공법"),
    "J": (one("2026-10-07-공인중개사법-*.md"), "자격증::공인중개사::공인중개사법", "hg-b", "공인중개사 공인중개사법"),
    "S": (one("2026-10-08-부동산세법-*.md"), "자격증::공인중개사::부동산세법", "hg-o", "공인중개사 부동산세법"),
    "P": (one("2026-10-09-부동산공시법-*.md"), "자격증::공인중개사::부동산공시법", "hg-b", "공인중개사 부동산공시법"),
    "K": (one("2026-10-10-부동산학개론-*.md"), "자격증::공인중개사::부동산학개론", "hg-o", "공인중개사 부동산학개론"),
}
LINES = {k: open(f"{ROOT}/공인중개사/{v[0]}", encoding="utf-8").read().split("\n") for k, v in NOTES.items()}
def L(note, n): return LINES[note][n - 1].strip()

def hl(s): return f"<span class=hg-hl>{s}</span>"
def table(headers, rows):
    h = "".join(f"<th>{c}</th>" for c in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table class=hg-t><tr>{h}</tr>{b}</table>"
def tree(items):
    def li(x):
        if isinstance(x, (list, tuple)):
            return f"<li>{x[0]}<ul>{''.join(li(y) for y in x[1])}</ul></li>"
        return f"<li>{x}</li>"
    return f"<div class=hg-tr><ul>{''.join(li(i) for i in items)}</ul></div>"

CARDS = []
def card(note, kind, front, key, lane, lines, *, a=None, f=None, w=None, m=None, x=None, v=False, dsrc="", split=False, mustcontain=None, binary_curly=False):
    fn, deck, color, tagbase = NOTES[note]
    parts = []
    if a: parts.append(f"<div class=hg-a>📐 {a}</div>")
    if f: parts.append(f"<div class=hg-f>{f}</div>")
    if w: parts.append(f"<div class=hg-w><b>왜</b> {w}</div>")
    if m: parts.append(f"<div class=hg-w><b>기억</b> {m}</div>")
    if x: parts.append(f"<div class=hg-x><b>함정</b> {x}</div>")
    if v: parts.append("<span class=hg-v>현행 기준 확인</span>")
    body = f"<div class='hg {color}'>" + "".join(parts) + "</div>" if parts else ""
    back_html = (CSS + body) if body else ""
    base = lane.split("+")[0]
    lane_tag = {"★★": "강조 기출직결", "★": "강조", "무표식": "무표식"}[base]
    if "{}" in lane: lane_tag += " 중괄호"
    tags = " ".join(dict.fromkeys(f"{tagbase} {lane_tag} {kind}".split()))
    for vv in (front, back_html, tags, fn, key, deck):
        assert "\t" not in vv and "\n" not in vv, key
    assert '="' not in front and '="' not in back_html, key
    assert "{{" not in back_html and "}}" not in back_html, key
    assert "class='hg " not in front, key
    assert kind != "T1" or not f, key
    assert kind != "T3" or (a and f), key
    assert kind != "T4" or f, key
    nclz = len(set(re.findall(r"\{\{c(\d+)::", front)))
    assert 1 <= nclz <= 3, key
    assert front.count("{{c") == front.count("}}"), key
    mark = [L(note, n) for n in lines]
    if base != "무표식":
        assert any(("★" in ml or "!" in ml) for ml in mark), key
    if mustcontain:
        for mc in mustcontain: assert any(mc in ml for ml in mark), (key, mc)
    CARDS.append(dict(deck=deck, type="cloze", front=front, back=back_html, tags=tags, src=fn, key=key, kind=kind, lane=lane,
                      lines=lines, mark=mark, dsrc=dsrc, split=split, note=note, ncards=nclz, has_f=bool(f), has_a=bool(a), binary_curly=binary_curly))
    return key

HOLD = []  # (note, line, lane, 항목, 근거, 해소조건)
def hold(note, line, lane, item, why, cond):
    HOLD.append(dict(src=NOTES[note][0], line=line, lane=lane, item=item, why=why, cond=cond, mark=L(note, line)))

exec(open(os.path.join(HERE, "작성_2026-10-12_p1.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "작성_2026-10-12_p2.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "작성_2026-10-12_p3.py"), encoding="utf-8").read())
