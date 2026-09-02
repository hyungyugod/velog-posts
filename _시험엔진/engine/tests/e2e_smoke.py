#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/tests/e2e_smoke.py — 새 퀴즈 파이프라인 E2E 스모크 하네스 (HG 무한복습체계 v1, 2026-09-02)

  python3 tests/e2e_smoke.py --root /tmp/e2e/velog-posts --exam gongin --kind daily
          [--date YYYY-MM-DD] [--stage allday|S2|S3|seed-ledger] [--seed N]
          [--fail-mode drop-one] [--repeat 2] [--keep]

무엇을 하나 (prepare → questions.json → render → validate 전 경로 관통)
  ① prepare_quiz.py --no-ingest 실행 → plan.json
     (그 날짜 html이 이미 있으면 사본에서 지우고 재실행 — 사본이므로 안전)
  ② plan(쿼터·원천·픽) + exams.json(규격)에 맞춘 **구조적으로 유효한 합성 questions.json**을
     결정론적으로 생성한다. 내용은 더미지만 validate_quiz.js 의 검사를 전부 통과하도록 만든다.
  ③ render_quiz.py 실행(검증 포함) → PASS 확인 → 부수 산출 점검
     (html · _장기복습_로그.json · _push/<date>.json · _시험엔진/_runs.log)
  ④ 최종 html에 validate_quiz.js --json 을 한 번 더 직접 걸어 검사 목록·요약을 받는다.
     (검증기는 --file 의 상위 폴더를 문제지 폴더로 보고 램프업 단계·과거중복을 판정하므로,
      임시본이 어디에 놓이든 최종 파일 기준으로 한 번 더 확인해 두는 편이 안전하다.)

--stage 는 램프업 단계를 재현하기 위한 **사본 전용 픽스처**를 깐다.
  gongin  allday      : 최근 7일 노트를 사본 밖으로 옮겨 신규 0 (→ 장기 40 + 한달전 10)
  bupsa1  S2          : -2차- 없는 신규 노트 3 + 장기 노트 3 (B1·B2·B3)
  bupsa2  S3          : -2차- 장기 노트 3 + 30일 전 데일리 html 1 (→ 신규 12 + 장기 4 + 한달전 4)
  *       seed-ledger : _inbox에 합성 결과 JSON을 넣고 build_ledger.py --ingest 로 원장 생성

프로덕션 보호: --root 가 이 파일이 속한 트리(velog-posts)면 즉시 거부한다.
종료 코드: 0 통과 · 1 실패(어느 단계든) · 2 사용법·환경 오류
"""

import argparse
import datetime as _dt
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import unicodedata
import zlib
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
PROD_ROOT = ENGINE.parents[1]                       # <root>/_시험엔진/engine → <root>
PREPARE = ENGINE / "prepare_quiz.py"
RENDER = ENGINE / "render_quiz.py"
VALIDATE = ENGINE / "validate_quiz.js"
BUILD_LEDGER = ENGINE / "build_ledger.py"

NEG_MARKUP = "<b>옳지 않은</b>"
STASH = "_e2e_stash"

# ─────────────────────────────────────────────── 더미 문장 생성기 (결정론)
#  같은 문항 안에서 보기끼리 2-gram이 겹치지 않아야 한다(해설↔정답 정합 휴리스틱 통과 조건).
#  보기 id(oid)마다 어절 인덱스 구간을 7칸씩 떼어 쓰면 같은 문항 안에서는 절대 겹치지 않는다.
_SYL = list("가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허고노도로모보소오조초코토포호"
            "구누두루무부수우주추쿠투푸후그느드르므브스으즈츠크트프흐")


def _word(i):
    return _SYL[i % len(_SYL)] + _SYL[(i * 13 + 7) % len(_SYL)]


def phrase(oid, nwords=4):
    return " ".join(_word(oid * 7 + j) for j in range(nwords))


def js_round(x):
    """JS Math.round (half-up) — 파이썬 round()는 은행가 반올림이라 경계에서 어긋난다."""
    return int(math.floor(float(x) + 0.5))


def expl_of(correct, oid, extra=""):
    """[정답 근거] {정답 보기 그대로}이다. [메커니즘] …이다. [함정] …이다.
       검사기는 첫 문장('다. ' 앞)과 각 보기의 2-gram Dice를 비교한다."""
    return ("[정답 근거] %s이다. [메커니즘] %s이다. [함정] %s%s이다."
            % (correct, phrase(oid + 5000, 4), phrase(oid + 9000, 4), extra))


# ─────────────────────────────────────────────── 공용 실행 유틸

class Fail(Exception):
    pass


def run(cmd, cwd=None):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def read_json(p, default=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return default


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def questions_of(html_path):
    """문제지 html → QUESTIONS 배열(마커 주석 제거 후 JSON 파싱)."""
    txt = Path(html_path).read_text(encoding="utf-8")
    m = re.search(r"const QUESTIONS = (\[[\s\S]*?\n\]);", txt)
    if not m:
        raise Fail("QUESTIONS 배열을 찾지 못함: %s" % html_path)
    body = (m.group(1).replace("/*__QUESTIONS_START__*/", "")
                      .replace("/*__QUESTIONS_END__*/", ""))
    return json.loads(body)


def say(msg):
    print(msg, flush=True)


# ─────────────────────────────────────────────── 픽스처 (사본 전용)

NOTE_BODY = ("# {title}\n\n"
             "★★ {a}\n"
             "★ {b}\n"
             "- n: {c}\n\n"
             "본문 더미 — E2E 스모크 하네스가 만든 합성 노트다. 실제 학습 내용이 아니다.\n")


def write_note(path, title, oid):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(NOTE_BODY.format(title=title, a=phrase(oid, 5),
                                     b=phrase(oid + 1, 5), c=phrase(oid + 2, 5)),
                    encoding="utf-8")
    return path


def write_quiz_html(path, questions):
    """한달전 블록 원천용 최소 문제지 — prepare 의 QUESTIONS 추출 정규식만 만족하면 된다."""
    body = ",\n".join(json.dumps(q, ensure_ascii=False, indent=1) for q in questions)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "<!DOCTYPE html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
        "<title>E2E 합성 문제지</title></head><body><script>\n"
        "const QUESTIONS = [\n/*__QUESTIONS_START__*/\n%s\n/*__QUESTIONS_END__*/\n];\n"
        "</script></body></html>\n" % body, encoding="utf-8")
    return path


def fixture(root, exam, kind, date, stage, cfg, log):
    """--stage 에 맞는 사본 전용 픽스처를 깐다. 이미 있으면 건드리지 않는다."""
    if not stage:
        return
    ex = cfg["exams"][exam]
    notes_dir = root / ex["notes_dir"]
    d = _dt.date.fromisoformat(date)

    if stage == "allday":
        stash = root / STASH / "gongin_new_notes"
        stash.mkdir(parents=True, exist_ok=True)
        moved = 0
        for p in sorted(notes_dir.iterdir()):
            if not p.is_file() or not re.match(r"^20\d{2}-\d{2}-\d{2}.*\.md$", p.name):
                continue
            nd = _dt.date.fromisoformat(p.name[:10])
            if 0 <= (d - nd).days < 7:
                shutil.move(str(p), str(stash / p.name))
                moved += 1
        log.append("픽스처 allday: 최근 7일 노트 %d개를 %s 로 이동" % (moved, stash))
        return

    if stage == "S2" and exam == "bupsa1":
        made = []
        for k, (age, subj) in enumerate([(1, "민법"), (2, "상법"), (3, "공탁법")]):
            nd = (d - _dt.timedelta(days=age)).isoformat()
            made.append(write_note(notes_dir / ("%s-%s-(E2E 합성 1차 신규 %d).md" % (nd, subj, k)),
                                   "E2E 1차 신규 %s" % subj, 700 + k).name)
        for k, (age, subj) in enumerate([(20, "부동산등기법"), (60, "민사집행법"), (120, "헌법")]):
            nd = (d - _dt.timedelta(days=age)).isoformat()
            made.append(write_note(notes_dir / ("%s-%s-(E2E 합성 1차 장기 %d).md" % (nd, subj, k)),
                                   "E2E 1차 장기 %s" % subj, 730 + k).name)
        log.append("픽스처 S2(bupsa1): 합성 노트 %d개 (%s …)" % (len(made), made[0]))
        return

    if stage == "S3" and exam == "bupsa2":
        made = []
        for k, (age, subj) in enumerate([(23, "민사집행법"), (74, "부동산등기법"), (204, "상업등기법")]):
            nd = (d - _dt.timedelta(days=age)).isoformat()
            made.append(write_note(notes_dir / ("%s-%s-2차-(E2E 합성 2차 장기 %d).md" % (nd, subj, k)),
                                   "E2E 2차 장기 %s" % subj, 760 + k).name)
        mdate = (d - _dt.timedelta(days=30)).isoformat()
        qs = []
        subs = ["결론이유", "요건개수", "판별식"]
        for ci, cat in enumerate(["형법", "민사집행법"]):
            for si, sub in enumerate(subs):
                oid = 800 + ci * 10 + si
                qs.append({"type": "단답", "exam": "2차", "cat": cat, "sub": sub,
                           "q": "E2EM%s-%d%d %s 항목을 기재하시오." % (mdate.replace("-", ""), ci, si, phrase(oid, 3)),
                           "answer": phrase(oid + 1, 8),
                           "keywords": [phrase(oid + 2, 2), phrase(oid + 3, 2)],
                           "expl": "%s이다. 합성 원천이다." % phrase(oid + 4, 5),
                           "src": "%s %s %s" % (mdate, cat, phrase(oid + 5, 2)),
                           "conceptKey": "E2EM-%s-%d-%d" % (mdate, ci, si)})
        p = write_quiz_html(root / ex["dir"] / "데일리퀴즈" / ("%s.html" % mdate), qs)
        made.append(p.name)
        log.append("픽스처 S3(bupsa2): 합성 노트 3개 + 한달전 원천 %s" % p.name)
        return

    if stage == "seed-ledger":
        seed_ledger(root, exam, date, cfg, log)
        return

    if stage == "rebuild-ledger":
        # 상한(exams.json retry.cap)을 바꾸면 원장의 pick 플래그·졸업후보 예약칸이 옛 값이다.
        # 사본에서 원장을 다시 만들어 새 상한을 반영한다(프로덕션은 수거 때 자동으로 갱신).
        rc, out = run([sys.executable, BUILD_LEDGER, "--exam", exam, "--root", root])
        if rc != 0:
            raise Fail("build_ledger 재생성 실패(exit %s):\n%s" % (rc, out[-1500:]))
        led = read_json(led_path(root, exam, cfg), {}) or {}
        due = led.get("dueQueue") or []
        log.append("픽스처 rebuild-ledger(%s): 원장 재생성 · 듀 %d · pick %d · 졸업후보 %d"
                   % (exam, len(due), sum(1 for d in due if d.get("pick") is True),
                      sum(1 for d in due if d.get("status") == "졸업후보")))
        return

    raise Fail("알 수 없는 --stage: %r (exam=%s)" % (stage, exam))


def led_path(root, exam, cfg):
    ex = cfg["exams"][exam]
    paths = cfg.get("_paths") or {}
    return (Path(root) / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답")
            / paths.get("ledger_subdir", "_ledger") / "오답_원장.json")


def retry_contract(root, exam, plan, cfg, log):
    """오답 계약 — 문항 수 = min(exams.json retry.cap, 듀) · 졸업후보 예약칸이 상위 N에 들어왔나."""
    ex = cfg["exams"][exam]
    cap = int((ex.get("retry") or {}).get("cap") or 0)
    due_total = int(plan.get("due_total") or 0)
    exp = min(cap, due_total)
    if int(plan.get("n") or 0) != exp:
        raise Fail("오답 문항 수 %s ≠ min(상한 %d, 듀 %d) = %d"
                   % (plan.get("n"), cap, due_total, exp))
    led = read_json(led_path(root, exam, cfg), {}) or {}
    due = led.get("dueQueue") or []
    slots = int((cfg.get("_fsrs") or {}).get("graduation_slots") or 0)
    n_grad_due = sum(1 for d in due if d.get("status") == "졸업후보")
    k = min(slots, max(1, exp // 4), n_grad_due, exp) if (slots and n_grad_due) else 0
    got = sum(1 for p in (plan.get("picks") or []) if p.get("status") == "졸업후보")
    if got < k:
        raise Fail("졸업후보 예약 %d칸 기대인데 상위 %d문에 %d개뿐" % (k, exp, got))
    log.append("오답 계약: %d문 = min(상한 %d, 듀 %d) · 졸업후보 예약 %d칸(현재 %d · 듀 전체 %d)"
               % (exp, cap, due_total, k, got, n_grad_due))


def seed_ledger(root, exam, date, cfg, log):
    """_inbox 에 합성 결과 JSON을 넣고 build_ledger.py --ingest 로 원장을 만든다."""
    ex = cfg["exams"][exam]
    paths = cfg.get("_paths") or {}
    inbox = (root / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답")
             / paths.get("inbox_dir", "_inbox"))
    inbox.mkdir(parents=True, exist_ok=True)
    d = _dt.date.fromisoformat(date)
    subjects = ["민법", "부동산등기법", "민사집행법", "상법", "공탁법", "헌법"]
    # 3회차 × 10문 = 개념 24종(앞 6종은 2회 이상 오답 → 상습 → 단답 승격 후보)
    concepts = [("E2E-%s-%02d %s 쟁점" % (exam, i, subjects[i % len(subjects)]),
                 subjects[i % len(subjects)]) for i in range(24)]
    rounds = [(d - _dt.timedelta(days=d0)) for d0 in (14, 10, 6)]
    for ri, rd in enumerate(rounds):
        picks = concepts[:6] if ri < 2 else concepts[6:24]
        results = []
        for qi, (ck, subj) in enumerate(picks):
            oid = 4000 + ri * 100 + qi
            results.append({
                "id": "%s-q%d" % (rd.isoformat(), qi + 1),
                "cat": subj, "type": "일반",
                "q": "%s 관련 합성 문항" % ck,
                "options": [phrase(oid + k, 4) for k in range(5)],
                "myAnswer": phrase(oid + 1, 4), "correct": phrase(oid, 4),
                "expl": "합성 해설이다.", "src": "%s %s 합성" % (rd.isoformat(), subj),
                "conceptKey": ck, "correctAnswered": False,
                "missedKeys": ([phrase(oid + 20, 2)] if qi % 2 == 0 else []),
                "errorCause": "혼동"})
        payload = {"schemaVersion": 2, "subject": ex["payload_subject"],
                   "date": rd.isoformat(), "quizId": rd.isoformat(),
                   "score": 50 - len(results), "total": 50, "wrongCount": len(results),
                   "results": results}
        (inbox / ("%s%s.json" % (ex["result_prefix"], rd.isoformat()))).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rc, out = run([sys.executable, BUILD_LEDGER, "--exam", exam, "--ingest", "--root", root])
    if rc not in (0,):
        raise Fail("build_ledger 실패(exit %s):\n%s" % (rc, out[-1500:]))
    led = read_json(root / ex["dir"] / paths.get("ledger_dir", "claude_ox_오답")
                    / paths.get("ledger_subdir", "_ledger") / "오답_원장.json", {}) or {}
    log.append("픽스처 seed-ledger(%s): 결과 JSON 3건 → 원장 듀 큐 %d개"
               % (exam, len(led.get("dueQueue") or [])))


# ─────────────────────────────────────────────── ① prepare

def do_prepare(root, exam, kind, date, cfg, log):
    ex = cfg["exams"][exam]
    qdir = root / ex["dir"] / ("데일리퀴즈" if kind == "daily" else "오답퀴즈")
    out = qdir / ("%s.html" % date)
    if out.exists():
        out.unlink()
        log.append("사본에서 기존 %s 삭제 후 재실행" % out.name)
    rc, txt = run([sys.executable, PREPARE, "--exam", exam, "--kind", kind,
                   "--date", date, "--root", root, "--no-ingest"])
    if rc != 0:
        raise Fail("prepare_quiz.py 실패(exit %s):\n%s" % (rc, txt))
    plan_p = qdir / "_work" / ("%s.plan.json" % date)
    plan = read_json(plan_p)
    if plan is None:
        raise Fail("plan.json을 읽지 못함: %s\n%s" % (plan_p, txt))
    if plan.get("status") != "ready":
        raise Fail("plan.status=%r (ready 아님) — %s\n%s"
                   % (plan.get("status"), plan.get("ai_brief"), txt))
    return plan, plan_p, qdir, txt.strip()


# ─────────────────────────────────────────────── 슬롯(원천 → 문항 자리)

def new_slots(plan, n):
    """신규 문항 자리 — new_sources 를 라운드로빈해 과목이 균등(차이 ≤1)해지도록."""
    srcs = plan.get("new_sources") or []
    if n <= 0:
        return []
    if not srcs:
        raise Fail("plan.new_sources 가 비었는데 신규 쿼터가 %d" % n)
    by_subject = OrderedDict()
    for s in srcs:
        by_subject.setdefault(s["subject"], []).append(s)
    subs = list(by_subject)
    out = []
    for i in range(n):
        subj = subs[i % len(subs)]
        pool = by_subject[subj]
        s = pool[(i // len(subs)) % len(pool)]
        out.append({"subject": subj, "date": s["date"], "source": "new", "note": None})
    return out


def long_slots(plan):
    """장기복습 문항 자리 — longrev_picks[].count 합과 정확히 같은 수."""
    out = []
    for p in plan.get("longrev_picks") or []:
        for _ in range(int(p.get("count") or 0)):
            out.append({"subject": p["subject"], "date": p["date"], "source": "longrev",
                        "note": p["path"]})
    return out


def src_of(slot, oid):
    return "%s %s %s" % (slot["date"], slot["subject"], phrase(oid + 3000, 2))


def uid_of(date, i):
    return "E2E%s-%03d" % (date.replace("-", ""), i)


# ─────────────────────────────────────────────── 문항 빌더

def mcq_options(oid, opts_count):
    """정답 1 + 오답 (opts_count-1). 첫 오답을 길게 만들어 '정답=최장보기'를 피한다."""
    correct = phrase(oid, 4)
    dists = [phrase(oid + k, 6 if k == 1 else 4) for k in range(1, opts_count)]
    return correct, dists


def calc_item(oid, i):
    a, b = 1200 + i * 360, 4
    val = a // b
    correct = "%d만원" % val
    dists = ["%d만원" % (val + 137), "%d만원" % (val + 251), "%d만원 안팎" % (val + 369)]
    return correct, dists, {"expr": "%d/%d" % (a, b), "expected": val}


def combo_items(oid, n_items, n_true):
    """조합형 지문 — 참/거짓 배치는 렌더러가 셔플하므로 개수만 맞춘다."""
    items = []
    for j in range(n_items):
        items.append({"text": phrase(oid + 40 + j, 4), "truth": j < n_true})
    return items


def spread(counts):
    """{유형: 개수} → 같은 유형이 몰리지 않게 라운드로빈으로 편 리스트(결정론).
       같은 유형이 줄줄이 붙으면 OX 3연속 같은 배치 사고가 나기 쉬워, 실제 출제처럼 흩는다."""
    order = sorted(counts, key=lambda t: (-counts[t], t))
    left, out = dict(counts), []
    while any(v > 0 for v in left.values()):
        for t in order:
            if left[t] > 0:
                out.append(t)
                left[t] -= 1
    return out


def ox_pattern(n, n_o):
    """OX n문 중 O를 n_o개 — 같은 답이 연달아 오지 않게 한 칸 걸러 배치."""
    pat, placed = ["X"] * n, 0
    for i in list(range(0, n, 2)) + list(range(1, n, 2)):
        if placed >= n_o:
            break
        pat[i] = "O"
        placed += 1
    return pat


def base_item(typ, slot, uid, cat, oid, date, q_text, extra=None):
    it = {"type": typ, "cat": cat, "source": slot["source"],
          "q": q_text, "src": src_of(slot, oid),
          "conceptKey": "%s-%s" % (uid, phrase(oid + 7000, 1))}
    if slot.get("note"):
        it["note"] = slot["note"]
    if extra:
        it.update(extra)
    return it


# ─────────────────────────────────────────────── ② 합성: 공인중개사 데일리

def synth_gongin_daily(plan, date, cfg, log):
    d = cfg["exams"]["gongin"]["daily"]
    q = plan["quotas"]
    n_new, n_long, n_mon = q["new"], q["longrev"], q["monthly"]
    main = n_new + n_long
    tq = d["type_quota_main40"]
    ox, combo, case = tq["OX"][0], tq["조합"][0], tq["사례"][0]
    sa = min(int(q.get("sa_swap_max") or 0), n_new, tq["단답"][1])
    calc = tq["계산"][0] + 1                                   # 2~4 안쪽
    gen = 24 - calc - sa                                       # 일반+계산+단답 = 24
    if gen + calc + sa + ox + combo + case != main:
        # 본편이 40이 아닌 변형이면 계산형으로 흡수한다(쿼터 계약을 깨지 않는 선에서).
        calc += main - (gen + calc + sa + ox + combo + case)
        if not (tq["계산"][0] <= calc <= tq["계산"][1]):
            raise Fail("본편 %d문에 gongin 유형 쿼터를 맞출 수 없음 (계산 %d)" % (main, calc))

    slots = new_slots(plan, n_new) + long_slots(plan)
    if len(slots) != main:
        raise Fail("슬롯 %d ≠ 본편 쿼터 %d (장기복습 count 합 확인)" % (len(slots), main))

    # 단답은 신규 몫에만(⏪ 치환 금지) → 앞자리 고정, 나머지는 흩는다
    types = ["단답"] * sa + spread({"일반": gen, "계산": calc, "사례": case,
                                    "조합": combo, "OX": ox})
    if len(types) != main:
        raise Fail("유형 배열 %d ≠ 본편 %d" % (len(types), main))

    # 4지 본편 문항 수 = 본편 − OX − 단답 → 부정형 34~52%
    mc_n = main - ox - sa
    nr = d["negative_ratio_mcq"]
    lo, hi = js_round(mc_n * nr[0]), js_round(mc_n * nr[1])
    n_neg = (lo + hi) // 2
    ox_pat = ox_pattern(ox, d["ox_balance"]["O"][1])             # O 3 / X 2, 교대 배치

    qs, neg_used, ox_used, calc_i = [], 0, 0, 0
    for i, (slot, typ) in enumerate(zip(slots, types)):
        uid, oid = uid_of(date, i + 1), 100 + i * 4
        cat, topic = slot["subject"], phrase(oid + 2000, 2)
        if typ == "단답":
            it = base_item(typ, slot, uid, cat, oid, date,
                           "%s %s의 %s에 해당하는 용어를 쓰시오." % (uid, cat, topic),
                           {"answer": phrase(oid + 1, 3),
                            "keywords": [phrase(oid + 2, 2), phrase(oid + 3, 2)],
                            "expl": "[정답 근거] %s이다. [메커니즘] %s이다. [함정] %s이다."
                                    % (phrase(oid + 1, 3), phrase(oid + 11, 4), phrase(oid + 12, 4))})
        elif typ == "OX":
            ans = ox_pat[ox_used]
            ox_used += 1
            it = base_item(typ, slot, uid, cat, oid, date,
                           "%s %s에서 %s는 원칙적으로 인정된다." % (uid, cat, topic),
                           {"answer": ans,
                            "expl": "%s. [정답 근거] %s이다. [메커니즘] %s이다. [함정] %s이다."
                                    % (ans, phrase(oid, 4), phrase(oid + 11, 4), phrase(oid + 12, 4))})
        elif typ == "조합":
            neg = neg_used < n_neg
            neg_used += 1 if neg else 0
            stem = ("%s %s의 %s에 관한 설명으로 옳지 %s 것을 모두 고른 것은?"
                    % (uid, cat, topic, "<b>않은</b>") if neg else
                    "%s %s의 %s에 관한 설명으로 옳은 것을 모두 고른 것은?" % (uid, cat, topic))
            it = base_item(typ, slot, uid, cat, oid, date, stem,
                           {"stem_target": "false" if neg else "true",
                            "items": combo_items(oid, 4, 2),
                            "expl": expl_of(phrase(oid + 60, 4), oid)})
        elif typ == "계산":
            correct, dists, calc_spec = calc_item(oid, calc_i)
            calc_i += 1
            it = base_item(typ, slot, uid, cat, oid, date,
                           "%s %s의 %s 자료로 계산한 값은?" % (uid, cat, topic),
                           {"correct": correct, "distractors": dists, "calc": calc_spec,
                            "expl": expl_of(correct, oid)})
        else:                                                   # 일반 · 사례
            neg = neg_used < n_neg
            neg_used += 1 if neg else 0
            stem = ("%s %s의 %s에 관한 설명으로 %s 것은?" % (uid, cat, topic, NEG_MARKUP) if neg
                    else "%s %s의 %s에 관한 설명으로 옳은 것은?" % (uid, cat, topic))
            if typ == "사례":
                stem = ("%s 갑이 %s에서 %s를 한 사례에 관한 설명으로 %s 것은?"
                        % (uid, cat, topic, NEG_MARKUP if neg else "옳은"))
            correct, dists = mcq_options(oid, d["opts_count"])
            it = base_item(typ, slot, uid, cat, oid, date, stem,
                           {"correct": correct, "distractors": dists,
                            "expl": expl_of(correct, oid)})
        qs.append(it)

    if neg_used != n_neg:
        raise Fail("부정형 %d/%d — 부정형에 쓸 유형이 모자람" % (neg_used, n_neg))

    push_ox = [{"q": "%s 푸시 OX %d — %s" % (uid_of(date, 900 + k), k + 1, phrase(6000 + k, 4)),
                "a": "O" if k < 2 else "X",
                "exp": "%s이다." % phrase(6100 + k, 4)} for k in range(3)]
    doc = {"date": date, "exam": "gongin", "kind": "daily", "questions": qs, "push_ox": push_ox}
    log.append("합성 gongin daily: 본편 %d(신규 %d·장기 %d) + 한달전 %d = %d · "
               "유형 일반%d 계산%d 단답%d 사례%d 조합%d OX%d · 부정형 %d/%d(4지)"
               % (main, n_new, n_long, n_mon, main + n_mon, gen, calc, sa, case, combo, ox,
                  n_neg, mc_n))
    return doc, main + n_mon


# ─────────────────────────────────────────────── ② 합성: 공인중개사 오답

def synth_gongin_retry(plan, date, cfg, log):
    r = cfg["exams"]["gongin"]["retry"]
    picks = plan["picks"]
    sa_idx = [i for i, p in enumerate(picks) if p.get("promote_sa")]
    n_ox = min(3, max(0, len(picks) - len(sa_idx) - 6))
    qs, ox_used = [], 0
    for i, p in enumerate(picks):
        uid, oid = uid_of(date, i + 1), 2000 + i * 4
        cat, topic = p.get("subject") or "기타", phrase(oid + 2000, 2)
        slot = {"subject": cat, "date": date, "source": None, "note": None}
        common = {"cat": cat, "conceptKey": p["conceptKey"],
                  "src": "%s %s %s" % (date, cat, topic)}
        if i in sa_idx:
            mt = [k for k in (p.get("missedTop") or [])
                  if k != "결론·방향 자체" and not str(k).startswith("기타:")]
            kws = (mt[:2] + [phrase(oid + 2, 2), phrase(oid + 3, 2)])[:4]
            kws = kws if len(kws) >= 2 else kws + [phrase(oid + 4, 2)]
            qs.append(dict(common, type="단답",
                           q="%s %s의 %s를 쓰시오." % (uid, cat, topic),
                           answer=phrase(oid + 1, 3), keywords=kws,
                           expl="[정답 근거] %s이다. [메커니즘] %s이다. [함정] %s이다."
                                % (phrase(oid + 1, 3), phrase(oid + 11, 4), phrase(oid + 12, 4))))
        elif ox_used < n_ox:
            ans = "O" if ox_used % 2 == 0 else "X"
            ox_used += 1
            qs.append(dict(common, type="OX",
                           q="%s %s에서 %s는 인정된다." % (uid, cat, topic), answer=ans,
                           expl="%s. [정답 근거] %s이다. [메커니즘] %s이다. [함정] %s이다."
                                % (ans, phrase(oid, 4), phrase(oid + 11, 4), phrase(oid + 12, 4))))
        else:
            typ = "사례" if i % 4 == 3 else "일반"
            neg = (i % 3 != 2)
            stem = ("%s %s의 %s에 관한 설명으로 %s 것은?"
                    % (uid, cat, topic, NEG_MARKUP if neg else "옳은"))
            correct, dists = mcq_options(oid, r["opts_count"])
            qs.append(dict(common, type=typ, q=stem, correct=correct, distractors=dists,
                           expl=expl_of(correct, oid)))
    doc = {"date": date, "exam": "gongin", "kind": "retry", "questions": qs}
    log.append("합성 gongin retry: %d문 (단답 승격 %d · OX %d · 객관식 %d)"
               % (len(qs), len(sa_idx), ox_used, len(qs) - len(sa_idx) - ox_used))
    return doc, len(qs)


# ─────────────────────────────────────────────── ② 합성: 법무사 1차

def synth_bupsa1_daily(plan, date, cfg, log):
    d = cfg["exams"]["bupsa1"]["daily"]
    q = plan["quotas"]
    n_new, n_long, n_mon = q["new"], q["longrev"], q["monthly"]
    main = n_new + n_long
    sa = min(int(q.get("sa_swap_max") or 0), n_new)
    combo, cnt, prec, case = 4, 1, 6, 5
    gen = main - sa - combo - cnt - prec - case
    if gen < 0:
        combo, cnt, prec, case = 2, 0, 2, 2
        gen = main - sa - combo - cnt - prec - case
    if gen < 0:
        raise Fail("본편 %d문에 bupsa1 유형을 못 채움" % main)

    slots = new_slots(plan, n_new) + long_slots(plan)
    if len(slots) != main:
        raise Fail("슬롯 %d ≠ 본편 %d" % (len(slots), main))
    types = ["단답"] * sa + spread({"일반": gen, "판례": prec, "사례": case,
                                    "조합": combo, "개수": cnt})

    mc_n = main - sa
    nr, rnd = d["negative_ratio_mcq"], d["negative_ratio_round"]
    lo = getattr(math, rnd[0])(mc_n * nr[0])
    hi = getattr(math, rnd[1])(mc_n * nr[1])
    n_neg = min(int((lo + hi) // 2), gen + prec + case)
    if n_neg < lo:
        raise Fail("부정형 하한 %d을 채울 유형이 부족" % lo)

    qs, neg_used = [], 0
    for i, (slot, typ) in enumerate(zip(slots, types)):
        uid, oid = uid_of(date, i + 1), 3000 + i * 4
        cat, topic = slot["subject"], phrase(oid + 2000, 2)
        if typ == "단답":
            qs.append(base_item(typ, slot, uid, cat, oid, date,
                                "%s %s의 %s를 쓰시오." % (uid, cat, topic),
                                {"exam": "1차", "answer": phrase(oid + 1, 3),
                                 "keywords": [phrase(oid + 2, 2), phrase(oid + 3, 2)],
                                 "expl": "[정답 근거] %s이다. [메커니즘] %s이다. [함정] %s이다."
                                         % (phrase(oid + 1, 3), phrase(oid + 11, 4), phrase(oid + 12, 4))}))
            continue
        if typ == "조합":
            stem = "%s %s의 %s에 관한 설명 중 옳은 것을 모두 고른 것은?" % (uid, cat, topic)
            qs.append(base_item(typ, slot, uid, cat, oid, date, stem,
                                {"exam": "1차", "stem_target": "true",
                                 "items": combo_items(oid, 5, 3),
                                 "expl": expl_of(phrase(oid + 60, 4), oid)}))
            continue
        if typ == "개수":
            correct, dists = "2개", ["1개", "3개", "4개", "5개 이상"]
            stem = "%s %s의 %s에 해당하는 것은 모두 몇 개인가?" % (uid, cat, topic)
            qs.append(base_item(typ, slot, uid, cat, oid, date, stem,
                                {"exam": "1차", "correct": correct, "distractors": dists,
                                 "expl": expl_of(correct, oid)}))
            continue
        neg = neg_used < n_neg
        neg_used += 1 if neg else 0
        # bupsa1 은 발문 화이트리스트(stem_whitelist_regex)가 상투구를 통째로 본다 →
        # 부정형에 <b> 태그를 끼우면 "가장 옳지 않은 것은" 이 끊겨 검사에 걸린다(평문 유지).
        stem = ("%s %s의 %s에 관한 다음 설명 중 가장 옳지 않은 것은?" % (uid, cat, topic) if neg
                else "%s %s의 %s에 관한 다음 설명 중 가장 옳은 것은?" % (uid, cat, topic))
        correct, dists = mcq_options(oid, d["opts_count"])
        extra = {"exam": "1차", "correct": correct, "distractors": dists,
                 "expl": expl_of(correct, oid, extra=(" 결론을 가른 변수는 %s" % phrase(oid + 70, 2))
                                 if typ == "판례" else "")}
        qs.append(base_item(typ, slot, uid, cat, oid, date, stem, extra))

    doc = {"date": date, "exam": "bupsa1", "kind": "daily", "questions": qs}
    log.append("합성 bupsa1 daily(%s): 본편 %d(신규 %d·장기 %d)+한달전 %d · "
               "일반%d 판례%d 사례%d 조합%d 개수%d 단답%d · 부정형 %d/%d(5지)"
               % (plan.get("stage"), main, n_new, n_long, n_mon, gen, prec, case,
                  combo, cnt, sa, n_neg, mc_n))
    return doc, main + n_mon


def synth_bupsa1_retry(plan, date, cfg, log):
    r = cfg["exams"]["bupsa1"]["retry"]
    picks = plan["picks"]
    sa_idx = [i for i, p in enumerate(picks) if p.get("promote_sa")]
    qs = []
    for i, p in enumerate(picks):
        uid, oid = uid_of(date, i + 1), 3500 + i * 4
        cat, topic = p.get("subject") or "기타", phrase(oid + 2000, 2)
        common = {"cat": cat, "exam": "1차", "conceptKey": p["conceptKey"],
                  "src": "%s %s %s" % (date, cat, topic)}
        if i in sa_idx:
            mt = [k for k in (p.get("missedTop") or [])
                  if k != "결론·방향 자체" and not str(k).startswith("기타:")]
            kws = (mt[:2] + [phrase(oid + 2, 2), phrase(oid + 3, 2)])[:4]
            qs.append(dict(common, type="단답",
                           q="%s %s의 %s를 쓰시오." % (uid, cat, topic),
                           answer=phrase(oid + 1, 3), keywords=kws,
                           expl="[정답 근거] %s이다. [메커니즘] %s이다. [함정] %s이다."
                                % (phrase(oid + 1, 3), phrase(oid + 11, 4), phrase(oid + 12, 4))))
        else:
            typ = "판례" if i % 3 == 1 else ("사례" if i % 3 == 2 else "일반")
            neg = (i % 4 != 3)
            stem = ("%s %s의 %s에 관한 다음 설명 중 가장 옳지 않은 것은?" % (uid, cat, topic)
                    if neg else "%s %s의 %s에 관한 다음 설명 중 가장 옳은 것은?" % (uid, cat, topic))
            correct, dists = mcq_options(oid, r["opts_count"])
            qs.append(dict(common, type=typ, q=stem, correct=correct, distractors=dists,
                           expl=expl_of(correct, oid,
                                        extra=(" 결론을 가른 변수는 %s" % phrase(oid + 70, 2))
                                        if typ == "판례" else "")))
    doc = {"date": date, "exam": "bupsa1", "kind": "retry", "questions": qs}
    log.append("합성 bupsa1 retry: %d문 (단답 승격 %d · 5지 객관식 %d)"
               % (len(qs), len(sa_idx), len(qs) - len(sa_idx)))
    return doc, len(qs)


# ─────────────────────────────────────────────── ② 합성: 법무사 2차

def mini_answer(oid):
    """미니답안 골격 — <br> 문단 3개 · 150~500자."""
    p1 = "결론은 %s이다." % phrase(oid, 6)
    p2 = "논거는 %s에 있다. 그 근거로 %s를 든다." % (phrase(oid + 1, 8), phrase(oid + 2, 8))
    p3 = "따라서 사안에서는 %s로 귀결된다." % phrase(oid + 3, 8)
    ans = "<br>".join([p1, p2, p3])
    while len(ans) < 165:
        ans += " 부연하면 %s이다." % phrase(oid + 4, 6)
    return ans[:480]


def sa_body(oid, sub, cat, topic, uid, mini=False):
    if mini:
        return {"sub": "미니답안",
                "q": "%s 갑과 을 사이의 %s 사안에서 %s에 관한 결론과 이유를 기재하시오. (10점)"
                     % (uid, cat, topic),
                "answer": mini_answer(oid),
                "keywords": [phrase(oid + 2, 2), phrase(oid + 3, 2), phrase(oid + 4, 2)],
                "expl": "%s이다. %s이다." % (phrase(oid + 11, 5), phrase(oid + 12, 5))}
    return {"sub": sub,
            "q": "%s %s의 %s에 관하여 서술하시오." % (uid, cat, topic),
            "answer": "%s라 할 것이다." % phrase(oid + 1, 10),
            "keywords": [phrase(oid + 2, 2), phrase(oid + 3, 2)],
            "expl": "%s이다. %s이다." % (phrase(oid + 11, 5), phrase(oid + 12, 5))}


def synth_bupsa2_daily(plan, date, cfg, log):
    d = cfg["exams"]["bupsa2"]["daily"]
    q = plan["quotas"]
    n_new, n_long, n_mon, mini = q["new"], q["longrev"], q["monthly"], q["mini"]
    main = n_new + n_long
    slots = new_slots(plan, n_new) + long_slots(plan)
    if len(slots) != main:
        raise Fail("슬롯 %d ≠ 본편 %d" % (len(slots), main))
    subs = [s for s in d["sub_types"] if s != "미니답안"]

    qs = []
    for i, slot in enumerate(slots):
        uid, oid = uid_of(date, i + 1), 5000 + i * 4
        cat, topic = slot["subject"], phrase(oid + 2000, 2)
        is_mini = i < mini
        body = sa_body(oid, subs[i % len(subs)], cat, topic, uid, mini=is_mini)
        qs.append(base_item("단답", slot, uid, cat, oid, date, body.pop("q"),
                            dict(body, exam="2차")))
    doc = {"date": date, "exam": "bupsa2", "kind": "daily", "questions": qs}
    log.append("합성 bupsa2 daily(%s): 본편 %d(신규 %d·장기 %d)+한달전 %d · 미니답안 %d · sub %d종"
               % (plan.get("stage"), main, n_new, n_long, n_mon, mini,
                  len({x["sub"] for x in qs})))
    return doc, main + n_mon


def synth_bupsa2_retry(plan, date, cfg, log):
    d = cfg["exams"]["bupsa2"]["daily"]
    picks = plan["picks"]
    subs = [s for s in d["sub_types"] if s != "미니답안"]
    qs = []
    for i, p in enumerate(picks):
        uid, oid = uid_of(date, i + 1), 5500 + i * 4
        cat, topic = p.get("subject") or "기타", phrase(oid + 2000, 2)
        body = sa_body(oid, subs[i % len(subs)], cat, topic, uid, mini=(i == 0))
        it = {"type": "단답", "exam": "2차", "cat": cat, "conceptKey": p["conceptKey"],
              "src": "%s %s %s" % (date, cat, topic)}
        it.update(body)
        qs.append(it)
    doc = {"date": date, "exam": "bupsa2", "kind": "retry", "questions": qs}
    log.append("합성 bupsa2 retry: %d문 전부 단답 (미니답안 1 · sub %d종)"
               % (len(qs), len({x["sub"] for x in qs})))
    return doc, len(qs)


SYNTH = {("gongin", "daily"): synth_gongin_daily, ("gongin", "retry"): synth_gongin_retry,
         ("bupsa1", "daily"): synth_bupsa1_daily, ("bupsa1", "retry"): synth_bupsa1_retry,
         ("bupsa2", "daily"): synth_bupsa2_daily, ("bupsa2", "retry"): synth_bupsa2_retry}


# ────────────────────────────── evidence(노트 원문 인용) 부착 · 파괴
#  render_quiz.py 의 환각 게이트를 실제로 통과·실패시키는 경로. 합성 문항이 지어낸 문장을
#  쓰지 않도록, 데일리 단답은 **원천 노트의 실제 줄**을, 재도전 단답은 **samples 의 q/expl**을
#  그대로 인용한다(렌더의 정규화 규칙과 같은 방식으로 대조된다).

BAD_QUOTE = "E2E 환각 인용 — 이 문장은 원천 노트에도 samples 에도 존재하지 않는다"


def ev_norm(s):
    s = re.sub(r"<[^>]*>", " ", str(s or "")).lower()
    return "".join(ch for ch in s if unicodedata.category(ch)[0] not in "PSZC")


def note_quote(path, seed=0):
    """노트 원문에서 길이 15~120자짜리 줄 하나를 고른다(120자 초과면 앞 100자로 자른다)."""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    cands = []
    for ln in text.splitlines():
        s = ln.strip()
        if len(s) < 15:
            continue
        s = s[:100]
        if len(ev_norm(s)) >= 10:
            cands.append(s)
    if not cands:                       # 줄이 전부 짧으면 이어 붙인 본문의 앞 100자(공백은 정규화에서 사라짐)
        joined = " ".join(x.strip() for x in text.splitlines() if x.strip())
        if len(ev_norm(joined)) >= 10 and len(joined) >= 15:
            cands = [joined[:100]]
    return cands[seed % len(cands)] if cands else None


def _daily_note_for(plan, item):
    """단답 문항의 원천 노트 경로 — longrev 는 note, 신규는 같은 과목의 new_source."""
    if item.get("note"):
        return item["note"]
    srcs = plan.get("new_sources") or []
    same = [s for s in srcs if s.get("subject") == item.get("cat")]
    pool = same or srcs
    return pool[0]["path"] if pool else None


def attach_evidence(doc, plan, kind, log):
    """합성 단답 문항에 evidence{note, quote} 를 실제 원천에서 뽑아 붙인다."""
    n_note, n_smp, miss = 0, 0, []
    picks = {p.get("conceptKey"): p for p in (plan.get("picks") or [])}
    for i, q in enumerate(doc["questions"]):
        if q.get("type") != "단답":
            continue
        if kind == "retry":
            pk = picks.get(q.get("conceptKey")) or {}
            texts = []
            for s in (pk.get("samples") or []):
                if isinstance(s, dict):
                    texts += [s.get("q"), s.get("expl")]
                else:
                    texts.append(s)
            quote = None
            for t0 in texts:
                t0 = str(t0 or "").strip()
                if len(t0) >= 15 and len(ev_norm(t0)) >= 10:
                    quote = t0[:100]
                    break
            if quote:
                q["evidence"] = {"note": "samples", "quote": quote}
                n_smp += 1
            else:
                miss.append("q[%d] samples 인용 불가(짧거나 없음)" % i)
            continue
        p = _daily_note_for(plan, q)
        quote = note_quote(p, i) if p else None
        if not quote:
            raise Fail("evidence 원천 인용 실패 — q[%d] 노트 %r 에서 15자 이상인 줄을 못 찾음" % (i, p))
        q["evidence"] = {"note": p, "quote": quote}
        n_note += 1
    log.append("evidence 부착: 노트 인용 %d · samples 인용 %d%s"
               % (n_note, n_smp, (" · 생략 %d(%s)" % (len(miss), miss[0])) if miss else ""))


def break_evidence(doc, plan, kind, log):
    """--fail-mode bad-evidence — 첫 단답의 quote 를 원천에 없는 문장으로 바꾼다."""
    for i, q in enumerate(doc["questions"]):
        if q.get("type") != "단답":
            continue
        note = (q.get("evidence") or {}).get("note")
        if not note:
            note = "samples" if kind == "retry" else _daily_note_for(plan, q)
        q["evidence"] = {"note": note, "quote": BAD_QUOTE}
        log.append("⚠ fail-mode=bad-evidence — q[%d] evidence.quote 를 원천에 없는 문장으로 교체 "
                   "(note=%s)" % (i, Path(str(note)).name))
        return
    raise Fail("bad-evidence 를 걸 단답 문항이 없다 (이 케이스는 단답이 있는 조합에서만 쓴다)")


# ─────────────────────────────────────────────── 자체 위생검사(렌더 전)

BAD_CHARS = re.compile(r"[`\"]")


def selfcheck(doc, exam, kind, cfg, log):
    bad = []
    for i, q in enumerate(doc["questions"]):
        for k, v in q.items():
            if isinstance(v, str) and BAD_CHARS.search(v):
                bad.append("q[%d].%s 에 큰따옴표/백틱" % (i, k))
    seen = Counter(q.get("conceptKey") for q in doc["questions"])
    dup = [k for k, n in seen.items() if n > 1]
    if dup:
        bad.append("conceptKey 중복: %s" % dup[:3])
    heads = Counter(re.sub(r"<[^>]+>|\s", "", str(q.get("q")))[:30] for q in doc["questions"])
    dup2 = [k for k, n in heads.items() if n > 1]
    if dup2:
        bad.append("문제문 앞 30자 중복: %s" % dup2[:3])
    if bad:
        raise Fail("합성 위생검사 실패:\n  - " + "\n  - ".join(bad))
    log.append("위생검사 OK (큰따옴표·백틱 0 · conceptKey 고유 · 앞 30자 고유)")


# ─────────────────────────────────────────────── ③ render + ④ validate

def do_render(root, exam, kind, date, qdir, ques_p, seed, out=None):
    cmd = [sys.executable, RENDER, "--exam", exam, "--kind", kind, "--date", date,
           "--root", root, "--questions", ques_p, "--seed", seed]
    if out:
        cmd += ["--out", out]
    return run(cmd)


def do_validate(root, exam, kind, date, html):
    rc, txt = run(["node", VALIDATE, "--exam", exam, "--kind", kind,
                   "--file", html, "--date", date, "--root", root, "--json"])
    try:
        return rc, json.loads(txt)
    except Exception:                                          # noqa: BLE001
        return rc, {"pass": False, "checks": [], "summary": {"raw": txt[-1200:]}}


def side_effects(root, exam, kind, date, qdir, plan, log):
    """부수 산출 점검 — _장기복습_로그 · _push · _runs.log"""
    got = {}
    lr_log = qdir / "_장기복습_로그.json"
    picks = plan.get("longrev_picks") or []
    if kind == "daily" and picks:
        log_j = read_json(lr_log, {}) or {}
        miss = [Path(p["path"]).name for p in picks
                if (log_j.get(Path(p["path"]).name) or {}).get("last") != date]
        if miss:
            raise Fail("_장기복습_로그 갱신 누락: %s" % miss[:3])
        got["장기복습로그"] = "%d노트 last=%s" % (len(picks), date)
    push = qdir / "_push" / ("%s.json" % date)
    if exam == "gongin" and kind == "daily":
        pj = read_json(push)
        if pj is None:
            raise Fail("_push/%s.json 미생성" % date)
        ox = pj.get("ox") or []
        o_n = sum(1 for x in ox if x.get("a") == "O")
        if len(ox) != 3 or not (1 <= o_n <= 2):
            raise Fail("_push ox 계약 위반: %d문 · O %d" % (len(ox), o_n))
        got["push"] = "counts=%s · ox %d(O %d) · dueBacklog %s" % (
            pj.get("counts"), len(ox), o_n, pj.get("dueBacklog"))
    runs = root / "_시험엔진" / "_runs.log"
    lines = [l for l in runs.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if runs.exists() else []
    tail = [l for l in lines if ("\t%s\t%s\t" % (exam, kind)) in l]
    if not tail:
        raise Fail("_runs.log 에 %s %s 기록 없음" % (exam, kind))
    got["runs.log"] = tail[-1].split("\t", 3)[-1][:90]
    log.append("부수 산출: " + " | ".join("%s=%s" % kv for kv in got.items()))
    return got


# ─────────────────────────────────────────────── main

def main(argv=None):
    ap = argparse.ArgumentParser(description="퀴즈 파이프라인 E2E 스모크 하네스")
    ap.add_argument("--root", required=True, help="프로덕션 **복사본** 루트 (예: /tmp/e2e/velog-posts)")
    ap.add_argument("--exam", required=True, choices=["gongin", "bupsa1", "bupsa2"])
    ap.add_argument("--kind", required=True, choices=["daily", "retry"])
    ap.add_argument("--date")
    ap.add_argument("--stage", help="allday | S2 | S3 | seed-ledger | rebuild-ledger (사본 전용 픽스처)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--fail-mode", choices=["drop-one", "bad-evidence"],
                    help="일부러 깨서 FAIL 경로를 확인 (drop-one=문항 1개 제거 · "
                         "bad-evidence=단답 evidence.quote 를 원천에 없는 문장으로)")
    ap.add_argument("--repeat", type=int, default=1, help="2면 같은 시드로 재렌더 후 바이트 비교")
    ap.add_argument("--keep", action="store_true", help="_work 임시 산출물을 지우지 않는다")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    if root == PROD_ROOT.resolve():
        say("❌ --root 가 프로덕션 트리(%s)다. 복사본을 지정하라." % PROD_ROOT)
        return 2
    if not root.is_dir():
        say("❌ --root 없음: %s" % root)
        return 2
    for p in (PREPARE, RENDER, VALIDATE):
        if not p.exists():
            say("❌ 엔진 파일 없음: %s" % p)
            return 2

    date = a.date or _dt.date.today().isoformat()
    cfg = json.loads((ENGINE / "exams.json").read_text(encoding="utf-8"))
    seed = a.seed if a.seed is not None else \
        zlib.crc32(("e2e|%s|%s|%s" % (a.exam, a.kind, date)).encode())
    log, t0 = [], _dt.datetime.now()
    tag = "%s %s %s%s" % (a.exam, a.kind, date, (" [%s]" % a.stage) if a.stage else "")

    try:
        fixture(root, a.exam, a.kind, date, a.stage, cfg, log)
        plan, plan_p, qdir, prep_out = do_prepare(root, a.exam, a.kind, date, cfg, log)
        log.append("prepare: " + prep_out.splitlines()[0].strip())
        if a.kind == "retry":
            retry_contract(root, a.exam, plan, cfg, log)

        doc, expect_n = SYNTH[(a.exam, a.kind)](plan, date, cfg, log)
        selfcheck(doc, a.exam, a.kind, cfg, log)
        attach_evidence(doc, plan, a.kind, log)
        if a.fail_mode == "drop-one":
            doc["questions"] = doc["questions"][:-1]
            expect_n -= 1
            log.append("⚠ fail-mode=drop-one — 문항 1개 제거(검증 실패를 유도)")
        elif a.fail_mode == "bad-evidence":
            break_evidence(doc, plan, a.kind, log)

        ques_p = qdir / "_work" / ("%s.questions.json" % date)
        ques_p.parent.mkdir(parents=True, exist_ok=True)
        ques_p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        out_html = qdir / ("%s.html" % date)
        rc, rtxt = do_render(root, a.exam, a.kind, date, qdir, ques_p, seed)

        # ── FAIL 경로 검증
        if a.fail_mode:
            draft = qdir / "_work" / ("%s.draft.html" % date)
            probs = []
            if rc == 0:
                probs.append("render가 exit 0 (실패해야 정상)")
            if not draft.exists():
                probs.append("_work/%s.draft.html 미생성" % date)
            if out_html.exists():
                probs.append("최종 html이 생성됨 (미생성이어야 정상)")
            runs = root / "_시험엔진" / "_runs.log"
            last = [l for l in runs.read_text(encoding="utf-8").splitlines() if l.strip()][-1] \
                if runs.exists() else ""
            if "\tFAIL\t" not in last:
                probs.append("_runs.log 마지막 줄에 FAIL 없음: %r" % last[:80])
            if a.fail_mode == "bad-evidence" and "evidence" not in rtxt:
                probs.append("실패 사유가 evidence 게이트가 아님 — stderr: %r" % rtxt[-200:])
            if probs:
                raise Fail("실패 경로 계약 위반:\n  - " + "\n  - ".join(probs))
            say("\n".join("· " + l for l in log))
            say("✅ [FAIL 경로] %s — exit %d · draft %s · 최종 html 미생성 · _runs.log FAIL 기록"
                % (tag, rc, draft.name))
            say("   render stderr 첫 줄: %s" % (rtxt.strip().splitlines() or [""])[0][:160])
            return 0

        if rc != 0:
            raise Fail("render_quiz.py 실패(exit %s):\n%s" % (rc, rtxt[-2500:]))
        if not out_html.exists():
            raise Fail("최종 html 미생성: %s" % out_html)

        # ── ④ 최종 파일 재검증 (past_dup 포함 — 렌더 중 검증은 _work 기준이라 못 본다)
        vrc, vj = do_validate(root, a.exam, a.kind, date, out_html)
        fails = [c for c in (vj.get("checks") or []) if not c.get("ok")]
        if vrc != 0 or not vj.get("pass"):
            raise Fail("최종 html validate FAIL (%d건):\n  - %s"
                       % (len(fails), "\n  - ".join("%s: %s" % (c["id"], c["msg"])
                                                    for c in fails[:12])))
        html_q = questions_of(out_html)
        if len(html_q) != expect_n:
            raise Fail("html 문항 수 %d ≠ 기대 %d" % (len(html_q), expect_n))

        side = side_effects(root, a.exam, a.kind, date, qdir, plan, log)

        # ── 결정론
        det = "-"
        if a.repeat > 1:
            # 재렌더 산출도 문제지 폴더에 둔다(검증기가 같은 폴더를 보게) — 파일명은 최종과 다르게
            re_out = qdir / ("%s.rerender.html" % date)
            h0 = sha(out_html)
            for _ in range(a.repeat - 1):
                rc2, t2 = do_render(root, a.exam, a.kind, date, qdir, ques_p, seed, out=re_out)
                if rc2 != 0:
                    raise Fail("재렌더 실패(exit %s):\n%s" % (rc2, t2[-1200:]))
                if sha(re_out) != h0:
                    raise Fail("결정론 위반 — 같은 시드인데 바이트가 다르다 (%s ≠ %s)"
                               % (h0, sha(re_out)))
            det = "동일(sha16 %s, %d회)" % (h0, a.repeat)
            if not a.keep:
                re_out.unlink(missing_ok=True)
            log.append("결정론: 같은 시드 %d회 재렌더 → html 바이트 %s" % (a.repeat, det))

        # ── 요약
        summ = vj.get("summary") or {}
        cats = Counter(q.get("cat") for q in html_q)
        types = Counter(q.get("type") for q in html_q)
        say("\n".join("· " + l for l in log))
        say("✅ [PASS] %s" % tag)
        say("   문항 %d (기대 %d) · 유형 %s" % (len(html_q), expect_n, dict(types)))
        say("   과목 %s" % dict(cats))
        say("   validate: %d검사 전부 PASS · %s"
            % (len(vj.get("checks") or []),
               " ".join("%s=%s" % (k, summ[k]) for k in
                        ("stage", "expected", "main", "monthly", "longrev", "sa", "dueLen", "dueRest")
                        if k in summ and summ[k] is not None)))
        say("   산출: %s · %s" % (out_html, " · ".join("%s(%s)" % kv for kv in side.items())))
        say("   결정론: %s · 시드 %d · %.1fs" % (det, seed, (_dt.datetime.now() - t0).total_seconds()))
        if not a.keep:
            (qdir / "_work" / ("%s.draft.html" % date)).unlink(missing_ok=True)
        return 0

    except Fail as e:
        say("\n".join("· " + l for l in log))
        say("❌ [FAIL] %s\n%s" % (tag, e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
