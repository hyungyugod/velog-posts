#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오답 누적 원장 빌더 v3.1 [법무사판] — 닫힌 루프(상태머신) + FSRS-6 스케줄링 + 과목 별칭 정규화 · 2026-08-20

공인중개사판 build_ledger.py(v3.1)를 법무사로 이식한 것이다. 바뀐 것은 딱 두 축이다:
  ① RESULT_GLOB(수거할 결과 JSON 파일명 패턴)  ② SUBJECT_ALIAS(과목 별칭 표)
FSRS 리플레이·상태머신·듀 큐 선정/정렬·중복 파일 제거는 원본과 바이트 단위로 동일하다.

v3 → v3.1에서 달라진 것 — **과목명 표기 통일만** 바뀌었다:
- 같은 과목이 회차마다 다른 이름으로 들어와 따로 집계되던 문제를 고쳤다.
  (예: "민집" / "민사집행법", "부등" / "부동산등기법"처럼 축약형과 정식 명칭이 갈리면
   각각 별개 과목으로 잡혀 과목별 약점 표에서 실제 비중이 과소평가된다.)
- SUBJECT_ALIAS 표를 두고 이벤트 생성 시점에 subject(= 결과 JSON의 `cat`)를 대표명으로 접는다.
  레코드의 `subject` 필드와 `subjectWeakness` 집계가 같은 값에서 갈라져 나오므로 양쪽이
  자동으로 일관된다(듀 큐의 `subject`도 같은 레코드에서 오므로 함께 정규화된다).
- **conceptKey/label(concept·aliases)은 절대 건드리지 않는다.** 원장 매칭 키이자
  소비자(데일리퀴즈)가 재도전 문항을 되찾는 유일한 열쇠라서, 개념 병합은 일어나지 않는다.
  → uniqueConcepts·statusCounts·dueQueue 구성은 정의상 불변이다.

v3에서 v2와 달라진 것 — **스케줄링만** 바뀌었다:
- 고정 간격 사다리 [3, 7, 16, 35]일을 버리고 **FSRS-6**(py-fsrs 6.3.2 벤더링본)로
  개념별 기억 모델(stability/difficulty)을 추정해 nextReviewDate를 발급한다.
- 개념별 오답/재도전정답 이벤트를 시간순으로 FSRS에 리플레이한다.
    오답(w) → Rating.Again · 재도전 정답(c) → Rating.Good
- 레코드에 fsrs{stability,difficulty,due,state,reps,lapses,retrievability}가 붙는다.
- 듀 큐 정렬이 '상태 우선순위 → 망각위험(retrievability) 오름차순'으로 바뀐다.
  즉 같은 상습이면 **가장 많이 잊어버린 것부터** 나온다.
- 사다리는 폴백으로만 남는다(FSRS 실패 개념 한정).

v2에서 **그대로 유지**한 것:
- §1 이벤트 추출(파일 → 이벤트 스트림), --ingest, v1 하위호환
- 비파괴(어떤 파일도 삭제·이동 안 함) · 멱등(매번 전체 재생성) ·
  무음실패 불가(원천 0건이면 exit 2로 크게 알림)
- 상태머신(상습/재도전중/졸업후보/졸업) 판정 규칙 — 한 글자도 안 건드렸다
- dueQueue 선정 규칙(졸업 제외 · nextReviewDate ≤ 오늘)과 기존 8개 필드
- ledger[].dates / ledger[].samples / statusCounts 등 소비자 계약 필드
- (2026-09-01 추가) ledger[].missedKeys{포인트:횟수} · samples[].missedKeys/fixTyped ·
  dueQueue[].missedTop[≤3] — 단답 자가채점에서 고른 '놓친 채점 포인트'. 재도전 출제의 조준점.
- (2026-09-01 추가) ledger[].errorCauses{원인:횟수} · samples[].errorCause/causeNote · dueQueue[].causeTop — 객관식 오답 원인 진단. 재출제 각도·Anki 편입 라우팅의 원천.

사용:  python3 build_ledger.py                 (원장 재생성 — 기존 위치)
       python3 build_ledger.py --ingest        (추가로 _inbox JSON을 _raw로 복사·보존)
       python3 build_ledger.py --out DIR       (원장을 DIR에 쓴다 — 스테이징/드라이런)
       python3 build_ledger.py --base DIR      (원천 루트를 명시 — 보통 불필요)

종료 코드:  0 정상 · 2 원천 0건(무음실패 방지) · 3 FSRS 엔진 로드 실패

[상태머신 규칙 — v2와 동일]
  오답 발생             -> consecutiveCorrect=0
  재도전 정답           -> consecutiveCorrect+1
  consecutiveCorrect=2  -> 졸업후보 (마지막 확인 대기)
  consecutiveCorrect>=3 -> 졸업 (듀 큐에서 제외, 시험 전 총복습 리스트엔 포함)
  (미졸업) timesWrong>=2 또는 retryMissed>=1 -> 상습 = 출제 최우선

[FSRS 설정 — 왜 이렇게 잡았나]
  learning_steps=() / relearning_steps=()  하루 단위 시스템이라 분 단위 학습단계는 무의미
  enable_fuzzing=False                     멱등 원칙(같은 입력 → 같은 출력)
  desired_retention=0.9                    목표 회상률 90%
  maximum_interval=60                      시험 대비 상한 — 공인중개사판 값(60일)을 그대로 승계했다
                                           (법무사 시험일 확정 시 재검토. 값 자체는 미변경.)
  parameters=<FSRS-6 기본 21개>            개인 최적화 파라미터 없음(리뷰 로그 부족)
"""
import json, glob, os, re, sys, datetime, shutil

# ─────────────────────────────────────────────────────────────────────────────
# FSRS 엔진 로드 — sys.path 조작 없이(스크립트 디렉터리가 이미 sys.path[0]이다)
#   ① 같은 폴더의 fsrs_vendor/ (py-fsrs 6.3.2 벤더링본, 순수 표준 라이브러리)
#   ② 실패 시 pip 설치본 fsrs
#   ③ 둘 다 없으면 조용히 넘어가지 않고 exit 3
# ─────────────────────────────────────────────────────────────────────────────
try:
    from fsrs_vendor import Scheduler, Card, Rating, State  # noqa: F401
    FSRS_ORIGIN = "fsrs_vendor (벤더링 py-fsrs 6.3.2)"
except ImportError as _e_vendor:
    try:
        from fsrs import Scheduler, Card, Rating, State  # noqa: F401
        FSRS_ORIGIN = "fsrs (pip 설치본)"
    except ImportError as _e_pip:
        sys.stderr.write(
            "❌ FSRS 엔진을 못 찾았다 — 원장을 만들 수 없다.\n"
            f"   ① 벤더링본 실패: {_e_vendor}\n"
            f"   ② pip 설치본 실패: {_e_pip}\n"
            "   해결: build_ledger.py 옆에 fsrs_vendor/ 폴더를 두거나,\n"
            "         pip install fsrs==6.3.2 (필요시 --break-system-packages)\n"
        )
        sys.exit(3)

FSRS_VERSION = "6.3.2"
FSRS_DESIRED_RETENTION = 0.9
FSRS_MAX_INTERVAL = 60                            # 상한(일) — 공인중개사판 값 승계(법무사 시험일 미확정)
FSRS_RATING_MAP = "wrong=Again, retryCorrect=Good"

KST = datetime.timezone(datetime.timedelta(hours=9))
REVIEW_HOUR_KST = 12                              # 이벤트 시각을 그날 정오(KST)로 고정
DUE_BACKLOG_WARN = 100                            # 듀 큐가 이보다 크면 적체 경고

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = RAW = INBOX = None                         # main()에서 확정
LADDER = [3, 7, 16, 35]                           # v2 사다리 — FSRS 실패 개념 폴백용

# 결과 JSON 파일명 패턴.
#   표준:   법무사_오답_2026-08-24.json
#   변형:   법무사_민사집행법전범위_오답_2026-08-24.json  (과목명이 '_오답_' 앞에 끼는 형태)
# '*'가 빈 문자열도 매칭하므로 하나의 패턴으로 둘 다 잡는다.
# (공인중개사판과 동일한 이유 — 고정 접두어 패턴은 변형을 조용히 누락시킨다)
RESULT_GLOB = "법무사2차_*오답_*.json"

def find_jsons():
    seen = {}
    for d in (RAW, INBOX):
        for f in glob.glob(os.path.join(d, RESULT_GLOB)):
            base = re.sub(r" \(\d+\)(?=\.json$)", "", os.path.basename(f))
            if base not in seen or os.path.getmtime(f) > os.path.getmtime(seen[base]):
                seen[base] = f
    return list(seen.values())

def dedate(s):  return re.sub(r"^\s*\d{4}-\d{2}-\d{2}\s*", "", s or "").strip()
def deretry(s): return re.sub(r"\s*\(재도전\)\s*$", "", s or "").strip()
def concept_label(src): return deretry(dedate(src))
def norm(s): return re.sub(r"\s+", " ", s or "").strip()
def canon(s): return re.sub(r"[\s/]+", "", norm(s))

# ─────────────────────────────────────────────────────────────────────────────
# v3.1 — 과목 별칭 정규화
#   퀴즈 생성기가 회차마다 과목을 다르게 적는다(축약형으로 적거나, 접미어 '법'을 빼거나).
#   집계 축이 쪼개지면 "민법이 약점 1위"라는 사실이 표에서 사라지므로 대표명으로 접는다.
#   ⚠️ subject(집계 축)에만 적용한다. conceptKey/concept/aliases(매칭 키)는 무관하다.
# ─────────────────────────────────────────────────────────────────────────────
SUBJECT_ALIAS = {"민집": "민사집행법", "부등": "부동산등기법",
                 "상등": "상업등기법", "민소": "민사소송법",
                 "형소": "형사소송법", "가등": "가족관계등록",
                 "부동산등기": "부동산등기법", "상업등기": "상업등기법"}
# 표에 없는 과목(예: "형법", "헌법")은 norm_subject가 원문 그대로 통과시킨다(identity).

def norm_subject(s):
    """과목명을 대표명으로 접는다. 표에 없으면 원문 그대로(공백만 정규화)."""
    s = norm(s or "")
    return SUBJECT_ALIAS.get(s, s)

def date_prefix(s):
    m = re.match(r"\d{4}-\d{2}-\d{2}", s or "")
    return m.group(0) if m else None

def date_anywhere(s):
    """파일명 어디에 있든 YYYY-MM-DD를 찾는다.
    (표준·변형 파일명 모두 대응 — 고정 접두어 replace는 변형에서 실패했다)"""
    m = re.search(r"\d{4}-\d{2}-\d{2}", s or "")
    return m.group(0) if m else None

# ─────────────────────────────────────────────────────────────────────────────
# (2026-09-01) 객관식 오답 원인 — 틀린 뒤 본인이 고른 진단값(errorCause) 집계 유틸
#   동률이면 진단 가치가 큰 쪽을 대표로 삼는다: 개념부재 > 혼동 > 함정 > 실수.
#   표에 없는 값(구버전·오타)은 맨 뒤로 밀되 버리지 않는다.
# ─────────────────────────────────────────────────────────────────────────────
ERROR_CAUSE_PRIORITY = ["개념부재", "혼동", "함정", "실수"]

def cause_rank(c):
    return ERROR_CAUSE_PRIORITY.index(c) if c in ERROR_CAUSE_PRIORITY else len(ERROR_CAUSE_PRIORITY)

def cause_sorted(causes):
    """(원인, 횟수)를 빈도 내림차순 → 원인 우선순위 → 이름순으로 정렬해 돌려준다."""
    return sorted((causes or {}).items(), key=lambda kv: (-kv[1], cause_rank(kv[0]), kv[0]))

def cause_top(causes):
    """최빈 오답 원인 1개(동률이면 개념부재 > 혼동 > 함정 > 실수). 비면 None."""
    s = cause_sorted(causes)
    return s[0][0] if s else None

def new_rec(subject, label):
    return {"conceptKey": label, "aliases": [], "subject": subject, "concept": label,
            "status": "재도전중", "timesWrong": 0, "retryMissed": 0, "consecutiveCorrect": 0,
            "firstWrong": None, "lastWrong": None, "lastCorrect": None,
            "lastResult": None, "lastDp": None, "nextReviewDate": None,
            "dates": [], "samples": [], "missedKeys": {}, "errorCauses": {}}

# ─────────────────────────────────────────────────────────────────────────────
# 경로 해석 — v2는 스크립트가 항상 _ledger/ 안에 있다고 가정했다.
# v3는 스테이징 폴더에서도 돌려야 하므로(드라이런), 원천 루트를 유연하게 찾는다.
# ─────────────────────────────────────────────────────────────────────────────
def _looks_like_base(d):
    return bool(d) and (os.path.isdir(os.path.join(d, "_raw")) or
                        os.path.isdir(os.path.join(d, "_inbox")))

def resolve_base(here, cli_base):
    """원천 데이터 루트(claude_ox_오답/)를 정한다.
       ① --base 명시  ② 스크립트가 _ledger/ 안 → 그 부모 (v2와 동일)
       ③ 현재 작업 디렉터리  ④ 스크립트 부모 (마지막 폴백; 0건이면 exit 2가 알린다)"""
    if cli_base:
        return os.path.abspath(cli_base)
    parent = os.path.dirname(here)
    if os.path.basename(here) == "_ledger" and _looks_like_base(parent):
        return parent
    cwd = os.getcwd()
    if _looks_like_base(cwd):
        return cwd
    if _looks_like_base(parent):
        return parent
    return parent

def default_out_dir(here, base):
    """--out 미지정 시 원장을 쓸 곳 = 기존 위치(프로덕션 _ledger/)."""
    if os.path.basename(here) == "_ledger":
        return here
    cand = os.path.join(base, "_ledger")
    return cand if os.path.isdir(cand) else here

def parse_args(argv):
    ingest = "--ingest" in argv
    out_dir = base = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            if i + 1 >= len(argv):
                sys.stderr.write("❌ --out 뒤에 디렉터리를 적어야 한다.\n"); sys.exit(3)
            out_dir = argv[i + 1]; i += 1
        elif a.startswith("--out="):
            out_dir = a.split("=", 1)[1]
        elif a == "--base":
            if i + 1 >= len(argv):
                sys.stderr.write("❌ --base 뒤에 디렉터리를 적어야 한다.\n"); sys.exit(3)
            base = argv[i + 1]; i += 1
        elif a.startswith("--base="):
            base = a.split("=", 1)[1]
        i += 1
    return ingest, out_dir, base

# ─────────────────────────────────────────────────────────────────────────────
# FSRS 리플레이
# ─────────────────────────────────────────────────────────────────────────────
def make_scheduler():
    return Scheduler(desired_retention=FSRS_DESIRED_RETENTION,
                     learning_steps=(), relearning_steps=(),
                     maximum_interval=FSRS_MAX_INTERVAL,
                     enable_fuzzing=False)

def review_datetime(dp, nth):
    """dp(YYYY-MM-DD)의 12:00 KST를 UTC로. 같은 날 n번째 이벤트는 +n분(단조 증가용)."""
    d = datetime.date.fromisoformat(dp)
    local = datetime.datetime(d.year, d.month, d.day, REVIEW_HOUR_KST, 0, tzinfo=KST) \
            + datetime.timedelta(minutes=nth)
    return local.astimezone(datetime.timezone.utc)

def fsrs_replay(sched, card_id, kinds, now_utc):
    """개념 하나의 이벤트 시퀀스를 FSRS에 통과시킨다.
       kinds: [(dp, 'w'|'c'), ...]  — 이미 시간순으로 정렬된 상태여야 한다."""
    card = Card(card_id=card_id)
    per_day, prev, reps, lapses = {}, None, 0, 0
    for dp, kind in kinds:
        nth = per_day.get(dp, 0); per_day[dp] = nth + 1
        dt = review_datetime(dp, nth)
        if prev is not None and dt <= prev:        # 단조 증가 보장(방어적)
            dt = prev + datetime.timedelta(minutes=1)
        prev = dt
        card, _ = sched.review_card(card, Rating.Again if kind == "w" else Rating.Good, dt)
        reps += 1
        if kind == "w":
            lapses += 1
    return {"stability": round(card.stability, 3) if card.stability is not None else None,
            "difficulty": round(card.difficulty, 3) if card.difficulty is not None else None,
            "due": card.due.astimezone(KST).date().isoformat(),
            "state": card.state.name,
            "reps": reps, "lapses": lapses,
            "retrievability": round(sched.get_card_retrievability(card, now_utc), 3)}

def main():
    global BASE, RAW, INBOX
    ingest, cli_out, cli_base = parse_args(sys.argv)
    BASE  = resolve_base(HERE, cli_base)
    RAW   = os.path.join(BASE, "_raw")
    INBOX = os.path.join(BASE, "_inbox")
    OUT   = os.path.abspath(cli_out) if cli_out else default_out_dir(HERE, BASE)
    os.makedirs(OUT, exist_ok=True)

    files = find_jsons()
    if not files:
        print("⚠️  접근 실패/0건 — _raw 와 _inbox 에서 채점결과 JSON을 찾지 못했다.")
        print("    (조용히 넘어가지 않는다. 퀴즈 결과 JSON을 _inbox/ 에 넣고 다시 실행.)")
        print(f"    찾아본 곳: {RAW} · {INBOX}")
        sys.exit(2)

    if ingest:
        os.makedirs(RAW, exist_ok=True)
        for f in glob.glob(os.path.join(INBOX, RESULT_GLOB)):
            dst = os.path.join(RAW, os.path.basename(f))
            if not os.path.exists(dst):
                shutil.copy2(f, dst); print("  ↳ 보존:", os.path.basename(f))

    # 1) 파일 -> 시간순 이벤트 스트림  ── v2와 동일(한 글자도 안 바꿨다)
    events = []
    subs = score_sum = tot_sum = perfect = v2files = 0
    dps_all = set()
    for f in sorted(files, key=lambda p: os.path.basename(p)):
        fname = os.path.basename(f)
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print("PARSE FAIL", fname, e); continue
        subs += 1; score_sum += d.get("score", 0); tot_sum += d.get("total", 0)
        if d.get("wrongCount") == 0: perfect += 1
        date_raw = str(d.get("date") or "")
        dp = date_prefix(date_raw) or date_anywhere(fname) or "0000-00-00"
        if dp == "0000-00-00":
            print(f"⚠️  날짜 판독 실패 — {fname} (date 필드·파일명 모두에서 YYYY-MM-DD를 못 찾음)")
        dps_all.add(dp)
        sv = d.get("schemaVersion", 1)
        if sv >= 2 and isinstance(d.get("results"), list):
            v2files += 1
            for r in d["results"]:
                label = deretry(dedate(str(r.get("conceptKey") or ""))) or concept_label(r.get("src", ""))
                label = norm(label) or norm(str(r.get("cat", "")) + " " + str(r.get("q", ""))[:20])
                retry = bool(r.get("retryOf")) or "(재도전)" in str(r.get("src", ""))
                subject = norm_subject(r.get("cat"))          # v3.1 별칭 정규화(subject 전용)
                if r.get("correctAnswered") is False:
                    events.append((dp, fname, "w", canon(label), label, subject, date_raw, retry, r))
                elif r.get("correctAnswered") is True and retry:
                    events.append((dp, fname, "c", canon(label), label, subject, date_raw, retry, None))
        else:
            for w in d.get("wrong", []):
                label = concept_label(w.get("src", ""))
                label = norm(label) or norm(str(w.get("cat", "")) + " " + str(w.get("q", ""))[:20])
                retry = "(재도전)" in str(w.get("src", ""))
                subject = norm_subject(w.get("cat"))          # v3.1 별칭 정규화(subject 전용)
                events.append((dp, fname, "w", canon(label), label, subject, date_raw, retry, w))

    # 2) 리플레이: 개념 레코드 갱신 ── v2와 동일 + FSRS용 이벤트 시퀀스 수집
    #    정렬 키 (dp, fname)은 v2 그대로. 파이썬 sort는 안정 정렬이라
    #    같은 (dp, fname) 안에서는 파일 내 등장 순서가 보존된다.
    ledger, subj_wrong, seq = {}, {}, {}
    for dp, fname, kind, ckey, label, subject, date_raw, retry, sample in sorted(events, key=lambda e: (e[0], e[1])):
        r = ledger.setdefault(ckey, new_rec(subject, label))
        seq.setdefault(ckey, []).append((dp, kind))          # ← FSRS 리플레이 입력
        if label != r["concept"] and label not in r["aliases"]:
            r["aliases"].append(label)
        if kind == "w":
            r["timesWrong"] += 1
            r["consecutiveCorrect"] = 0
            if retry: r["retryMissed"] += 1
            r["dates"].append(date_raw or dp)
            r["firstWrong"] = r["firstWrong"] or (date_raw or dp)
            r["lastWrong"] = date_raw or dp
            r["lastResult"] = "wrong"; r["lastDp"] = dp
            subj_wrong[subject] = subj_wrong.get(subject, 0) + 1
            # 놓친 채점 포인트(단답 자가채점에서 본인이 고른 것) — 다음 재도전의 조준점
            for mk in (sample.get("missedKeys") or []) if isinstance(sample, dict) else []:
                mk = str(mk).strip()
                if mk:
                    r["missedKeys"][mk] = r["missedKeys"].get(mk, 0) + 1
            # 객관식 오답 원인(본인이 고른 진단) — 재출제 각도·Anki 편입 라우팅의 원천
            ec = str(sample.get("errorCause") or "").strip() if isinstance(sample, dict) else ""
            if ec:
                r["errorCauses"][ec] = r["errorCauses"].get(ec, 0) + 1
            if sample is not None and len(r["samples"]) < 3:
                r["samples"].append({"date": date_raw or dp, "type": sample.get("type"), "q": sample.get("q"),
                                     "myAnswer": sample.get("myAnswer"), "correct": sample.get("correct"),
                                     "expl": sample.get("expl"),
                                     "missedKeys": sample.get("missedKeys") or [],
                                     "fixTyped": sample.get("fixTyped"),
                                     "errorCause": sample.get("errorCause"),
                                     "causeNote": sample.get("causeNote")})
        else:
            r["consecutiveCorrect"] += 1
            r["lastCorrect"] = date_raw or dp
            r["lastResult"] = "correct"; r["lastDp"] = dp

    # 3) 상태 판정 ── v2와 동일. 사다리는 폴백 기준선으로만 계산해 둔다.
    for r in ledger.values():
        cc = r["consecutiveCorrect"]
        if cc >= 3:
            r["status"] = "졸업"
        elif cc == 2:
            r["status"] = "졸업후보"
        elif r["retryMissed"] > 0 or r["timesWrong"] >= 2:
            r["status"] = "상습"
        else:
            r["status"] = "재도전중"
        try:
            base = datetime.date.fromisoformat(r["lastDp"])
            delta = LADDER[0] if r["lastResult"] == "wrong" else LADDER[min(cc, 3)]
            r["nextReviewDate"] = (base + datetime.timedelta(days=delta)).isoformat()
        except Exception:
            r["nextReviewDate"] = None

    # 3-b) FSRS-6 스케줄링 — nextReviewDate를 FSRS due로 갈아끼운다.
    sched = make_scheduler()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    fsrs_failed = []
    for idx, (ckey, r) in enumerate(ledger.items(), 1):
        try:
            f = fsrs_replay(sched, idx, seq.get(ckey, []), now_utc)
            r["fsrs"] = f
            r["fsrsFallback"] = False
            r["nextReviewDate"] = f["due"]
        except Exception as e:
            r["fsrs"] = None
            r["fsrsFallback"] = True                          # nextReviewDate는 사다리 값 유지
            fsrs_failed.append((r["conceptKey"], f"{type(e).__name__}: {e}"))
    if fsrs_failed:
        print(f"⚠️  FSRS 실패 {len(fsrs_failed)}개 개념 — v2 사다리 {LADDER}로 폴백했다:")
        for ck, msg in fsrs_failed[:10]:
            print(f"     · {ck} — {msg}")
        if len(fsrs_failed) > 10:
            print(f"     … 외 {len(fsrs_failed) - 10}개")

    prio = {"상습": 0, "재도전중": 1, "졸업후보": 2, "졸업": 3}
    recs = sorted(ledger.values(), key=lambda r: (prio[r["status"]], -r["retryMissed"], -r["timesWrong"], r["nextReviewDate"] or "9999"))

    # 4) 듀 큐 (퀴즈 생성이 소비)
    #    선정 규칙은 v2 그대로(졸업 제외 · nextReviewDate ≤ 오늘).
    #    정렬만 바뀐다: 상태 우선순위 → 망각위험(retrievability) 오름차순.
    #    R이 낮을수록 이미 잊었다는 뜻이므로, 가장 위태로운 개념이 큐 앞에 온다.
    today = datetime.date.today().isoformat()
    due = [r for r in recs if r["status"] != "졸업" and r["nextReviewDate"] and r["nextReviewDate"] <= today]

    def _r_of(r):
        f = r.get("fsrs") or {}
        v = f.get("retrievability")
        return v if v is not None else 2.0        # 폴백 개념은 같은 상태 그룹의 맨 뒤로
    def _s_of(r):
        f = r.get("fsrs") or {}
        return f.get("stability")

    due.sort(key=lambda r: (prio[r["status"]], _r_of(r), r["nextReviewDate"] or "9999", r["conceptKey"]))
    dueQueue = [{"conceptKey": r["conceptKey"], "subject": r["subject"], "status": r["status"],
                 "timesWrong": r["timesWrong"], "retryMissed": r["retryMissed"],
                 "consecutiveCorrect": r["consecutiveCorrect"],
                 "lastWrong": r["lastWrong"], "nextReviewDate": r["nextReviewDate"],
                 "retrievability": (r.get("fsrs") or {}).get("retrievability"),
                 "stability": _s_of(r),
                 "missedTop": [k for k, _ in sorted(r.get("missedKeys", {}).items(),
                                                    key=lambda kv: -kv[1])[:3]],
                 "causeTop": cause_top(r.get("errorCauses")),
                 "errorCauses": r.get("errorCauses") or {}} for r in due]

    status_counts = {}
    for r in recs:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    out = {"ledgerSchema": 3,
           "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
           "fsrsMeta": {"version": FSRS_VERSION,
                        "desiredRetention": FSRS_DESIRED_RETENTION,
                        "maximumInterval": FSRS_MAX_INTERVAL,
                        "fuzzing": False,
                        "ratingMap": FSRS_RATING_MAP},
           "sourceFiles": len(files), "v2Files": v2files, "submissions": subs,
           "avgScore": round(score_sum/subs, 1) if subs else None,
           "avgTotal": round(tot_sum/subs) if subs else None, "perfectRuns": perfect,
           "totalWrongItems": sum(r["timesWrong"] for r in recs),
           "uniqueConcepts": len(recs),
           "dateRange": [min(dps_all), max(dps_all)] if dps_all else None,
           "statusCounts": status_counts,
           "fsrsFallbacks": len(fsrs_failed),
           "subjectWeakness": dict(sorted(subj_wrong.items(), key=lambda x: -x[1])),
           "dueQueue": dueQueue, "ledger": recs}
    json.dump(out, open(os.path.join(OUT, "오답_원장.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # 5) 사람이 읽는 원장(.md)
    def pct(v):
        return "—" if v is None else f"{v*100:.0f}%"

    DUE_TABLE_ROWS = 20
    L = []
    L.append(f"# 📒 법무사 오답 누적 원장 v3.1 · FSRS-6 스케줄링  ·  갱신 {out['generatedAt']}")
    L.append("")
    L.append(f"> 기간 {out['dateRange'][0]} ~ {out['dateRange'][1]} · 제출 {subs}회 · 평균 {out['avgScore']}/{out['avgTotal']} · 만점 {perfect}회")
    L.append(f"> 누적 오답 {out['totalWrongItems']}건 · 고유 개념 {out['uniqueConcepts']}개 · 원천 JSON {len(files)}개 (v2 스키마 {v2files}개)")
    L.append(f"> 상태: " + " · ".join(f"{k} {v}" for k, v in status_counts.items()))
    L.append(f"> 스케줄러: FSRS-6 {FSRS_VERSION} · 목표 회상률 {int(FSRS_DESIRED_RETENTION*100)}% · 최대 간격 {FSRS_MAX_INTERVAL}일 · 퍼징 off · 매핑 {FSRS_RATING_MAP}")
    if len(dueQueue) > DUE_BACKLOG_WARN:
        L.append(f"> ⚠️ **복습 적체 {len(dueQueue)}개** — 하루 8개씩 소화해도 {-(-len(dueQueue)//8)}일치다. 큐 상단(망각위험 큰 것)부터 끊어 가라.")
    if fsrs_failed:
        L.append(f"> ⚠️ FSRS 실패 {len(fsrs_failed)}개 개념은 v2 사다리 {LADDER}로 폴백했다.")
    L.append(">")
    if v2files == 0:
        L.append("> ⚠️ 아직 전부 v1 결과(오답만 기록)라 '졸업'은 발생할 수 없다. v2 템플릿(_template.html)으로")
        L.append(">  생성된 퀴즈를 제출하는 시점부터 재도전 정답이 기록되어 졸업이 굴러가기 시작한다.")
        L.append(">")
    L.append(f"## 🗓️ 오늘의 복습 큐 (due — 퀴즈 생성이 여기서 재도전 5~8개를 뽑는다) · {len(dueQueue)}개")
    L.append("")
    L.append("_정렬: 상태(상습 우선) → 망각위험(R) 오름차순. R = 지금 떠올릴 확률이라 **낮을수록 이미 잊었다**는 뜻이고, 그런 개념이 큐 위로 온다._")
    L.append("")
    L.append("_`놓친 포인트` = 단답 자가채점에서 본인이 \"이것 때문에 틀렸다\"고 고른 채점 포인트(빈도순 상위 3). **재도전 문항은 이 지점을 정면으로 겨냥해 출제한다** — 없으면(`—`) 종전대로 개념 전체를 변형 출제._")
    L.append("")
    L.append("_`원인` = 틀린 뒤 본인이 고른 오답 원인(개념부재/혼동/함정/실수) 누적. **재출제 각도와 Anki 편입이 이 값을 따른다** — 실수뿐인 개념은 Anki 카드화 제외._")
    L.append("")
    if dueQueue:
        L.append("| 우선 | 과목 | 개념 | 상태 | 틀림 | 재도전실패 | 연속정답 | 복습예정일 | 망각위험(R) | 놓친 포인트 | 원인 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for i, q in enumerate(dueQueue[:DUE_TABLE_ROWS], 1):
            mtop = " · ".join(q.get("missedTop") or []) or "—"
            ctop = "·".join(f"{k}×{v}" for k, v in cause_sorted(q.get("errorCauses"))) or "—"
            L.append(f"| {i} | {q['subject']} | {q['conceptKey']} | {q['status']} | {q['timesWrong']} | {q['retryMissed']} | {q['consecutiveCorrect']} | {q['nextReviewDate']} | {pct(q['retrievability'])} | {mtop} | {ctop} |")
        if len(dueQueue) > DUE_TABLE_ROWS:
            L.append("")
            L.append(f"_…외 {len(dueQueue) - DUE_TABLE_ROWS}개 (전체 목록은 JSON 원장의 `dueQueue`)_")
    else:
        L.append("_오늘 복습 기한이 된 개념 없음_")
    L.append("")
    sections = [("## 🔴 상습 (재도전 실패·반복 오답 — 최우선)", "상습"),
                ("## 🟠 재도전중", "재도전중"),
                ("## 🟡 졸업후보 (연속정답 2 — 마지막 확인 대기)", "졸업후보"),
                ("## 🎓 졸업 (연속정답 3 — 듀 큐 제외, 총복습엔 포함)", "졸업")]
    for title, st in sections:
        L.append(title); L.append("")
        rows = [r for r in recs if r["status"] == st]
        if not rows:
            L.append("_해당 없음_"); L.append(""); continue
        L.append("| 과목 | 개념 | 틀림 | 재도전실패 | 연속정답 | 최근오답 | 최근정답 | 다음복습 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in rows:
            L.append(f"| {r['subject']} | {r['concept']} | {r['timesWrong']} | {r['retryMissed']} | {r['consecutiveCorrect']} | {r['lastWrong'] or '—'} | {r['lastCorrect'] or '—'} | {r['nextReviewDate'] or '—'} |")
        L.append("")
    L.append("## 📊 과목별 약점 (누적 오답 수)")
    L.append("")
    L.append("_과목명은 대표명으로 통일해 집계한다(v3.1) — 민집 → 민사집행법, 부등 → 부동산등기법, 상등 → 상업등기법 등._")
    L.append("")
    L.append("| 과목 | 오답 |")
    L.append("|---|---|")
    for k, v in out["subjectWeakness"].items():
        L.append(f"| {k} | {v} |")
    L.append("")
    open(os.path.join(OUT, "오답_원장.md"), "w", encoding="utf-8").write("\n".join(L))

    print("✅ 원장 v3.1 재생성 완료 (FSRS-6 스케줄링 · 과목 별칭 정규화)")
    print(f"   엔진 {FSRS_ORIGIN} · 목표 회상률 {FSRS_DESIRED_RETENTION} · 최대 간격 {FSRS_MAX_INTERVAL}일 · 퍼징 off")
    print(f"   원천 {RAW} + {INBOX}  →  출력 {OUT}")
    print(f"   원천 {len(files)}개(v2: {v2files}) · 제출 {subs}회 · 누적 오답 {out['totalWrongItems']}건 · 개념 {len(recs)}개")
    print(f"   상태: " + " · ".join(f"{k} {v}" for k, v in status_counts.items()))
    print(f"   🗓️ 듀 큐 {len(dueQueue)}개: " + (", ".join(f"{q['conceptKey']}(R{pct(q['retrievability'])})" for q in dueQueue[:6]) or "없음"))
    if len(dueQueue) > DUE_BACKLOG_WARN:
        print(f"   ⚠️ 복습 적체 {len(dueQueue)}개 — 하루 8개 기준 {-(-len(dueQueue)//8)}일치다.")
    print(f"   과목별 약점 TOP3: " + ", ".join(f"{k}({v})" for k, v in list(out['subjectWeakness'].items())[:3]))

if __name__ == "__main__":
    main()
