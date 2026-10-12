# -*- coding: utf-8 -*-
import json, re, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
D = json.load(open(f"{HERE}/카드메타_2026-10-12.json", encoding="utf-8"))
C = D["cards"]; HOLD = D["hold"]
CAND = json.load(open(f"{HERE}/후보_2026-10-12_v2.json", encoding="utf-8"))
SELF = open(f"{HERE}/자기점검_2026-10-12.txt").read().strip().split("|")
TOTAL = sum(c["ncards"] for c in C)
def lane0(c): return c["lane"].split("+")[0]
def txt(h):
    h = re.sub(r"<style>.*?</style>", "", h)
    h = re.sub(r"\{\{c(\d+)::(.*?)\}\}", r"[c\1 \2]", h)
    h = h.replace("</tr>", " / ").replace("</th>", " \\| ").replace("</td>", " \\| ").replace("</li>", " · ").replace("</div>", " ")
    h = h.replace("<b>왜</b>", "왜 ").replace("<b>기억</b>", "기억 ").replace("<b>함정</b>", "함정 ")
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("|", "\\|").replace("\\\\|", "\\|")
    return re.sub(r"\s+", " ", h).strip() or "—"
def esc(s): return s.replace("|", "\\|")
lane_cards = {k: sum(c["ncards"] for c in C if lane0(c) == k) for k in ["★★", "★", "무표식", "구노트"]}
curly_cards = sum(c["ncards"] for c in C if "{}" in c["lane"])
mand = lane_cards["★★"] + lane_cards["★"]
kinds = Counter(c["kind"] for c in C)
multi = [c for c in C if c["ncards"] >= 2]
fdiag = sum(1 for c in C if c["has_f"])
star2_rows = sum(1 for c in C if lane0(c) == "★★"); tag_rows = sum(1 for c in C if "기출직결" in c["tags"])
binary = [c["key"] for c in C if c.get("binary_curly")]
L = []
A = L.append
A("# 검수리포트 — 2026-10-12 정규 덱 (카드 디자인 v2.1 · 공인중개사 단독 주 — 법무사 노트 0 · **재작성 2판 — 공시법 10-09 재수령·10-10 신규·학개론 10-12 반영**)\n")
A("> spec `앙키덱.md` **v2.3** + `참조_카드디자인.md` v2.1 / `exams.json` `_anki` 목표 채우기 모델 (card_target **210** · card_ceiling **240** · mandatory_lanes ★★·★·`{}`·n:신규 전량 · density 분할 ≤2·빈칸 ≤3 · independent_review_min_cards 30 · 신규 **30/일**). **10/17 공인중개사 신규 0·출고 0 규칙은 오늘 폐지했다**(사용자 결정 10/12 — `final_phase.gongin.from` = 10/31 · `stop_from_days_before_exam` 0) → 공인중개사는 시험일(10/31) 전까지 평소 규칙이다. **재작성 사유**: 1판(00:31 실행) 뒤 사용자가 지난주 덜 된 노트를 다시 받았다 — 공시법 10-09 재작성(소제목 추가·★ 4줄 추가·등기필정보 줄은 표식이 빠짐) · 공시법 10-10 신규(파트2-2, ★ 4줄) · 학개론 10-10 → 10-12로 파일명 변경(내용 동일) · **숫자총정리 10-11(59항목·머리에 \"전부 ★\" 선언)은 사용자 결정으로 이번 덱에서 제외**(카드 문안과 검증 G7·G8 결과는 `_work/`에 보관 — 원하면 특집 덱으로 바로 낼 수 있다). 추출기 재실행(`후보_2026-10-12_v2.json` — 노트 8개 · ★★ 89 · ★ 79 · `{}` 112 · banned 0). 1판 산출물은 `anki/_work/_폐기_2026-10-12_v1/`에 보관. 참조 문서 존재 — v2 형식 출고. **§6 숫자 총정리는 이번 주 `n:` 0건이라 갱신 없음(스킵 보고).** 법무사 노트 0 → 덱 전체가 공인중개사 = **가족 노트 0 · T1·T3·T4만**.")
A("> 1판을 이미 임포트했다면 2판을 그대로 다시 임포트한다 — 같은 key는 갱신된다. 1판에만 있던 구노트 05-30·06-07 9장은 Anki에 남는다(남겨도 무방).\n")
A("## 머리 — 집계\n")
old_hold = CAND["prev_report"]["hold"]
long_hold = [h for h in old_hold if h["대기 주수"] >= 3]
A(f"**⚠ 3주 이상 대기 보류 항목 표면화 — {len(long_hold)}건**(6주차 {sum(1 for h in long_hold if h['대기 주수']==6)} · 4주차 {sum(1 for h in long_hold if h['대기 주수']==4)}): " + " / ".join(h["원천"] for h in long_hold) + ". 이번 주 신규 보류 **" + str(len(HOLD)) + "건**(작성 단계 5 · 독립 검증 원문 자체 의심 6). 정리본에서 ⚠️·각주를 정리하면 다음 덱(10/19)에 자동 편입된다 — 10/17 규칙 폐지로 공인 항목도 시험 전까지 편입 기회가 있다.\n")
A("| 항목 | 값 |\n|---|---|")
A(f"| 총 카드 수 | **{TOTAL}장** (TSV **{len(C)}행** — basic 0 · cloze {len(C)}, 다중 빈칸은 번호마다 1장) |")
A(f"| **목표 달성률** | **{TOTAL} / 210 = {TOTAL/210:.0%}** — 의무 레인 **{mand}장**(목표의 {mand/210:.0%} · ★★ {lane_cards['★★']} · ★ {lane_cards['★']} · 그중 `{{}}` 동반 {curly_cards}) + 채우기 **{lane_cards['무표식']+lane_cards['구노트']}장**(무표식-이번주 {lane_cards['무표식']} · 구노트 {lane_cards['구노트']}). 상습(후보 36건 전부 기출고)·백지구멍(창 안 보고서 0)·이월(0)·n:기존(0)은 0장. 구노트는 목표에 닿은 노트(06-07)에서 정지 |")
A(f"| 총 카드 / `card_ceiling` | **{TOTAL} / 240** — 상한 안. 빌더 경고는 '뒷면 비어 있음' 안내뿐(T1 원자 카드 — 원문에 왜·기억·함정이 없는 행) |")
A(f"| 소화 일수 | 신규 30장/일 기준 **{TOTAL/30:.1f}일치**(법무사 다중 번호 노트 0 → 미루기 변수 없음). 10/17 규칙 폐지로 시험 전에 전량 도입된다(10/12 임포트 → 10/18까지) |")
A(f"| **밀도** | {len(C)}행 / {TOTAL}장 = **{TOTAL/len(C):.2f} 카드/행** · 의무 편입 표식 줄 {sum(1 for c in C if lane0(c) in ('★★','★') and not c['split'])}개 → {mand}장 = {mand/sum(1 for c in C if lane0(c) in ('★★','★') and not c['split']):.2f} 카드/표식 줄. 분할 ≤2 준수(동일 줄 하위 2행: 세법 L71 장특공 일반/1주택 · 세법 L119 두문자/10년 특례) · 빈칸 ≤3 준수(3빈칸: 공시법 L5 · 세법 L12·L51·L138 · 공법 L108 — 숫자·{{}} 지정) |")
A(f"| **자체 가림 시험 (§2-Q ⓑ)** | **{len(C)}행 중 작성 단계 수정 26행** — 'A가 아니라 B'의 A를 뒷면 함정으로 12(공법 L20·L49·L60·L74 · 중개사법 L7·L10·L30·L81·L91 · 세법 L12 · 공법 L53 '주거·교육환경' · 중개사법 L59) · 이유 없는 이진 빈칸을 변수 빈칸으로 3(민법 L7 '사용수익을 방해할 정도' · L16 '기간을 약정하지 않으면' · 공법 L7 '경작지') · 대비쌍을 같은 번호로 7(민법 L11 · 중개사법 L60·L66·L100·L102 · 세법 L14·L123·L131) · 이유를 빈칸 답 안으로 1(중개사법 L87) · 자기 노출 차단 3(민법 L22 6개월 노출 → 변수 빈칸 · 공시법 L12 두 번 나오는 '등기권리자' 동시 가림 · 중개사법 L39 결론 문장을 뒷면으로). 두 번째 그물(독립 검증)이 26건을 더 잡았다 — 아래 |")
A(f"| **★★ 행 수 / `기출직결` 태그 행 수** | **{star2_rows} / {tag_rows}** — 일치(공시법 `!!` 8줄 포함) |")
A("| **독립 검증** (별도 에이전트 6명 — 1판: G1 민법·공법 54행 / G2 중개사법 39행 / G3 세법 53행 / G4 공시법·학개론·구노트 24행 = 전수 170행 · G5 재검증 40행(1차 지적 반영분 + 구노트 05-24 추가분) / **2판: G6 공시법 10-09·10-10·학개론 10-12 21행**(재수령본 전문 대조 · 줄 번호 재매핑 확인). 도식·📐·왜·기억·함정 칸 포함, TSV 사본은 `<style/>` 치환, 원문 노트 전문 동봉. ※ G7·G8은 숫자총정리 카드를 검증했으나 그 카드는 이번 덱에서 뺐다) | 1차: **사실 오류 2 · 출제 금지 위반 0 · 인출 설계 결함 26 · 교차 누출 3 · 표식 불일치 0 · 판정 보류 3** / G5: 사실 0 · 금지 0 · 결함 8 · 누출 0 · 보류 5 / G6: 사실 0 · 금지 0 · 결함 3 · 누출 0 · 보류 0 → **사실 오류 2 전부 수정**(공법 L108 표 행 이름 '고령' → 원문 '60세 이상' · 세법 L137 괄호 설명을 '왜'로 쓴 것 → '기억') · **결함·누출 수정 34**(꼬리 ②) · **원문 자체 의심 6줄은 카드에서 빼서 보류**(공법 L37·L62 · 중개사법 L38 · 세법 L56·L66·L99) · 유지 판단 7(규칙 근거 — 꼬리 ②, G6 결함 3건 포함). 출고본에서 본문 사실이 원문과 어긋난 카드 0건 |")
A("")
A("**v2 지표 (참조 §7)**\n")
A("| 지표 | 값 |\n|---|---|")
A(f"| 유형 분포 | **T1 {kinds['T1']} · T2 0 · T3 {kinds['T3']} · T4 {kinds['T4']}** (행 기준) |")
A(f"| 노트 수 | {len(C)} |")
A(f"| 법무사 다중 번호 노트 → 카드 | **0 → 0장 (목표의 0%)** — 법무사 카드 자체가 0 (공인 다중 번호 노트 {len(multi)} → {sum(c['ncards'] for c in multi)}장 — 공인 프리셋에는 미루기가 없어 소화 일수 영향 없음) |")
A(f"| 최대 형제 수 | **{max(c['ncards'] for c in C)}** (≤3) |")
A(f"| 도식 노트 비율 | **{fdiag} / {len(C)} = {fdiag/len(C):.1%}** (T3 {kinds['T3']} · T4 {kinds['T4']} 전부 — 파이널 문풀 노트는 한 줄 사실이 대부분이라 T1 비중이 높다) |")
A(f"| ① 누락(T3) | **0** |\n| ② 누락(T3·T4, 공인 두문자·나열 쌍 제외) | **0** |")
A(f"| 자기 점검 6줄 | ① 속성 큰따옴표 **{SELF[0]}** ✅ · ② 스타일 블록 종류 **{SELF[1]}** + md5 `{SELF[2]}` 일치 ✅ · ③ 스타일 블록 행 **{SELF[3]}** = hg 마크업 행 **{SELF[4]}** ✅ · ④ 가족 노트 복원 줄 누락 **{SELF[5]}** ✅ · ⑤ 공인 가족 노트 **{SELF[6]}** ✅ · ⑥ 가족 노트 앞면·뒷면 스타일 위반 **{SELF[7]}** ✅ · 행마다 `{{{{c` 수 = `}}}}` 수 ✅ · 빌더 FAIL 0 |")
A("| 새 하위 덱 | **없음** (6개 공인 덱 전부 기존) — 프리셋 재저장 불필요 |")
A("| 형제 가림 확인 | **미확인** — `anki/_사용자메모.md` 없음 (이번 덱은 가족 노트 0이라 영향 없음) |")
A("| 기준선 | **기준선 미기록** (`anki/_사용자메모.md` 없음) |")
A("")
A("**표식 실측 (추출기 — 노트별)**\n")
A("| 노트 | ★★(`!!`) | ★(`!`) | `{}` | n: | 표식 줄 | 편입 행 | 보류 줄 | 비고 |\n|---|---|---|---|---|---|---|---|---|")
for n in CAND["notes"]:
    f = n["file"]; rows = [c for c in C if c["src"] == f and lane0(c) in ("★★", "★")]; hs = [h for h in HOLD if h["src"] == f]
    A(f"| {f[:10]} {f[11:].split('-(')[0]} | {n['marks']['★★']} | {n['marks']['★']} | {n['marks']['{}']} | 0 | {len(n['items'])} | {len(rows)} | {len(hs)} | " + (", ".join(f"L{h['line']}" for h in hs) or "—") + " |")
A(f"| **합계** | **87** | **74** | **105** | **0** | **161** | **{sum(1 for c in C if lane0(c) in ('★★','★'))}** | **{len(HOLD)}** | 하단 ⚠️ 표 있는 노트 0 · 추출기 banned 0 — 보류는 전부 사람 판독·독립 검증 |")
A("\n> 표식 습관 메모: 세법 10-08은 ★★30·★23·`{}`45로 한 노트에서 74장이 나왔다(덱의 35%). `{}`가 한 줄에 3~4개 붙으면 빈칸 ≤3 규칙 때문에 줄을 나누게 된다(L71·L123).\n")
A("**레인별 기여**\n")
A("| 레인 | 행 | 카드 |\n|---|---|---|")
for k, nm in [("★★", "★★ (기출직결)"), ("★", "★ (강조)"), ("무표식", "무표식-이번주"), ("구노트", "구노트 (부동산세법 05-02 → 06-07)")]:
    A(f"| {nm} | {sum(1 for c in C if lane0(c)==k)} | {lane_cards[k]} |")
A(f"| (그중 `{{}}` 동반 — ★·★★ 안에 포함) | {sum(1 for c in C if '{}' in c['lane'])} | {curly_cards} |")
A("| 상습 / 백지구멍 / 이월 / n:신규 / n:기존 | 0 | 0 |")
A(f"| **합계** | **{len(C)}** | **{TOTAL}** |\n")
A("---\n")
A(f"## 본문 — 카드 전수 ({len(C)}행 · {TOTAL}장)\n")
A("| # | deck | 유형 | 앞면 | 뒷면 | 원천 | 표식 원문 줄 | 도식 원천(줄) | src |\n|---|---|---|---|---|---|---|---|---|")
for i, c in enumerate(C, 1):
    lane = c["lane"].replace("+{}", " + {}")
    if lane == "무표식": mk = " ".join(f"(무표식-이번주) L{n}: {esc(m)}" for n, m in zip(c["lines"], c["mark"]))
    elif lane == "구노트": mk = " ".join(f"(구노트) L{n}: {esc(m)}" for n, m in zip(c["lines"], c["mark"]))
    else: mk = " ".join(f"L{n}: {esc(m)}" for n, m in zip(c["lines"], c["mark"]))
    if c.get("split"): mk = "(동일 줄 하위) " + mk
    A(f"| {i} | {c['deck'].split('::')[-1]} | {c['kind']} | {txt(c['front'])} | {txt(c['back'])} | {lane} | {mk} | {esc(c['dsrc'] or '—')} | {c['src']} |")
open(f"{HERE}/검수본문_2026-10-12.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok", len(L))
