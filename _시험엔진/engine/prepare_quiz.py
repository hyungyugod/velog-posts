#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/prepare_quiz.py — 문제지 준비(사실 수집 → plan.json)  (HG 무한복습체계 v1, 2026-09-02)

  python3 prepare_quiz.py --exam gongin|bupsa1|bupsa2 --kind daily|retry|weekly
                          [--date YYYY-MM-DD] [--root ROOT] [--downloads DIR]
                          [--no-ingest] [--json]

이 스크립트는 **문항을 쓰지 않는다.** AI 실행자(스킬)가 문항을 쓰기 전에 필요한
'사실'만 기계적으로 모아 plan.json으로 넘긴다 — 어떤 노트를 몇 문항 쓸지, 한달전
블록에 무엇이 들어갈지, 듀 큐에서 무엇을 재도전할지까지가 여기서 확정된다.

산출(쓰기)은 두 곳뿐이다:
  · <시험폴더>/<데일리퀴즈|오답퀴즈|claude_ox_오답>/_work/*.plan.json
  · _시험엔진/_runs.log  (종료 사유 EXISTS/SKIP/DUE0 한 줄 — ready는 렌더러가 남긴다)
노트·문제지·원장·_inbox 는 읽기만 한다(수거는 Downloads → _inbox 로의 cp -n 뿐이며
Downloads 는 불변, 원장 갱신은 build_ledger.py 에 위임).

절차 정본: _시험엔진/spec/데일리퀴즈.md · spec/오답퀴즈.md · spec/주간리포트.md
          + spec/프로파일_*.md 3종. 파라미터 정본: engine/exams.json.
소비자: engine/render_quiz.py (plan 계약 — longrev_picks[].path/age_days, monthly_block
        확정본, stage · rest · alert_html · monthly_src_range · due_backlog).

표준 라이브러리만 사용(python 3.10). 종료 코드는 항상 0(종료 사유는 plan.status).
"""

import argparse
import datetime as _dt
import glob as _glob
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = ENGINE_DIR.parents[1]              # <root>/_시험엔진/engine → <root>
KST = _dt.timezone(_dt.timedelta(hours=9))
SCHEMA = 1

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]
STAGE_RANK = {"스킵": -1, "유지": 0, "S0-1": 1, "S0": 1, "S0-2": 2,
              "S1": 3, "S2": 4, "S3": 5}

QUESTIONS_RE = re.compile(r"const QUESTIONS = (\[[\s\S]*?\n\]);")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
QUIZ_FILE_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}\.html$")

NODE_EXTRACT = r"""
const fs = require('fs');
const rx = /const QUESTIONS = (\[[\s\S]*?\n\]);/;
const out = {};
for (const p of process.argv.slice(1)) {
  try {
    const m = fs.readFileSync(p, 'utf8').match(rx);
    out[p] = m ? eval(m[1]) : null;
  } catch (e) { out[p] = null; }
}
process.stdout.write(JSON.stringify(out));
"""


# ────────────────────────────────────────────────────────────── 공용 유틸

def load_exams(root):
    p = ENGINE_DIR / "exams.json"
    if not p.exists():
        p = Path(root) / "_시험엔진" / "engine" / "exams.json"
    return json.loads(p.read_text(encoding="utf-8"))


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return default


def kst_today():
    return _dt.datetime.now(KST).date()


def d_of(s):
    return _dt.date.fromisoformat(s)


def days_between(today, other):
    """레거시 JS day() 와 같은 정의: (오늘 − 대상) 일수."""
    return (today - other).days


def fmt_range(a, b):
    """2026-08-01~08-07 (같은 해면 뒤쪽을 MM-DD 로 줄인다)."""
    if not a or not b:
        return ""
    return "%s~%s" % (a, b[5:] if a[:4] == b[:4] else b)


def js_eval(expr, env):
    """exams.json rampup 표의 JS 식(`new==0 && long==0`, `long>=3 ? 20 : 15`)을 평가한다.
       변수는 new · long · monthly_window 셋뿐이고 리터럴·비교·논리 연산만 쓴다."""
    if isinstance(expr, (int, float)):
        return expr
    s = str(expr).replace("&&", " and ").replace("||", " or ")
    m = re.match(r"^([^?]+)\?([^:]+):(.+)$", s)
    if m:
        s = "(%s) if (%s) else (%s)" % (m.group(2), m.group(1), m.group(3))
    return eval(s, {"__builtins__": {}}, dict(env))              # noqa: S307


def append_runs_log(root, exam, kind, status, summary):
    p = Path(root) / "_시험엔진" / "_runs.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    line = "%s\t%s\t%s\t%s\t%s\n" % (
        _dt.datetime.now(KST).replace(microsecond=0, tzinfo=None).isoformat(),
        exam, kind, status, str(summary).replace("\n", " ")[:400])
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
    return p


# ────────────────────────────────────────────────────────────── 노트·표식

def note_date(name):
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", name)
    return d_of(m.group(1)) if m else None


def note_subject(name, alias=None):
    """파일명 두 번째 토큰: 2026-08-31-민법-(…).md → 민법."""
    body = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    subj = body.split("-", 1)[0].strip()
    subj = re.sub(r"\.md$", "", subj)
    return (alias or {}).get(subj, subj)


def track_ok(name, track):
    """track: {token, include} — bupsa1은 '-2차-' 미포함, bupsa2는 포함. gongin은 None."""
    if not track:
        return True
    has = track["token"] in name
    return has if track.get("include") else not has


def scan_notes(notes_dir, pattern, track):
    """<notes_dir> 최상위의 날짜 정리본. (path, date, size) 리스트를 파일명 순으로."""
    out = []
    if not notes_dir.is_dir():
        return out
    rx = re.compile(pattern)
    for p in sorted(notes_dir.iterdir(), key=lambda x: x.name):
        if not p.is_file() or not rx.match(p.name):
            continue
        if not track_ok(p.name, track):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        if size <= 0:
            continue
        dt = note_date(p.name)
        if dt is None:
            continue
        out.append((p, dt, size))
    return out


def front_matter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def count_marks(text, marks_cfg):
    anchor = re.compile(marks_cfg.get("anchor_regex", r"^\s*(?:[-*]|\d+\.)?\s*(★★|★|n:)"), re.M)
    warn = re.compile(marks_cfg.get("warn_regex", r"⚠️?|확인 ?필요"))
    c = Counter(anchor.findall(text))
    marks = {"★★": c.get("★★", 0), "★": c.get("★", 0), "n:": c.get("n:", 0)}
    warn_lines = sum(1 for ln in text.splitlines() if warn.search(ln))
    return marks, warn_lines


# ────────────────────────────────────────────────────────────── 과거 문제지 QUESTIONS

def extract_questions(paths):
    """문제지 HTML → QUESTIONS 배열. json.loads 우선, 실패분은 node 한 번으로 일괄 eval.
       (구형 문제지는 따옴표 없는 키·// 주석이라 JSON 파서로 못 읽는다.)"""
    out, need_node = {}, []
    for p in paths:
        try:
            txt = Path(p).read_text(encoding="utf-8")
        except OSError:
            out[str(p)] = []
            continue
        m = QUESTIONS_RE.search(txt)
        if not m:
            out[str(p)] = []
            continue
        body = (m.group(1).replace("/*__QUESTIONS_START__*/", "")
                          .replace("/*__QUESTIONS_END__*/", ""))
        try:
            v = json.loads(body)
            out[str(p)] = v if isinstance(v, list) else []
        except Exception:                                       # noqa: BLE001
            need_node.append(str(p))
    if need_node:
        try:
            r = subprocess.run(["node", "-e", NODE_EXTRACT] + need_node,
                               capture_output=True, text=True, timeout=120)
            got = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
        except Exception:                                       # noqa: BLE001
            got = {}
        for p in need_node:
            v = got.get(p)
            out[p] = v if isinstance(v, list) else []
    return out


def quiz_files(qdir):
    """<폴더>의 YYYY-MM-DD.html 을 (date, path) 로, 날짜 오름차순."""
    if not qdir.is_dir():
        return []
    got = []
    for p in qdir.iterdir():
        if p.is_file() and QUIZ_FILE_RE.match(p.name):
            got.append((d_of(p.stem), p))
    got.sort(key=lambda t: t[0])
    return got


# ────────────────────────────────────────────────────────────── 수거·원장

def find_downloads(cfg, cli):
    if cli:
        p = Path(cli)
        return p if p.is_dir() else None
    pat = (cfg.get("_paths") or {}).get("downloads_glob") or "/sessions/*/mnt/Downloads"
    for c in sorted(_glob.glob(pat)):
        if Path(c).is_dir():
            return Path(c)
    return None


def ingest(root, exam, ex, cfg, dl_dir, warnings):
    """Downloads → _inbox 복사(cp -n) 후 build_ledger.py 위임. Downloads 는 절대 불변."""
    paths = cfg.get("_paths") or {}
    inbox = Path(root) / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답") / paths.get("inbox_dir", "_inbox")
    inbox.mkdir(parents=True, exist_ok=True)
    copied = 0
    if dl_dir:
        for src in sorted(dl_dir.glob(ex["result_glob"])):
            dst = inbox / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
                copied += 1
        lg = ex.get("legacy_result_glob")
        if lg:
            pre_from, pre_to = ex.get("legacy_rename_prefix") or ["", ""]
            until = ex.get("legacy_until")
            for src in sorted(dl_dir.glob(lg)):
                m = DATE_RE.search(src.name)
                if until and m and m.group(1) > until:
                    continue
                name = src.name.replace(pre_from, pre_to, 1) if pre_from else src.name
                dst = inbox / name
                if not dst.exists():
                    shutil.copy2(src, dst)
                    copied += 1
    else:
        warnings.append("Downloads 미연결: 기존 _inbox 분으로 진행")

    exit_code, summary = None, ""
    bl = ENGINE_DIR / "build_ledger.py"
    if bl.exists():
        r = subprocess.run([sys.executable, str(bl), "--exam", exam, "--ingest",
                            "--root", str(root)], capture_output=True, text=True)
        exit_code = r.returncode
        lines = [l.strip() for l in (r.stdout or "").splitlines() if l.strip()]
        summary = " | ".join(lines[-3:])[:400] if lines else (r.stderr or "").strip()[:400]
        if exit_code == 2:
            warnings.append("원장: 원천 0건(exit 2) — 정상 범위")
        elif exit_code not in (0, 2):
            warnings.append("원장 갱신 실패(exit %s): %s" % (exit_code, summary[:160]))
        if exit_code == 0 and ex.get("dashboard"):
            bd = ENGINE_DIR / "build_dashboard.py"
            if bd.exists():
                rd = subprocess.run([sys.executable, str(bd), "--exam", exam,
                                     "--root", str(root)], capture_output=True, text=True)
                if rd.returncode != 0:
                    warnings.append("대시보드 갱신 실패(exit %s)" % rd.returncode)
    else:
        warnings.append("build_ledger.py 없음 — 원장 갱신 생략")

    return {"copied": copied, "downloads": "mounted" if dl_dir else "unmounted",
            "ledger_exit": exit_code, "ledger_summary": summary}


def load_ledger(root, ex, cfg):
    paths = cfg.get("_paths") or {}
    p = (Path(root) / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답")
         / paths.get("ledger_subdir", "_ledger") / "오답_원장.json")
    return read_json(p), p


# ────────────────────────────────────────────────────────────── 결과 신호(제출 확인)

def result_signals(root, ex, cfg, dl_dir):
    """제출 신호로 인정되는 파일 이름 집합(-RQ 제외 판정은 호출부에서)."""
    paths = cfg.get("_paths") or {}
    inbox = Path(root) / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답") / paths.get("inbox_dir", "_inbox")
    names = set()
    if inbox.is_dir():
        names |= {p.name for p in inbox.iterdir() if p.is_file()}
    if dl_dir and dl_dir.is_dir():
        names |= {p.name for p in dl_dir.iterdir() if p.is_file()}
    return names


def _sig_variants(prefix, date, suffix=""):
    base = "%s%s%s" % (prefix, date, suffix)
    out = {base + ".json"}
    for n in range(1, 10):
        out.add("%s (%d).json" % (base, n))
    return out


def has_result(names, ex, date, retry=False):
    """정확히 <result_prefix><날짜>[-RQ].json (± ' (N)' 사본)만 신호로 인정."""
    suffix = "-RQ" if retry else ""
    cands = _sig_variants(ex["result_prefix"], date, suffix)
    if not retry and ex.get("legacy_result_glob") and ex.get("legacy_rename_prefix"):
        until = ex.get("legacy_until")
        if not until or date <= until:
            cands |= _sig_variants(ex["legacy_rename_prefix"][0], date, suffix)
    return bool(cands & names)


# ────────────────────────────────────────────────────────────── 신규 원천

def collect_new_sources(root, ex, cfg, date, marks_cfg, warnings):
    """최상위 정리본(파일명 날짜 −N일) + 백지복습/(mtime −N일). 같은 basename 이면 노트만."""
    paths = cfg.get("_paths") or {}
    daily = ex["daily"]
    notes_dir = Path(root) / ex["notes_dir"]
    alias = ex.get("subject_alias") or {}
    track = ex.get("track")
    win_new = int(daily.get("new_note_window_days", 7))
    win_blank = int(daily.get("blank_review_window_days", 7))

    notes = scan_notes(notes_dir, (paths.get("note_pattern") or r"^20\d{2}-\d{2}-\d{2}.*\.md$"), track)
    new_notes = [(p, dt, sz) for (p, dt, sz) in notes if 0 <= days_between(date, dt) < win_new]
    long_cands = [(p, dt, sz) for (p, dt, sz) in notes
                  if days_between(date, dt) >= int(((daily.get("buckets") or {}).get("B1") or [7])[0])]

    srcs, seen = [], set()
    for p, dt, sz in new_notes:
        marks, warn = count_marks(p.read_text(encoding="utf-8", errors="replace"), marks_cfg)
        srcs.append({"path": str(p), "file": p.name, "subject": note_subject(p.name, alias),
                     "date": dt.isoformat(), "kind": "note", "size": sz,
                     "marks": marks, "warn_lines": warn})
        seen.add(p.stem)

    bdir = notes_dir / paths.get("blank_review_dir", "백지복습")
    if bdir.is_dir():
        for p in sorted(bdir.iterdir(), key=lambda x: x.name):
            if not p.is_file() or p.suffix != ".md":
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_size <= 0:
                continue
            mdate = _dt.date.fromtimestamp(st.st_mtime)
            if days_between(date, mdate) >= win_blank:
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            fm = front_matter(text)
            # 트랙 판별: 파일명 -2차- → 2차, 없으면 front matter exam:, 둘 다 없으면 제외
            if track:
                if track["token"] in p.name:
                    is_track = bool(track.get("include"))
                elif fm.get("exam"):
                    is_track = fm["exam"].strip() == track.get("front_matter_exam")
                else:
                    warnings.append("백지복습 트랙 판별 불가 — 제외: %s" % p.name)
                    continue
                if not is_track:
                    continue
            if (fm.get("status") or "").strip() == "닫힘":
                continue
            if p.stem in seen:                    # 최상위와 중복이면 노트 1건만
                continue
            marks, warn = count_marks(text, marks_cfg)
            fdt = note_date(p.name)
            srcs.append({"path": str(p), "file": p.name,
                         "subject": (fm.get("subject") or note_subject(p.name, alias)).strip(),
                         "date": (fdt or mdate).isoformat(), "kind": "blank_review",
                         "size": st.st_size, "marks": marks, "warn_lines": warn})
    srcs.sort(key=lambda s: (s["date"], s["file"]))
    return srcs, new_notes, long_cands


# ────────────────────────────────────────────────────────────── 장기복습 선정

def split_quota(total, ratio):
    """비례 배분(최대잔여법) + 잔여가 같으면 뒤(오래된 버킷)부터.
       3문·[3,3,4] → 1·1·1, 4문 → 1·1·2, 10문 → 3·3·4.
       2026-09-02: 단순 내림+B3몰아주기는 3문에서 0·1·2가 되어 B1(최근 버킷)이 굶었다."""
    s = sum(ratio) or 1
    base = [total * r // s for r in ratio]
    left = total - sum(base)
    rem = [total * r % s for r in ratio]                          # 잔여(정수 비교용)
    order = sorted(range(len(ratio)), key=lambda i: (-rem[i], -i))  # 잔여 큰 순 → 동률이면 B3
    for i in range(left):
        base[order[i % len(order)]] += 1
    return base


def pick_longrev(root, ex, cfg, date, long_cands, n_quota, mode, warnings):
    """버킷별 문항 배분 → 미서빙 우선 노트 선정 → 노트별 문항 수."""
    daily = ex["daily"]
    paths = cfg.get("_paths") or {}
    alias = ex.get("subject_alias") or {}
    if n_quota <= 0 or not long_cands:
        if n_quota > 0:
            warnings.append("장기복습 후보 0 — 장기복습 %d문 미편성" % n_quota)
        return [], {}, 0

    allday = (mode == "allday")
    amode = daily.get("allday_mode") or {}
    buckets_cfg = daily.get("buckets") or {"B1": [7, 44], "B2": [45, 89], "B3": [90, None]}
    names = ["B1", "B2", "B3"]
    npb = (amode.get("notes_per_bucket") if allday else None) or daily.get("notes_per_bucket") or [1, 2]

    split = (amode.get("bucket_split") if allday else None) or daily.get("bucket_split")
    ratio = daily.get("bucket_split_ratio")
    if split and sum(split) == n_quota:
        alloc = list(split)                                       # 절대 배분(합이 몫과 같을 때)
    else:
        alloc = split_quota(n_quota, split or ratio or [3, 3, 4])

    # 버킷별 후보
    pool = {b: [] for b in names}
    for p, dt, sz in long_cands:
        age = days_between(date, dt)
        for b in names:
            lo, hi = (buckets_cfg.get(b) or [0, None])[0], (buckets_cfg.get(b) or [0, None])[1]
            if age >= lo and (hi is None or age <= hi):
                pool[b].append((p, dt, sz, age))
                break

    # 후보 없는 버킷 몫 이월: 더 오래된 버킷 → 없으면 가장 가까운 젊은 버킷 → 없으면 감축
    for i, b in enumerate(names):
        if alloc[i] <= 0 or pool[b]:
            continue
        moved = False
        for j in range(i + 1, len(names)):
            if pool[names[j]]:
                alloc[j] += alloc[i]
                warnings.append("%s 후보 없음 — %d문을 %s로 이월" % (b, alloc[i], names[j]))
                alloc[i] = 0
                moved = True
                break
        if not moved:
            for j in range(i - 1, -1, -1):
                if pool[names[j]]:
                    alloc[j] += alloc[i]
                    warnings.append("%s 후보 없음 — %d문을 %s로 이월(젊은 쪽)" % (b, alloc[i], names[j]))
                    alloc[i] = 0
                    moved = True
                    break
        if not moved:
            warnings.append("%s 후보 없음 — 장기복습 %d문 감축" % (b, alloc[i]))
            alloc[i] = 0

    log = read_json(Path(root) / ex["dir"] / (paths.get("quiz_dirs") or {}).get("daily", "데일리퀴즈")
                    / paths.get("longrev_log", "_장기복습_로그.json"), {}) or {}

    picks, per_bucket = [], {}
    for i, b in enumerate(names):
        q = alloc[i]
        cands = pool[b]
        if q <= 0 or not cands:
            per_bucket[b] = {"notes": 0, "questions": 0}
            continue
        # ① 미서빙 우선(파일명 오래된 순) ② 전부 서빙됐으면 last 오래된 순
        unserved = [c for c in cands if c[0].name not in log]
        served = [c for c in cands if c[0].name in log]
        unserved.sort(key=lambda c: (c[1], c[0].name))
        served.sort(key=lambda c: ((log.get(c[0].name) or {}).get("last") or "", c[1], c[0].name))
        ordered = unserved + served
        lo, hi = int(npb[0]), int(npb[-1])
        n_notes = min(hi, len(ordered), q)
        n_notes = max(n_notes, min(lo, len(ordered), q)) or 1
        chosen = ordered[:n_notes]
        base, extra = divmod(q, n_notes)
        for k, (p, dt, sz, age) in enumerate(chosen):
            picks.append({"path": str(p), "file": p.name,
                          "subject": note_subject(p.name, alias), "date": dt.isoformat(),
                          "age_days": age, "bucket": b, "count": base + (1 if k < extra else 0)})
        per_bucket[b] = {"notes": n_notes, "questions": q}
    return picks, per_bucket, sum(p["count"] for p in picks)


# ────────────────────────────────────────────────────────────── 한달전 복원

def build_monthly(qdir, ex, date, n_quota, warnings):
    """창(오늘−33 ~ 오늘−27)의 문제지에서 확정본 블록을 만든다. 폴백은 프로파일 규칙."""
    daily = ex["daily"]
    if n_quota <= 0:                                   # 한달전 몫 0(램프업 저단계·유지) — 조회 자체를 생략
        return [], None, 0, False
    lo, hi = (daily.get("monthly_window") or [27, 33])
    per_cat = int(daily.get("monthly_per_cat_max") or 3)
    fallback = daily.get("monthly_fallback") or "none"
    files = quiz_files(qdir)
    win = [(dt, p) for dt, p in files if lo <= days_between(date, dt) <= hi]
    src_range = fmt_range((date - _dt.timedelta(days=hi)).isoformat(),
                          (date - _dt.timedelta(days=lo)).isoformat())
    used_fallback = False

    if not win:
        if fallback == "oldest_week" and files:
            d0 = files[0][0]
            win = [(dt, p) for dt, p in files if d0 <= dt <= d0 + _dt.timedelta(days=6)]
            src_range = fmt_range(d0.isoformat(), (d0 + _dt.timedelta(days=6)).isoformat())
            used_fallback = True
            warnings.append("한달전 창 비어 최고(最古) 주 폴백: %s" % src_range)
        else:
            warnings.append("한달전 창 비어 블록 미편성(폴백 없음)")
            return [], None, 0, False

    if n_quota <= 0 or not win:
        return [], (src_range if win else None), 0, used_fallback

    sub_key = "sub" if ex.get("daily", {}).get("type") == "단답" else "type"
    got = extract_questions([p for _, p in win])
    by_cat = OrderedDict()
    for dt, p in win:
        for q in got.get(str(p), []):
            if not isinstance(q, dict) or q.get("retryOf") or q.get("monthlyOf"):
                continue
            by_cat.setdefault(q.get("cat") or "기타", []).append((dt, q))

    chosen, used_types = [], {c: set() for c in by_cat}
    taken = {c: 0 for c in by_cat}
    progress = True
    while len(chosen) < n_quota and progress:
        progress = False
        for c, items in by_cat.items():
            if len(chosen) >= n_quota or taken[c] >= per_cat:
                continue
            for idx, (dt, q) in enumerate(items):
                if q.get("_used"):
                    continue
                t = q.get(sub_key) or q.get("type")
                if t in used_types[c]:
                    continue
                q["_used"] = True
                used_types[c].add(t)
                chosen.append((c, dt, q))
                taken[c] += 1
                progress = True
                break
    if len(chosen) < n_quota:
        warnings.append("한달전 후보 부족 — %d문 중 %d문만 편성" % (n_quota, len(chosen)))

    # 블록 안은 같은 과목 연속
    order = list(by_cat.keys())
    chosen.sort(key=lambda t: order.index(t[0]))

    block = []
    for _c, dt, q in chosen:
        it = {k: v for k, v in q.items() if k != "_used"}
        qtext = re.sub(r"^\s*[🔁⏪🔄]\s*", "", str(it.get("q") or ""))
        it["q"] = "🔄 " + qtext
        it["src"] = "%s (한달전 재출제·원본 %s)" % (str(it.get("src") or "").strip(), dt.isoformat())
        it["monthlyOf"] = dt.isoformat()
        block.append(it)
    return block, src_range, len(block), used_fallback


# ────────────────────────────────────────────────────────────── 과거 문제 색인

def index_past(qdir, date, focus_dates):
    """관련 노트에서 이미 낸 문항 — AI가 같은 개념·같은 각도를 피하게."""
    files = [(dt, p) for dt, p in quiz_files(qdir) if dt != date]
    got = extract_questions([p for _, p in files])
    past, total = [], 0
    for dt, p in files:
        for q in got.get(str(p), []):
            if not isinstance(q, dict):
                continue
            total += 1
            m = DATE_RE.match(str(q.get("src") or "").strip())
            if m and m.group(1) in focus_dates:
                # 문제문은 앞 90자만 — 개념·각도 회피에는 충분하고 plan 크기(≈100KB→30KB)를 줄인다.
                qt = re.sub(r"<[^>]+>", " ", str(q.get("q") or "")).strip()
                qt = re.sub(r"\s+", " ", qt)
                past.append({"q": qt[:90] + ("…" if len(qt) > 90 else ""), "conceptKey": q.get("conceptKey"),
                             "type": q.get("type"), "file": p.name})
    return past, total


# ────────────────────────────────────────────────────────────── kind=daily

def do_daily(root, exam, ex, cfg, date, ing, warnings):
    paths = cfg.get("_paths") or {}
    daily = ex["daily"]
    qdir = Path(root) / ex["dir"] / (paths.get("quiz_dirs") or {}).get("daily", "데일리퀴즈")
    work = qdir / paths.get("work_subdir", "_work")
    ds = date.isoformat()

    ledger, _lp = load_ledger(root, ex, cfg)
    due_backlog = len((ledger or {}).get("dueQueue") or []) if ledger else None

    plan = {"schema": SCHEMA, "status": "ready", "exam": exam, "kind": "daily", "date": ds,
            "root": str(root), "generated_at": _dt.datetime.now(KST).replace(microsecond=0).isoformat()}

    out = qdir / ("%s.html" % ds)
    if out.exists():
        plan.update({"status": "exists", "quiz_path": str(out), "due_backlog": due_backlog,
                     "ingest": ing, "warnings": warnings,
                     "ai_brief": "오늘(%s) 데일리 문제지가 이미 있다 — 재생성 금지." % ds})
        return plan, work / ("%s.plan.json" % ds), "이미 생성됨: %s" % out, "EXISTS"

    marks_cfg = cfg.get("_marks") or {}
    new_srcs, new_notes, long_cands = collect_new_sources(root, ex, cfg, date, marks_cfg, warnings)
    n_new_notes = len(new_notes)
    n_long = len(long_cands)
    mlo, mhi = (daily.get("monthly_window") or [27, 33])
    n_mon = sum(1 for dt, _p in quiz_files(qdir) if mlo <= days_between(date, dt) <= mhi)

    # ── 모드·단계·쿼터
    model = daily.get("model") or "fixed"
    mode, stage = model, None
    q = {"total": 0, "new": 0, "longrev": 0, "monthly": 0, "sa_swap_max": 0, "mini": 0}
    if model == "fixed":
        # 전일 모드 판정은 '신규 노트 0'(백지복습 보고서만 있는 날도 전일) — 보고서 한두 장으로
        # 신규 20문을 억지로 만들지 않는다. 백지 구멍은 오답·Anki 경로가 따로 소화한다.
        if n_new_notes == 0:
            if new_srcs:
                warnings.append("신규 노트 0 · 백지복습 보고서만 %d건 — 전일 모드로 판정(보고서는 출제 원천에서 제외)" % len(new_srcs))
                new_srcs = []
            am = daily.get("allday_mode") or {}
            mode = "allday"
            q["new"] = int(am.get("new", 0))
            q["longrev"] = int(am.get("longrev", 0))
            q["monthly"] = int(am.get("monthly", 0))
        else:
            q["new"] = int(daily.get("new", 0))
            q["longrev"] = int(daily.get("longrev", 0))
            q["monthly"] = int(daily.get("monthly", 0))
        q["total"] = int(daily.get("total") or (q["new"] + q["longrev"] + q["monthly"])) \
            if mode == "fixed" else q["new"] + q["longrev"] + q["monthly"]
    else:
        env = {"new": n_new_notes, "long": n_long, "monthly_window": n_mon}
        row = None
        for r in daily.get("rampup") or []:
            if js_eval(r.get("when", "False"), env):
                row = r
                break
        if row is None:
            row = {"stage": "스킵", "total": 0}
        stage = row.get("stage")
        q["total"] = int(js_eval(row.get("total", 0), env))
        q["monthly"] = int(js_eval(row.get("monthly", 0), env) or 0)
        if row.get("longrev") == "all":                 # 유지 모드 = 전부 장기복습
            q["new"] = 0
            q["longrev"] = max(0, q["total"] - q["monthly"])
        else:
            q["new"] = int(js_eval(row.get("new", 0), env) or 0)
            q["longrev"] = int(js_eval(row.get("longrev", 0), env) or 0)

    # 단답 치환 상한
    sa = int(daily.get("sa_swap_max") or 0)
    zero_from = daily.get("sa_swap_zero_from")
    if zero_from and ds >= zero_from:
        sa = 0
    min_stage = daily.get("sa_swap_min_stage")
    if min_stage and STAGE_RANK.get(stage or "", 9) < STAGE_RANK.get(min_stage, 0):
        sa = 0
    if q["new"] <= 0:
        sa = 0
    q["sa_swap_max"] = sa

    # 미니답안(2차)
    mac = daily.get("mini_answer_counts")
    if mac:
        # 기준은 '총 문항'(한달전 포함) — 레거시 검증 스크립트(exp>=12)와 validate_quiz.js가 같은 기준.
        if stage == "유지" or q["total"] <= 0:
            q["mini"] = int(mac.get("maintain", 0))
        elif q["total"] >= int(mac.get("total_gte", 12)):
            q["mini"] = int(mac.get("high", 2))
        else:
            q["mini"] = int(mac.get("low", 1))

    plan.update({"mode": mode, "stage": stage, "quotas": q,
                 "counts": {"new_notes": n_new_notes, "blank_reviews":
                            sum(1 for s in new_srcs if s["kind"] == "blank_review"),
                            "long_candidates": n_long, "monthly_window_files": n_mon}})

    if q["total"] <= 0:
        plan.update({"status": "skip", "new_sources": new_srcs, "longrev_picks": [],
                     "monthly_block": [], "monthly_src_range": None,
                     "past_questions": [], "past_total": 0, "due_backlog": due_backlog,
                     "alert_html": "", "ingest": ing, "warnings": warnings,
                     "ai_brief": "신규 0·장기 0 — 오늘은 %s 데일리 문제지를 만들지 않는다(스킵)." % exam})
        return plan, work / ("%s.plan.json" % ds), \
            "스킵 — 신규 0·장기 0 (문제지 미생성)", "SKIP"

    # ── 장기복습
    picks, per_bucket, lr_got = pick_longrev(root, ex, cfg, date, long_cands, q["longrev"], mode, warnings)
    if lr_got != q["longrev"]:
        q["longrev"] = lr_got
        q["total"] = q["new"] + q["longrev"] + q["monthly"]

    # ── 한달전
    block, src_range, mo_got, _fb = build_monthly(qdir, ex, date, q["monthly"], warnings)
    if mo_got != q["monthly"]:
        q["monthly"] = mo_got
        q["total"] = q["new"] + q["longrev"] + q["monthly"]

    # ── 과거 문제 색인
    focus = {s["date"] for s in new_srcs} | {p["date"] for p in picks}
    past, past_total = index_past(qdir, date, focus)

    # ── 미제출 경보
    alert_html = ""
    alert_cfg = daily.get("alert")
    if alert_cfg:
        dl = ing.get("_dl_dir")
        names = result_signals(root, ex, cfg, dl)
        prior = [dt for dt, _p in quiz_files(qdir) if dt < date][-int(alert_cfg.get("missed_runs", 2)):]
        if prior:
            missed, unknown = 0, False
            for dt in prior:
                if has_result(names, ex, dt.isoformat()):
                    continue
                if ing.get("downloads") != "mounted":
                    unknown = True                     # Downloads 미마운트 + _inbox 부재 = 확인 불가
                missed += 1
            if unknown:
                warnings.append("미제출 확인 불가(Downloads 미연결) — 경보 생략")
            elif missed >= int(alert_cfg.get("missed_runs", 2)) and len(prior) >= int(alert_cfg.get("missed_runs", 2)):
                alert_html = alert_cfg.get("text") or ""

    brief = ("%s %s 데일리 — %s 총 %d문(신규 %d · 장기복습 %d · 한달전 %d). "
             "신규는 new_sources 의 노트/백지복습에서만 출제하고(★★→★ 우선, ⚠️·확인 필요 배제), "
             "장기복습은 longrev_picks 의 노트별 count 만큼, 한달전 블록(monthly_block)은 확정본이라 "
             "그대로 배열 맨 뒤에 붙인다. past_questions 의 문항과 같은 개념·같은 각도는 피한다."
             % (ex.get("name"), ds, ("단계 " + stage) if stage else ("모드 " + mode),
                q["total"], q["new"], q["longrev"], q["monthly"]))
    brief += (" 단답 문항은 evidence{note, quote} 필수 — quote 는 그 노트 원문에서 그대로 복사한"
              " 15~120자여야 하고, 렌더 전에 원문 대조로 검사한다(환각 게이트).")
    if q["sa_swap_max"]:
        brief += " 신규 중 최대 %d문은 단답으로 치환한다." % q["sa_swap_max"]
    if q["mini"]:
        brief += " 미니답안형 %d문 고정 편성." % q["mini"]

    plan.update({"quotas": q, "new_sources": new_srcs, "longrev_picks": picks,
                 "monthly_block": block, "monthly_src_range": src_range,
                 "past_questions": past, "past_total": past_total,
                 "due_backlog": due_backlog, "alert_html": alert_html,
                 "ingest": ing, "warnings": warnings, "ai_brief": brief})

    mk = Counter()
    for s in new_srcs:
        for k, v in (s.get("marks") or {}).items():
            mk[k] += v
    lr_txt = " ".join("%s %d노트/%d문" % (b, per_bucket.get(b, {}).get("notes", 0),
                                         per_bucket.get(b, {}).get("questions", 0))
                      for b in ("B1", "B2", "B3") if per_bucket.get(b, {}).get("questions"))
    summary = ("mode=%s%s · 총 %d = 신규 %d + 장기 %d + 한달전 %d · 단답 치환 ≤%d"
               " · 신규 원천 %d(노트 %d·백지 %d, ★★%d ★%d) · 장기복습 %s · 한달전 원본 %s · 듀 적체 %s"
               % (mode, ("(" + stage + ")") if stage else "", q["total"], q["new"], q["longrev"],
                  q["monthly"], q["sa_swap_max"], len(new_srcs), n_new_notes,
                  sum(1 for s in new_srcs if s["kind"] == "blank_review"),
                  mk.get("★★", 0), mk.get("★", 0), lr_txt or "없음", src_range or "없음",
                  due_backlog if due_backlog is not None else "—"))
    if q["mini"]:
        summary += " · 미니답안 %d" % q["mini"]
    return plan, work / ("%s.plan.json" % ds), summary, None


# ────────────────────────────────────────────────────────────── kind=retry

def do_retry(root, exam, ex, cfg, date, ing, warnings):
    paths = cfg.get("_paths") or {}
    retry = ex.get("retry") or {}
    qdir = Path(root) / ex["dir"] / (paths.get("quiz_dirs") or {}).get("retry", "오답퀴즈")
    work = qdir / paths.get("work_subdir", "_work")
    ds = date.isoformat()
    plan = {"schema": SCHEMA, "status": "ready", "exam": exam, "kind": "retry", "date": ds,
            "root": str(root), "generated_at": _dt.datetime.now(KST).replace(microsecond=0).isoformat()}

    ledger, lp = load_ledger(root, ex, cfg)
    due = list((ledger or {}).get("dueQueue") or [])
    due_total = len(due) if ledger else 0

    out = qdir / ("%s.html" % ds)
    if out.exists():
        plan.update({"status": "exists", "quiz_path": str(out), "cap": retry.get("cap"),
                     "n": 0, "due_total": due_total, "rest": due_total, "picks": [],
                     "ingest": ing, "warnings": warnings,
                     "ai_brief": "오늘(%s) 오답 재도전 문제지가 이미 있다 — 재생성 금지." % ds})
        return plan, work / ("%s.plan.json" % ds), "이미 생성됨: %s" % out, "EXISTS"

    if ledger is None:
        warnings.append("원장 없음: %s — 듀 0으로 처리" % lp)

    cap = int(retry.get("cap") or 20)
    n = min(cap, due_total)
    if n <= 0:
        plan.update({"status": "due0", "cap": cap, "n": 0, "due_total": due_total,
                     "rest": 0, "picks": [], "sa_promote_cap": retry.get("sa_promote_cap"),
                     "promoted": 0, "ingest": ing, "warnings": warnings,
                     "ai_brief": "듀 0 — 오늘 %s 오답 재도전 문제지는 만들지 않는다." % exam})
        return plan, work / ("%s.plan.json" % ds), "듀 0 — 오답퀴즈 없음", "DUE0"

    # 원장 pick 플래그(졸업후보 예약 포함)를 우선 쓰되, 개수는 언제나 min(cap, 듀)에 맞춘다.
    # 상한(exams.json retry.cap)을 올린 직후에는 원장이 옛 상한으로 만들어져 있어 플래그가
    # 모자란다 — 그때는 듀 순서로 보충한다(검사기는 min(cap,듀)를 기대한다).
    idx = {id(d): i for i, d in enumerate(due)}
    flagged = [d for d in due if d.get("pick") is True]
    if not flagged:
        picks_src = due[:n]
    else:
        picks_src = flagged[:n]
        if len(flagged) > n:
            warnings.append("원장 pick==true %d건 > min(cap,듀) %d건 — 듀 순서 상위 %d건만 사용"
                            % (len(flagged), n, n))
        elif len(picks_src) < n:
            taken = {idx[id(d)] for d in picks_src}
            picks_src = picks_src + [d for i, d in enumerate(due) if i not in taken][:n - len(picks_src)]
            warnings.append("원장 pick==true %d건 < min(cap,듀) %d건 — 듀 순서로 %d건 보충"
                            "(상한 변경 후 원장 미갱신: build_ledger.py --exam %s 권장)"
                            % (len(flagged), n, n - len(flagged), exam))

    recs = {r.get("conceptKey"): r for r in ((ledger or {}).get("ledger") or [])}
    alias = ex.get("subject_alias") or {}
    notes = scan_notes(Path(root) / ex["notes_dir"],
                       (paths.get("note_pattern") or r"^20\d{2}-\d{2}-\d{2}.*\.md$"), ex.get("track"))
    by_date = {}
    for p, dt, _sz in notes:
        by_date.setdefault(dt.isoformat(), []).append(str(p))

    # 단답 승격
    sa_cap = retry.get("sa_promote_cap")
    all_sa = (ex.get("daily", {}).get("type") == "단답") or retry.get("sa_promote_unlimited") \
        or (retry.get("type") == "단답")
    if not all_sa:
        sa_cap = int(sa_cap or 0)
        zf = retry.get("sa_promote_zero_from")
        if zf and ds >= zf:
            sa_cap = 0
    promoted = 0

    picks = []
    for d in picks_src:
        key = d.get("conceptKey")
        r = recs.get(key) or {}
        samples = r.get("samples") or []
        rel = []
        for s in samples:
            sd = str(s.get("date") or "")[:10]
            m = DATE_RE.match(str(s.get("src") or "").strip())
            for cand in filter(None, [sd, m.group(1) if m else None]):
                for path in by_date.get(cand, []):
                    if path not in rel:
                        rel.append(path)
        item = {"conceptKey": key,
                "subject": alias.get(d.get("subject"), d.get("subject")),
                "status": d.get("status"), "timesWrong": d.get("timesWrong"),
                "retryMissed": d.get("retryMissed"),
                "consecutiveCorrect": d.get("consecutiveCorrect"),
                "nextReviewDate": d.get("nextReviewDate"),
                "retrievability": d.get("retrievability"),
                "missedTop": d.get("missedTop") or [], "causeTop": d.get("causeTop"),
                "errorCauses": d.get("errorCauses") or {},
                "samples": [{k: s.get(k) for k in
                             ("date", "type", "q", "expl", "myAnswer", "correct",
                              "missedKeys", "errorCause", "causeNote")} for s in samples],
                "related_notes": rel}
        if all_sa:
            item["promote_sa"] = None                    # 전 문항 단답 트랙 — 승격 개념 없음
        else:
            cond = (d.get("status") == "상습" or int(d.get("retryMissed") or 0) >= 1
                    or int(d.get("timesWrong") or 0) >= 3)
            ok = bool(cond and promoted < sa_cap)
            item["promote_sa"] = ok
            promoted += 1 if ok else 0
        picks.append(item)

    brief = ("%s %s 오답 재도전 — 듀 큐 %d개 중 상위 %d문. picks 의 conceptKey 를 그대로 쓰고"
             "(retryOf 동일), samples 의 원 문제를 복사하지 말고 같은 개념을 다른 각도로 변형한다."
             " missedTop 이 있으면 그 포인트를 정면 조준하고, causeTop 은 각도(개념부재=정면·"
             "혼동=판별식·함정=같은 유형 변형·실수=각도 변경 없음)로 쓴다."
             % (ex.get("name"), ds, due_total, len(picks)))
    brief += (" 단답 문항에 evidence{note, quote} 를 달면 렌더가 원문 대조로 검사한다 —"
              " note 는 samples 근거면 'samples', 노트 근거면 related_notes 의 파일명.")
    if all_sa:
        brief += " 이 트랙은 전 문항 단답이라 승격 개념이 없다."
    elif promoted:
        brief += " 그중 %d문은 단답으로 승격(상한 %d)." % (promoted, sa_cap)

    plan.update({"cap": cap, "n": len(picks), "due_total": due_total,
                 "rest": due_total - len(picks), "picks": picks,
                 "sa_promote_cap": (None if all_sa else sa_cap),
                 "promoted": (None if all_sa else promoted),
                 "ingest": ing, "warnings": warnings, "ai_brief": brief})

    summary = ("재도전 %d문 (상한 %d · 듀 %d · 잔여 %d) · 승격 %s · pick 플래그 %s"
               % (len(picks), cap, due_total, due_total - len(picks),
                  "전 문항 단답" if all_sa else "%d/%d" % (promoted, sa_cap),
                  "있음(%d)" % len(flagged) if flagged else "없음(상위 N 폴백)"))
    return plan, work / ("%s.plan.json" % ds), summary, None


# ────────────────────────────────────────────────────────────── kind=weekly

def parse_schedule_days(spec):
    """'월~토' · '화·목 (11/1 …)' → 요일 인덱스 집합(월=0)."""
    s = re.split(r"[(（]", str(spec or ""))[0]
    days = set()
    for m in re.finditer(r"([월화수목금토일])\s*~\s*([월화수목금토일])", s):
        a, b = WEEKDAY_KO.index(m.group(1)), WEEKDAY_KO.index(m.group(2))
        days |= set(range(a, b + 1)) if a <= b else set(range(a, 7)) | set(range(0, b + 1))
    if not days:
        days = {WEEKDAY_KO.index(c) for c in s if c in WEEKDAY_KO}
    return days


def do_weekly(root, exam, ex, cfg, date, ing, warnings):
    paths = cfg.get("_paths") or {}
    base = Path(root) / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답")
    work = base / paths.get("work_subdir", "_work")
    ds = date.isoformat()
    note_name = ((ex.get("weekly") or {}).get("note_name") or "{date}-claude_oxquize.md").replace("{date}", ds)
    plan = {"schema": SCHEMA, "status": "ready", "exam": exam, "kind": "weekly", "date": ds,
            "root": str(root), "generated_at": _dt.datetime.now(KST).replace(microsecond=0).isoformat(),
            "note_path": str(base / note_name)}

    if (base / note_name).exists():
        plan.update({"status": "exists", "ingest": ing, "warnings": warnings,
                     "ai_brief": "이번 주 오답노트가 이미 있다 — 재생성 금지."})
        return plan, work / ("%s.weekly.plan.json" % ds), "이미 생성됨: %s" % (base / note_name), "EXISTS"

    ledger, lp = load_ledger(root, ex, cfg)
    if ledger is None:
        warnings.append("원장 없음: %s" % lp)
        ledger = {}
    week = [(date - _dt.timedelta(days=i)).isoformat() for i in range(1, 8)]
    wset = set(week)

    due = list(ledger.get("dueQueue") or [])
    stats = {k: ledger.get(k) for k in ("submissions", "avgScore", "avgTotal", "perfectRuns",
                                        "totalWrongItems", "uniqueConcepts", "dateRange",
                                        "statusCounts", "subjectWeakness", "generatedAt")}
    stats["due_total"] = len(due)

    # ── 기대치 검증
    dl = ing.get("_dl_dir")
    names = result_signals(root, ex, cfg, dl)
    dqdir = Path(root) / ex["dir"] / (paths.get("quiz_dirs") or {}).get("daily", "데일리퀴즈")
    rqdir = Path(root) / ex["dir"] / (paths.get("quiz_dirs") or {}).get("retry", "오답퀴즈")
    daily_rows = [{"date": dt.isoformat(), "result": has_result(names, ex, dt.isoformat())}
                  for dt, _p in quiz_files(dqdir) if dt.isoformat() in wset]
    retry_rows = [{"date": dt.isoformat(), "result": has_result(names, ex, dt.isoformat(), retry=True)}
                  for dt, _p in quiz_files(rqdir) if dt.isoformat() in wset]
    missing = ([r["date"] for r in daily_rows if not r["result"]]
               + [r["date"] + "-RQ" for r in retry_rows if not r["result"]])
    alert = ("⚠️ 결과 미수거 %d건 — 문제지만 쌓이고 원장이 늙는 중" % len(missing)) if len(missing) >= 3 else ""

    # 이번 주 수거 JSON 날짜 ↔ 원장 dates 대조
    led_dates = set()
    for r in ledger.get("ledger") or []:
        for d0 in r.get("dates") or []:
            led_dates.add(str(d0)[:10])
    inbox_dates = sorted({m.group(1) for n in names for m in [DATE_RE.search(n)]
                          if m and m.group(1) in wset and n.startswith(ex["result_prefix"])})
    ingest_check = [{"date": d0, "in_ledger": d0 in led_dates} for d0 in inbox_dates]

    # ── 지난주 오답
    last_week, graduated, grad_cand, chronic = [], [], [], []
    for r in ledger.get("ledger") or []:
        st = r.get("status")
        if st == "졸업":
            graduated.append(r.get("conceptKey"))
        elif st == "졸업후보":
            grad_cand.append(r.get("conceptKey"))
        elif st == "상습":
            chronic.append({"conceptKey": r.get("conceptKey"), "subject": r.get("subject"),
                            "timesWrong": r.get("timesWrong"), "retryMissed": r.get("retryMissed")})
        hits = [d0 for d0 in (r.get("dates") or []) if str(d0)[:10] in wset]
        if hits:
            last_week.append({"conceptKey": r.get("conceptKey"), "subject": r.get("subject"),
                              "status": st, "timesWrong": r.get("timesWrong"),
                              "repeat": len(hits) >= 2 or int(r.get("timesWrong") or 0) >= 2,
                              "dates": hits, "missedKeys": r.get("missedKeys") or {},
                              "errorCauses": r.get("errorCauses") or {},
                              "samples": [{k: s.get(k) for k in
                                           ("date", "type", "q", "expl", "myAnswer", "correct",
                                            "missedKeys", "errorCause", "causeNote")}
                                          for s in (r.get("samples") or [])]})
    last_week.sort(key=lambda x: (not x["repeat"], x["subject"] or "", x["conceptKey"] or ""))

    # ── 표식 지표(Phase 2 관찰용)
    notes = scan_notes(Path(root) / ex["notes_dir"],
                       (paths.get("note_pattern") or r"^20\d{2}-\d{2}-\d{2}.*\.md$"), ex.get("track"))
    marks_cfg = cfg.get("_marks") or {}
    mark_rows, tot = [], Counter()
    for p, dt, _sz in notes:
        if dt.isoformat() not in wset:
            continue
        mk, warn = count_marks(p.read_text(encoding="utf-8", errors="replace"), marks_cfg)
        mark_rows.append({"file": p.name, "date": dt.isoformat(), "marks": mk, "warn_lines": warn})
        for k, v in mk.items():
            tot[k] += v
    n_notes = len(mark_rows) or 1
    marks_stat = {"notes": len(mark_rows), "total": dict(tot),
                  "per_note": {k: round(v / n_notes, 2) for k, v in tot.items()}}

    # ── 실행 로그 요약
    log_p = Path(root) / "_시험엔진" / "_runs.log"
    runs = {"daily": Counter(), "retry": Counter()}
    seen_days = {"daily": set(), "retry": set()}
    exam_lines, first_day = 0, None
    lines = []
    if log_p.exists():
        lines = [l for l in log_p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    for ln in lines:
        f = ln.split("\t")
        if len(f) < 4:
            continue
        day = f[0][:10]
        if first_day is None or day < first_day:
            first_day = day
        if f[1] != exam:
            continue
        exam_lines += 1
        if day not in wset or f[2] not in runs:
            continue
        runs[f[2]][f[3]] += 1
        seen_days[f[2]].add(day)
    # kind별 요일 — 2026-09-02 법무사2차 재설계로 데일리(화·목)와 재도전(수·금·토·일) 요일이
    # 갈렸다. schedule_days_<kind> 가 있으면 그것을, 없으면 종전 schedule_days(=daily)를 쓴다.
    sched = {k: parse_schedule_days(ex.get("schedule_days_" + k) or ex.get("schedule_days"))
             for k in ("daily", "retry")}
    if not (ex.get("schedule_days_retry") or "").strip():
        sched["retry"] = set()                    # 재도전 요일이 명시되지 않은 트랙은 미실행 집계 대상 아님
    not_run = sorted({d0 + ("" if k == "daily" else "-RQ")
                      for k in ("daily", "retry")
                      for d0 in week
                      if d_of(d0).weekday() in sched[k] and d0 not in seen_days[k]})
    # 로그가 이번 주를 못 덮으면(설치 직후 등) '미실행'이 아니라 '로그 부족'이다 — 오탐 금지
    log_note = ""
    if not exam_lines:
        log_note = "로그 부족(이 시험 실행 기록 없음)"
    elif first_day and first_day > week[-1]:
        log_note = "로그 부족(수집 시작 %s)" % first_day
    if log_note:
        not_run = []
    runs_summary = {"daily": dict(runs["daily"]), "retry": dict(runs["retry"]),
                    "schedule_days": ex.get("schedule_days"),
                    "schedule_days_daily": ex.get("schedule_days_daily") or ex.get("schedule_days"),
                    "schedule_days_retry": ex.get("schedule_days_retry"),
                    "not_run": not_run, "note": log_note}

    brief = ("%s 주간리포트(%s) — 지난 7일 %s. 원장 통계·지난주 오답 %d개(2회+ %d개)·"
             "졸업 %d·졸업후보 %d·상습 %d·듀 큐 %d개가 사실 원천이다. 여기 없는 수치는 쓰지 않는다."
             % (ex.get("name"), ds, "%s~%s" % (week[-1], week[0]), len(last_week),
                sum(1 for x in last_week if x["repeat"]), len(graduated), len(grad_cand),
                len(chronic), len(due)))

    plan.update({"week": {"from": week[-1], "to": week[0], "dates": sorted(week)},
                 "stats": stats, "due_top8": due[:8],
                 "expectation": {"daily": daily_rows, "retry": retry_rows,
                                 "missing": missing, "alert": alert,
                                 "ingest_check": ingest_check},
                 "last_week_wrong": last_week, "graduated": graduated,
                 "grad_candidates": grad_cand, "chronic": chronic,
                 "marks": {"per_note": mark_rows, "stat": marks_stat},
                 "runs": runs_summary, "ingest": ing, "warnings": warnings, "ai_brief": brief})

    summary = ("주간 사실 수집 — 제출 %s · 평균 %s/%s · 지난주 오답 %d(2회+ %d) · 졸업 %d/후보 %d · "
               "상습 %d · 듀 %d · 결과 미도착 %d%s · 표식 노트 %d(★★%d ★%d) · 미실행일 %s"
               % (stats.get("submissions"), stats.get("avgScore"), stats.get("avgTotal"),
                  len(last_week), sum(1 for x in last_week if x["repeat"]), len(graduated),
                  len(grad_cand), len(chronic), len(due), len(missing),
                  " ⚠경보" if alert else "", marks_stat["notes"], tot.get("★★", 0), tot.get("★", 0),
                  (", ".join(not_run) if not_run else (log_note or "없음"))))
    return plan, work / ("%s.weekly.plan.json" % ds), summary, None


# ────────────────────────────────────────────────────────────── main

def main(argv=None):
    ap = argparse.ArgumentParser(description="문제지 준비 — 사실 수집 → plan.json")
    ap.add_argument("--exam", required=True, choices=["gongin", "bupsa1", "bupsa2"])
    ap.add_argument("--kind", required=True, choices=["daily", "retry", "weekly"])
    ap.add_argument("--date")
    ap.add_argument("--root")
    ap.add_argument("--downloads")
    ap.add_argument("--no-ingest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    cfg = load_exams(root)
    ex = cfg["exams"][a.exam]
    date = d_of(a.date) if a.date else kst_today()
    warnings = []

    dl_dir = find_downloads(cfg, a.downloads)
    if a.no_ingest:
        ing = {"copied": 0, "downloads": "mounted" if dl_dir else "unmounted",
               "ledger_exit": None, "ledger_summary": "--no-ingest (수거·원장 갱신 생략)"}
    else:
        ing = ingest(root, a.exam, ex, cfg, dl_dir, warnings)
    ing["_dl_dir"] = dl_dir

    fn = {"daily": do_daily, "retry": do_retry, "weekly": do_weekly}[a.kind]
    plan, plan_path, summary, log_status = fn(root, a.exam, ex, cfg, date, ing, warnings)

    plan["ingest"] = {k: v for k, v in (plan.get("ingest") or ing).items() if k != "_dl_dir"}
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    if log_status:
        append_runs_log(root, a.exam, a.kind, log_status, summary)

    if a.json:
        print(json.dumps(plan, ensure_ascii=False, indent=1))
        return 0

    print("[%s %s %s] %s" % (a.exam, a.kind, date.isoformat(), summary))
    ig = plan["ingest"]
    print("  수거 %s건 · Downloads %s · 원장 exit %s%s"
          % (ig.get("copied"), ig.get("downloads"), ig.get("ledger_exit"),
             (" · " + ig["ledger_summary"][:120]) if ig.get("ledger_summary") else ""))
    for w in plan.get("warnings") or []:
        print("  ⚠ %s" % w)
    print("  plan: %s" % plan_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
