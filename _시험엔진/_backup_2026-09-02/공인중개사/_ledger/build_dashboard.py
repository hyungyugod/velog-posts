#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 복습 퀘스트 보드 — 정적 HTML 대시보드 생성기.

배치 위치(가정):
    공인중개사/claude_ox_오답/_ledger/build_dashboard.py

사용법:
    python3 build_dashboard.py                      # 데일리퀴즈/_오늘의복습.html 갱신
    python3 build_dashboard.py --root <공인중개사 경로>   # 경로 수동 지정
    python3 build_dashboard.py --out  <폴더>          # 프로덕션 대신 스테이징에 출력

원칙
  - 표준 라이브러리만 사용한다(파이썬 3.9에서 동작).
  - 원장(오답_원장.json)의 **미리 계산된 값만** 읽는다. 재집계·FSRS 계산을 하지 않는다.
  - 읽기 대상이 없거나 필드가 비어도 그 섹션만 조용히 접고 나머지는 그린다.
  - 실패해도 트레이스백 대신 한국어 한 줄만 출력한다.
"""

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- 상수

EXAM_DATE = datetime.date(2026, 10, 31)
EXAM_LABEL = "10/31 제37회"

DASHBOARD_NAME = "_오늘의복습.html"
HISTORY_NAME = "dashboard_history.json"
LEDGER_NAME = "오답_원장.json"
LONGREV_LOG_NAME = "_장기복습_로그.json"

NOTE_AGE_DAYS = 14          # 장기복습 후보가 되는 최소 나이(파일명 날짜 기준)
HISTORY_KEEP = 400          # 히스토리 보관 개수(1년 반 남짓)
STREAK_MAX_BACK = 400       # 스트릭 역추적 안전 상한(일)

WEEKDAY_KR = ("월", "화", "수", "목", "금", "토", "일")
DATE_RE = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")

C_BLUE = "#378ADD"
C_GREEN = "#1D9E75"
C_ORANGE = "#D85A30"


class BuildError(Exception):
    """사용자에게 그대로 보여줄 한국어 오류."""


# ---------------------------------------------------------------- 공통 유틸

def nfc(text):
    """macOS는 파일명을 NFD로 돌려줄 수 있다. 비교 전에 NFC로 통일한다."""
    try:
        return unicodedata.normalize("NFC", text)
    except (TypeError, ValueError):
        return text


def load_json(path):
    """파일이 없거나 깨졌으면 None. 예외를 밖으로 내보내지 않는다."""
    try:
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception:
        return None


def parse_date(text):
    """문자열 어딘가의 YYYY-MM-DD를 date로. 못 찾으면 None."""
    if not text:
        return None
    match = DATE_RE.search(str(text))
    if not match:
        return None
    try:
        return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def as_int(value, default=None):
    """bool은 숫자로 치지 않는다(True가 1로 새는 것 방지)."""
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return default


def day_label(day):
    return "%d년 %d월 %d일 (%s)" % (day.year, day.month, day.day, WEEKDAY_KR[day.weekday()])


def esc(text):
    """HTML 이스케이프(속성값 포함)."""
    out = str(text)
    out = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return out.replace('"', "&quot;")


def prev_weekday(day):
    """직전 평일(월~금). 오늘은 포함하지 않는다."""
    cursor = day - datetime.timedelta(days=1)
    for _ in range(10):
        if cursor.weekday() < 5:
            return cursor
        cursor -= datetime.timedelta(days=1)
    return cursor


# ---------------------------------------------------------------- 경로 해석

def resolve_paths(root_opt):
    """스크립트가 _ledger/에 있다고 보고 상대 경로로 나머지를 유도한다."""
    here = os.path.dirname(os.path.abspath(__file__))
    if root_opt:
        gongin = os.path.abspath(os.path.expanduser(root_opt))
        base = os.path.join(gongin, "claude_ox_오답")
        ledger_dir = os.path.join(base, "_ledger")
    else:
        ledger_dir = here
        base = os.path.dirname(ledger_dir)          # claude_ox_오답
        gongin = os.path.dirname(base)              # 공인중개사
    quiz_dir = os.path.join(gongin, "데일리퀴즈")
    return {
        "here": here,
        "ledger_dir": ledger_dir,
        "base": base,
        "gongin": gongin,
        "quiz_dir": quiz_dir,
    }


# ---------------------------------------------------------------- 수집기

def collect_submission_dates(base_dir):
    """_raw·_inbox의 결과 JSON에서 제출 날짜 집합을 만든다(YYYY-MM-DD 문자열)."""
    dates = set()
    for sub in ("_raw", "_inbox"):
        folder = os.path.join(base_dir, sub)
        if not os.path.isdir(folder):
            continue
        try:
            names = os.listdir(folder)
        except OSError:
            continue
        for raw_name in names:
            name = nfc(raw_name)
            if not name.lower().endswith(".json"):
                continue
            if not name.startswith("공인중개사") or "오답" not in name:
                continue
            found = parse_date(name)
            if found is None:
                # 파일명에 날짜가 없으면 그때만 열어서 date 필드를 본다.
                data = load_json(os.path.join(folder, raw_name))
                if isinstance(data, dict):
                    found = parse_date(data.get("date"))
            if found is not None:
                dates.add(found.isoformat())
    return dates


def compute_streak(today, submitted):
    """평일 연속 제출 일수. 주말은 건너뛰되 끊지 않는다.

    오늘이 평일인데 미제출이면 오늘은 세지 않고 어제까지로 계산한다.
    """
    cursor = today
    if today.weekday() < 5 and today.isoformat() not in submitted:
        cursor = today - datetime.timedelta(days=1)

    streak = 0
    for _ in range(STREAK_MAX_BACK):
        if cursor.weekday() >= 5:                    # 토·일은 건너뜀
            cursor -= datetime.timedelta(days=1)
            continue
        if cursor.isoformat() in submitted:
            streak += 1
            cursor -= datetime.timedelta(days=1)
            continue
        break
    return streak


def count_old_notes(gongin_dir, cutoff):
    """공인중개사 최상위의 20*.md 중 파일명 날짜가 cutoff 이하인 개수. 폴더 없으면 None."""
    if not os.path.isdir(gongin_dir):
        return None
    try:
        names = os.listdir(gongin_dir)
    except OSError:
        return None
    total = 0
    for raw_name in names:
        name = nfc(raw_name)
        if not name.startswith("20") or not name.lower().endswith(".md"):
            continue
        found = parse_date(name[:10])
        if found is None or found > cutoff:
            continue
        if os.path.isfile(os.path.join(gongin_dir, raw_name)):   # 하위 폴더 제외
            total += 1
    return total


def top_weakness(ledger, limit=3):
    """subjectWeakness 상위 N. 동점이면 과목명 사전순으로 고정(실행마다 흔들리지 않게)."""
    table = ledger.get("subjectWeakness") if isinstance(ledger, dict) else None
    if not isinstance(table, dict):
        return []
    rows = []
    for subject, count in table.items():
        value = as_int(count)
        if value is None or value <= 0:
            continue
        rows.append((str(subject), value))
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows[:limit]


# ---------------------------------------------------------------- 히스토리

def load_history(path):
    data = load_json(path)
    if isinstance(data, dict):                       # {"entries": [...]} 형태도 받아준다
        data = data.get("entries")
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and row.get("date")]


def merge_history(history, entry):
    """같은 날짜는 교체(멱등). 날짜 오름차순 정렬 후 최근 것만 남긴다."""
    kept = [row for row in history if str(row.get("date")) != entry["date"]]
    kept.append(entry)
    kept.sort(key=lambda row: str(row.get("date")))
    return kept[-HISTORY_KEEP:]


def backlog_delta(history, today, current):
    """7일 전(없으면 그 이전 최근) 기록 대비 적체 증감. 비교 불가면 None."""
    if current is None:
        return None
    target = (today - datetime.timedelta(days=7)).isoformat()
    today_key = today.isoformat()
    best = None
    for row in history:
        key = str(row.get("date"))
        if key == today_key or key > target:
            continue
        if best is None or key > str(best.get("date")):
            best = row
    if best is None:
        return None
    previous = as_int(best.get("dueCount"))
    if previous is None:
        return None
    return {"prev": previous, "date": str(best.get("date")), "diff": current - previous}


# ---------------------------------------------------------------- HTML

CSS = """
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{
    margin:0;
    padding:28px 16px 56px;
    background-color:#FAFAFA;
    background-image:linear-gradient(#EFEFEF 1px,transparent 1px),
                     linear-gradient(90deg,#EFEFEF 1px,transparent 1px);
    background-size:36px 36px;
    background-position:-1px -1px;
    color:#23262b;
    font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',
                'Malgun Gothic',sans-serif;
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  .wrap{max-width:720px;margin:0 auto}
  .card{background:#fff;border:1px solid #ececec;border-radius:12px;
        box-shadow:0 1px 2px rgba(20,24,32,.04)}
  header.head{margin:2px 0 22px;padding:22px 22px 20px;background:#fff;
        border:1px solid #ececec;border-radius:12px;box-shadow:0 1px 2px rgba(20,24,32,.04)}
  .eyebrow{font-size:12.5px;font-weight:700;letter-spacing:.06em;color:#378ADD}
  h1{margin:6px 0 10px;font-size:27px;font-weight:800;letter-spacing:-.01em}
  .headrow{display:flex;align-items:center;justify-content:space-between;
           gap:10px;flex-wrap:wrap}
  .today{font-size:14.5px;color:#6b7280;font-weight:600}
  .streak{display:inline-block;padding:5px 13px;border-radius:999px;font-size:13.5px;
          font-weight:700;background:#FFF3EC;color:#D85A30;border:1px solid #F6DDD0;
          white-space:nowrap}
  .streak.zero{background:#F4F5F7;color:#7a8290;border-color:#e7e9ee}
  h2.sect{margin:26px 2px 11px;font-size:13px;font-weight:800;color:#8a919c;
          letter-spacing:.05em}
  .mission{padding:6px 20px}
  .row{display:flex;align-items:flex-start;gap:11px;padding:14px 0;
       border-top:1px solid #f2f2f2}
  .row:first-child{border-top:none}
  .mark{flex:0 0 auto;font-size:16px;line-height:1.5}
  .body{flex:1 1 auto;min-width:0}
  .title{font-size:15.5px;font-weight:700;color:#23262b}
  .title.done{color:#1D9E75}
  .sub{margin-top:3px;font-size:13.5px;color:#6b7280;word-break:keep-all}
  .go{display:inline-block;margin-top:9px;padding:7px 15px;border-radius:9px;
      background:#378ADD;color:#fff;font-size:13.5px;font-weight:700;text-decoration:none}
  .go.ghost{background:#F2F7FD;color:#2b6fb4;border:1px solid #dbe8f6}
  .warn{margin-top:12px;padding:15px 18px;border-left:4px solid #D85A30}
  .warn .title{color:#D85A30}
  .tiles{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(148px,1fr))}
  .tile{padding:16px 15px 15px}
  .tile .k{font-size:12.5px;font-weight:700;color:#8a919c}
  .tile .v{margin-top:5px;font-size:29px;font-weight:800;letter-spacing:-.02em;
           line-height:1.15}
  .tile .u{font-size:14px;font-weight:700;color:#9aa1ad;margin-left:2px}
  .tile .d{margin-top:5px;font-size:12.5px;font-weight:600;color:#8a919c}
  .up{color:#D85A30}
  .down{color:#1D9E75}
  .blue{color:#378ADD}
  .green{color:#1D9E75}
  .orange{color:#D85A30}
  .weak{padding:18px 20px 20px}
  .wrow{margin-top:15px}
  .wrow:first-child{margin-top:0}
  .wtop{display:flex;justify-content:space-between;align-items:baseline;
        font-size:14px;margin-bottom:7px}
  .wname{font-weight:700}
  .wnum{color:#8a919c;font-size:13px;font-weight:700}
  .track{height:9px;background:#F1F3F5;border-radius:999px;overflow:hidden}
  .fill{display:block;height:100%;background:#378ADD;border-radius:999px}
  .fill.f2{background:#6FA9E6;opacity:.92}
  .fill.f3{background:#A8CBF0}
  .empty{padding:18px 20px;color:#8a919c;font-size:13.5px}
  footer{margin-top:26px;padding:0 4px;display:flex;justify-content:space-between;
         gap:10px;flex-wrap:wrap;font-size:12.5px;color:#9aa1ad}
  footer .dday{font-weight:800;color:#D85A30}
  @media (max-width:420px){
    body{padding:20px 12px 44px}
    h1{font-size:24px}
    .tile .v{font-size:26px}
  }
"""


def render_html(ctx):
    out = []
    add = out.append

    add("<!DOCTYPE html>")
    add('<html lang="ko">')
    add("<head>")
    add('<meta charset="utf-8">')
    add('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    add('<meta name="color-scheme" content="light">')
    add("<title>오늘의 복습 · %s</title>" % esc(ctx["today"].isoformat()))
    add("<style>%s</style>" % CSS)
    add("</head>")
    add("<body>")
    add('<div class="wrap">')

    # ── 헤더
    streak = ctx["streak"]
    badge_class = "streak" if streak > 0 else "streak zero"
    add('<header class="head">')
    add('<div class="eyebrow">공인중개사 · 데일리 복습</div>')
    add("<h1>오늘의 복습</h1>")
    add('<div class="headrow">')
    add('<span class="today">%s</span>' % esc(day_label(ctx["today"])))
    add('<span class="%s">🔥 스트릭 %d일</span>' % (badge_class, streak))
    add("</div>")
    add("</header>")

    # ── 오늘의 미션
    add('<h2 class="sect">오늘의 미션</h2>')
    add('<div class="card mission">')

    if ctx["quiz_exists"]:
        if ctx["submitted_today"]:
            add('<div class="row"><span class="mark">✅</span><div class="body">')
            add('<div class="title done">오늘 문제지 제출 완료</div>')
            add('<div class="sub">%s · 채점 결과가 원장에 반영될 예정입니다.</div>'
                % esc(ctx["quiz_name"]))
            add('<a class="go ghost" href="./%s">다시 보기</a>' % esc(ctx["quiz_name"]))
            add("</div></div>")
        else:
            add('<div class="row"><span class="mark">⬜</span><div class="body">')
            add('<div class="title">오늘 문제지 대기 중</div>')
            add('<div class="sub">%s · 15분이면 끝납니다.</div>' % esc(ctx["quiz_name"]))
            add('<a class="go" href="./%s">문제지 열기</a>' % esc(ctx["quiz_name"]))
            add("</div></div>")
    else:
        add('<div class="row"><span class="mark">⬜</span><div class="body">')
        add('<div class="title">오늘 문제지가 아직 없습니다</div>')
        add('<div class="sub">%s 파일이 보이지 않습니다. 아침 생성 예약작업을 확인하세요.</div>'
            % esc(ctx["quiz_name"]))
        add("</div></div>")

    if ctx["ox_count"] is not None:
        add('<div class="row"><span class="mark">✅</span><div class="body">')
        add('<div class="title done">점심 OX %d문 발송됨</div>' % ctx["ox_count"])
        add('<div class="sub">정답은 저녁 카톡으로 도착합니다.</div>')
        add("</div></div>")

    add("</div>")

    if ctx["warn_day"] is not None:
        add('<div class="card warn">')
        add('<div class="row"><span class="mark">⚠️</span><div class="body">')
        add('<div class="title">%s 문제지 미제출</div>' % esc(day_label(ctx["warn_day"])))
        add('<div class="sub">직전 평일 결과가 원장에 들어오지 않았습니다. '
            '오늘 것부터 다시 스트릭을 쌓으세요.</div>')
        add("</div></div>")
        add("</div>")

    # ── 지표 타일
    tiles = ctx["tiles"]
    if tiles:
        add('<h2 class="sect">지표</h2>')
        add('<div class="tiles">')
        for tile in tiles:
            add('<div class="card tile">')
            add('<div class="k">%s</div>' % esc(tile["k"]))
            add('<div class="v %s">%s<span class="u">%s</span></div>'
                % (tile.get("tone", ""), esc(tile["v"]), esc(tile.get("u", ""))))
            add('<div class="d %s">%s</div>' % (tile.get("dtone", ""), esc(tile.get("d", ""))))
            add("</div>")
        add("</div>")

    # ── 과목 약점
    weak = ctx["weakness"]
    if weak:
        add('<h2 class="sect">과목 약점 TOP 3</h2>')
        add('<div class="card weak">')
        top = weak[0][1] or 1
        for index, pair in enumerate(weak):
            subject, count = pair
            width = int(round(100.0 * count / top))
            width = max(6, min(100, width))
            add('<div class="wrow">')
            add('<div class="wtop"><span class="wname">%s</span>'
                '<span class="wnum">%d건</span></div>' % (esc(subject), count))
            add('<div class="track"><span class="fill f%d" style="width:%d%%"></span></div>'
                % (index + 1, width))
            add("</div>")
        add("</div>")

    # ── 푸터
    add("<footer>")
    add("<span>생성 %s</span>" % esc(ctx["generated_at"]))
    dday = ctx["dday"]
    if dday >= 0:
        add('<span><span class="dday">D-%d</span> (%s)</span>' % (dday, esc(EXAM_LABEL)))
    else:
        add('<span><span class="dday">시험 종료</span> (%s)</span>' % esc(EXAM_LABEL))
    add("</footer>")

    add("</div>")
    add("</body>")
    add("</html>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- 조립

def build(paths, today, out_dir):
    quiz_dir = paths["quiz_dir"]
    stamp = today.isoformat()

    # 1) 원장 — 미리 계산된 값만 읽는다
    ledger_path = os.path.join(paths["ledger_dir"], LEDGER_NAME)
    ledger = load_json(ledger_path)
    if not isinstance(ledger, dict):
        ledger = {}
    due_queue = ledger.get("dueQueue")
    due_count = len(due_queue) if isinstance(due_queue, list) else None
    status_counts = ledger.get("statusCounts")
    if not isinstance(status_counts, dict):
        status_counts = {}
    graduated = as_int(status_counts.get("졸업"))
    chronic = as_int(status_counts.get("상습"))

    # 2) 제출 이력·스트릭
    submitted = collect_submission_dates(paths["base"])
    streak = compute_streak(today, submitted)
    submitted_today = stamp in submitted

    warn_day = prev_weekday(today)
    if today.weekday() >= 5 or warn_day.isoformat() in submitted:
        warn_day = None

    # 3) 오늘 문제지·점심 OX
    quiz_name = "%s.html" % stamp
    quiz_exists = os.path.isfile(os.path.join(quiz_dir, quiz_name))
    ox_count = None
    payload = load_json(os.path.join(quiz_dir, "_push", "%s.json" % stamp))
    if isinstance(payload, dict):
        items = payload.get("ox")
        ox_count = len(items) if isinstance(items, list) else 0

    # 4) 장기복습 커버리지
    log_data = load_json(os.path.join(quiz_dir, LONGREV_LOG_NAME))
    served = len(log_data) if isinstance(log_data, dict) else None
    cutoff = today - datetime.timedelta(days=NOTE_AGE_DAYS)
    candidates = count_old_notes(paths["gongin"], cutoff)
    if candidates:
        coverage = int(round(100.0 * (served or 0) / candidates))
    else:
        coverage = None

    # 5) 히스토리(먼저 읽어 7일 전과 비교한 뒤, 오늘 것을 넣어 저장)
    history_path = os.path.join(out_dir, HISTORY_NAME)
    history = load_history(history_path)
    if out_dir != paths["ledger_dir"] and not history:
        # 스테이징 첫 실행: 프로덕션 히스토리를 '읽기만' 해서 화면을 동일하게 맞춘다.
        history = load_history(os.path.join(paths["ledger_dir"], HISTORY_NAME))
    delta = backlog_delta(history, today, due_count)

    # 6) 타일
    tiles = []
    if due_count is not None:
        if delta is None:
            note = "7일 전 기록 없음"
            dtone = ""
        elif delta["diff"] > 0:
            note = "▲ %d (7일 전 %d)" % (delta["diff"], delta["prev"])
            dtone = "up"
        elif delta["diff"] < 0:
            note = "▼ %d (7일 전 %d)" % (-delta["diff"], delta["prev"])
            dtone = "down"
        else:
            note = "변화 없음 (7일 전 %d)" % delta["prev"]
            dtone = ""
        tiles.append({"k": "원장 적체", "v": "%d" % due_count, "u": "건",
                      "tone": "orange" if due_count >= 60 else "", "d": note, "dtone": dtone})
    if graduated is not None:
        tiles.append({"k": "🎓 졸업", "v": "%d" % graduated, "u": "개",
                      "tone": "green", "d": "다시 안 틀린 개념"})
    if chronic is not None:
        tiles.append({"k": "상습", "v": "%d" % chronic, "u": "개",
                      "tone": "orange", "d": "반복해서 틀리는 개념"})
    if candidates is None:
        tiles.append({"k": "장기복습 커버리지", "v": "0", "u": "%",
                      "d": "옛 노트 목록 없음"})
    elif not candidates:
        tiles.append({"k": "장기복습 커버리지", "v": "0", "u": "%",
                      "d": "14일 지난 노트 없음"})
    elif served is None:
        tiles.append({"k": "장기복습 커버리지", "v": "0", "u": "%",
                      "d": "로그 없음 — 내일부터 쌓임"})
    else:
        tiles.append({"k": "장기복습 커버리지", "v": "%d" % coverage, "u": "%",
                      "tone": "blue" if coverage > 0 else "",
                      "d": "%d / %d개 노트" % (served, candidates)})

    context = {
        "today": today,
        "streak": streak,
        "submitted_today": submitted_today,
        "quiz_exists": quiz_exists,
        "quiz_name": quiz_name,
        "ox_count": ox_count,
        "warn_day": warn_day,
        "tiles": tiles,
        "weakness": top_weakness(ledger),
        "dday": (EXAM_DATE - today).days,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    html = render_html(context)

    entry = {
        "date": stamp,
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "streak": streak,
        "submitted": bool(submitted_today),
        "dueCount": due_count,
        "graduated": graduated,
        "chronic": chronic,
        "longRevServed": served,
        "longRevCandidates": candidates,
        "coverage": coverage,
    }
    return html, merge_history(history, entry), {
        "due": due_count, "graduated": graduated, "chronic": chronic,
        "streak": streak, "coverage": coverage, "served": served,
        "candidates": candidates, "quiz": quiz_exists, "ox": ox_count,
        "submitted": submitted_today, "warn": warn_day,
    }


def write_text(path, text):
    try:
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(text)
    except OSError as exc:
        raise BuildError("파일을 저장하지 못했습니다: %s (%s)" % (path, exc))


def run(argv):
    parser = argparse.ArgumentParser(
        prog="build_dashboard.py",
        description="오늘의 복습 퀘스트 보드(정적 HTML) 생성기",
        allow_abbrev=False,
    )
    parser.add_argument("--root", default=None,
                        help="공인중개사 폴더 경로(기본: 스크립트 위치에서 자동 탐지)")
    parser.add_argument("--out", default=None,
                        help="출력 폴더(기본: 데일리퀴즈/, 히스토리는 _ledger/)")
    args = parser.parse_args(argv)

    paths = resolve_paths(args.root)
    if not os.path.isdir(paths["gongin"]):
        raise BuildError("공인중개사 폴더를 찾지 못했습니다: %s" % paths["gongin"])

    if args.out:
        out_dir = os.path.abspath(os.path.expanduser(args.out))
        html_dir = out_dir
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as exc:
            raise BuildError("출력 폴더를 만들지 못했습니다: %s (%s)" % (out_dir, exc))
    else:
        out_dir = paths["ledger_dir"]                # 히스토리는 원장 옆에
        html_dir = paths["quiz_dir"]
        if not os.path.isdir(html_dir):
            raise BuildError("데일리퀴즈 폴더를 찾지 못했습니다: %s" % html_dir)

    today = datetime.date.today()
    html, history, summary = build(paths, today, out_dir)

    html_path = os.path.join(html_dir, DASHBOARD_NAME)
    write_text(html_path, html)
    write_text(os.path.join(out_dir, HISTORY_NAME),
               json.dumps(history, ensure_ascii=False, indent=1) + "\n")

    print("✅ 대시보드 생성: %s" % html_path)
    print("   스트릭 %d일 · 적체 %s · 졸업 %s · 상습 %s · 커버리지 %s%%" % (
        summary["streak"],
        "-" if summary["due"] is None else summary["due"],
        "-" if summary["graduated"] is None else summary["graduated"],
        "-" if summary["chronic"] is None else summary["chronic"],
        0 if summary["coverage"] is None else summary["coverage"],
    ))
    return 0


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        return run(argv)
    except BuildError as exc:
        print("❌ %s" % exc)
        return 1
    except Exception as exc:                          # 스택 대신 읽을 수 있는 한 줄
        print("❌ 대시보드를 만들지 못했습니다: %s: %s" % (type(exc).__name__, exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
