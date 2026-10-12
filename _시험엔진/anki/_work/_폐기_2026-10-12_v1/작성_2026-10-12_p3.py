# ═════════════════ 구노트 — 부동산세법 05-02부터 (10-05 1판 문안 재사용 · 원문 재대조) ═════════════════
V1 = json.load(open(os.path.join(HERE, "_폐기_2026-10-05_v1/카드메타_2026-10-05.json"), encoding="utf-8"))
OLD_ORDER = ["2026-05-02", "2026-05-09", "2026-05-16", "2026-05-24", "2026-05-30", "2026-06-07", "2026-06-13"]
# 이번 주 의무 카드와 같은 사실(교차 누출·중복) → 제외
OLD_DROP = {"세법-구-국외부동산임대-무조건과세": "이번 주 세법 10-08 L106(국외 소재 주택 월세 과세)과 같은 사실",
            "세법-구-지방세제척기간-사기부정상속증여-10년": "이번 주 세법 10-08 L119(사기가 아닌 무신고 10년 = 상속·증여·명의신탁약정·과점주주)과 같은 사실"}
OLD_DROPPED = []
OLD_CHANGED = []
def _ov_gogi(c):
    c["front"] = "재산세 + {{c1::지방교육세}} + {{c2::소방분 지역자원시설세}} → 동일 고지서로 발송된다"; c["ncards"] = 2
def _ov_gihan(c):
    c["kind"] = "T1"; c["has_f"] = False; c["tags"] = c["tags"].replace(" T4", " T1"); c["dsrc"] = ""
    c["back"] = CSS + "<div class='hg hg-o'><span class=hg-v>현행 기준 확인</span></div>"
def _ov_buin(c):
    c["front"] = "배우자·직계존비속 외의 특수관계인 간 증여 후 양도 — 양도행위를 부인하면 {{c1::증여자}}가 납세의무를 부담한다"
def _ov_daesu(c):
    c["front"] = "취득세 — 취득 당시 시가표준액 9억원 이하 공동주택 개수는 비과세 / 대수선은 {{c1::금액 무관 무조건 과세}}"
def _ov_gwonri(c):
    c["front"] = c["front"].replace("취득세 과세대상인 권리 = {{c1::", "취득세 과세대상인 권리 6 = {{c1::"); assert " 6 = " in c["front"]
def _ov_sangsok(c):
    c["front"] = "취득세 상속의 범위 — 사실상 상속에 포함되는 것 3 = {{c1::유증·포괄유증·신탁재산의 상속}}"
OLD_OVERRIDE = {"세법-구-대수선-무조건과세": _ov_daesu, "세법-구-취득세과세대상-권리6": _ov_gwonri, "세법-구-상속범위-유증포괄유증신탁재산": _ov_sangsok, "세법-구-재산세고지-병합세목3": _ov_gogi, "세법-구-기한후신고-감면-50-30-20": _ov_gihan, "세법-구-양도행위부인-증여자납세의무": _ov_buin}
TARGET = 210
acc = sum(c["ncards"] for c in CARDS)
MANDATORY_COUNT = sum(c["ncards"] for c in CARDS if c["lane"] != "무표식")
OLD_KEEP_NOTES, OLD_NEXT = [], None
for d in OLD_ORDER:
    if acc >= TARGET:
        OLD_NEXT = OLD_NEXT or d; continue
    rows = [m for m in V1 if m["lane"] == "구노트" and m["src"].startswith(d)]
    assert rows, d
    src = rows[0]["src"]
    lines_now = open(f"{ROOT}/공인중개사/{src}", encoding="utf-8").read().split("\n")
    for m in rows:
        if m["key"] in OLD_DROP:
            OLD_DROPPED.append((m, OLD_DROP[m["key"]])); continue
        now = [lines_now[n - 1].strip() for n in m["lines"]]
        assert now == m["mark"], (m["key"], now, m["mark"])  # 원문이 바뀌었으면 멈춘다
        c = dict(m); c["lane"] = "구노트"; c["note"] = d; c.setdefault("binary_curly", False)
        if c["key"] in OLD_OVERRIDE: OLD_OVERRIDE[c["key"]](c); OLD_CHANGED.append(c["key"])
        assert "\t" not in c["front"] + c["back"] and '="' not in c["front"] + c["back"]
        CARDS.append(c); acc += c["ncards"]
    OLD_KEEP_NOTES.append(d)
assert OLD_NEXT, "구노트 7개 노트를 다 써도 목표 미달 — OLD_ORDER 확장 필요"
print("구노트 변경:", OLD_CHANGED); print("구노트 유지:", OLD_KEEP_NOTES, "| 다음 시작점:", OLD_NEXT, "| 제외:", [k["key"] for k, _ in OLD_DROPPED])

# ═════════════════ 출력 ═════════════════
TOTAL = sum(c["ncards"] for c in CARDS)
keys = [c["key"] for c in CARDS]
assert len(keys) == len(set(keys)), [k for k in keys if keys.count(k) > 1]
existing = set()
for fpath in glob.glob(f"{ROOT}/_시험엔진/anki/카드_*.tsv"):
    if "2026-10-12" in fpath: continue
    for i, l in enumerate(open(fpath, encoding="utf-8")):
        if i: existing.add(l.rstrip("\n").split("\t")[-1])
dup = [k for k in keys if k in existing]
assert not dup, dup
out = f"{ROOT}/_시험엔진/anki/카드_2026-10-12.tsv"
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\t".join(["deck", "type", "front", "back", "tags", "src", "key"]) + "\n")
    for c in CARDS:
        row = [c["deck"], c["type"], c["front"], c["back"], c["tags"], c["src"], c["key"]]
        for vv in row: assert "\t" not in vv and "\n" not in vv
        fh.write("\t".join(row) + "\n")
json.dump(dict(cards=CARDS, hold=HOLD, old_keep=OLD_KEEP_NOTES, old_next=OLD_NEXT, old_dropped=[(m["key"], r) for m, r in OLD_DROPPED], old_changed=OLD_CHANGED, mandatory=MANDATORY_COUNT),
          open(f"{HERE}/카드메타_2026-10-12.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rows", len(CARDS), "cards", TOTAL, "mandatory", MANDATORY_COUNT)
print(Counter(c["kind"] for c in CARDS))
print("lane cards:", {k: sum(c["ncards"] for c in CARDS if c["lane"].split("+")[0] == k) for k in ["★★", "★", "무표식", "구노트"]})
print("{} rows", sum(1 for c in CARDS if "{}" in c["lane"]))
print("★★ rows", sum(1 for c in CARDS if c["lane"].startswith("★★")), "기출직결 tag rows", sum(1 for c in CARDS if "기출직결" in c["tags"]))
print("multi-number notes", sum(1 for c in CARDS if c["ncards"] >= 2), "cards", sum(c["ncards"] for c in CARDS if c["ncards"] >= 2))
print("도식 노트", sum(1 for c in CARDS if c["has_f"]), "/", len(CARDS))
print("T3 without ①", [c["key"] for c in CARDS if c["kind"] == "T3" and not c["has_a"]])
print("T3/T4 without ②", [c["key"] for c in CARDS if c["kind"] in ("T3", "T4") and not c["has_f"]])
print("cards per deck:", {d: sum(c["ncards"] for c in CARDS if c["deck"] == d) for d in sorted(set(c["deck"] for c in CARDS))})
print("holds", len(HOLD))
