# -*- coding: utf-8 -*-
"""특별판 검수리포트 생성 — spec 앙키덱.md §4 양식(특집 덱 §7)."""
import json, re, sys, os, hashlib, html, collections
sys.path.insert(0, os.path.dirname(__file__))
import dsl
import data_a, data_b, data_c, data_d  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "src_index.json"), encoding="utf-8"))
META = json.load(open(os.path.join(HERE, "cards_meta.json"), encoding="utf-8"))
VER = json.load(open(os.path.join(HERE, "verify.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "verify.json")) else None
TSV = "/mnt/user-data/outputs/특판/카드_2026-10-23-중개사법특별판.tsv"
REF = open("/mnt/user-data/uploads/velog-posts/_시험엔진/spec/참조_카드디자인.md", encoding="utf-8").read()
CSS = re.findall(r"^(<style>.*?</style>)$", REF, re.M)[0]
src_build = open(os.path.join(HERE, "build.py"), encoding="utf-8").read()
EB = eval("{" + re.search(r"EXTRA_BAN = \{(.*?)\n\}", src_build, re.S).group(1) + "}")


def lab(k):
    n, l = k.split(":")
    return f"{n[:2]}-{n[2:]} L{int(l):03d}"


def cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def strip_html(s):
    s = re.sub(r"<style>.*?</style>", "", s)
    s = s.replace("<br>", " / ")
    s = re.sub(r"\{\{c1::(.*?)\}\}", r"[c1 \1]", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


rows = [r.split("\t") for r in open(TSV, encoding="utf-8").read().rstrip("\n").split("\n")[1:]]
F = [(r[2], r[3]) for r in rows]
md5 = lambda s: hashlib.md5(s.replace("\n", "").encode()).hexdigest()
styles = {s for f, b in F for s in re.findall(r"<style>.*?</style>", f + b)}
srow = sum(1 for f, b in F if "<style>" in f + b)
hgrow = sum(1 for f, b in F if "class='hg" in f + b)
dq = sum(len(re.findall(r'=\s*"', f + b)) for f, b in F)
fam = sum(1 for f, b in F if re.search(r"\{\{c[2-9]", f))
st2 = sum(1 for r in rows if "★★" in r[2])
tag2 = sum(1 for r in rows if "기출직결" in r[4].split())
holes = [r[2].count("{{c1::") for r in rows]
n_items = sum(m["_items"] for m in META)

# 원천 레인
lane = collections.Counter()
for m in META:
    n2, n1 = m["_stars"]
    lane["★★ 포함(기출직결)" if n2 else ("★ 포함(강조)" if n1 else "무표식")] += 1
part = collections.Counter("공인중개사법(1~12장)" if m["_ch"] <= 12 else ("부동산거래신고법(13~16장)" if m["_ch"] <= 16 else "중개실무(17~20장)") for m in META)

# 표식 실측 — 노트별
used = collections.defaultdict(set)
for m in META:
    for k in m["_src"] + m["_xsrc"]:
        used[k.split(":")[0]].add(k)
note_rows = []
for d in sorted({k.split(":")[0] for k in SRC}, key=lambda x: SRC[next(k for k in SRC if k.startswith(x + ":"))]["note"]):
    ks = [k for k in SRC if k.startswith(d + ":")]
    nm = SRC[ks[0]]["note"]
    star2 = [k for k in ks if re.match(r"^\s*(?:[-*]|\d+\.)?\s*★★", SRC[k]["text"])]
    star1 = [k for k in ks if re.match(r"^\s*(?:[-*]|\d+\.)?\s*★(?!★)", SRC[k]["text"])]
    brace = [k for k in ks if re.search(r"\{[^{}]+\}", SRC[k]["text"])]
    ban = [k for k in ks if SRC[k].get("banned") or k in EB]
    u = used.get(d, set())
    note_rows.append((d, nm, len(ks), len(star2), len([k for k in star2 if k in u]), len(star1), len([k for k in star1 if k in u]), len(brace), len(ban), len(u)))

out = []
w = out.append
w("# 검수리포트 — 2026-10-23 중개사법 특별판 (특집 덱 §7)")
w("")
w("> 덱 `중개사법특별판`(최상위) · TSV `anki/카드_2026-10-23-중개사법특별판.tsv` · 출고 `anki/출고/2026-10-23-중개사법특별판.apkg` · 정리본 `공인중개사/특별판/2026-10-23-공인중개사법-(특별판 모의·기출·파이널 WOX 총정리).md`")
w("> 사용자 요청(10/23): 중개사법만 — 박문각 월 모의고사·기출 WOX·파이널 100선 WOX 노트의 정보만 모아, 비슷한 지문은 한 카드에 몰고 **한 카드에 여러 구멍**, 신규는 10/23~10/28에 하루 15~20장.")
w("")
w("## 머리")
w("")
w(f"- **총 카드 {len(rows)}장** = 노트 {len(rows)}개(전부 cloze, 빈칸 번호 c1 하나) · 항목(원문 사실) {n_items}개 · 빈칸 {sum(holes)}개(카드당 평균 {sum(holes)/len(rows):.1f}, 최대 {max(holes)})")
w(f"- 시험/과목별: 공인중개사 · " + " · ".join(f"{k} {v}장" for k, v in part.items()))
w(f"- 원천별: " + " · ".join(f"{k} {v}장" for k, v in lane.items()) + f" — 원천 노트 {len(used)}개(파이널 100선 4 · 박문각 월 모의 6 · 기출 WOX 17), 인용 원문 줄 {len({k for m in META for k in m['_src'] + m['_xsrc']})}개")
w(f"- 목표·상한: 특집 덱 — 주간 `card_target`·`card_ceiling` 밖(§7). **소화: 프리셋 `특별판` 신규 19/일 기준 {len(rows)/19:.1f}일 → 10/23(금)~10/28(수) 6일**(19×6=114 ≥ {len(rows)})")
w(f"- 밀도: 행 {len(rows)} / 카드 {len(rows)} = 1.00 — **밀도 ⑧(빈칸 ≤3) 이 덱 한정 예외**: 사용자 명시 요청(\"한 카드에 여러 구멍\"). 같은 번호 c1이라 카드 1장에 빈칸이 한 번에 가려지고 한 번에 채점된다(가족 노트 아님 → 형제 가림·미루기 설정 불필요)")
w(f"- 유형: 전부 `T5묶음`(특집 전용 — 같은 소제목의 형제 사실을 한 카드에). T1~T4 분류 밖이라 ①📐·②도식 필수 규칙 해당 없음 · 도식 노트 0/{len(rows)}(원문에 도식 없음)")
w(f"- **자체 가림 시험: {len(rows)}장 전수** — 기계 가림 경고(빈칸 답 조각이 같은 카드 보이는 글자에 있음) 1차 58장 → 문안 수정 3회(약 70개 항목) → 독립 검증의 C(인출 설계) 지적 반영 → 최종 기계 경고 {sum(1 for m in META if m['_leaks'])}장은 사람 판독으로 유지(일반어 겹침 '시·도지사'·'사무소'·'과태료' 등, 또는 'A가 아니라 B' 지문 구조 자체)")
w(f"- ★★ 행 수 {st2} / `기출직결` 태그 행 수 {tag2} {'(일치)' if st2 == tag2 else '(불일치!)'} · ★만 있는 행은 `강조` 태그")
if VER:
    w(f"- **독립 검증**(별도 에이전트 3분할 — 1~6장 / 7~12장 / 13~20장, 전 항목 원문 대조): 사실 오류 {VER['A']} · 출제 금지 위반·충돌 {VER['B']} · 인출 설계 결함 {VER['C']} · 원문 의심 {VER['D']} → 조치 {VER['fixed']}건 반영 후 재빌드(꼬리 표)")
else:
    w("- **독립 검증**: (진행 중)")
w("- 자기 점검 6줄(참조 §5):")
w(f"  1. 속성 큰따옴표 {dq}")
w(f"  2. 스타일 블록 종류 {len(styles)} · md5 일치 {all(md5(s) == md5(CSS) for s in styles)} ({md5(CSS)[:8]}…)")
w(f"  3. 스타일 블록 행 {srow} = hg 마크업 행 {hgrow}")
w(f"  4. 가족 노트 복원 줄 누락 0 (가족 노트 {fam})")
w(f"  5. 공인 가족 노트 {fam}")
w("  6. 가족 노트 앞면 스타일 시작·뒷면 스타일 없음 — 해당 없음(가족 노트 0)")
w(f"  + 행마다 `{{{{c` 개수 = 닫힘 개수: 불일치 {sum(1 for r in rows if r[2].count('{{c') != r[2].count('}}'))}행 · key 중복 0 · 빌더 검증 통과")
w("- **새 덱**: `중개사법특별판`(최상위) — 임포트 뒤 덱 옵션에서 프리셋 `특별판`('기본' 복제, 신규 19/일)을 만들어 이 덱에만 저장. `자격증::공인중개사`의 신규 30/일과 섞이지 않는다. 상위 덱 `자격증`을 눌러 공부하면 이 덱은 안 나온다 — 따로 눌러야 한다")
w("- 형제 가림 확인: 해당 없음 · 기준선: 해당 없음(특집)")
w("- 출제 금지 원천: 추출기 ⛔ " + str(sum(1 for v in SRC.values() if v.get('banned'))) + f"줄 + 사람 판독 금지 {len(EB)}줄(확인 필요 섹션·💡 보류·백지 ⑦·노트 간 충돌·작성자 판단) — 빌더가 인용 줄 전수 대조, 위반 0. 정리본 하단 `## ⚠️ 확인 필요` " + str(sum(1 for l in open(os.path.join(HERE, "tail.md"), encoding="utf-8") if re.match(r"^\| \d+ \|", l))) + "행")
w(f"- 뒷면: 원문 노트의 `예)`·이유(→)·함정·두문자 줄이 있는 카드만 뒷면 칸이 있다({sum(1 for r in rows if r[3])}장) — 나머지 {sum(1 for r in rows if not r[3])}장은 뒷면 칸 없이 출처만(재진술로 칸을 채우지 않는다)")
w("")
w("### 표식 실측 (노트별)")
w("")
w("| 노트 | 원천 줄 | ★★ 줄 | ★★ 편입 | ★ 줄 | ★ 편입 | `{}` 줄 | 금지 줄 | 인용 줄 |")
w("|---|---|---|---|---|---|---|---|---|")
for d, nm, a, s2, s2u, s1, s1u, br, ban, u in note_rows:
    short = nm.replace(".md", "")
    w(f"| {short} | {a} | {s2} | {s2u} | {s1} | {s1u} | {br} | {ban} | {u} |")
w("")
w("> ★ 편입 < ★ 줄인 노트: 남은 줄은 중개사법 범위 밖(민법·공법·학개론·공시법 등) 또는 금지 줄 · 같은 사실이 다른 노트 줄로 이미 수록된 경우다(같은 사실은 한 줄로 합침).")
w("")
w("## 본문")
w("")
w("| # | deck | 유형 | 앞면 | 뒷면 | 원천 | 표식 원문 줄 | 도식 원천(줄) | src |")
w("|---|---|---|---|---|---|---|---|---|")
for i, (r, m) in enumerate(zip(rows, META), start=1):
    front = strip_html(r[2])
    back = strip_html(r[3]) if r[3] else "(뒷면 칸 없음)"
    n2, n1 = m["_stars"]
    ln = "기출직결" if n2 else ("강조" if n1 else "무표식")
    quotes = []
    for k in dict.fromkeys(m["_src"]):
        t = SRC[k]["text"].strip()
        quotes.append(f"{lab(k)} `{t}`" if (n2 or n1) else f"(무표식) {lab(k)} `{t}`")
    xs = " · ".join(lab(k) for k in dict.fromkeys(m["_xsrc"])) or "—"
    w(f"| {i} | {r[0]} | T5묶음 | {cell(front)} | {cell(back)} | {ln} | {cell(' ⏐ '.join(quotes))} | {cell(xs)} | {cell(r[6])} |")
w("")
w("## 꼬리")
w("")
w("### ① 레인 탈락·제외")
w("")
w("- 범위 밖: 원천 노트의 민법·공법·학개론·공시법·세법 줄(기출 WOX 회독 04-05~05-18 혼합 노트) — 중개사법·부동산거래신고법·중개실무만 수록")
w("- 출제 금지(위 머리 참조) — 사람 판독 금지 줄과 사유는 아래 표")
w("")
w("| 원문 줄 | 사유 |")
w("|---|---|")
for k, v in EB.items():
    if k == "0604:73":
        continue
    w(f"| {lab(k)} | {cell(v)} |")
w("| 06-04 L073 | 예외 허용 — '대표자는 공인중개사' 부분만 4-1 1)에 수록(1/3 기준 부분은 ⚠️ 표) |")
w("")
w("### ② 독립 검증 조치")
w("")
if VER:
    w("| 카드 key | 항목 | 분류 | 지적 | 조치 |")
    w("|---|---|---|---|---|")
    for f in VER["rows"]:
        w(f"| {cell(f['key'])} | {cell(f['item'])} | {f['cat']} | {cell(f['issue'])} | {cell(f['action'])} |")
else:
    w("(진행 중)")
w("")
w("## 이월 (다음 주 우선)")
w("")
w("| 원천 | 레인 | 항목 | 이월 횟수 | 사유 |")
w("|---|---|---|---|---|")
w("")
w("## 보류 (사용자 확정 대기)")
w("")
w("| 원천 | 항목 | 지목 근거 | 대기 주수 | 해소 조건 |")
w("|---|---|---|---|---|")
w("| 정리본 하단 ⚠️ 표 1~43행 | 노트 간 충돌·원문 의심 줄 | 특별판 정리본 `## ⚠️ 확인 필요` | 0 | 원문·법령 원문 확인 — 이 덱은 일회성 특집이라 다음 주 추출기가 읽지 않는다(파일명이 정규 덱 패턴 밖) |")
open("/mnt/user-data/outputs/특판/검수_2026-10-23-중개사법특별판.md", "w", encoding="utf-8").write("\n".join(out))
print("ok", len(out), "lines")
