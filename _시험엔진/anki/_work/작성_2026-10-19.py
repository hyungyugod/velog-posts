# -*- coding: utf-8 -*-
"""2026-10-19 정규 덱 — 카드 문안 (디자인 v2.1 · 공인중개사 T1·T3·T4 + 법무사 민소 2차 T1~T4, 가족 노트는 법무사만).
스타일 블록은 참조 문서에서 정규식으로 읽는다. 실행: python3 작성_2026-10-19.py → ../카드_2026-10-19.tsv + 카드메타_2026-10-19.json
"""
import re, json, os, hashlib, glob
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
REF = open(f"{ROOT}/_시험엔진/spec/참조_카드디자인.md", encoding="utf-8").read()
CSS, RESTORE = re.findall(r"^(<style>.*?</style>)$", REF, re.M)[:2]
assert CSS.startswith("<style>.hg{") and RESTORE.startswith("<style>.hg .cloze-inactive{")
assert hashlib.md5(CSS.encode()).hexdigest() == "590d23d548cc89eff7885eeb94fdc4ea"
assert hashlib.md5(RESTORE.encode()).hexdigest() == "b92b4c230f9abb5105adf5137d9eac5a"

def one(folder, pattern):
    fs = glob.glob(f"{ROOT}/{folder}/{pattern}")
    assert len(fs) == 1, (pattern, fs)
    return os.path.basename(fs[0])
# note id: (folder, file, deck, color, tagbase)
NOTES = {
    "K1": ("공인중개사", one("공인중개사", "2026-10-12-부동산학개론-*.md"), "자격증::공인중개사::부동산학개론", "hg-o", "공인중개사 부동산학개론"),
    "M":  ("공인중개사", one("공인중개사", "2026-10-13-민법-*.md"), "자격증::공인중개사::민법", "hg-o", "공인중개사 민법"),
    "G":  ("공인중개사", one("공인중개사", "2026-10-14-부동산공법-*.md"), "자격증::공인중개사::부동산공법", "hg-b", "공인중개사 부동산공법"),
    "J":  ("공인중개사", one("공인중개사", "2026-10-15-공인중개사법-*.md"), "자격증::공인중개사::공인중개사법", "hg-b", "공인중개사 공인중개사법"),
    "S":  ("공인중개사", one("공인중개사", "2026-10-15-부동산세법-*.md"), "자격증::공인중개사::부동산세법", "hg-o", "공인중개사 부동산세법"),
    "K2": ("공인중개사", one("공인중개사", "2026-10-16-부동산학개론-*.md"), "자격증::공인중개사::부동산학개론", "hg-o", "공인중개사 부동산학개론"),
    "P":  ("공인중개사", one("공인중개사", "2026-10-17-부동산공시법-*.md"), "자격증::공인중개사::부동산공시법", "hg-b", "공인중개사 부동산공시법"),
    "N1": ("공인중개사", one("공인중개사", "2026-10-18-공인중개사-*.md"), "자격증::공인중개사::부동산학개론", "hg-o", "공인중개사 부동산학개론"),
    "N2": ("공인중개사", one("공인중개사", "2026-10-18-공인중개사-*.md"), "자격증::공인중개사::민법", "hg-o", "공인중개사 민법"),
    "N3": ("공인중개사", one("공인중개사", "2026-10-18-공인중개사-*.md"), "자격증::공인중개사::공인중개사법", "hg-b", "공인중개사 공인중개사법"),
    "N4": ("공인중개사", one("공인중개사", "2026-10-18-공인중개사-*.md"), "자격증::공인중개사::부동산공법", "hg-b", "공인중개사 부동산공법"),
    "N5": ("공인중개사", one("공인중개사", "2026-10-18-공인중개사-*.md"), "자격증::공인중개사::부동산공시법", "hg-b", "공인중개사 부동산공시법"),
    "B":  ("법무사", one("법무사", "2026-10-17-민사소송법-2차-*.md"), "자격증::법무사::민사소송법", "hg-b", "법무사 민사소송법 2차"),
}
# 구노트 (세법)
for tag, pat in [("O0530", "2026-05-30-부동산세법-*.md"), ("O0607", "2026-06-07-부동산세법-*.md"), ("O0613", "2026-06-13-부동산세법-*.md"),
                 ("O0620", "2026-06-20-부동산세법-*.md"), ("O0627", "2026-06-27-부동산세법-*.md"), ("O0705", "2026-07-05-부동산세법-*.md"),
                 ("O0711", "2026-07-11-부동산세법-*.md"), ("O0712", "2026-07-12-부동산세법-*.md"), ("O0719", "2026-07-19-부동산세법-*.md"), ("O0725", "2026-07-25-부동산세법-*.md")]:
    NOTES[tag] = ("공인중개사", one("공인중개사", pat), "자격증::공인중개사::부동산세법", "hg-o", "공인중개사 부동산세법")
LINES = {k: open(f"{ROOT}/{v[0]}/{v[1]}", encoding="utf-8").read().split("\n") for k, v in NOTES.items()}
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
def branch(q, lines_):
    return f"<div class=hg-q>{q}</div><div class=hg-br>" + "".join(f"<div>{x}</div>" for x in lines_) + "</div>"

CARDS = []
LANE_TAG = {"★★": "강조 기출직결", "★": "강조", "{}": "중괄호", "무표식": "무표식", "구노트": "구노트"}
def card(note, kind, front, key, lane, lines, *, a=None, f=None, w=None, m=None, x=None, v=False, dsrc="", split=False,
         mustcontain=None, binary_curly=False, pair=False, family=False, merged=False):
    folder, fn, deck, color, tagbase = NOTES[note]
    parts = []
    if a: parts.append(f"<div class=hg-a>📐 {a}</div>")
    if f: parts.append(f"<div class=hg-f>{f}</div>")
    if w: parts.append(f"<div class=hg-w><b>왜</b> {w}</div>")
    if m: parts.append(f"<div class=hg-w><b>기억</b> {m}</div>")
    if x: parts.append(f"<div class=hg-x><b>함정</b> {x}</div>")
    if v: parts.append("<span class=hg-v>현행 기준 확인</span>")
    body = f"<div class='hg {color}'>" + "".join(parts) + "</div>" if parts else ""
    if family:
        assert "법무사" in deck, key
        front = CSS + f"<div class='hg {color}'>" + front + "</div>"
        back_html = RESTORE + body
    else:
        back_html = (CSS + body) if body else ""
    base = lane.split("+")[0]
    lane_tag = LANE_TAG[base]
    if "{}" in lane and base != "{}": lane_tag += " 중괄호"
    tags = " ".join(dict.fromkeys(f"{tagbase} {lane_tag} {kind}".split()))
    for vv in (front, back_html, tags, fn, key, deck):
        assert "\t" not in vv and "\n" not in vv, key
    assert '="' not in front and '="' not in back_html, key
    assert "{{" not in back_html and "}}" not in back_html, key
    if not family: assert "class='hg " not in front, key
    assert kind != "T1" or not f, key
    assert kind != "T3" or (a and (f or family)), key
    assert kind != "T4" or f or pair, key
    assert kind != "T2" or family, key
    nclz = len(set(re.findall(r"\{\{c(\d+)::", front)))
    assert 1 <= nclz <= 3, key
    assert front.count("{{c") == front.count("}}"), key
    assert all(f"{{{{c{i}::" in front for i in range(1, nclz + 1)), key
    if not family and "공인중개사" in deck and kind in ("T2",): raise AssertionError(key)
    mark = [L(note, n) for n in lines]
    if base not in ("무표식", "구노트", "{}"):
        assert any(("★" in ml or "!" in ml) for ml in mark), key
    if "{}" in lane:
        assert any(re.search(r"\{[^{}]+\}", ml) for ml in mark), key
    if mustcontain:
        for mc in mustcontain: assert any(mc in ml for ml in mark), (key, mc)
    assert key not in [c["key"] for c in CARDS], key
    CARDS.append(dict(deck=deck, type="cloze", front=front, back=back_html, tags=tags, src=fn, key=key, kind=kind, lane=lane,
                      lines=lines, mark=mark, dsrc=dsrc, split=split, merged=merged, note=note, ncards=nclz, has_f=bool(f) or (family and kind == "T2"),
                      has_a=bool(a), binary_curly=binary_curly, family=family, pair=pair))
    return key

HOLD = []
def hold(note, line, lane, item, why, cond):
    HOLD.append(dict(src=NOTES[note][1], line=line, lane=lane, item=item, why=why, cond=cond, mark=L(note, line)))
DUP = []  # 기출고 중복 제외 (note, line, lane, existing key(s), memo)
def dup(note, line, lane, keys, memo=""):
    DUP.append(dict(src=NOTES[note][1], line=line, lane=lane, keys=keys, memo=memo, mark=L(note, line)))
SKIP = []  # 요령·머리줄 등 카드 없음
def skip(note, line, lane, why):
    SKIP.append(dict(src=NOTES[note][1], line=line, lane=lane, why=why, mark=L(note, line)))

for part in ("p1", "p2", "p3", "p4"):
    exec(open(os.path.join(HERE, f"작성_2026-10-19_{part}.py"), encoding="utf-8").read())

# ── 기출고 key 충돌 검사 ──
EXIST = set(open(os.path.join(HERE, "기출키_2026-10-19.txt"), encoding="utf-8").read().split())
REUSED = {c["key"] for c in CARDS if c["lane"] == "구노트" and c["key"] in EXIST}
clash = [c["key"] for c in CARDS if c["key"] in EXIST and c["key"] not in REUSED]
assert not clash, clash
# ── TSV ──
out = f"{HERE}/../카드_2026-10-19.tsv"
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\t".join(["deck", "type", "front", "back", "tags", "src", "key"]) + "\n")
    for c in CARDS:
        row = [c["deck"], c["type"], c["front"], c["back"], c["tags"], c["src"], c["key"]]
        for vv in row: assert "\t" not in vv and "\n" not in vv
        fh.write("\t".join(row) + "\n")
json.dump(dict(cards=CARDS, hold=HOLD, dup=DUP, skip=SKIP, old_keep=OLD_KEEP, old_next=OLD_NEXT, old_dropped=OLD_DROPPED),
          open(f"{HERE}/카드메타_2026-10-19.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(c["ncards"] for c in CARDS)
print("rows", len(CARDS), "cards", tot, Counter(c["kind"] for c in CARDS), Counter(c["lane"].split("+")[0] for c in CARDS))
print("법무사 다중", sum(c["ncards"] for c in CARDS if "법무사" in c["deck"] and c["ncards"] >= 2), "hold", len(HOLD), "dup", len(DUP), "skip", len(SKIP))
