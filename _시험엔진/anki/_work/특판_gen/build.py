# -*- coding: utf-8 -*-
"""특별판 빌더 — data_*.py → 검증 → 정리본 md · 카드 TSV · 검수 표 원재료(json)."""
import json, re, sys, os, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import dsl
import data_a, data_b, data_c, data_d  # noqa: F401  (등록 부수효과)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "src_index.json"), encoding="utf-8"))
REF = open("/mnt/user-data/uploads/velog-posts/_시험엔진/spec/참조_카드디자인.md", encoding="utf-8").read()
CSS, RESTORE = re.findall(r"^(<style>.*?</style>)$", REF, re.M)[:2]
assert CSS.startswith("<style>.hg{") and RESTORE.startswith("<style>.hg .cloze-inactive{")

# ── 출제 금지 줄: 추출기 banned(⛔) + 사람 판독(Sonnet 매핑 · 작성자 판단) ─────────────────────
EXTRA_BAN = {
    # Sonnet 매핑 — 확인 필요 섹션·💡 보류·백지 ⑦
    "1021:73": "💡 '원문 수치 대조 전까지 출제 보류'", "1021:76": "백지⑦ #2 이용의무 3개월·이행강제금 6개월",
    "1021:47": "백지⑦ #1(안전 쪽) — 같은 사실은 05-21 L080·L116으로 카드화",
    "0727:11": "확인 필요 #4 소속공인중개사 정의(제2조 제5호와 반대)",
    "0830:135": "⚠️ 배당요구 시한 '매각결정기일'", "0830:136": "⚠️ 배당요구 시한 '매각결정기일'",
    "0521:393": "확인 필요 안내줄", "0521:394": "확인 필요 안내줄", "0521:395": "확인 필요 안내줄",
    "0527:256": "확인 필요 안내줄", "0527:257": "확인 필요 안내줄", "0527:71": "인장 규격 확인 필요(안전 쪽)",
    "0722:21": "확인 필요 #1 지정 주체 '시장군수'", "0722:26": "확인 필요 #2 해제 '할 수 있다'(기속 문언과 충돌)",
    "0722:49": "확인 필요 #3 포상금 범위", "0722:50": "확인 필요 #3 포상금 범위", "0722:101": "확인 필요 #4 자연장지 구분",
    "0510:171": "확인 필요 외국인 허가 대상 구역 매핑", "0503:199": "확인 필요 포상금 금액(안전 쪽)",
    "0503:326": "확인 필요 '아아' 범위(안전 쪽)", "0708:59": "암기코드 대조 권장(안전 쪽) — 같은 사실은 06-10 L188·L203",
    "0708:109": "자진신고 감면 범위(안전 쪽)",
    # Sonnet 권고(같은 쟁점 — 안전 쪽)
    "0624:62": "07-22 L049와 같은 주장(포상금 제외 범위)", "0521:363": "05-10 L213과 같은 주장(외국인 무허가 벌칙)",
    "0510:218": "06-24 L060과 같은 수치(포상금 한도)", "0521:314": "포상금 암기코드 철자 불일치", "0604:198": "포상금 암기코드 철자 불일치",
    "0419:139": "주택면적 1/3 ↔ 05-21 L284 1/2 미만 충돌", "0419:137": "같은 소제목 머리(1/3)",
    "0503:352": "주택임대차 신고 60일 ↔ 06-17 30일 충돌", "0503:353": "주택임대차 신고 60일 ↔ 06-17 30일 충돌",
    "0521:271": "확인설명서 5년 ↔ 04-12·05-27 3년 충돌",
    # 작성자 판단 — 법문·다른 노트와 어긋나 보이는 줄(하단 확인 필요 표에 기재)
    "0521:30": "법인 겸업: 공매대상 부동산 입찰신청 대리는 가능 — '동산' 함정과 혼동 의심",
    "0521:82": "자격정지 '셔(서식) 미사용' — 서식 미사용은 소공 자격정지 사유 아님(10-21 L044·07-08 L088과 충돌)",
    "0503:255": "05-21 L082와 같은 행", "0521:386": "자격정지 '재량 없음' — 자격정지는 '할 수 있다'",
    "0601:57": "💡 '실시기관은 모두 시·도지사' — 직무교육은 시·도지사 또는 등록관청", "0601:68": "같은 주장(셋 다 시·도지사)",
    "0601:70": "실무교육 효력 '기간 제한 없음' — 등록신청일 전 1년 이내 이수 원칙과 충돌", "0601:71": "같은 줄 이어짐",
    "0629:54": "소공 '자격정지 + 500만원 과태료' — 다른 노트 4곳은 소공 = 자격정지만",
    "0617:119": "정정신청도 '등기 전' — 등기신청 전 요건은 변경신고 쪽", "0617:122": "자진신고 감면(07-08 L109와 같은 쟁점)",
    "0624:63": "무허가 계약 '30% 과태료' — 다른 노트는 벌금", "0517:213": "'선의 제3자' 보호·판단 시점 — 실명법 제3자는 선의·악의 불문",
    "0517:214": "같은 쟁점", "1007:38": "배임죄 '벌'의 종류 미특정 — 금고 이상이면 결격",
    "0604:73": "'대표자를 포함한 임원·사원 1/3' — 대표자 부분만 카드화(1/3 기준은 '대표자를 제외한')",
    "0521:238": "100과 '보증 하지 않은 경우' — 손해배상책임 설명·증서 미교부와 혼동 의심", "0503:188": "같은 행",
    "0426:163": "조합 재산 '공유' — 06-17 L009는 합유", "0510:187": "허가 의무 사유 '녹지지역' 표현 불명확",
    "0527:18": "법인 '일반사원' 결격 판단 불명확", "0527:14": "집행유예 결격 기간 표현 불명확",
    "0624:30": "외국인 '6000·30 초과' 문장 의미 불명확",
    # 10/23 독립 검증 반영
    "0521:305": "05-21 하단 확인 필요 박스(L395)가 지목 — 500명·30명 대조 필요", "0527:83": "공개 매체 '무조건 일간신문' ↔ 10-18 L121 '정보망 또는 일간신문'",
    "0419:125": "주택 중개보수 '시·군 조례' — 다른 노트(05-21 L283·L291)는 시·도 조례", "0527:138": "×70 산식에 보증금 누락", "0527:132": "'5천만원 이하' — 같은 노트 L138·06-10 L179는 미만",
    "0527:162": "포상금 '접수일부터 2개월' — 공인중개사법 포상금(06-17 L030 결정일부터 1개월)과 섞임 의심",
    "0604:144": "분사무소 '구마다 하나씩' — 주된 사무소 소재 시·군·구 제외 여부 확인", "0601:93": "분사무소 폐업 첨부 서류 명칭(설치신고서 vs 설치신고확인서)", "0601:97": "같은 쟁점", "0601:101": "같은 쟁점",
    "0604:41": "'거나' 문언 — 07-08 L008(명인방법만 갖추면 대상)과 충돌", "0517:226": "'개인묘지 분묘 1기 10㎡' — 개인묘지 면적 기준 확인",
    "0521:376": "매수신청대리 변동 신고 대상 '위임인' — 10-15 L049는 지방법원장", "0527:242": "같은 쟁점", "0518:137": "같은 쟁점",
    "0527:181": "시도회·지회 설치 '필수 아님' — 2026-08-28 협회 법정단체화 개정 후 조문 확인", "0617:50": "💡 요약 — 같은 절 본문(⛔L053 청문·L057)이 추출기 금지라 우회 금지",
    "0624:42": "'의견 들을 필요 없다' — 07-22 W177: 재지정 때는 의견청취(최초 지정 기준)",
}
# 0604:73은 '대표자는 공인중개사' 부분만 쓰므로 예외로 허용
ALLOW = {"0604:73"}


def is_banned(k):
    if k in ALLOW:
        return None
    e = SRC.get(k)
    if e is None:
        return "원천 없음"
    if e.get("banned"):
        return "추출기 금지: " + "; ".join(e["banned"])
    if k in EXTRA_BAN:
        return "사람 판독 금지: " + EXTRA_BAN[k]
    return None


import stars as _stars


def star_of(k):
    return _stars.star_of(k)


HOLE = re.compile(r"\{([^{}]+)\}")
CIRC = "①②③④⑤⑥⑦⑧⑨⑩"
GROUP = {}  # note short → group
for k, v in SRC.items():
    n = v["note"]
    g = "A" if "파이널" in n else ("B" if "박문각" in n else ("C2" if "민법, 공법" in n else "C"))
    GROUP[k.split(":")[0]] = g

errors, warns = [], []
cards, outline = [], []
for ch in dsl.CHAPTERS:
    for sec in ch.secs:
        for si, sub in enumerate(sec.subs, start=1):
            items_meta = []
            for it in sub.items:
                for k in it.src + it.extra_src:
                    b = is_banned(k)
                    if b:
                        errors.append(f"{sec.no} '{sub.title}' — {k}: {b}")
                if not HOLE.search(it.text):
                    errors.append(f"{sec.no} '{sub.title}' — 빈칸 없음: {it.text[:40]}")
                if "{{" in it.text or "}}" in it.text:
                    errors.append(f"{sec.no} — 이중 중괄호 금지")
                stars = [star_of(k) for k in it.src if k in SRC]
                st = "★★" if "★★" in stars else ("★" if "★" in stars else "")
                items_meta.append((it, st))
            cards.append(dict(ch=ch, sec=sec, si=si, sub=sub, items=items_meta))

# ── 카드 문안 ─────────────────────────────────────────────────────────────
def to_cloze(text):
    def rep(m):
        body = m.group(1)
        if "::" in body:
            a, h = body.split("::", 1)
            return "{{c1::" + a.strip() + "::" + h.strip() + "}}"
        return "{{c1::" + body.strip() + "}}"
    return HOLE.sub(rep, text)


def to_md(text):
    return HOLE.sub(lambda m: "{" + m.group(1).split("::")[0].strip() + "}", text)


def visible(text):
    return HOLE.sub(" ▢ ", text)


def esc(s):
    return s.replace("\t", " ").replace("\n", " ")


def src_label(keys):
    out = []
    for k in keys:
        n, l = k.split(":")
        out.append(f"{n[:2]}-{n[2:]} L{int(l):03d}")
    return " · ".join(dict.fromkeys(out))


rows, review = [], []
for c in cards:
    sec, sub = c["sec"], c["sub"]
    head = f"<b>특판 {sec.no} · {sub.title}</b>"
    lines = []
    for i, (it, st) in enumerate(c["items"]):
        mark = f"{st} " if st else ""
        lines.append(f"{CIRC[i]} {mark}{to_cloze(it.text)}")
    front = head + "<br>" + "<br>".join(lines)
    back_parts = []
    for i, (it, st) in enumerate(c["items"]):
        tagn = CIRC[i]
        if it.why:
            back_parts.append(f"<div class='hg-w'><b>왜</b>{tagn} {it.why}</div>")
        if it.mem:
            back_parts.append(f"<div class='hg-w'><b>기억</b>{tagn} {it.mem}</div>")
        if it.ex:
            back_parts.append(f"<div class='hg-w'><b>예</b>{tagn} {it.ex}</div>")
        if it.trap:
            back_parts.append(f"<div class='hg-x'><b>함정</b>{tagn} {it.trap}</div>")
    if any(it.chip for it, _ in c["items"]):
        back_parts.append("<span class='hg-v'>현행 기준 확인</span>")
    back = (CSS + "<div class='hg hg-b'>" + "".join(back_parts) + "</div>") if back_parts else ""
    all_src = []
    for it, _ in c["items"]:
        all_src += it.src
    allx = []
    for it, _ in c["items"]:
        allx += it.extra_src
    src = f"중개사법 특별판 §{sec.no} | {src_label(all_src)}"
    key = f"특판-중개사법-{sec.no}-{c['si']}"
    n2 = sum(1 for _, st in c["items"] if st == "★★")
    n1 = sum(1 for _, st in c["items"] if st == "★")
    tags = ["특별판", "공인중개사", "중개사법", "T5묶음"]
    if n2:
        tags += ["기출직결", "강조"]
    elif n1:
        tags += ["강조"]
    if any(it.chip for it, _ in c["items"]):
        tags.append("현행기준")
    holes = sum(len(HOLE.findall(it.text)) for it, _ in c["items"])
    groups = {GROUP.get(k.split(":")[0], "C") for k in all_src}
    score = 3 * n2 + n1 + (2 if ({"A", "B"} & groups) else 0)
    # 자체 가림 시험(기계): 빈칸 답이 같은 카드의 보이는 글자에 그대로 있으면 경고
    vis = " ".join(visible(it.text) for it, _ in c["items"]) + " " + sub.title
    leaks = []
    for it, _ in c["items"]:
        for h in HOLE.findall(it.text):
            a = h.split("::")[0].strip()
            for piece in re.split(r"[·,/()+ ]+", a):
                piece = piece.strip("'\"‘’“”")
                if len(piece) >= 3 and piece in vis:
                    leaks.append(piece)
    for v in (front, back):
        assert "\t" not in v and "\n" not in v
    rows.append(dict(deck="중개사법특별판", type="cloze", front=esc(front), back=esc(back), tags=" ".join(tags),
                     src=esc(src), key=key, _ch=c["ch"].no, _score=score, _holes=holes, _items=len(c["items"]),
                     _leaks=sorted(set(leaks)), _sec=sec.no, _title=sub.title, _src=all_src, _xsrc=allx,
                     _stars=(n2, n1), _chip=any(it.chip for it, _ in c["items"])))

# ── 도입 순서: 장마다 우선순위 정렬 → 장 순환(매일 전 범위가 한 바퀴) ─────────────────────
from collections import defaultdict
bych = defaultdict(list)
for r in rows:
    bych[r["_ch"]].append(r)
for k in bych:
    bych[k].sort(key=lambda r: (-r["_score"], r["_sec"], r["key"]))
order = []
while any(bych.values()):
    for chn in sorted(bych):
        if bych[chn]:
            order.append(bych[chn].pop(0))

OUT = "/mnt/user-data/outputs/특판"
tsv_path = os.path.join(OUT, "카드_2026-10-23-중개사법특별판.tsv")
with open(tsv_path, "w", encoding="utf-8", newline="") as f:
    f.write("\t".join(["deck", "type", "front", "back", "tags", "src", "key"]) + "\n")
    for r in order:
        f.write("\t".join([r[c] for c in ["deck", "type", "front", "back", "tags", "src", "key"]]) + "\n")
json.dump([{k: v for k, v in r.items()} for r in order], open(os.path.join(HERE, "cards_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("카드", len(order), "| 빈칸", sum(r["_holes"] for r in order), "| 오류", len(errors))
for e in errors:
    print("  ERR", e)
lk = [r for r in order if r["_leaks"]]
print("가림 경고", len(lk))
for r in lk:
    print("  LEAK", r["key"], r["_title"], r["_leaks"])
mx = max(r["_holes"] for r in order)
print("최대 빈칸", mx, [r["key"] for r in order if r["_holes"] >= 8])
