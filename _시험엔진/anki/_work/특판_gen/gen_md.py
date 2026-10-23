# -*- coding: utf-8 -*-
"""특별판 정리본(.md) 생성 — data_*.py가 단일 원천(카드 TSV와 같은 문장·같은 빈칸)."""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import dsl
import data_a, data_b, data_c, data_d  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "src_index.json"), encoding="utf-8"))
META = json.load(open(os.path.join(HERE, "cards_meta.json"), encoding="utf-8"))
HOLE = re.compile(r"\{([^{}]+)\}")


from stars import star_of, item_star  # noqa: E402


def to_md(text):
    return HOLE.sub(lambda m: "{" + m.group(1).split("::")[0].strip() + "}", text)


def src_line(keys):
    order, byn = [], {}
    for k in keys:
        n, l = k.split(":")
        if n not in byn:
            byn[n] = []
            order.append(n)
        if int(l) not in byn[n]:
            byn[n].append(int(l))
    return " | ".join(f"{n[:2]}-{n[2:]} L" + "·".join(str(x) for x in byn[n]) for n in order)


NOTES = {
    "파이널 100선 문제풀이": ["0930", "1007", "1015", "1021"],
    "박문각 월 모의고사(2차 중개사법 부분)": ["0601", "0629", "0727", "0830", "0920", "1018"],
    "기출 WOX 회독": ["0405", "0412", "0419", "0426", "0503", "0510", "0517", "0518",
                    "0521", "0527", "0604", "0610", "0617", "0624", "0703", "0708", "0722"],
}
used_notes = set()
for ch in dsl.CHAPTERS:
    for sec in ch.secs:
        for sub in sec.subs:
            for it in sub.items:
                for k in it.src + it.extra_src:
                    used_notes.add(k.split(":")[0])

out = []
w = out.append
n_items = sum(len(sub.items) for ch in dsl.CHAPTERS for sec in ch.secs for sub in sec.subs)
n_holes = sum(len(HOLE.findall(it.text)) for ch in dsl.CHAPTERS for sec in ch.secs for sub in sec.subs for it in sub.items)
n_s2 = sum(1 for ch in dsl.CHAPTERS for sec in ch.secs for sub in sec.subs for it in sub.items if item_star(it) == "★★")
n_s1 = sum(1 for ch in dsl.CHAPTERS for sec in ch.secs for sub in sec.subs for it in sub.items if item_star(it) == "★")

w("> **중개사법 특별판 — 모의·기출·파이널 WOX 총정리** (2026-10-23)")
w(">")
w("> 공인중개사법·부동산거래신고법·중개실무를 한 파일로 모았다. 노트에 적힌 문장만 썼다 — 같은 사실은 한 줄로 합쳤고, "
  "노트끼리 어긋나거나 ⚠️·확인 필요가 붙은 줄은 본문에서 빼서 맨 아래 「⚠️ 확인 필요」 표로 보냈다.")
w(">")
srcs = []
for g, ds in NOTES.items():
    ds_used = [d for d in ds if d in used_notes]
    srcs.append(f"{g} {len(ds_used)}개(" + "·".join(f"{d[:2]}-{d[2:]}" for d in ds_used) + ")")
w("> - 원천: " + " / ".join(srcs) + f" = 노트 {len(used_notes)}개")
w(f"> - 규모: 20장 · 항목 {n_items}개(★★ {n_s2} · ★ {n_s1}) · 빈칸 {n_holes}개 → Anki `중개사법특별판` 덱 {len(META)}장(소제목 1개 = 카드 1장)")
w("> - `{ }` = Anki 빈칸과 같은 자리 — 읽을 때 `{ }` 안을 손으로 가리고 먼저 말해 본다")
w("> - ★★·★ = 원문 줄머리 표식 승계 · (현행 기준 참고) = 시행령·고시 수치(개정 여부 확인) · `예)`·`→`(이유)·`기억)`·`함정)` = 원문 노트의 줄(소제목에 단 ★도 그 아래 항목에 승계)")
w("> - 소제목 끝 *원천* = 노트 날짜·줄 번호 — 이상하면 원문 노트에서 그 줄을 찾는다")
w("")
w("| 장 | 주제 | 항목 | ★★ | 카드 |")
w("|---|---|---|---|---|")
for ch in dsl.CHAPTERS:
    its = [it for sec in ch.secs for sub in sec.subs for it in sub.items]
    nc = sum(len(sec.subs) for sec in ch.secs)
    w(f"| {ch.no} | {ch.title} | {len(its)} | {sum(1 for it in its if item_star(it) == '★★')} | {nc} |")
w("")
w("---")
w("")

for ch in dsl.CHAPTERS:
    w(f"# 📌 {ch.no}. {ch.title}")
    w("")
    for sec in ch.secs:
        w(f"## {sec.no}. {sec.title}")
        tip = sec.tip if sec.tip.startswith("💡") else "💡 " + sec.tip
        w(f"> {tip}")
        w("")
        for si, sub in enumerate(sec.subs, start=1):
            w(f"### {si}) {sub.title}")
            keys = []
            for it in sub.items:
                st = item_star(it)
                t = to_md(it.text)
                if it.chip and "현행 기준" not in t:
                    t += " (현행 기준 참고)"
                w(f"- {st + ' ' if st else ''}{t}")
                if it.why:
                    w(f"  - → {it.why}")
                if it.mem:
                    w(f"  - 기억) {it.mem}")
                if it.ex:
                    w(f"  - 예) {it.ex}")
                if it.trap:
                    w(f"  - 함정) {it.trap}")
                keys += it.src + it.extra_src
            w(f"- *원천: {src_line(keys)}*")
            w("")
    w("---")
    w("")

open(os.path.join(HERE, "body.md"), "w", encoding="utf-8").write("\n".join(out))
print("items", n_items, "holes", n_holes, "★★", n_s2, "★", n_s1, "notes", len(used_notes))
print("unused notes:", sorted(set(d for ds in NOTES.values() for d in ds) - used_notes))
