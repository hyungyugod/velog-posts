#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/extract_anki_candidates.py — 주간 Anki 덱 후보 추출기 (HG 무한복습체계, 2026-09-14 신설)

  python3 extract_anki_candidates.py [--date YYYY-MM-DD] [--root ROOT] [--out PATH]
                                     [--window-days 7] [--exams PATH] [--json]

이 스크립트는 **카드 문안을 쓰지 않는다.** spec/앙키덱.md v1.4 §0·§1의 '수집' 중
기계로 할 수 있는 부분만 한다 — AI 실행자는 이 산출을 읽고 문안·빈칸 위치·인출
설계만 한다(banned[]는 어떤 이유로도 되살리지 않는다).

하는 일
  ① 창 계산 — 활성 시험 노트폴더 최상위 20*.md 중 파일명 날짜가 date−window ~ date
  ② 표식 추출 — 줄머리 ★★/★/n: (exams.json _marks.anchor_regex) + 인라인 {단어}
  ③ 출제 금지 마킹 3경로 —
     ⓐ 줄 안 ⚠️ / 확인 필요 / ? (warn_regex)
     ⓑ 정리본 하단 `## ⚠️ 확인 필요` 표의 `위치`(소제목 번호)·`원문 표현`(키워드) 역참조
        · 신양식(코어 v3.11: # | 위치 | 원문 표현 | 확인 포인트 | 범위) — 범위=항목 → 금지, 범위=전체 → 일반 주의문
        · 구양식(불릿·번호·자유 표) — 텍스트에서 소제목 번호·따옴표 키워드를 추정, 못 풀면 unresolved_warns[]
        · 본문의 `(⚠️ N)`·`(하단 확인 필요 N)` 인라인 참조 — 표에 N행이 없으면 그 줄 금지(안전 쪽)
     ⓒ 백지복습 보고서 `## ⑦ ⚠️ 확인 필요` (source:/subject로 노트에 짝지음)
  ④ 기출고 key 취합 — anki/카드_*.tsv
  ⑤ 원장 상습 — timesWrong>=2 or retryMissed>=1, 기출고 key 제외, 실수 전용 제외 표시
  ⑥ 백지복습 mtime −window — ③ 남은 구멍 · ④ 교정된 개념 표 항목
  ⑦ 직전 정규 검수리포트의 `## 이월 (다음 주 우선)`·`## 보류 (사용자 확정 대기)` 표 파싱
  ⑧ n: 줄 수집(§6 입력) + 숫자 총정리본에 이미 있을 가능성(summary_hits)

산출: <out>.json + <out>.md (기본 anki/_work/후보_<date>.json). 노트·원장·리포트는 읽기만 한다.
표준 라이브러리만 사용. 종료 코드: 정상 0 / 입력(루트·exams.json) 문제 2.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = ENGINE_DIR.parents[1]  # <root>/_시험엔진/engine → <root>

# ── 정규식 ─────────────────────────────────────────────────────────────
RE_BRACE = re.compile(r"(?<!\{)\{([^{}\n]+)\}(?!\})")          # 단일 중괄호 {단어} (cloze {{..}} 제외)
RE_H2 = re.compile(r"^##\s+(\d+)-(\d+)\.")                     # ## 1-3. 대제목
RE_H2_ANY = re.compile(r"^##\s+")
RE_H3 = re.compile(r"^###\s+(\d+)\)")                          # ### 2) 소제목
RE_INLINE_REF = re.compile(r"\((?:⚠️?|하단)\s*(?:확인\s*필요)?\s*[#]?\s*([0-9①-⑳]+)\)")
RE_WARN_HEAD = re.compile(r"^##+\s*(?:\d+-\d+\.\s*)?(?:⚠️?\s*)?확인\s*필요")
RE_LOC = re.compile(r"(\d+)-(\d+)(?:\s*[-·\s]?\s*(\d+)\))?")     # 1-3 2) / 1-3-2) / 1-3
RE_QUOTED = re.compile(r"[\"“'‘]([^\"”'’]{2,40})[\"”'’]")
RE_NUMTOK = re.compile(r"\d+(?:[.,]\d+)?\s*(?:년|개월|달|월|일|시간|분|%|퍼센트|㎡|m|층|세대|호|명|회|배|만원|억)")
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
RE_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")


def circled_to_int(s):
    s = s.strip()
    if s and all(c in "0123456789" for c in s):
        return int(s)
    i = CIRCLED.find(s[0]) if s else -1
    return i + 1 if i >= 0 else None


def read_text(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def load_exams(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def note_date(name):
    m = re.match(r"^(20\d{2}-\d{2}-\d{2})", name)
    return dt.date.fromisoformat(m.group(1)) if m else None


def split_row(line):
    m = RE_TABLE_ROW.match(line)
    if not m:
        return None
    return [c.strip() for c in m.group(1).split("|")]


# ── 노트 파싱 ───────────────────────────────────────────────────────────
class Note:
    def __init__(self, path, exam_id, exam_name, track_tag):
        self.path = Path(path)
        self.name = self.path.name
        self.exam = exam_id
        self.exam_name = exam_name
        self.track = track_tag
        self.lines = read_text(path).splitlines()
        self.subsec = []          # line index → "1-3 2)" (소제목 번호)
        self.marks = {"★★": 0, "★": 0, "n:": 0, "{}": 0}
        self.items = []           # 표식 항목 (후보 전)
        self.warn_table = []      # 하단 표 행
        self.warn_format = None   # "v3.11" | "legacy" | None
        self.general = []         # 범위=전체 (일반 주의문)
        self.unresolved = []
        self.banned = {}          # line_no → [사유]
        self.n_lines = []
        self.mtime = dt.datetime.fromtimestamp(self.path.stat().st_mtime).isoformat(timespec="minutes")

    def subsection_of(self, idx):
        return self.subsec[idx] if idx < len(self.subsec) else ""


def index_subsections(note):
    cur_h2 = ""
    cur_h3 = ""
    out = []
    for ln in note.lines:
        m2 = RE_H2.match(ln)
        if m2:
            cur_h2 = f"{m2.group(1)}-{m2.group(2)}"
            cur_h3 = ""
        elif RE_H2_ANY.match(ln):
            cur_h2 = ""
            cur_h3 = ""
        m3 = RE_H3.match(ln)
        if m3:
            cur_h3 = f"{m3.group(1)})"
        out.append((cur_h2 + (" " + cur_h3 if cur_h3 else "")).strip())
    note.subsec = out


def find_warn_section(note):
    """하단 확인 필요 섹션의 (시작, 끝) 줄 인덱스. 없으면 None."""
    start = None
    for i, ln in enumerate(note.lines):
        if RE_WARN_HEAD.match(ln.strip()):
            start = i
            break
    if start is None:
        return None
    end = len(note.lines)
    for j in range(start + 1, len(note.lines)):
        s = note.lines[j].strip()
        if s.startswith("## ") or s.startswith("# ") or s.startswith("■ 백지시트") or s.startswith("```"):
            end = j
            break
    return start, end


def parse_warn_section(note):
    sec = find_warn_section(note)
    if not sec:
        return
    a, b = sec
    body = note.lines[a + 1:b]
    rows = [split_row(l) for l in body]
    rows = [r for r in rows if r]
    header = None
    if rows:
        header = [c.replace("*", "").strip() for c in rows[0]]
    if header and "위치" in header:
        note.warn_format = "v3.11"
        idx = {h: k for k, h in enumerate(header)}
        for r in rows[1:]:
            if all(set(c) <= set("-: ") for c in r):
                continue
            g = lambda h: (r[idx[h]] if h in idx and idx[h] < len(r) else "").strip()
            row = {"no": g("#"), "loc": g("위치"), "expr": g("원문 표현"), "point": g("확인 포인트"), "scope": g("범위") or "항목"}
            note.warn_table.append(row)
    else:
        note.warn_format = "legacy"
        # 구양식: 표(자유 열) / 번호 불릿 / 하이픈 불릿 — 한 줄 = 한 항목으로 본다
        n = 0
        for l in body:
            s = l.strip()
            if not s or s.startswith("|---") or s.startswith("> ") and "표기" in s:
                continue
            r = split_row(l)
            if r:
                if r[0].replace("*", "").strip() in ("#", "위치", "원문", "원문 표현", "필기 내용"):
                    continue
                txt = " | ".join(r)
                num = r[0].strip() if r[0].strip().isdigit() else None
            else:
                mnum = re.match(r"^(?:-\s*)?(?:⚠️\s*)?(\d+)[.)]\s*(.*)", s)
                if mnum:
                    num, txt = mnum.group(1), mnum.group(2)
                elif s.startswith("- ") or s.startswith("* "):
                    num, txt = None, s[2:]
                else:
                    continue
            n += 1
            note.warn_table.append({"no": num or str(n), "loc": "", "expr": txt, "point": "", "scope": "항목", "legacy": True})


def resolve_loc_from_text(txt):
    """구양식 텍스트에서 소제목 번호 추정: '1-4', '1-7 3)', '[1-2 주차장]' 등."""
    m = RE_LOC.search(txt)
    if not m:
        return ""
    loc = f"{m.group(1)}-{m.group(2)}"
    if m.group(3):
        loc += f" {m.group(3)})"
    return loc


def keywords_from_expr(expr):
    kws = RE_QUOTED.findall(expr)
    kws += RE_NUMTOK.findall(expr)
    # 굵은 글씨 **..**
    kws += re.findall(r"\*\*([^*]{2,30})\*\*", expr)
    # 폴백: 한글 명사 덩어리 4자 이상
    if not kws:
        kws = [w for w in re.findall(r"[가-힣]{4,}", expr)][:3]
    return [k.strip() for k in kws if k.strip()]


def ban(note, i, reason):
    note.banned.setdefault(i, [])
    if reason not in note.banned[i]:
        note.banned[i].append(reason)


def apply_bans(note, warn_re):
    # ⓐ 줄 안 경고
    for i, ln in enumerate(note.lines):
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith(">"):
            continue
        if warn_re.search(s) or re.match(r"^\s*(?:[-*]|\d+\.)?\s*\?", s):
            ban(note, i, "줄 안 ⚠️/확인 필요/?")
    # 하단 표 역참조 ⓑ
    sec = find_warn_section(note)
    sec_range = range(sec[0], sec[1]) if sec else range(0, 0)
    rows_by_no = {}
    for row in note.warn_table:
        if row.get("no"):
            rows_by_no[str(row["no"])] = row
        loc = row.get("loc") or resolve_loc_from_text(row.get("expr", ""))
        if not loc and row.get("legacy"):
            note.unresolved.append({"no": row.get("no"), "text": row.get("expr")})
            continue
        if loc == "전체" or row.get("scope") == "전체":
            note.general.append({"no": row.get("no"), "expr": row.get("expr"), "point": row.get("point")})
            continue
        if not loc:
            note.unresolved.append({"no": row.get("no"), "text": row.get("expr")})
            continue
        kws = keywords_from_expr(row.get("expr", "") + " " + row.get("point", "") if row.get("legacy") else row.get("expr", ""))
        hit = []
        for i, ln in enumerate(note.lines):
            if i in sec_range:
                continue
            sub = note.subsection_of(i)
            if not (sub == loc or sub.startswith(loc + " ") or (" " not in loc and sub.split(" ")[0] == loc)):
                continue
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith(">"):
                continue
            if any(k in s for k in kws):
                hit.append(i)
        if hit:
            for i in hit:
                ban(note, i, f"하단 ⚠️표 #{row.get('no')} 역참조({loc})")
        else:
            # 키워드로 못 짚으면 그 소제목의 표식 줄을 전부 금지(보수적) + 표면화
            broad = []
            for i, ln in enumerate(note.lines):
                if i in sec_range:
                    continue
                sub = note.subsection_of(i)
                if sub == loc or sub.startswith(loc + " ") or (" " not in loc and sub.split(" ")[0] == loc):
                    if re.match(r"^\s*(?:[-*]|\d+\.)?\s*(★★|★|n:)", ln) or RE_BRACE.search(ln):
                        broad.append(i)
            for i in broad:
                ban(note, i, f"하단 ⚠️표 #{row.get('no')} 소제목 전체({loc}, 키워드 미매칭)")
            note.unresolved.append({"no": row.get("no"), "text": row.get("expr"), "loc": loc, "note": "키워드 미매칭 → 소제목 표식 줄 %d개 보수 금지" % len(broad)})
    # 인라인 참조 (⚠️ N) / (하단 확인 필요 N)
    for i, ln in enumerate(note.lines):
        if i in sec_range:
            continue
        for m in RE_INLINE_REF.finditer(ln):
            n = circled_to_int(m.group(1))
            row = rows_by_no.get(str(n)) if n is not None else None
            if row is None:
                ban(note, i, f"인라인 참조 (⚠️ {m.group(1)}) — 하단 표에 해당 행 없음(안전 쪽 금지)")
            elif row.get("scope") == "전체":
                pass
            else:
                ban(note, i, f"인라인 참조 (⚠️ {m.group(1)})")


def extract_items(note, anchor_re):
    sec = find_warn_section(note)
    sec_range = range(sec[0], sec[1]) if sec else range(0, 0)
    in_code = False
    for i, ln in enumerate(note.lines):
        s = ln.rstrip()
        if s.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or i in sec_range:
            continue
        st = s.strip()
        if st.startswith("■ 백지시트") or st.startswith("#") and "백지시트" in st:
            # 백지시트 이후는 카드 원천이 아니다
            break
        lane = None
        m = anchor_re.match(s)
        if m:
            tok = m.group(1)
            lane = {"!!": "★★", "!": "★"}.get(tok, tok)
        braces = [b.strip() for b in RE_BRACE.findall(s)] if "{{" not in s else []
        if lane == "n:":
            note.marks["n:"] += 1
            note.n_lines.append({"line": i + 1, "subsection": note.subsection_of(i), "text": st,
                                 "banned": note.banned.get(i, [])})
        elif lane in ("★★", "★"):
            note.marks[lane] += 1
        if braces:
            note.marks["{}"] += 1
        if lane in ("★★", "★") or braces:
            note.items.append({
                "line": i + 1, "subsection": note.subsection_of(i), "lane": lane or "{}",
                "braces": braces, "text": st, "banned": note.banned.get(i, []),
            })


def anchor_regex_with_bang(base):
    # exams.json 앵커(★★|★|n:)에 필기 원표기 !!/! 도 허용 (spec §1 ②-A/B)
    return re.compile(base.replace("(★★|★|n:)", "(★★|★|n:|!!|!)") if "(★★|★|n:)" in base else base)


# ── 백지복습 보고서 ──────────────────────────────────────────────────────
def parse_front_matter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for l in text[3:end].splitlines():
        if ":" in l:
            k, v = l.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def section_lines(text, head_regex):
    lines = text.splitlines()
    start = None
    for i, l in enumerate(lines):
        if re.match(head_regex, l.strip()):
            start = i
            break
    if start is None:
        return []
    out = []
    for l in lines[start + 1:]:
        if l.startswith("## "):
            break
        out.append(l)
    return out


def parse_blank_reports(root, ex, cfg, notes, date, window_days):
    paths = cfg.get("_paths") or {}
    bdir = Path(root) / ex["notes_dir"] / paths.get("blank_review_dir", "백지복습")
    out = []
    if not bdir.is_dir():
        return out
    lo = dt.datetime.combine(date - dt.timedelta(days=window_days), dt.time.min)
    for p in sorted(bdir.glob("*.md")):
        text = read_text(p)
        fm = parse_front_matter(text)
        if fm.get("type", "").strip() != "백지복습보고서":
            continue
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
        src = fm.get("source", "")
        # 노트 짝짓기: source 파일명 일치 → 과목+창 안 노트
        matched = None
        for n in notes:
            if src and (n.name in src or src.endswith(n.name)):
                matched = n
                break
        if matched is None:
            subj = fm.get("subject", "")
            cands = [n for n in notes if subj and subj.split("·")[0] in n.name]
            matched = cands[0] if len(cands) == 1 else None
        holes = [l.strip() for l in section_lines(text, r"^##\s*③") if l.strip().startswith(("|", "-")) and "---" not in l]
        fixed = [l.strip() for l in section_lines(text, r"^##\s*④") if l.strip().startswith("|") and "---" not in l and "개념 |" not in l]
        warns = [l.strip() for l in section_lines(text, r"^##\s*⑦") if l.strip().startswith(("|", "-")) and "---" not in l and "| # |" not in l]
        rec = {"file": p.name, "mtime": mtime.isoformat(timespec="minutes"), "in_window": mtime >= lo,
               "source": src, "subject": fm.get("subject", ""), "status": fm.get("status", ""),
               "matched_note": matched.name if matched else None,
               "holes": holes, "fixed": fixed, "warns": warns}
        out.append(rec)
        # ⓒ ⑦ 역참조 → 노트 금지
        if matched and warns:
            for w in warns:
                loc = resolve_loc_from_text(w)
                kws = keywords_from_expr(w)
                hit = []
                sec = find_warn_section(matched)
                sec_range = range(sec[0], sec[1]) if sec else range(0, 0)
                for i, ln in enumerate(matched.lines):
                    if i in sec_range:
                        continue
                    if loc:
                        sub = matched.subsection_of(i)
                        if not (sub == loc or sub.startswith(loc + " ") or sub.split(" ")[0] == loc):
                            continue
                    s = ln.strip()
                    if s and not s.startswith("#") and any(k in s for k in kws):
                        hit.append(i)
                if hit:
                    for i in hit:
                        ban(matched, i, f"백지보고서 ⑦ ({p.name})")
                        for it in matched.items:
                            if it["line"] == i + 1:
                                it["banned"] = matched.banned[i]
                else:
                    matched.unresolved.append({"no": "⑦", "text": w, "note": f"백지보고서 {p.name} — 지목 줄 미매칭(사람 판독 필요)"})
    return out


# ── 기출고 key · 원장 ────────────────────────────────────────────────────
def existing_keys(root):
    ak = Path(root) / "_시험엔진" / "anki"
    keys = {}
    for p in sorted(ak.glob("카드_*.tsv")):
        try:
            with open(p, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                    k = (r.get("key") or "").strip()
                    if k:
                        keys[k] = p.name
        except Exception:
            continue
    return keys


def ledger_habitual(root, ex, cfg, keys):
    paths = cfg.get("_paths") or {}
    p = Path(root) / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답") / paths.get("ledger_subdir", "_ledger") / "오답_원장.json"
    if not p.exists():
        return []
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return []
    led = d.get("ledger", d)
    if isinstance(led, dict):
        led = list(led.values())
    out = []
    for e in led:
        tw = e.get("timesWrong", 0) or 0
        rm = e.get("retryMissed", 0) or 0
        if not (tw >= 2 or rm >= 1):
            continue
        ck = e.get("conceptKey", "")
        causes = e.get("errorCauses") or {}
        only_slip = bool(causes) and set(causes.keys()) <= {"실수"}
        samples = []
        for s in (e.get("samples") or [])[-3:]:
            samples.append({"date": s.get("date"), "q": (s.get("q") or "")[:200], "correct": (s.get("correct") or "")[:200],
                            "expl": (s.get("expl") or "")[:300], "causeNote": s.get("causeNote")})
        out.append({"conceptKey": ck, "subject": e.get("subject"), "timesWrong": tw, "retryMissed": rm,
                    "lastWrong": e.get("lastWrong"), "errorCauses": causes, "only_slip": only_slip,
                    "already_issued": ck in keys, "samples": samples})
    return out


# ── 직전 검수리포트 ──────────────────────────────────────────────────────
def prev_report_tables(root, date):
    out_dir = Path(root) / "_시험엔진" / "anki" / "출고"
    best = None
    for p in out_dir.glob("검수_????-??-??.md"):
        m = re.match(r"검수_(\d{4}-\d{2}-\d{2})\.md$", p.name)
        if not m:
            continue
        d = dt.date.fromisoformat(m.group(1))
        if d < date and (best is None or d > best[0]):
            best = (d, p)
    if not best:
        return {"file": None, "carry": [], "hold": []}
    text = read_text(best[1])

    def table_after(head):
        rows = []
        lines = section_lines(text, head)
        for l in lines:
            r = split_row(l)
            if not r or all(set(c) <= set("-: ") for c in r):
                continue
            rows.append(r)
        return rows[1:] if rows else []  # 첫 행은 헤더

    carry = []
    for r in table_after(r"^##\s*이월"):
        cell = " ".join(r)
        if "~~" in cell or "소진" in cell:
            continue
        carry.append({"원천": r[0], "레인": r[1] if len(r) > 1 else "", "항목": r[2] if len(r) > 2 else "",
                      "이월 횟수": r[3] if len(r) > 3 else "", "사유": r[4] if len(r) > 4 else ""})
    hold = []
    for r in table_after(r"^##\s*보류"):
        weeks = r[3] if len(r) > 3 else "1"
        try:
            weeks_n = int(re.sub(r"\D", "", weeks) or "1") + 1
        except Exception:
            weeks_n = 2
        hold.append({"원천": r[0], "항목": r[1] if len(r) > 1 else "", "지목 근거": r[2] if len(r) > 2 else "",
                     "대기 주수": weeks_n, "해소 조건": r[4] if len(r) > 4 else "", "표면화": weeks_n >= 3})
    return {"file": best[1].name, "carry": carry, "hold": hold}


# ── n: 총정리 대조 ───────────────────────────────────────────────────────
def summary_hits(root, ex, n_line):
    cand = {"gongin": "공인중개사/공인중개사_날짜기간_총정리_v1.md", "bupsa1": "법무사/법무사_숫자체계_v1.md", "bupsa2": "법무사/법무사_숫자체계_v1.md"}
    p = Path(root) / cand.get(ex, "")
    if not p.exists():
        return {"summary_file": None, "hits": []}
    text = read_text(p)
    nums = RE_NUMTOK.findall(n_line)
    kws = [w for w in re.findall(r"[가-힣]{3,}", n_line) if w not in ("이내에", "경우는", "경우에", "이내")][:4]
    hits = []
    for l in text.splitlines():
        if not l.startswith("|") and not l.startswith("- "):
            continue
        if any(n.replace(" ", "") in l.replace(" ", "") for n in nums) and any(k in l for k in kws):
            hits.append(l.strip()[:160])
            if len(hits) >= 3:
                break
    return {"summary_file": p.name, "hits": hits}


# ── 메인 ────────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="주간 Anki 덱 후보 추출기 — 카드 문안은 쓰지 않는다")
    ap.add_argument("--date")
    ap.add_argument("--root")
    ap.add_argument("--exams")
    ap.add_argument("--out")
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument("--json", action="store_true", help="요약을 stdout에 JSON으로")
    a = ap.parse_args(argv)

    root = Path(a.root) if a.root else DEFAULT_ROOT
    exams_path = Path(a.exams) if a.exams else root / "_시험엔진" / "engine" / "exams.json"
    if not exams_path.exists():
        print(f"[FAIL] exams.json 없음: {exams_path}", file=sys.stderr)
        return 2
    cfg = load_exams(exams_path)
    date = dt.date.fromisoformat(a.date) if a.date else dt.date.today()
    lo = date - dt.timedelta(days=a.window_days)
    marks_cfg = cfg.get("_marks") or {}
    anchor_re = anchor_regex_with_bang(marks_cfg.get("anchor_regex", r"^\s*(?:[-*]|\d+\.)?\s*(★★|★|n:)"))
    warn_re = re.compile(marks_cfg.get("warn_regex", r"⚠️?|확인 ?필요"))
    note_pat = re.compile((cfg.get("_paths") or {}).get("note_pattern", r"^20\d{2}-\d{2}-\d{2}.*\.md$"))
    anki_cfg = cfg.get("_anki") or {}

    notes = []
    seen_dirs = set()
    exams = cfg.get("exams") or {}
    for ex_id, ex in exams.items():
        if ex.get("status") == "closed":
            continue
        ndir = root / ex["notes_dir"]
        if not ndir.is_dir():
            continue
        track = ex.get("track") or {}
        for p in sorted(ndir.iterdir()):
            if not p.is_file() or not note_pat.match(p.name):
                continue
            d = note_date(p.name)
            if not d or not (lo <= d <= date):
                continue
            # 트랙 스위치(법무사 1·2차 공유 폴더): token 포함 여부로 배정
            if track:
                has = track.get("token", "") in p.name
                if bool(track.get("include")) != has:
                    continue
            key = (str(p), ex_id)
            if key in seen_dirs:
                continue
            seen_dirs.add(key)
            n = Note(p, ex_id, ex.get("name", ex_id), track.get("front_matter_exam", ""))
            index_subsections(n)
            parse_warn_section(n)
            apply_bans(n, warn_re)
            extract_items(n, anchor_re)
            notes.append(n)

    keys = existing_keys(root)
    blank = []
    habitual = {}
    for ex_id, ex in exams.items():
        if ex.get("status") == "closed":
            continue
        ex_notes = [n for n in notes if n.exam == ex_id]
        blank += [dict(r, exam=ex_id) for r in parse_blank_reports(root, ex, cfg, ex_notes, date, a.window_days)]
        habitual[ex_id] = ledger_habitual(root, ex, cfg, keys)
    # 백지 ⑦ 금지 반영 후 items의 banned 재동기화
    for n in notes:
        for it in n.items:
            it["banned"] = n.banned.get(it["line"] - 1, [])
        for nl in n.n_lines:
            nl["banned"] = n.banned.get(nl["line"] - 1, [])
            nl.update(summary_hits(root, n.exam, nl["text"]))

    prev = prev_report_tables(root, date)

    # 집계
    tot = {"★★": 0, "★": 0, "{}": 0, "n:": 0}
    banned_total = 0
    cand_by_lane = {"★★": 0, "★": 0, "{}": 0}
    for n in notes:
        for k in tot:
            tot[k] += n.marks[k]
        for it in n.items:
            if it["banned"]:
                banned_total += 1
            else:
                lane = it["lane"] if it["lane"] in cand_by_lane else "{}"
                cand_by_lane[lane] += 1
                if it["lane"] in ("★★", "★") and it["braces"]:
                    pass
    result = {
        "date": date.isoformat(), "window": [lo.isoformat(), date.isoformat()], "root": str(root),
        "params": {"card_target": (anki_cfg.get("weekly") or {}).get("card_target"),
                   "card_ceiling": (anki_cfg.get("weekly") or {}).get("card_ceiling"),
                   "mandatory_lanes": (anki_cfg.get("weekly") or {}).get("mandatory_lanes"),
                   "fill_order": (anki_cfg.get("weekly") or {}).get("fill_order"),
                   "density": anki_cfg.get("density")},
        "marks_total": tot, "candidates_by_lane": cand_by_lane, "banned_marked_items": banned_total,
        "notes": [{
            "file": n.name, "exam": n.exam, "exam_name": n.exam_name, "track": n.track, "mtime": n.mtime,
            "marks": n.marks, "warn_format": n.warn_format, "warn_table": n.warn_table,
            "general_notices": n.general, "unresolved_warns": n.unresolved,
            "banned": [{"line": i + 1, "text": n.lines[i].strip()[:160], "reasons": r} for i, r in sorted(n.banned.items())],
            "items": n.items, "n_lines": n.n_lines,
        } for n in notes],
        "existing_keys": len(keys),
        "habitual": habitual,
        "blank_reports": blank,
        "prev_report": prev,
    }

    out = Path(a.out) if a.out else root / "_시험엔진" / "anki" / "_work" / f"후보_{date.isoformat()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    md = render_md(result)
    out.with_suffix(".md").write_text(md, encoding="utf-8")
    if a.json:
        print(json.dumps({"out": str(out), "notes": len(notes), "marks_total": tot, "candidates_by_lane": cand_by_lane,
                          "banned_marked_items": banned_total}, ensure_ascii=False))
    else:
        print(f"[OK] 후보 추출 → {out}\n     노트 {len(notes)}개 · 표식 {tot} · 후보 {cand_by_lane} · 표식 줄 금지 {banned_total}건")
        for n in notes:
            if n.unresolved:
                print(f"     ⚠ {n.name}: 사람 판독 필요 {len(n.unresolved)}건")
    return 0


def render_md(r):
    L = []
    L.append(f"# Anki 후보 추출 — {r['date']} (창 {r['window'][0]} ~ {r['window'][1]})\n")
    L.append("## 표식 실측 (추출기)\n")
    L.append("| 노트 | 시험 | ★★ | ★ | `{}` | n: | 하단 ⚠️ 양식 | 금지 줄 | 사람 판독 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for n in r["notes"]:
        m = n["marks"]
        L.append(f"| {n['file']} | {n['exam']} | {m['★★']} | {m['★']} | {m['{}']} | {m['n:']} | {n['warn_format'] or '없음'} | {len(n['banned'])} | {len(n['unresolved_warns'])} |")
    t = r["marks_total"]
    L.append(f"| **합계** | | **{t['★★']}** | **{t['★']}** | **{t['{}']}** | **{t['n:']}** | | | |\n")
    L.append(f"후보(표식 줄, 금지 제외): ★★ {r['candidates_by_lane']['★★']} · ★ {r['candidates_by_lane']['★']} · `{{}}` {r['candidates_by_lane']['{}']} — 표식 줄 금지 {r['banned_marked_items']}건. 밀도 규칙(줄 1 = 카드 1 · 분할 ≤2 · 빈칸 ≤3) 적용 시 예상 카드 ≈ 후보 줄 수 × 1.2.\n")
    L.append("## 출제 금지 (banned) — 되살리지 않는다\n")
    for n in r["notes"]:
        if not n["banned"] and not n["general_notices"] and not n["unresolved_warns"]:
            continue
        L.append(f"### {n['file']}")
        for b in n["banned"]:
            L.append(f"- L{b['line']} · {' / '.join(b['reasons'])} · `{b['text'][:90]}`")
        for g in n["general_notices"]:
            L.append(f"- (일반 주의문 #{g.get('no')}) {g.get('expr')} — 항목 금지 아님, 해당 카드 뒷면 '현행 기준 확인'")
        for u in n["unresolved_warns"]:
            L.append(f"- ❓ 사람 판독: #{u.get('no')} {str(u.get('text'))[:120]} {('— ' + u['note']) if u.get('note') else ''}")
        L.append("")
    L.append("## 후보 항목 (표식 줄)\n")
    for n in r["notes"]:
        L.append(f"### {n['file']} ({n['exam']}{(' ' + n['track']) if n['track'] else ''})")
        for it in n["items"]:
            flag = "🚫" if it["banned"] else "✅"
            br = (" `{}`=" + ", ".join(it["braces"])) if it["braces"] else ""
            L.append(f"- {flag} L{it['line']} [{it['lane']}]{br} {it['text'][:140]}")
        if n["n_lines"]:
            L.append("  - n: 줄")
            for nl in n["n_lines"]:
                hit = "총정리 유사행 %d" % len(nl.get("hits") or [])
                L.append(f"    - {'🚫' if nl['banned'] else '·'} L{nl['line']} {nl['text'][:120]} ({hit})")
        L.append("")
    L.append("## 원장 상습 (기출고 key 제외 후보)\n")
    for ex, rows in r["habitual"].items():
        new = [x for x in rows if not x["already_issued"]]
        L.append(f"- {ex}: 후보 {len(rows)} · 기출고 중복 {len(rows) - len(new)} · 신규 {len(new)}")
        for x in new:
            L.append(f"  - {x['conceptKey']} (tw{x['timesWrong']} rm{x['retryMissed']} · {x['lastWrong']}{' · 실수 전용' if x['only_slip'] else ''})")
    L.append("\n## 백지복습 보고서 (창 안 mtime · 짝지은 노트)\n")
    for b in r["blank_reports"]:
        L.append(f"- {'🟢' if b['in_window'] else '⚪'} {b['file']} → {b['matched_note'] or '미매칭'} · 구멍 {len(b['holes'])} · 교정 {len(b['fixed'])} · ⑦ {len(b['warns'])} · {b['status']}")
    p = r["prev_report"]
    L.append(f"\n## 직전 검수리포트 ({p['file'] or '없음'})\n")
    L.append(f"- 이월 {len(p['carry'])}행 · 보류 {len(p['hold'])}행 (대기 주수 +1 승계, 3주 이상 표면화 {sum(1 for h in p['hold'] if h.get('표면화'))}건)")
    for h in p["hold"]:
        L.append(f"  - {'‼️' if h.get('표면화') else '·'} [{h['대기 주수']}주] {h['항목'][:90]} — {h['해소 조건'][:60]}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
