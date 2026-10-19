# -*- coding: utf-8 -*-
import json, re, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
D = json.load(open(f"{HERE}/카드메타_2026-10-19.json", encoding="utf-8"))
C = D["cards"]; HOLD = D["hold"]; DUP = D["dup"]; SKIP = D["skip"]
CAND = json.load(open(f"{HERE}/후보_2026-10-19.json", encoding="utf-8"))
SELF = open(f"{HERE}/자기점검_2026-10-19.txt").read().strip().split("|")
TOTAL = sum(c["ncards"] for c in C)
def lane0(c): return c["lane"].split("+")[0]
def txt(h):
    h = re.sub(r"<style>.*?</style>", "", h)
    h = re.sub(r"\{\{c(\d+)::(.*?)\}\}", r"[c\1 \2]", h)
    h = h.replace("</tr>", " / ").replace("</th>", " \\| ").replace("</td>", " \\| ").replace("</li>", " · ").replace("</div>", " ").replace("</span><i>", " ").replace("</i>", " ")
    h = h.replace("<b>왜</b>", "왜 ").replace("<b>기억</b>", "기억 ").replace("<b>함정</b>", "함정 ").replace("<sup>", "^").replace("</sup>", "")
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("|", "\\|").replace("\\\\|", "\\|")
    return re.sub(r"\s+", " ", h).strip() or "—"
def esc(s): return s.replace("|", "\\|")
LANES = ["★★", "★", "{}", "무표식", "구노트"]
lane_cards = {k: sum(c["ncards"] for c in C if lane0(c) == k) for k in LANES}
lane_rows = {k: sum(1 for c in C if lane0(c) == k) for k in LANES}
curly_rows = sum(1 for c in C if "{}" in c["lane"]); curly_cards = sum(c["ncards"] for c in C if "{}" in c["lane"])
mand = lane_cards["★★"] + lane_cards["★"] + lane_cards["{}"]
fill = lane_cards["무표식"] + lane_cards["구노트"]
kinds = Counter(c["kind"] for c in C)
bupsa = [c for c in C if "법무사" in c["deck"]]
bmulti = [c for c in bupsa if c["ncards"] >= 2]
gmulti = [c for c in C if "공인중개사" in c["deck"] and c["ncards"] >= 2]
fdiag = sum(1 for c in C if c["has_f"])
star2_rows = sum(1 for c in C if lane0(c) == "★★"); tag_rows = sum(1 for c in C if "기출직결" in c["tags"])
assert star2_rows == tag_rows
binary = [c["key"] for c in C if c.get("binary_curly")]
old = [c for c in C if c["lane"] == "구노트"]
exam_cards = Counter(("법무사" if "법무사" in c["deck"] else "공인중개사", c["deck"].split("::")[-1]) for c in C for _ in range(c["ncards"]))
prev_decks = set()
import glob
for f in glob.glob(f"{HERE}/../카드_*.tsv"):
    if "2026-10-19" in f: continue
    prev_decks |= {ln.split("\t")[0] for ln in open(f, encoding="utf-8").read().split("\n")[1:] if ln}
new_decks = sorted({c["deck"] for c in C} - prev_decks)
old_hold = CAND["prev_report"]["hold"]
long_hold = [h for h in old_hold if h["대기 주수"] >= 3]
wk = Counter(h["대기 주수"] for h in long_hold)
L = []; A = L.append
A("# 검수리포트 — 2026-10-19 정규 덱 (카드 디자인 v2.1 · 공인중개사 파이널 100선 2회차·10월 모의고사 + 법무사 민소 2차 1노트)\n")
A("> spec `앙키덱.md` **v2.3** + `참조_카드디자인.md` v2.1 / `exams.json` `_anki` 목표 채우기 모델 (card_target **210** · card_ceiling **240** · mandatory_lanes ★★·★·`{}`·n:신규 전량 · density 분할 ≤2·빈칸 ≤3·가족 빈칸 ≤3·법무사 다중 번호 ≤50% · independent_review_min_cards 30 · 신규 **30/일**). `final_phase.gongin.from` = 10/31 → 공인중개사는 시험일 전까지 평소 규칙(10/17 출고 0 규칙은 10/12 폐지). 참조 문서 존재 — v2 형식 출고. 추출기 `extract_anki_candidates.py --date 2026-10-19` 실행(`후보_2026-10-19.json` — 노트 9개 · ★★ 91 · ★ 52 · `{}` 95 · n: 0 · banned 0). **§6 숫자 총정리는 이번 주 `n:` 0건이라 갱신 없음(스킵 보고).** 법무사 노트 1개(민소 10-17) → 가족 노트(T2) 1 · 법무사 T3·T4 쌍은 형제 가림 미확인이라 같은 번호 c1·c1 한 장.\n")
A("## 머리 — 집계\n")
A(f"**⚠ 3주 이상 대기 보류 항목 표면화 — {len(long_hold)}건**(" + " · ".join(f"{k}주차 {v}" for k, v in sorted(wk.items(), reverse=True)) + "): " + " / ".join(h["원천"] for h in long_hold) + f". 보류 해소 0건(대기 항목의 원문 노트 중 10-12 이후 편집된 것은 공법 10-06뿐이고 지목 줄 L37·L62·L78은 그대로). 이번 주 신규 보류 **{len(HOLD)}건**(독립 검증 G4 원문 자체 의심 — 구노트 05-30 L125 세목). 정리본에서 ⚠️·각주를 정리하면 다음 덱(10/26)에 자동 편입된다.\n")
A("| 항목 | 값 |\n|---|---|")
A(f"| 총 카드 수 | **{TOTAL}장** (TSV **{len(C)}행** — basic 0 · cloze {len(C)}, 다중 빈칸은 번호마다 1장) |")
A(f"| 시험/과목별 | 공인중개사 **{sum(v for k, v in exam_cards.items() if k[0]=='공인중개사')}장**(" + " · ".join(f"{k[1]} {v}" for k, v in sorted(exam_cards.items()) if k[0] == "공인중개사") + f") / 법무사 2차 **{sum(v for k, v in exam_cards.items() if k[0]=='법무사')}장**(민사소송법) |")
A(f"| **목표 달성률** | **{TOTAL} / 210 = {TOTAL/210:.0%}** — 의무 레인 **{mand}장**(목표의 {mand/210:.0%} · ★★ {lane_cards['★★']} · ★ {lane_cards['★']} · `{{}}` 단독 {lane_cards['{}']} · 그중 `{{}}` 동반 {curly_cards}) + 채우기 **{fill}장**(무표식-이번주 {lane_cards['무표식']} · 구노트 {lane_cards['구노트']}). 상습(후보 공인 36·법무사2차 14 전부 기출고 key)·백지구멍(창 안 보고서 0)·이월(직전 표 0행)·n:신규·n:기존(`n:` 0)은 0장. 의무 레인이 목표의 {mand/210:.0%}뿐이라 구노트까지 내려갔다(이번 주 표식 줄 147 중 기출고 중복 {sum(1 for d in DUP if d['lane']!='무표식')}줄·요령 머리줄 {sum(1 for s in SKIP if s['lane']!='무표식')}줄 제외 — 파이널 2회차는 1회차·4회독과 같은 사실이 많다) |")
A(f"| 총 카드 / `card_ceiling` | **{TOTAL} / 240** — 상한 안. 빌더 경고는 '뒷면 비어 있음' 안내뿐(T1 원자 카드 — 원문에 왜·기억·함정이 없는 행) |")
A(f"| 소화 일수 | 신규 30장/일 기준 **{TOTAL/30:.1f}일치**. 법무사 다중 번호 노트 {len(bmulti)}개 → {sum(c['ncards'] for c in bmulti)}장(목표의 {sum(c['ncards'] for c in bmulti)/210:.0%}, 상한 50%)·최대 형제 2 → 미루기를 켜도 7~8일(참조 §6-2) |")
A(f"| **밀도** | {len(C)}행 / {TOTAL}장 = **{TOTAL/len(C):.2f} 카드/행** · 의무 편입 표식 줄 {sum(1 for c in C if lane0(c) in ('★★','★','{}') and not c['split'])}개 → {mand}장 = {mand/sum(1 for c in C if lane0(c) in ('★★','★','{}') and not c['split']):.2f} 카드/표식 줄. 분할 ≤2 준수(동일 줄 하위 {sum(1 for c in C if c['split'])}행: 공법 L13 두문자/전개 · 모의 L161 두문자/전개 · 모의 L70 소급 · 중개사법 L49 사유7 · 민소 L14 · 민소 L93) · 빈칸 ≤3 준수(3빈칸: 세법 L50~53 배율 · 모의 L69~70 해제 · 모의 L171 총회 · 구노트 07-12 세목 귀속) · 병합 {sum(1 for c in C if c.get('merged'))}행 |")
A(f"| **자체 가림 시험 (§2-Q ⓑ)** | **{len(C)}행 중 작성 단계 수정 25행** — 이유를 빈칸 답 안으로 8(학개론 L10·L16·L17 · 민법 L52·L81·L87·L90 · 중개사법 L108) · 'A가 아니라 B'의 A를 뒷면 함정으로 3(학개론 L40 · 세법 L17 · 민법 L55) · 대비쌍을 같은 번호 c1·c1로 10(민법 L58 · 중개사법 L115·L132 · 공법 L156 · 민소 L11·L16~18·L84~86 · 시설군 L96·L136 · 구노트 법정기일) · 두문자 앞면 노출 차단 2(공법 L13 · 모의 L161 — 전개 카드에 두문자 대신 개수 단서) · 이진 빈칸을 변수로 2(민소 L37·L62). 두 번째 그물(독립 검증)이 46건을 더 잡았다 — 아래 |")
A(f"| **★★ 행 수 / `기출직결` 태그 행 수** | **{star2_rows} / {tag_rows}** — 일치 |")
A("| **독립 검증** (별도 에이전트 6명 — 1차 원천별 5분할 전수: G1 공법·공시법 47행 / G2 학개론·민법 42행 / G3 중개사법·세법 24행 / G4 세법 구노트 39행 / G5 법무사 민소 34행 = 186행 전수 · **G6 재검증 40행**(1차 지적 반영분). 도식·📐·왜·기억·함정 칸 포함, TSV 사본은 `<style/>` 치환, 이번 주 노트 전문·구노트 인용 ±3 + 하단 확인 필요 섹션 동봉) | 1차: **사실 오류 3 · 출제 금지 위반 0 · 인출 설계 결함 35 · 교차 누출 7 · 표식 불일치 0 · 판정 보류 11** / G6: 사실 0 · 금지 0 · 결함 11 · 누출 0 · 보류 1 → **사실 오류 3 전부 조치**(#75 표의 원문 없는 '—' 칸 삭제 · #47 함정 칸이 L41 오기를 뒤집어 쓴 것 → 칸 삭제(L45 근거만) · #149 구노트 05-30 L125 세목 의심 → 카드 빼고 보류) · **결함·누출 수정 44**(꼬리 ②) · 유지 판단 9(규칙 근거 — 꼬리 ②). 출고본에서 본문 사실이 원문과 어긋난 카드 0건 |")
A("")
A("**v2 지표 (참조 §7)**\n")
A("| 지표 | 값 |\n|---|---|")
A(f"| 유형 분포 | **T1 {kinds['T1']} · T2 {kinds['T2']} · T3 {kinds['T3']} · T4 {kinds['T4']}** (행 기준) |")
A(f"| 노트 수 | {len(C)} |")
A(f"| 법무사 다중 번호 노트 → 카드 | **{len(bmulti)} → {sum(c['ncards'] for c in bmulti)}장 (목표의 {sum(c['ncards'] for c in bmulti)/210:.0%}, 상한 50%)** — " + " · ".join(f"{c['key'].split('-',1)[1]} {c['ncards']}" for c in bmulti) + f" (공인 다중 번호 노트 {len(gmulti)} → {sum(c['ncards'] for c in gmulti)}장 — 공인 프리셋에는 미루기가 없어 소화 일수 영향 없음) |")
A(f"| 최대 형제 수 | **{max(c['ncards'] for c in C)}** (≤3) · 법무사 최대 {max(c['ncards'] for c in bupsa)} |")
A(f"| 도식 노트 비율 | **{fdiag} / {len(C)} = {fdiag/len(C):.1%}** (T2 1 · T3 {kinds['T3']} · T4 중 도식 {sum(1 for c in C if c['kind']=='T4' and c['has_f'])} — 공인 두문자·나열 쌍 4행은 규칙상 도식 없음) |")
A(f"| ① 누락(T3) | **0** ({kinds['T3']}행 전부 📐 가르는 변수) |\n| ② 누락(T3·T4, 공인 두문자·나열 쌍 제외) | **0** |")
A(f"| 자기 점검 6줄 | ① 속성 큰따옴표 **{SELF[0]}** ✅ · ② 스타일 블록 종류 **{SELF[1]}** + md5 `{SELF[2]}` 일치 ✅ · ③ 스타일 블록 행 **{SELF[3]}** = hg 마크업 행 **{SELF[4]}** ✅ · ④ 가족 노트 복원 줄 누락 **{SELF[5]}** ✅ · ⑤ 공인 가족 노트 **{SELF[6]}** ✅ · ⑥ 가족 노트 앞면·뒷면 스타일 위반 **{SELF[7]}** ✅ · 행마다 `{{{{c` 수 = `}}}}` 수 ✅ · 빌더 FAIL 0 |")
A(f"| 새 하위 덱 | **{'없음' if not new_decks else ' · '.join(new_decks)}** (7개 덱 전부 지난 TSV에 있던 덱) — 프리셋 재저장 불필요 |")
A("| 법무사 프리셋 | 법무사 다중 번호 노트가 처음 든 덱은 09-28(안내 완료) → §5 '임포트 전 1회' 안내 조건 불충족. `법무사` 프리셋(미루기 3개 ON)이 `자격증::법무사::민사소송법`에 걸려 있는지만 확인 |")
A("| 형제 가림 확인 | **미기록** (`anki/_사용자메모.md` 없음) → 법무사 대비쌍·두문자+나열 쌍은 같은 번호 c1·c1 한 장(T3 2행 · T4 4행). T2 1건(선결적 법률관계 확인 가족표)만 가족 노트 |")
A("| 기준선 | **기준선 미기록** (`anki/_사용자메모.md` 없음) |")
A("")
A("**표식 실측 (추출기 — 노트별)**\n")
A("| 노트 | ★★ | ★ | `{}` | n: | 표식 줄 | 편입 행 | 기출고 중복·제외 줄 | 비고 |\n|---|---|---|---|---|---|---|---|---|")
for n in CAND["notes"]:
    f = n["file"]; rows = [c for c in C if c["src"] == f and lane0(c) in ("★★", "★", "{}")]
    ds = [d for d in DUP if d["src"] == f and d["lane"] not in ("무표식",)]; ss = [s for s in SKIP if s["src"] == f and s["lane"] != "무표식"]
    memo = (", ".join(f"L{d['line']}" for d in ds) + (" 중복" if ds else "")) + ((" · " if ds else "") + ", ".join(f"L{s['line']} 요령" for s in ss) if ss else "")
    A(f"| {f[:10]} {f[11:].split('-(')[0]} | {n['marks']['★★']} | {n['marks']['★']} | {n['marks']['{}']} | 0 | {len(n['items'])} | {len(rows)} | {len(ds)+len(ss)} | {memo or '—'} |")
A(f"| **합계** | **91** | **52** | **95** | **0** | **147** | **{sum(1 for c in C if lane0(c) in ('★★','★','{}'))}** | **{sum(1 for d in DUP if d['lane']!='무표식')+sum(1 for s in SKIP if s['lane']!='무표식')}** | 하단 ⚠️ 표 있는 노트 0 · 추출기 banned 0 — 제외는 전부 기출고 key·사실 대조(꼬리 ①) |")
A(f"\n> 표식 습관 메모: 파이널 2회차 노트는 1회차(09-28~10-04)·4회독 노트와 같은 사실에 다시 ★가 붙어 {sum(1 for d in DUP if d['lane']!='무표식')}줄이 기출고 중복이다(공법 10-14는 19줄 중 {sum(1 for d in DUP if d['src'].startswith('2026-10-14') and d['lane']!='무표식')}줄). 같은 key는 Anki에서 갱신되므로 다시 내도 중복 카드는 생기지 않지만, 이번 덱은 종전 규칙대로 제외했다. 10-18 모의고사는 53줄 중 50줄이 신규 — 모의고사 오답 정리가 가장 좋은 공급원이다.\n")
A("**레인별 기여**\n")
A("| 레인 | 행 | 카드 |\n|---|---|---|")
for k, nm in [("★★", "★★ (기출직결)"), ("★", "★ (강조)"), ("{}", "`{}` 단독 (중괄호)"), ("무표식", "무표식-이번주 (공법 10-14 시설군 블록 24 · 세법 10-15 L7~8 · 민소 10-17 L94)"), ("구노트", "구노트 (부동산세법 05-30 → 07-25)")]:
    A(f"| {nm} | {lane_rows[k]} | {lane_cards[k]} |")
A(f"| (그중 `{{}}` 동반 — ★·★★ 안에 포함) | {curly_rows} | {curly_cards} |")
A("| 상습 / 백지구멍 / 이월 / n:신규 / n:기존 | 0 | 0 |")
A(f"| **합계** | **{len(C)}** | **{TOTAL}** |\n")
A("---\n")
A(f"## 본문 — 카드 전수 ({len(C)}행 · {TOTAL}장)\n")
A("| # | deck | 유형 | 앞면 | 뒷면 | 원천 | 표식 원문 줄 | 도식 원천(줄) | src |\n|---|---|---|---|---|---|---|---|---|")
for i, c in enumerate(C, 1):
    lane = c["lane"].replace("+{}", " + {}")
    if lane == "무표식": mk = " ⏎ ".join(f"(무표식-이번주) L{n}: {esc(m)}" for n, m in zip(c["lines"], c["mark"]))
    elif lane == "구노트": mk = " ⏎ ".join(f"(구노트) L{n}: {esc(m)}" for n, m in zip(c["lines"], c["mark"]))
    else: mk = " ⏎ ".join(f"L{n}: {esc(m)}" for n, m in zip(c["lines"], c["mark"]))
    if c.get("split"): mk = "(동일 줄 하위) " + mk
    if c.get("merged"): mk = "(병합) " + mk
    deck = ("법무사::" if "법무사" in c["deck"] else "") + c["deck"].split("::")[-1]
    A(f"| {i} | {deck} | {c['kind']} | {txt(c['front'])} | {txt(c['back'])} | {lane} | {mk} | {esc(c['dsrc'] or '—')} | {c['src']} |")
open(f"{HERE}/검수본문_2026-10-19.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("body ok", len(L))
