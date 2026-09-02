#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/rerender_quiz.py — 이미 생성된 문제지를 **현재 템플릿**으로 다시 렌더한다 (템플릿 업그레이드용, 2026-09-02)

  python3 rerender_quiz.py --exam gongin|bupsa1|bupsa2 --kind daily|retry --date YYYY-MM-DD [--root ROOT] [--dry-run]

문항(QUESTIONS 배열)·META_LINE·TAGS_HTML·ALERT_HTML은 기존 HTML에서 그대로 뽑아 쓰고, 나머지 토큰은
exams.json에서 채운다. 문항 내용·정답 위치는 손대지 않는다(채점 payload 동일 — tests/payload_regression 근거).
- 결과 JSON이 이미 수거돼 있으면(_inbox) 재렌더하지 않는다(푼 문제지를 바꿀 이유가 없다).
- 기존 파일은 `<퀴즈폴더>/_work/<date>.pre-rerender.html` 로 보존한 뒤 덮어쓴다.
- validate_quiz.js 통과 전 덮어쓰지 않는다.
"""
import argparse
import glob
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_quiz as R  # noqa: E402


def _grab(html, pattern, what):
    m = re.search(pattern, html, flags=re.S)
    if not m:
        raise SystemExit("❌ 기존 HTML에서 %s 를 찾지 못함" % what)
    return m.group(1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="기존 문제지를 현재 템플릿으로 재렌더")
    ap.add_argument("--exam", required=True, choices=["gongin", "bupsa1", "bupsa2"])
    ap.add_argument("--kind", required=True, choices=["daily", "retry"])
    ap.add_argument("--date", required=True)
    ap.add_argument("--root")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve() if a.root else R.DEFAULT_ROOT
    exams_cfg = R.load_exams(root)
    ex = exams_cfg["exams"][a.exam]
    paths = exams_cfg.get("_paths") or {}
    qdir = root / ex["dir"] / (paths.get("quiz_dirs") or {}).get(a.kind, "데일리퀴즈" if a.kind == "daily" else "오답퀴즈")
    src = qdir / ("%s.html" % a.date)
    if not src.exists():
        raise SystemExit("❌ 문제지 없음: %s" % src)

    # 결과가 이미 수거된 문제지는 건드리지 않는다
    inbox = root / ex["dir"] / (paths.get("ledger_dir") or "claude_ox_오답") / (paths.get("inbox_dir") or "_inbox")
    suffix = "" if a.kind == "daily" else "-RQ"
    got = glob.glob(str(inbox / ("%s%s%s*.json" % (ex["result_prefix"], a.date, suffix))))
    got = [g for g in got if (a.kind == "retry") == ("-RQ" in Path(g).name)]
    if got:
        print("↩ 이미 결과가 수거된 문제지 — 재렌더 생략:", Path(got[0]).name)
        return 0

    old = src.read_text(encoding="utf-8")
    questions_json = _grab(old, r"/\*__QUESTIONS_START__\*/(.*?)/\*__QUESTIONS_END__\*/", "QUESTIONS 마커").strip("\n")
    # 마커 사이는 배열 괄호 없이 객체들이 나열된다 — 순수 JSON 인지 확인(구형 eval 문법이면 실패 → 재생성으로 처리)
    body = questions_json.strip().rstrip(",")
    json.loads("[" + body + "]")
    meta = _grab(old, r'<div class="meta">(.*?)</div>', "META_LINE")
    tags = _grab(old, r'<div class="tags">(.*?)</div>', "TAGS_HTML")
    m = re.search(r'<div class="alertbanner">(.*?)</div>', old, flags=re.S)
    alert = m.group(1) if m else ""

    ui = ex["ui"]
    warm, cool, on_accent, grad2, reveal = R._derive_colors(ui["accent"], ui["accent2"])
    tokens = {
        "QUIZ_DATE": a.date,
        "TITLE": ui["title_daily" if a.kind == "daily" else "title_retry"],
        "EYEBROW": ui["eyebrow_daily" if a.kind == "daily" else "eyebrow_retry"],
        "H1": ui["h1_daily" if a.kind == "daily" else "h1_retry"],
        "DESC_HTML": ui["desc_daily" if a.kind == "daily" else "desc_retry"],
        "META_LINE": meta, "TAGS_HTML": tags, "ALERT_HTML": alert,
        "SUBJECT": ex["payload_subject"],
        "RESULT_PREFIX": ex["result_prefix"],
        "QUIZ_ID_SUFFIX": suffix,
        "EXAM_DEFAULT": ui.get("exam_default", ""),
        "INBOX_NOTE": ui.get("inbox_note", ""),
        "ACCENT": ui["accent"], "ACCENT2": ui["accent2"],
        "WARM": warm, "COOL": cool, "ON_ACCENT": on_accent,
        "ACCENT_GRAD2": grad2, "REVEAL_HOVER": reveal,
        "T_MCQ": ui.get("time_per_mcq_sec", 72), "T_SA": ui.get("time_per_sa_sec", 90),
        "RESULT_MSGS": json.dumps(R.RESULT_MSGS[a.exam], ensure_ascii=False),
    }
    template = (R.ENGINE_DIR / R.TEMPLATE_NAME).read_text(encoding="utf-8")
    html = R.render_html(template, tokens, questions_json)
    left = R.residual_tokens(html)
    if left:
        raise SystemExit("❌ 토큰 잔존: %s" % ", ".join(left))

    # 검증 — 재렌더는 '문항 내용'이 아니라 '템플릿'만 바꾸므로, 생성 당시 규칙(쿼터·듀 큐)이 그 사이 바뀌어
    # 걸리는 검사는 허용하고, 구조·계약 검사(토큰·필드·계약·정합)는 통과해야 한다.
    QUOTA_CHECKS = {"longrev_count", "total_count", "main_count", "monthly_count", "conceptkey_in_due",
                    "sa_cap_daily", "sa_cap_retry", "sa_promote_cond", "recent_concept_dup", "mini_count",
                    "longrev_maintain", "ledger_load"}
    tmp = qdir / ("%s.rerender.tmp.html" % a.date)
    tmp.write_text(html, encoding="utf-8")
    import subprocess
    r = subprocess.run(["node", str(R.ENGINE_DIR / R.VALIDATOR_NAME), "--exam", a.exam, "--kind", a.kind,
                        "--file", str(tmp), "--date", a.date, "--root", str(root), "--json"],
                       capture_output=True, text=True, timeout=180)
    tmp.unlink(missing_ok=True)
    try:
        rep = json.loads(r.stdout)
    except Exception:
        print(r.stdout, r.stderr)
        raise SystemExit("❌ 검증기 출력 파싱 실패 — 재렌더하지 않음")
    bad = [c for c in rep.get("checks", []) if not c.get("ok")]
    hard = [c for c in bad if c.get("id") not in QUOTA_CHECKS]
    if hard:
        for c in hard:
            print("FAIL —", c.get("msg"))
        raise SystemExit("❌ 구조 검사 실패 — 재렌더하지 않음 (기존 파일 유지)")
    if bad:
        print("↪ 생성 당시 규칙 차이로 걸린 검사(허용):", ", ".join(c.get("id") for c in bad))

    if a.dry_run:
        print("✅ 드라이런 통과 (쓰지 않음): %s" % src)
        return 0
    work = qdir / (paths.get("work_subdir") or "_work")
    work.mkdir(parents=True, exist_ok=True)
    bak = work / ("%s.pre-rerender.html" % a.date)
    if not bak.exists():
        shutil.copy2(src, bak)
    src.write_text(html, encoding="utf-8")
    print("✅ 재렌더 완료: %s (이전본 → %s)" % (src, bak))
    return 0


if __name__ == "__main__":
    sys.exit(main())
