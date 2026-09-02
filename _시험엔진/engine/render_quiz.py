#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/render_quiz.py — 문항 JSON(+plan) → 퀴즈 HTML 렌더러  (HG 무한복습체계 v1, 2026-09-02)

  python3 render_quiz.py --exam gongin|bupsa1|bupsa2 --kind daily|retry
                         [--date YYYY-MM-DD] [--root ROOT] [--plan PATH]
                         [--questions PATH] [--out PATH] [--no-validate] [--seed N]

입력
  plan.json       prepare_quiz.py 출력 (계약은 README 상단 주석 / 보고서 §5 참조)
  questions.json  AI 작성 문항 — 정답 '위치'는 지정하지 않는다(이 스크립트가 균등 배정)

처리 순서
  ① questions.json 스키마 검증
  ①-2 evidence(노트 원문 인용) 대조 — 단답 환각 게이트. 통과분은 HTML 에 싣지 않는다
  ② 정답 위치 균등 배정(+같은 인덱스 3연속 금지, 한달전 블록 포함 최종 배열 기준)
  ③ 표기 부착 (⏪ 장기복습 / 🔁 재도전)
  ④ 배치 (본편 과목 연속 · 한달전 블록 맨 뒤)
  ⑤ META_LINE / TAGS_HTML / ALERT_HTML 생성
  ⑥ 템플릿 렌더 → 토큰 잔존 0 확인
  ⑦ engine/validate_quiz.js 실행 (--no-validate면 생략 / 검사기 부재·실행 실패는 렌더 중단 — 무검증 문제지 금지)
  ⑧ 통과 시에만 최종 경로 기록 + 부수 산출(_장기복습_로그 · _push · _runs.log)

결정론: 같은 입력 + 같은 시드 → 같은 HTML (기본 시드 = crc32("exam|kind|date"))
"""

import argparse
import ast
import datetime as _dt
import json
import os
import random
import re
import shutil
import subprocess
import sys
import unicodedata
import zlib
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = ENGINE_DIR.parents[1]          # <root>/_시험엔진/engine → <root>
TEMPLATE_NAME = "quiz_template.html"
VALIDATOR_NAME = "validate_quiz.js"

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]
SA_TYPE = "단답"
OX_TYPE = "OX"
COMBO_TYPE = "조합"
CALC_TYPE = "계산"
MCQ_TYPES = {"일반", "사례", "판례", "계산", "개수", "조합", "OX"}
ALL_TYPES = MCQ_TYPES | {SA_TYPE}

# accent → (on_accent, grad2, reveal_hover) — 레거시 6벌의 실제 값. 미등록 색은 아래 폴백으로 계산.
ACCENT_DERIVED = {
    "#ffd24a": ("#1a1a1a", "#ffb347", "#26261a"),
    "#7c9cff": ("#10131c", "#5f7fe8", "#1a2138"),
}


class RenderError(Exception):
    """검증·렌더 실패. message에 실패 항목이 줄 단위로 담긴다."""


# ────────────────────────────────────────────────────────────── 색 유틸

def _hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb2hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def _luminance(hexc):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = _hex2rgb(hexc)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _hue(hexc):
    r, g, b = (c / 255.0 for c in _hex2rgb(hexc))
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        return 0.0
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60.0


def _warm_cool(accent, accent2):
    """따뜻한 쪽(선택·강조)과 차가운 쪽(섹션·hover)을 색상환으로 고정 판정.
    레거시 6벌은 accent/accent2 배치가 시험별로 뒤집혀 있으나 화면상 역할색은 동일했다."""
    def warmth(h):                      # 45°(노랑)에서의 각거리 — 작을수록 warm
        d = abs(h - 45.0) % 360.0
        return min(d, 360.0 - d)
    return (accent, accent2) if warmth(_hue(accent)) <= warmth(_hue(accent2)) else (accent2, accent)


def _derive_colors(accent, accent2):
    warm, cool = _warm_cool(accent, accent2)
    if accent.lower() in ACCENT_DERIVED:
        on_accent, grad2, reveal = ACCENT_DERIVED[accent.lower()]
    else:
        on_accent = "#1a1a1a" if _luminance(accent) > 0.5 else "#10131c"
        grad2 = _rgb2hex([c * 0.88 for c in _hex2rgb(accent)])
        reveal = _rgb2hex([a * 0.12 + b * 0.88 for a, b in zip(_hex2rgb(accent), _hex2rgb("#0f1115"))])
    return warm, cool, on_accent, grad2, reveal


# ────────────────────────────────────────────────────────────── 계산형 안전 eval

_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Tuple, ast.Call, ast.Name,
)
_ALLOWED_CALLS = {"round": round, "abs": abs, "min": min, "max": max}


def safe_eval(expr):
    """계산형 expr — 산술 + round/abs/min/max 만 허용."""
    tree = ast.parse(str(expr), mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise RenderError("calc.expr 금지 구문: %s (%r)" % (type(node).__name__, expr))
        if isinstance(node, ast.Name) and node.id not in _ALLOWED_CALLS:
            raise RenderError("calc.expr 금지 식별자: %s" % node.id)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_CALLS:
                raise RenderError("calc.expr 금지 호출: %r" % expr)
    return eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, dict(_ALLOWED_CALLS))


def _num_in_text(value, text):
    """계산 결과가 정답 보기 문자열 안에 등장하는지 — 천단위 콤마·소수 표기 허용."""
    plain = re.sub(r"[,\s]", "", str(text or ""))
    cands = set()
    if float(value).is_integer():
        cands.add(str(int(value)))
        cands.add("%.1f" % value)
    cands.add(("%g" % value))
    cands.add(("%.2f" % value).rstrip("0").rstrip("."))
    return any(c and c in plain for c in cands)


# ────────────────────────────────────────────────────────────── 로드

def load_exams(root):
    p = ENGINE_DIR / "exams.json"
    if not p.exists():
        p = root / "_시험엔진" / "engine" / "exams.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_json(path, what):
    p = Path(path)
    if not p.exists():
        raise RenderError("%s 파일 없음: %s" % (what, p))
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RenderError("%s JSON 파싱 실패: %s (%s)" % (what, p, e))


# ────────────────────────────────────────────────────────────── ① 스키마 검증

def validate_questions(doc, exam, kind, cfg, plan, errors):
    if not isinstance(doc, dict):
        errors.append("questions.json 최상위가 객체가 아님")
        return []
    for k in ("date", "exam", "kind", "questions"):
        if k not in doc:
            errors.append("questions.json 필수 키 누락: %s" % k)
    if doc.get("exam") not in (None, exam):
        errors.append("questions.json exam 불일치: %r ≠ %r" % (doc.get("exam"), exam))
    if doc.get("kind") not in (None, kind):
        errors.append("questions.json kind 불일치: %r ≠ %r" % (doc.get("kind"), kind))

    qs = doc.get("questions")
    if not isinstance(qs, list) or not qs:
        errors.append("questions[]가 비어 있거나 배열이 아님")
        return []

    opts_count = cfg.get("opts_count", 4)
    combo_cfg = cfg.get("combo") or {}
    plan_keys = None
    if kind == "retry":
        plan_keys = {p.get("conceptKey") for p in (plan.get("picks") or [])}

    for i, q in enumerate(qs):
        tag = "q[%d]" % i
        if not isinstance(q, dict):
            errors.append("%s 객체가 아님" % tag)
            continue
        for k in ("type", "cat", "q", "expl", "src", "conceptKey"):
            if k == "src" and kind == "retry":
                continue                    # 재도전은 src가 비면 "오답원장 (재도전)"으로 채운다
            if not str(q.get(k, "")).strip():
                errors.append("%s 필수 필드 누락/빈값: %s" % (tag, k))
        t = q.get("type")
        if t not in ALL_TYPES:
            errors.append("%s 알 수 없는 type: %r" % (tag, t))
            continue
        if plan_keys is not None and q.get("conceptKey") not in plan_keys:
            errors.append("%s conceptKey가 plan.picks에 없음: %r" % (tag, q.get("conceptKey")))

        if t == SA_TYPE:
            if not str(q.get("answer", "")).strip():
                errors.append("%s 단답 answer 누락" % tag)
            kw = q.get("keywords")
            if not isinstance(kw, list) or not kw:
                errors.append("%s 단답 keywords[] 누락" % tag)
            if q.get("opts"):
                errors.append("%s 단답에 opts가 있으면 안 됨" % tag)
            if exam == "bupsa2" and not str(q.get("sub", "")).strip():
                errors.append("%s 법무사 2차 단답 sub 누락" % tag)
        elif t == OX_TYPE:
            if q.get("opts") is None and q.get("answer") not in ("O", "X"):
                errors.append('%s OX answer는 "O"|"X" 여야 함: %r' % (tag, q.get("answer")))
        elif t == COMBO_TYPE:
            if q.get("opts") is None:
                items = q.get("items")
                if not isinstance(items, list) or len(items) < 2:
                    errors.append("%s 조합 items[] 누락/부족" % tag)
                else:
                    for j, it in enumerate(items):
                        if not isinstance(it, dict) or not str(it.get("text", "")).strip() \
                                or not isinstance(it.get("truth"), bool):
                            errors.append("%s items[%d] {text, truth:bool} 형식 아님" % (tag, j))
                if q.get("stem_target") not in ("true", "false"):
                    errors.append('%s 조합 stem_target은 "true"|"false"' % tag)
        else:
            if q.get("opts") is None:
                if not str(q.get("correct", "")).strip():
                    errors.append("%s correct 누락" % tag)
                d = q.get("distractors")
                need = opts_count - 1
                if not isinstance(d, list) or len(d) != need:
                    errors.append("%s distractors 개수 %s (기대 %d)"
                                  % (tag, len(d) if isinstance(d, list) else "없음", need))
                if t == CALC_TYPE:
                    c = q.get("calc")
                    if not isinstance(c, dict) or "expr" not in c or "expected" not in c:
                        errors.append("%s 계산형 calc{expr,expected} 누락" % tag)

        if q.get("opts") is not None:           # 레거시(한달전 블록 등)
            if not isinstance(q["opts"], list) or len(q["opts"]) < 2:
                errors.append("%s 레거시 opts[] 형식 오류" % tag)
            elif not isinstance(q.get("answer"), int) or not (0 <= q["answer"] < len(q["opts"])):
                errors.append("%s 레거시 answer 인덱스 오류: %r" % (tag, q.get("answer")))
    return qs


# ──────────────────────────────────────────── evidence(노트 원문 인용) 게이트
#
# 2026-09-02 신설 — 단답 문항의 환각 방지. 문항의 evidence{note, quote} 에서 quote 가
# 대상 텍스트(노트 원문 또는 재도전 samples)에 **실제로 있는 문자열**인지 렌더 전에 대조한다.
#   · 정규화: HTML 태그 제거 → 소문자 → 유니코드 카테고리 P*(구두점)·S*(기호, 마크다운
#     * _ # > | - 포함)·Z*(공백)·C*(제어) 문자를 전부 삭제 → 부분 문자열 포함 검사.
#   · 필수: kind=daily 의 본편(한달전 블록 제외) 단답 전부. 그 외(객관식·retry·한달전)는
#     evidence 가 있으면 검사하고 없으면 통과.
#   · 통과한 evidence 는 HTML 에 싣지 않는다(문제지 비대화 방지) — normalize_questions·
#     dump_questions 의 키 화이트리스트가 자동으로 떨군다.

EVIDENCE_QUOTE_LEN = (15, 120)          # 원문 그대로 복사할 길이(정규화 전 원문 기준)
EVIDENCE_NORM_MIN = 8                   # 정규화 후 최소 길이 — 구두점만인 quote 차단
EVIDENCE_SAMPLES = "samples"            # note 특수값 — 재도전 plan.picks[].samples 를 원천으로


def ev_norm(s):
    """공백·마크다운 기호·구두점을 제거한 비교용 정규형."""
    s = re.sub(r"<[^>]*>", " ", str(s or "")).lower()
    return "".join(ch for ch in s if unicodedata.category(ch)[0] not in "PSZC")


def _ev_plan_paths(plan):
    """plan 의 원천 경로들 — basename → 경로 문자열."""
    out = {}
    for key in ("new_sources", "longrev_picks"):
        for s in (plan.get(key) or []):
            p = str((s or {}).get("path") or "")
            if p:
                out.setdefault(os.path.basename(p), p)
    for pk in (plan.get("picks") or []):
        for p in ((pk or {}).get("related_notes") or []):
            p = str(p or "")
            if p:
                out.setdefault(os.path.basename(p), p)
    return out


def _ev_resolve_note(name, root, ex, cfg, plan_paths):
    """note 값 → 실제 파일 경로. 절대경로 → plan 원천 basename → notes_dir → notes_dir/백지복습."""
    name = str(name or "").strip()
    if not name:
        return None
    cands = []
    p0 = Path(name)
    if p0.is_absolute():
        cands.append(p0)
    base = os.path.basename(name)
    hit = plan_paths.get(base) or plan_paths.get(name)
    if hit:
        hp = Path(hit)
        cands.append(hp if hp.is_absolute() else root / hp)
    notes = root / ex.get("notes_dir", "")
    blank = (cfg.get("_paths") or {}).get("blank_review_dir", "백지복습")
    cands += [notes / base, notes / blank / base, root / name]
    for c in cands:
        try:
            if c.is_file():
                return c
        except OSError:
            continue
    return None


def _ev_samples_text(plan, concept_key):
    """재도전 근거 텍스트 — 해당 pick 의 samples[].q + expl (문자열 샘플은 그대로)."""
    for pk in (plan.get("picks") or []):
        if (pk or {}).get("conceptKey") != concept_key:
            continue
        buf = []
        for s in (pk.get("samples") or []):
            if isinstance(s, dict):
                buf += [str(s.get("q") or ""), str(s.get("expl") or "")]
            else:
                buf.append(str(s or ""))
        return " ".join(buf), True
    return "", False


def check_evidence(qs, exam, kind, root, ex, cfg, plan, errors):
    """단답 문항의 evidence 를 노트 원문과 대조한다. 실패는 errors 에 열거."""
    plan_paths = _ev_plan_paths(plan)
    cache = {}
    lo, hi = EVIDENCE_QUOTE_LEN
    for i, q in enumerate(qs):
        if not isinstance(q, dict):
            continue
        ck = q.get("conceptKey")
        tag = "q[%d](%s)" % (i, str(ck or "")[:34])
        ev = q.get("evidence")
        # 필수 여부 — daily 본편(한달전 제외) 단답. 그 외는 있으면 검사, 없으면 통과.
        required = (kind == "daily" and q.get("type") == SA_TYPE
                    and not q.get("monthlyOf") and not q.get("retryOf"))
        if ev is None:
            if required:
                errors.append("%s 단답 evidence 누락 — evidence{note, quote} 필수"
                              "(노트 원문에서 그대로 복사한 %d~%d자)" % (tag, lo, hi))
            continue
        if not isinstance(ev, dict):
            errors.append("%s evidence 가 객체가 아님: %r" % (tag, ev))
            continue
        note_name = str(ev.get("note") or "").strip()
        quote = str(ev.get("quote") or "")
        head = quote.strip().replace("\n", " ")[:40]
        if not note_name or not quote.strip():
            errors.append("%s evidence{note, quote} 둘 다 필요 (note=%r · quote 앞 40자=%r)"
                          % (tag, note_name, head))
            continue
        if not (lo <= len(quote.strip()) <= hi):
            errors.append("%s evidence.quote 길이 %d자 (기대 %d~%d) · note=%s · quote 앞 40자=%r"
                          % (tag, len(quote.strip()), lo, hi, note_name, head))
            continue
        nq = ev_norm(quote)
        if len(nq) < EVIDENCE_NORM_MIN:
            errors.append("%s evidence.quote 가 정규화 후 %d자뿐(기호·구두점 위주) · note=%s · quote 앞 40자=%r"
                          % (tag, len(nq), note_name, head))
            continue

        if note_name == EVIDENCE_SAMPLES:
            if kind != "retry":
                errors.append("%s evidence.note='%s' 는 재도전 문항에서만 쓴다"
                              % (tag, EVIDENCE_SAMPLES))
                continue
            key = ("samples", ck)
            if key not in cache:
                text, found = _ev_samples_text(plan, ck)
                cache[key] = (ev_norm(text), found)
            target, found = cache[key]
            if not found:
                errors.append("%s evidence.note='%s' 인데 plan.picks 에 conceptKey %r 가 없음"
                              % (tag, EVIDENCE_SAMPLES, ck))
                continue
            if nq not in target:
                errors.append("%s evidence.quote 가 plan.picks[].samples(q·expl)에 없음 — "
                              "note=%s · quote 앞 40자=%r" % (tag, EVIDENCE_SAMPLES, head))
            continue

        if note_name not in cache:
            p = _ev_resolve_note(note_name, root, ex, cfg, plan_paths)
            if p is None:
                cache[note_name] = None
            else:
                try:
                    cache[note_name] = (p, ev_norm(p.read_text(encoding="utf-8", errors="replace")))
                except OSError as e:
                    cache[note_name] = None
                    errors.append("%s evidence.note 읽기 실패: %s (%s)" % (tag, p, e))
        entry = cache.get(note_name)
        if entry is None:
            errors.append("%s evidence.note 를 찾지 못함: %s — 절대경로 · plan 원천 basename · "
                          "%s/ · %s/%s/ 순으로 찾는다 · quote 앞 40자=%r"
                          % (tag, note_name, ex.get("notes_dir"), ex.get("notes_dir"),
                             (cfg.get("_paths") or {}).get("blank_review_dir", "백지복습"), head))
            continue
        path, target = entry
        if nq not in target:
            errors.append("%s evidence.quote 가 노트 원문에 없음(환각 의심) — note=%s · "
                          "quote 앞 40자=%r" % (tag, path.name, head))


# ────────────────────────────────────────────────────────────── 조합형

def _combo_label_of(idx, labels):
    return labels[idx] if idx < len(labels) else "?"


def build_combo(q, combo_cfg, rng, errors, tag):
    """조합형 1문항 생성 → (q텍스트, correct 문자열, distractor 문자열들, ㄱ참거짓, 정답조합 라벨셋)"""
    labels = combo_cfg.get("label_set", ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ"])
    opts_n = combo_cfg.get("opts", 4)
    opt_size = combo_cfg.get("opt_size")
    items = list(q["items"])
    order = list(range(len(items)))
    rng.shuffle(order)
    sh = [items[i] for i in order]
    want = (q.get("stem_target") == "true")
    corr = [i for i, it in enumerate(sh) if bool(it["truth"]) is want]
    comp = [i for i in range(len(sh)) if i not in corr]

    if opt_size is not None and len(corr) != opt_size:
        errors.append("%s 조합 opt_size=%d인데 %s 항목이 %d개 (셔플로 못 고침 — 문항 수정 필요)"
                      % (tag, opt_size, "참" if want else "거짓", len(corr)))
        return None
    if not corr or not comp:
        errors.append("%s 조합 정답 집합이 공집합이거나 전체집합" % tag)
        return None

    def fmt(idxs):
        return ", ".join(_combo_label_of(i, labels) for i in sorted(idxs))

    cands = []
    if opt_size is None:
        for x in corr:
            if len(corr) > 1:
                cands.append(tuple(sorted(set(corr) - {x})))
        for y in comp:
            cands.append(tuple(sorted(set(corr) | {y})))
    for x in corr:                                   # 한 개 교체(고정 크기용 · 가변에서도 보충)
        for y in comp:
            cands.append(tuple(sorted((set(corr) - {x}) | {y})))
    seen, uniq = {tuple(sorted(corr))}, []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            uniq.append(c)
    need = opts_n - 1
    if len(uniq) < need:
        errors.append("%s 조합 오답 후보 부족 (%d < %d)" % (tag, len(uniq), need))
        return None
    uniq.sort(key=lambda c: (len(c), c))
    picks = rng.sample(uniq, need)

    lines = "".join("<br>%s. %s" % (_combo_label_of(i, labels), sh[i]["text"]) for i in range(len(sh)))
    return {
        "q": str(q["q"]).rstrip() + lines,
        "correct": fmt(corr),
        "distractors": [fmt(p) for p in picks],
        "first_truth": bool(sh[0]["truth"]),
        "corr_labels": {_combo_label_of(i, labels) for i in corr},
    }


def build_all_combos(qs, combo_cfg, exam, base_seed, errors):
    """세트 단위 제약(ㄱ·ㄴ 정답 포함 비율 25~75% · gongin ㄱ 거짓 ≥2)을 만족할 때까지 시드 재시도."""
    idxs = [i for i, q in enumerate(qs) if q.get("type") == COMBO_TYPE and q.get("opts") is None]
    if not idxs:
        return {}, []
    lo, hi = (combo_cfg.get("position_truth_ratio") or [0.25, 0.75])[:2]
    min_n = combo_cfg.get("check_min_count", 4)
    min_first_false = combo_cfg.get("min_first_false", 0)
    labels = combo_cfg.get("label_set", ["ㄱ", "ㄴ"])
    best, best_score, warn = None, None, []
    for attempt in range(200):
        rng = random.Random(base_seed ^ (0x5bf03635 + attempt))
        local, built = [], {}
        for i in idxs:
            r = build_combo(qs[i], combo_cfg, rng, local, "q[%d]" % i)
            if r is None:
                errors.extend(local)                       # 셔플로 못 고치는 구조적 오류
                return {}, []
            built[i] = r
        n = len(idxs)
        ok = True
        score = 0
        if n >= min_n:
            for lab in labels[:2]:
                ratio = sum(1 for i in idxs if lab in built[i]["corr_labels"]) / n
                if not (lo <= ratio <= hi):
                    ok = False
                    score += 1
            if min_first_false:
                ff = sum(1 for i in idxs if not built[i]["first_truth"])
                if ff < min_first_false:
                    ok = False
                    score += 1
        if ok:
            return built, []
        if best_score is None or score < best_score:
            best, best_score = built, score
    warn.append("조합 세트 제약(ㄱ·ㄴ 비율/ㄱ거짓)을 200회 셔플로 만족하지 못해 최선안을 사용")
    return best, warn


# ────────────────────────────────────────────────────────────── 문항 정규화

def normalize_questions(qs, cfg, exam, kind, base_seed, errors):
    """questions.json 문항 → 템플릿 문항객체(opts는 확정, answer 인덱스는 뒤에서 배정)."""
    combo_cfg = cfg.get("combo") or {}
    combos, warns = build_all_combos(qs, combo_cfg, exam, base_seed, errors)
    out = []
    for i, q in enumerate(qs):
        tag = "q[%d]" % i
        t = q.get("type")
        item = {k: q[k] for k in ("type", "cat", "q", "expl", "src", "conceptKey") if k in q}
        for k in ("exam", "sub", "retryOf", "monthlyOf", "note", "source", "age_days"):
            if q.get(k) is not None:
                item[k] = q[k]
        if t == SA_TYPE:
            item["answer"] = q["answer"]
            item["keywords"] = list(q.get("keywords") or [])
            out.append(item)
            continue

        if q.get("opts") is not None:                       # 레거시 형식 — 그대로 둔다
            item["opts"] = list(q["opts"])
            item["answer"] = int(q["answer"])
            item["_fixed_answer"] = True
            if q.get("calc"):
                item["calc"] = q["calc"]
            out.append(item)
            continue

        if t == OX_TYPE:
            # OX는 정답 위치가 내용으로 결정된다 — 분산·3연속 배정에서 제외(고정)
            item["opts"] = ["O", "X"]
            item["answer"] = 0 if q.get("answer") == "O" else 1
            item["_fixed_answer"] = True
        elif t == COMBO_TYPE:
            c = combos.get(i)
            if c is None:
                continue
            item["q"] = c["q"]
            item["_correct"] = c["correct"]
            item["_distractors"] = list(c["distractors"])
        else:
            item["_correct"] = q["correct"]
            item["_distractors"] = list(q.get("distractors") or [])
            if t == CALC_TYPE and isinstance(q.get("calc"), dict):
                calc = q["calc"]
                try:
                    got = safe_eval(calc["expr"])
                except RenderError as e:
                    errors.append("%s %s" % (tag, e))
                    got = None
                if got is not None:
                    exp = calc.get("expected")
                    if abs(float(got) - float(exp)) > max(1e-6, abs(float(exp)) * 1e-9):
                        errors.append("%s calc.expr 값 %r ≠ expected %r" % (tag, got, exp))
                    elif not _num_in_text(exp, item["_correct"]):
                        errors.append("%s calc.expected(%r)가 정답 보기 %r 안에 없음"
                                      % (tag, exp, item["_correct"]))
                item["calc"] = {"expr": calc["expr"], "expected": calc["expected"]}
        out.append(item)
    return out, warns


# ────────────────────────────────────────────────────────────── ③ 표기 부착

def _note_age_map(plan):
    """장기복습 note 경로 → age_days. 경로·파일명·과목 3단 폴백."""
    m = {}
    picks = plan.get("longrev_picks") or []
    for p in picks:
        path, age = str(p.get("path") or ""), p.get("age_days")
        if path and age is not None:
            m[path] = age
            m[Path(path).name] = age
            m["과목:" + str(p.get("subject") or "")] = age
    if len(picks) == 1 and picks[0].get("age_days") is not None:
        m["_only"] = picks[0]["age_days"]
    return m


def _lookup_age(ages, item):
    note = str(item.get("note") or "")
    for key in (note, Path(note).name if note else "", "과목:" + str(item.get("cat") or "")):
        if key and key in ages:
            return ages[key]
    if item.get("age_days") is not None:
        return item["age_days"]
    return ages.get("_only")


def attach_marks(items, plan, kind, errors=None):
    """표기 부착. src 접미 서식은 exams.json _validate.src_marks 계약을 따른다.
       ⏪ (장기복습·N일전) / 🔁 (재도전) / 🔄 (한달전 재출제·원본 YYYY-MM-DD, prepare 쪽 책임)"""
    errors = errors if errors is not None else []
    ages = _note_age_map(plan)
    for it in items:
        if kind == "retry":
            if not str(it.get("q", "")).lstrip().startswith("🔁"):
                it["q"] = "🔁 " + str(it.get("q", ""))
            it["retryOf"] = it.get("retryOf") or it.get("conceptKey")
            src = str(it.get("src") or "").strip()
            if not src:
                src = "오답원장"
            if not src.endswith("(재도전)"):
                src = src + " (재도전)"
            it["src"] = src
        elif it.get("source") == "longrev":
            if not str(it.get("q", "")).lstrip().startswith("⏪"):
                it["q"] = "⏪ " + str(it.get("q", ""))
            age = _lookup_age(ages, it)
            if age is None:
                errors.append("장기복습 문항의 age_days를 찾을 수 없음 (plan.longrev_picks[].path ↔ "
                              "문항 note 불일치, 문항 age_days도 없음): %r" % str(it.get("q"))[:40])
            elif "(장기복습" not in str(it.get("src") or ""):
                it["src"] = ("%s (장기복습·%s일전)"
                             % (str(it.get("src") or "").strip(), age)).strip()
        it.pop("source", None)
        it.pop("age_days", None)
        it.pop("note", None)
    return items


# ────────────────────────────────────────────────────────────── ④ 배치

def group_by_cat(items):
    """같은 과목 연속 배치 — AI 순서 보존, 과목 블록 순서는 첫 등장 순."""
    order, buckets = [], {}
    for it in items:
        c = it.get("cat")
        if c not in buckets:
            buckets[c] = []
            order.append(c)
        buckets[c].append(it)
    return [it for c in order for it in buckets[c]]


def order_questions(main_items, monthly_items):
    return group_by_cat(main_items) + group_by_cat(monthly_items)


def check_monthly_contract(monthly, vcfg, errors):
    """한달전 블록은 plan(prepare_quiz)이 확정해 넘긴다 — 계약 위반을 여기서 조기에 잡는다.
       monthlyOf = 원본 문제지 날짜(YYYY-MM-DD) · src 접미 = (한달전 재출제·원본 YYYY-MM-DD)"""
    of_re = re.compile(vcfg.get("monthly_of_regex", r"^\d{4}-\d{2}-\d{2}$"))
    src_re = re.compile((vcfg.get("src_marks") or {}).get(
        "monthly", r"\(한달전 재출제·원본 \d{4}-\d{2}-\d{2}\)"))
    emo = (vcfg.get("emoji") or {}).get("monthly", "🔄")
    for i, it in enumerate(monthly):
        tag = "monthly_block[%d]" % i
        if not of_re.match(str(it.get("monthlyOf") or "")):
            errors.append("%s monthlyOf는 원본 문제지 날짜(YYYY-MM-DD)여야 함: %r"
                          % (tag, it.get("monthlyOf")))
        if not src_re.search(str(it.get("src") or "")):
            errors.append("%s src 접미가 '(한달전 재출제·원본 YYYY-MM-DD)' 형식이 아님: %r"
                          % (tag, it.get("src")))
        if emo not in str(it.get("q") or ""):
            errors.append("%s q에 %s 접두가 없음" % (tag, emo))
        if it.get("opts") is not None and not isinstance(it.get("answer"), int):
            errors.append("%s 객관식 answer 인덱스가 확정되지 않음" % tag)


# ────────────────────────────────────────────────────────────── ② 정답 배정

def _target_counts(n, k, lo, hi, rng):
    base = [n // k] * k
    for i in range(n % k):
        base[i] += 1
    rng.shuffle(base)
    if lo is not None and hi is not None and lo * k <= n <= hi * k:
        for _ in range(400):
            if all(lo <= c <= hi for c in base):
                break
            hi_i = max(range(k), key=lambda i: base[i])
            lo_i = min(range(k), key=lambda i: base[i])
            if base[hi_i] - base[lo_i] <= 0:
                break
            base[hi_i] -= 1
            base[lo_i] += 1
    return base


def _greedy(pool_counts, prev2, rng):
    """정답 인덱스 나열 — 같은 값 3연속 금지. prev2 = 앞선 두 값(없으면 None)."""
    counts = list(pool_counts)
    n = sum(counts)
    res, a, b = [], prev2[0], prev2[1]
    for _ in range(n):
        cand = [v for v in range(len(counts)) if counts[v] > 0 and not (v == a and v == b)]
        if not cand:
            return None
        cand.sort(key=lambda v: (-counts[v], rng.random()))
        v = cand[0]
        counts[v] -= 1
        res.append(v)
        a, b = b, v
    return res


def _has_triple(seq):
    return any(seq[i] == seq[i + 1] == seq[i + 2] for i in range(len(seq) - 2))


def _repair_triples(full, mutable_idx, rng, tries=800):
    for _ in range(tries):
        bad = None
        for i in range(len(full) - 2):
            if full[i] == full[i + 1] == full[i + 2]:
                bad = i
                break
        if bad is None:
            return True
        movable = [j for j in (bad, bad + 1, bad + 2) if j in mutable_idx]
        if not movable:
            return False
        fixed = False
        for j in movable:
            for k in sorted(mutable_idx, key=lambda _x: rng.random()):
                if full[k] == full[j]:
                    continue
                full[j], full[k] = full[k], full[j]
                if not _has_triple(full[max(0, min(j, k) - 2): max(j, k) + 3]):
                    fixed = True
                    break
                full[j], full[k] = full[k], full[j]
            if fixed:
                break
        if not fixed:
            return False
    return not _has_triple(full)


def is_dist_mcq(it):
    """정답 '분산' 배정의 대상 — 단답·OX는 제외(OX는 정답이 내용으로 고정)."""
    return it.get("type") not in (SA_TYPE, OX_TYPE)


def is_run_item(it):
    """'같은 정답 3연속 금지' 검사의 대상 — 단답만 제외하고 OX는 포함한다.
       validate_quiz.js 는 정답이 정수인 문항(=OX 포함)을 나열해 3연속을 보므로 범위를 맞춘다.
       OX는 배정 대상이 아니라 _fixed_answer 로 남고, 교체는 주변 가변 문항에서 일어난다."""
    return it.get("type") != SA_TYPE


def assign_answers(ordered, cfg, exam, kind, rng, errors, warns):
    """ordered: 최종 순서의 문항 리스트. _fixed_answer(한달전 블록·OX)는 건드리지 않는다."""
    k = cfg.get("answer_range", cfg.get("opts_count", 4))
    dist = cfg.get("answer_dist_main")
    lo, hi = (dist[0], dist[1]) if (dist and exam == "gongin" and kind == "daily") else (None, None)

    free = [i for i, it in enumerate(ordered)
            if is_dist_mcq(it) and not it.get("_fixed_answer")]
    if not free:
        return
    if lo is not None and not (lo * k <= len(free) <= hi * k):
        lo = hi = None          # 본편 객관식 수가 7~10×지수 범위를 벗어나면 균등 배분으로 폴백
    counts = _target_counts(len(free), k, lo, hi, rng)
    seq = None
    for _ in range(300):
        seq = _greedy(counts, (None, None), rng)
        if seq is not None:
            break
    if seq is None:
        errors.append("정답 인덱스 배정 실패(3연속 금지 조건)")
        return
    for pos, v in zip(free, seq):
        ordered[pos]["answer"] = v

    # 최종 배열(단답 제외·OX 포함 나열) 기준 3연속 검사 — 한달전 블록 포함
    mcq_pos = [i for i, it in enumerate(ordered) if is_run_item(it)]
    full = [ordered[i]["answer"] for i in mcq_pos]
    mutable = {j for j, i in enumerate(mcq_pos) if not ordered[i].get("_fixed_answer")}
    if _has_triple(full):
        if not _repair_triples(full, mutable, rng):
            warns.append("정답 3연속을 본편 교체로 못 없앰 — 한달전 블록 순서 교체 시도")
        for j, i in enumerate(mcq_pos):
            if j in mutable:
                ordered[i]["answer"] = full[j]

    # 실제 분산 확인
    got = [0] * k
    for i in free:
        got[ordered[i]["answer"]] += 1
    if lo is not None:
        if min(got) < lo or max(got) > hi:
            warns.append("정답 분산 %s (목표 %d~%d)" % (got, lo, hi))
    elif got and max(got) - min(got) > cfg.get("answer_dist_max_diff", 3):
        warns.append("정답 분산 %s (최대−최소 > %d)" % (got, cfg.get("answer_dist_max_diff", 3)))


def materialize_options(ordered, rng):
    """_correct/_distractors → opts[] (배정된 answer 인덱스 위치에 정답을 끼워 넣는다)."""
    for it in ordered:
        if it.get("type") == SA_TYPE or "_correct" not in it:
            it.pop("_fixed_answer", None)
            continue
        d = list(it.pop("_distractors"))
        c = it.pop("_correct")
        ans = max(0, min(int(it.get("answer", 0)), len(d)))
        it["opts"] = d[:ans] + [c] + d[ans:]
        it["answer"] = ans
        it.pop("_fixed_answer", None)


def fix_monthly_block_triples(ordered, n_main, rng):
    """한달전 블록 내부에서만 3연속이 남으면 블록 순서(과목 연속 유지)를 교체해 푼다."""
    monthly = ordered[n_main:]
    if len(monthly) < 3:
        return ordered
    def seq_of(lst):
        return [it["answer"] for it in ordered[:n_main] + lst if is_run_item(it)]
    if not _has_triple(seq_of(monthly)):
        return ordered
    cats, buckets = [], {}
    for it in monthly:
        buckets.setdefault(it["cat"], []).append(it)
        if it["cat"] not in cats:
            cats.append(it["cat"])
    for _ in range(200):
        cs = cats[:]
        rng.shuffle(cs)
        cand = []
        for c in cs:
            b = buckets[c][:]
            rng.shuffle(b)
            cand += b
        if not _has_triple(seq_of(cand)):
            return ordered[:n_main] + cand
    return ordered


# ────────────────────────────────────────────────────────────── ⑤ META/TAGS/ALERT

def _fmt(tpl, mapping):
    out = str(tpl or "")
    for k, v in mapping.items():
        out = out.replace("{%s}" % k, str(v))
    return out


def _cat_tags(exam, kind, ordered):
    cats = []
    for it in ordered:
        if it["cat"] not in cats:
            cats.append(it["cat"])
    prefix = "📚 " if (exam.startswith("bupsa") and kind == "daily") else ""
    return "".join('<span class="tag">%s%s</span>' % (prefix, c) for c in cats)


def build_meta(ex, exam, kind, cfg, date, ordered, plan):
    y, m, d = (int(x) for x in date.split("-"))
    wd = WEEKDAY_KO[_dt.date(y, m, d).weekday()]
    sa = sum(1 for it in ordered if it["type"] == SA_TYPE)
    mo = sum(1 for it in ordered if it.get("monthlyOf"))
    lr = sum(1 for it in ordered if str(it.get("q", "")).lstrip().startswith("⏪"))
    mini = sum(1 for it in ordered if it.get("sub") == "미니답안")
    n = len(ordered)
    base = {"Y": y, "M": m, "D": d, "W": wd, "N": n, "TOTAL": n, "SA": sa, "MO": mo,
            "LR": lr, "MINI": mini, "MAIN": n - mo,
            "STAGE": plan.get("stage") or "", "REST": plan.get("rest", 0)}
    base["SA_SUFFIX"] = _fmt(cfg.get("meta_sa_suffix", ""), base) if sa else ""
    base["LR_TAG"] = _fmt(cfg.get("tags_lr", ""), base) if lr else ""
    base["MO_TAG"] = _fmt(cfg.get("tags_mo", ""), base) if mo else ""
    base["SA_TAG"] = _fmt(cfg.get("tags_sa", ""), base) if sa else ""
    base["CAT_TAGS"] = _cat_tags(exam, kind, ordered)
    meta = re.sub(r"\s{2,}", " ", _fmt(cfg.get("meta_line", ""), base)).strip()
    tags = _fmt(cfg.get("tags_html", ""), base)
    alert = str(plan.get("alert_html") or "") if kind == "daily" else ""
    return meta, tags, alert, {"sa": sa, "mo": mo, "lr": lr, "mini": mini, "n": n}


# ────────────────────────────────────────────────────────────── ⑥ 렌더

def dump_questions(ordered):
    """HTML 에 실을 키만 남긴다 — evidence(노트 원문 인용)는 여기서 떨어진다(문제지 비대화 방지)."""
    clean = []
    for it in ordered:
        o = {}
        for k in ("type", "exam", "sub", "cat", "q", "opts", "answer", "calc",
                  "keywords", "expl", "src", "conceptKey", "retryOf", "monthlyOf"):
            if k in it and it[k] is not None:
                o[k] = it[k]
        clean.append(o)
    return ",\n".join(json.dumps(o, ensure_ascii=False, indent=1) for o in clean)


def render_html(template, tokens, questions_json):
    out = template
    for k, v in tokens.items():
        out = out.replace("{{%s}}" % k, str(v))
    out = re.sub(
        r"(/\*__QUESTIONS_START__\*/)(.*?)(/\*__QUESTIONS_END__\*/)",
        lambda m: m.group(1) + "\n" + questions_json + "\n" + m.group(3),
        out, flags=re.S)
    return out


def residual_tokens(html):
    return sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", html)))


# ────────────────────────────────────────────────────────────── ⑧ 부수 산출

def update_longrev_log(qd, plan, date):
    picks = plan.get("longrev_picks") or []
    if not picks:
        return None
    p = qd / "_장기복습_로그.json"
    log = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for pick in picks:
        name = Path(str(pick.get("path") or "")).name
        if not name:
            continue
        e = log.get(name) or {"last": None, "n": 0}
        e["last"] = date
        e["n"] = int(e.get("n", 0)) + 1
        log[name] = e
    p.write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return p


def _note_label(path, age):
    name = Path(str(path or "")).name
    name = re.sub(r"\.md$", "", name)
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    parts = name.split("-", 1)
    subject = parts[0].strip()
    title = parts[1].strip() if len(parts) > 1 else ""
    title = re.sub(r"^\((.*)\)$", r"\1", title).strip()
    if title.startswith(subject + " "):
        title = title[len(subject) + 1:]
    label = (subject + " " + title).strip()
    return "%s (%s일전)" % (label, age) if age is not None else label


def write_push(qd, date, plan, doc, ordered, counts):
    push_dir = qd / "_push"
    push_dir.mkdir(parents=True, exist_ok=True)
    new_n = sum(1 for it in ordered
                if not it.get("monthlyOf") and not str(it.get("q", "")).lstrip().startswith("⏪"))
    notes = [_note_label(p.get("path"), p.get("age_days"))
             for p in (plan.get("longrev_picks") or [])][:3]
    payload = {
        "date": date,
        "quizFile": "%s.html" % date,
        "counts": {"신규": new_n, "장기복습": counts["lr"], "재도전": 0, "한달전": counts["mo"]},
        "longRevNotes": notes,
        "monthlySrc": plan.get("monthly_src_range") or "",
        "dueBacklog": plan.get("due_backlog") or 0,
        "ox": doc.get("push_ox") or [],
    }
    p = push_dir / ("%s.json" % date)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return p


def append_runs_log(root, exam, kind, ok, summary):
    p = root / "_시험엔진" / "_runs.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    line = "%s\t%s\t%s\t%s\t%s\n" % (
        _dt.datetime.now().replace(microsecond=0).isoformat(),
        exam, kind, "OK" if ok else "FAIL", summary)
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
    return p


# ────────────────────────────────────────────────────────────── ⑦ validate

def run_validator(engine_dir, exam, kind, path, date, root=None):
    v = engine_dir / VALIDATOR_NAME
    if not v.exists():
        # 검사기 부재는 통과가 아니라 실패다 — 무검증 문제지가 아침 루틴에 들어가면 안 된다.
        return False, "validate_quiz.js 부재 — 렌더 중단 (engine/ 폴더 확인)"
    cmd = ["node", str(v), "--exam", exam, "--kind", kind, "--file", str(path), "--date", date]
    if root:
        cmd += ["--root", str(root)]              # 렌더러와 같은 트리를 보게 한다
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except Exception as e:                                    # noqa: BLE001
        return False, "validate 실행 실패 — 렌더 중단 (%s)" % e
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode == 0, out.strip()


# ────────────────────────────────────────────────────────────── main

def main(argv=None):
    ap = argparse.ArgumentParser(description="문항 JSON → 퀴즈 HTML 렌더러")
    ap.add_argument("--exam", required=True, choices=["gongin", "bupsa1", "bupsa2"])
    ap.add_argument("--kind", required=True, choices=["daily", "retry"])
    ap.add_argument("--date")
    ap.add_argument("--root")
    ap.add_argument("--plan")
    ap.add_argument("--questions")
    ap.add_argument("--out")
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args(argv)

    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    date = a.date or _dt.date.today().isoformat()
    exams_cfg = load_exams(root)
    ex = exams_cfg["exams"][a.exam]
    qd = root / ex["dir"] / ("데일리퀴즈" if a.kind == "daily" else "오답퀴즈")
    work = qd / "_work"
    plan_p = Path(a.plan) if a.plan else work / ("%s.plan.json" % date)
    ques_p = Path(a.questions) if a.questions else work / ("%s.questions.json" % date)
    out_p = Path(a.out) if a.out else qd / ("%s.html" % date)
    cfg = ex[a.kind]
    seed = a.seed if a.seed is not None else zlib.crc32(("%s|%s|%s" % (a.exam, a.kind, date)).encode())

    errors, warns = [], []
    try:
        plan = load_json(plan_p, "plan")
        doc = load_json(ques_p, "questions")
        tpl_p = ENGINE_DIR / TEMPLATE_NAME
        if not tpl_p.exists():
            raise RenderError("템플릿 없음: %s" % tpl_p)
        template = tpl_p.read_text(encoding="utf-8")

        if plan.get("date") not in (None, date):
            errors.append("plan.date 불일치: %r ≠ %r" % (plan.get("date"), date))
        if plan.get("exam") not in (None, a.exam):
            errors.append("plan.exam 불일치: %r ≠ %r" % (plan.get("exam"), a.exam))

        # ① 검증 → ①-2 evidence(노트 원문 인용) 대조 — 환각 게이트
        qs = validate_questions(doc, a.exam, a.kind, cfg, plan, errors)
        check_evidence(qs, a.exam, a.kind, root, ex, exams_cfg, plan, errors)

        # 정규화 (조합·OX·계산)
        rng = random.Random(seed)
        items, w = normalize_questions(qs, cfg, a.exam, a.kind, seed, errors)
        warns += w

        # 한달전 블록 = plan.monthly_block + questions 내 monthlyOf 보유분
        monthly = [it for it in items if it.get("monthlyOf")]
        main = [it for it in items if not it.get("monthlyOf")]
        for mq in (plan.get("monthly_block") or []):
            it = dict(mq)
            it["_fixed_answer"] = True
            monthly.append(it)

        # ③ 표기 → ④ 배치
        attach_marks(main, plan, a.kind, errors)
        check_monthly_contract(monthly, exams_cfg.get("_validate") or {}, errors)
        ordered = order_questions(main, monthly)
        n_main = len(main)

        # ② 정답 배정 → opts 구성 → 한달전 내부 3연속 보정
        assign_answers(ordered, cfg, a.exam, a.kind, rng, errors, warns)
        materialize_options(ordered, rng)
        ordered = fix_monthly_block_triples(ordered, n_main, rng)

        if errors:
            raise RenderError("\n".join(errors))

        # ⑤ META / TAGS / ALERT
        meta, tags, alert, counts = build_meta(ex, a.exam, a.kind, cfg, date, ordered, plan)

        ui = ex["ui"]
        warm, cool, on_accent, grad2, reveal = _derive_colors(ui["accent"], ui["accent2"])
        tokens = {
            "QUIZ_DATE": date,
            "TITLE": ui["title_daily" if a.kind == "daily" else "title_retry"],
            "EYEBROW": ui["eyebrow_daily" if a.kind == "daily" else "eyebrow_retry"],
            "H1": ui["h1_daily" if a.kind == "daily" else "h1_retry"],
            "DESC_HTML": ui["desc_daily" if a.kind == "daily" else "desc_retry"],
            "META_LINE": meta, "TAGS_HTML": tags, "ALERT_HTML": alert,
            "SUBJECT": ex["payload_subject"],
            "RESULT_PREFIX": ex["result_prefix"],
            "QUIZ_ID_SUFFIX": "" if a.kind == "daily" else "-RQ",
            "EXAM_DEFAULT": ui.get("exam_default", ""),
            "INBOX_NOTE": ui.get("inbox_note", ""),
            "ACCENT": ui["accent"], "ACCENT2": ui["accent2"],
            "WARM": warm, "COOL": cool, "ON_ACCENT": on_accent,
            "ACCENT_GRAD2": grad2, "REVEAL_HOVER": reveal,
            "T_MCQ": ui.get("time_per_mcq_sec", 72), "T_SA": ui.get("time_per_sa_sec", 90),
            "RESULT_MSGS": json.dumps(RESULT_MSGS[a.exam], ensure_ascii=False),
        }

        # ⑥ 렌더 + 토큰 잔존 검사
        html = render_html(template, tokens, dump_questions(ordered))
        left = residual_tokens(html)
        if left:
            raise RenderError("토큰 잔존: %s" % ", ".join(left))

        # ⑦ validate
        # 임시본은 **최종과 같은 폴더**에 쓴다. validate_quiz.js 는 --file 의 상위 폴더를
        # 문제지 폴더로 보고 ⓐ 램프업 단계(한달전 창의 YYYY-MM-DD.html 수)와 ⓑ 과거 문제문
        # 중복을 판정한다. _work 아래에 두면 두 검사가 빈 폴더를 보게 되어 무력화된다
        # (법무사 S3가 한달전창 0으로 S2 오판 · past_dup 항상 통과).
        # 파일명이 YYYY-MM-DD.html 이 아니고 오늘 날짜로 시작하므로 두 집계에 스스로 끼지 않는다.
        work.mkdir(parents=True, exist_ok=True)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_p.parent / ("%s.render.tmp.html" % date)
        tmp.write_text(html, encoding="utf-8")
        vmsg = ""
        if not a.no_validate:
            ok, vmsg = run_validator(ENGINE_DIR, a.exam, a.kind, tmp, date, root=root)
            if not ok:
                tmp.unlink(missing_ok=True)
                raise RenderError("validate_quiz.js 실패:\n%s" % vmsg)

    except RenderError as e:
        draft = None
        try:
            work.mkdir(parents=True, exist_ok=True)
            draft = work / ("%s.draft.html" % date)
            body = locals().get("html")
            if not body:                    # 렌더 전 단계에서 죽었으면 실패 항목을 담은 초안을 남긴다
                body = ("<!DOCTYPE html><meta charset=\"utf-8\">"
                        "<title>렌더 실패 %s %s %s</title><pre>%s</pre>\n"
                        % (a.exam, a.kind, date, str(e)))
            draft.write_text(body, encoding="utf-8")
        except Exception:                                     # noqa: BLE001
            pass
        summary = str(e).replace("\n", " / ")[:400]
        append_runs_log(root, a.exam, a.kind, False, summary)
        sys.stderr.write("❌ 렌더 실패\n%s\n" % e)
        if draft:
            sys.stderr.write("   draft: %s\n" % draft)
        return 1

    # ⑧ 최종 기록 + 부수 산출
    out_p.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp), str(out_p))
    side = []
    if a.kind == "daily":
        lp = update_longrev_log(qd, plan, date)
        if lp:
            side.append(str(lp))
        if a.exam == "gongin":
            side.append(str(write_push(qd, date, plan, doc, ordered, counts)))
    summary = "%d문항 (단답 %d · 한달전 %d · 장기복습 %d) → %s" % (
        counts["n"], counts["sa"], counts["mo"], counts["lr"], out_p.name)
    if warns:
        summary += " | 경고 %d" % len(warns)
    append_runs_log(root, a.exam, a.kind, True, summary)
    print("✅ %s" % out_p)
    for s in side:
        print("   부수 산출: %s" % s)
    for w in warns:
        print("   ⚠ %s" % w)
    return 0


RESULT_MSGS = {
    "gongin": [
        "만점. 오늘 등록증 발급해도 되겠는데요? 🏆",
        "합격권. 틀린 거 해설만 한 번 더 보면 완벽합니다.",
        "절반은 넘었어요. 오답 노트행 직행하는 개념들이 보이네요.",
        "아직 흔들리는 개념이 있어요. 해설 정독하고 내일 재도전!",
        "괜찮아요, 회독이 쌓이면 올라갑니다. 해설부터 차근차근.",
    ],
    "bupsa1": [
        "만점. 이 페이스면 동차가 농담이 아니게 됩니다 ⚖️",
        "합격권. 틀린 개념만 해설 한 번 더 — 그게 오늘의 회독입니다.",
        "절반 이상. 단답에서 막힌 건 백지 인출감이 아직이라는 신호예요.",
        "흔들리는 개념이 보입니다. 해설 정독 후 다음 회차에서 재도전.",
        "괜찮아요. 인출 실패 + 피드백이 읽기보다 낫다는 게 연구 결론입니다.",
    ],
}
RESULT_MSGS["bupsa2"] = RESULT_MSGS["bupsa1"]


if __name__ == "__main__":
    sys.exit(main())
