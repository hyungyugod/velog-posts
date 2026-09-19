#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/ingest_smoke.py — 수거(ingest) 회귀 (2026-09-16 동명이본 가드 + Downloads 수거완료 이동)

  python3 _시험엔진/engine/tests/ingest_smoke.py

프로덕션 트리는 읽지도 쓰지도 않는다 — 임시 ROOT·임시 Downloads 에서만 돈다.
build_ledger.py 는 ENGINE_DIR 을 빈 임시 폴더로 바꿔 건너뛴다(수거 단계만 검증).
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
spec = importlib.util.spec_from_file_location("prepare_quiz", ENGINE / "prepare_quiz.py")
pq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pq)

CFG = json.load(open(ENGINE / "exams.json", encoding="utf-8"))
FAILS = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        FAILS.append(msg)


def fresh(exam="gongin", sweep="_오답_수거완료"):
    tmp = Path(tempfile.mkdtemp(prefix="hg-ingest-"))
    root, dl, eng = tmp / "velog-posts", tmp / "Downloads", tmp / "engine-empty"
    ex = CFG["exams"][exam]
    paths = dict(CFG.get("_paths") or {})
    paths["downloads_sweep_dir"] = sweep
    cfg = dict(CFG); cfg["_paths"] = paths
    inbox = root / ex["dir"] / paths["ledger_dir"] / paths["inbox_dir"]
    inbox.mkdir(parents=True); dl.mkdir(); eng.mkdir()
    pq.ENGINE_DIR = eng                      # build_ledger.py 없음 → 원장 단계 생략
    return tmp, root, dl, inbox, ex, cfg


def run(root, exam, ex, cfg, dl):
    warnings = []
    r = pq.ingest(str(root), exam, ex, cfg, dl, warnings)
    return r, warnings


def write(p, text, mtime=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if mtime:
        os.utime(p, (mtime, mtime))


def main():
    print("══ ingest_smoke ══")
    name = "공인중개사_오답_2026-09-20.json"
    rq = "공인중개사_오답_2026-09-20-RQ.json"

    # 1) 신규 수거 → _inbox 사본 + Downloads 원본은 수거완료 폴더로 이동
    tmp, root, dl, inbox, ex, cfg = fresh()
    write(dl / name, '{"a":1}'); write(dl / rq, '{"rq":1}'); write(dl / "무관한파일.json", "{}"); write(dl / "메모.txt", "x")
    r, w = run(root, "gongin", ex, cfg, dl)
    sweep = dl / "_오답_수거완료"
    check(r["copied"] == 2 and r["moved"] == 2 and r["collided"] == 0, "① 신규 2건 수거·2건 이동 (copied=%s moved=%s)" % (r["copied"], r["moved"]))
    check((inbox / name).read_text() == '{"a":1}' and (inbox / rq).exists(), "① _inbox 사본 내용 일치")
    check(not (dl / name).exists() and (sweep / name).exists() and (sweep / rq).exists(), "① 원본은 Downloads/_오답_수거완료/ 로")
    check((dl / "무관한파일.json").exists() and (dl / "메모.txt").exists(), "① 글롭 밖 파일은 불변")
    check(r["sweep_dir"] == str(sweep) and not [x for x in w if "build_ledger" not in x], "① 수거 경고 없음(원장 생략 경고는 테스트 설정)")

    # 2) 같은 이름·같은 내용이 다시 떨어짐 → 복사 없이 이동만
    write(dl / name, '{"a":1}')
    r, w = run(root, "gongin", ex, cfg, dl)
    check(r["copied"] == 0 and r["moved"] == 1, "② 동일 내용 재등장 → 복사 0·이동 1")
    check((sweep / (name[:-5] + " (1).json")).exists(), "② 수거완료 폴더 이름 충돌은 ' (1)' 부여")

    # 3) 같은 이름·다른 내용(원본이 치워진 뒤 같은 날 재저장) → _inbox ' (1)' 사본, mtime 보존
    later = time.time() + 60
    write(dl / name, '{"a":2}', mtime=later)
    r, w = run(root, "gongin", ex, cfg, dl)
    alt = inbox / (name[:-5] + " (1).json")
    check(r["copied"] == 1 and r["collided"] == 1 and r["moved"] == 1, "③ 동명이본 → ' (1)' 사본 추가 수거 + 이동")
    check(alt.exists() and alt.read_text() == '{"a":2}' and (inbox / name).read_text() == '{"a":1}', "③ 원 사본 불변 · 새 내용은 (1)에")
    check(abs(alt.stat().st_mtime - later) < 2 and alt.stat().st_mtime > (inbox / name).stat().st_mtime, "③ (1) 사본 mtime 보존(원장이 최신본 채택)")

    # 4) 같은 다른 내용이 또 떨어짐(브라우저 사본 등) → 기존 (1)과 일치하므로 추가 복사 없이 이동
    write(dl / name, '{"a":2}')
    r, w = run(root, "gongin", ex, cfg, dl)
    check(r["copied"] == 0 and r["moved"] == 1 and not (inbox / (name[:-5] + " (2).json")).exists(), "④ 기존 (1)과 일치 → 복사 0·이동 1")

    # 5) 세 번째 내용 → (2)
    write(dl / name, '{"a":3}', mtime=later + 60)
    r, w = run(root, "gongin", ex, cfg, dl)
    check((inbox / (name[:-5] + " (2).json")).read_text() == '{"a":3}' and r["collided"] == 1, "⑤ 세 번째 내용 → (2)")

    # 6) 브라우저 ' (1)' 사본이 Downloads 에 직접 떨어지는 종전 경로도 그대로
    write(dl / (rq[:-5] + " (1).json"), '{"rq":2}')
    r, w = run(root, "gongin", ex, cfg, dl)
    check((inbox / (rq[:-5] + " (1).json")).exists() and r["moved"] == 1, "⑥ Downloads 의 ' (1)' 사본 수거·이동")
    shutil.rmtree(tmp)

    # 7) sweep_dir null → 종전대로 Downloads 불변
    tmp, root, dl, inbox, ex, cfg = fresh(sweep=None)
    write(dl / name, '{"a":1}')
    r, w = run(root, "gongin", ex, cfg, dl)
    check(r["copied"] == 1 and r["moved"] == 0 and (dl / name).exists() and r["sweep_dir"] is None, "⑦ downloads_sweep_dir null → 이동 없음")
    shutil.rmtree(tmp)

    # 8) 레거시 접두어(법무사_ → 법무사2차_) + legacy_until 이후 파일은 건너뜀
    tmp, root, dl, inbox, ex, cfg = fresh(exam="bupsa2")
    write(dl / "법무사_오답_2026-08-24.json", '{"l":1}')
    write(dl / "법무사_오답_2026-12-01.json", '{"l":2}')      # legacy_until(2026-09-30) 이후
    write(dl / "법무사2차_오답_2026-09-20-RQ.json", '{"b":1}')
    r, w = run(root, "bupsa2", ex, cfg, dl)
    check((inbox / "법무사2차_오답_2026-08-24.json").exists() and not (dl / "법무사_오답_2026-08-24.json").exists(), "⑧ 레거시 접두어 변환 수거 + 원본 이동")
    check((dl / "법무사_오답_2026-12-01.json").exists() and not (inbox / "법무사2차_오답_2026-12-01.json").exists(), "⑧ legacy_until 이후 파일은 수거·이동 모두 안 함")
    check((inbox / "법무사2차_오답_2026-09-20-RQ.json").exists() and r["moved"] == 2, "⑧ 표준 글롭 수거·이동 (moved=%s)" % r["moved"])

    # 9) Downloads 미연결 → 경고만
    r, w = run(root, "bupsa2", ex, cfg, None)
    check(r["downloads"] == "unmounted" and any("미연결" in x for x in w) and r["moved"] == 0, "⑨ Downloads 미연결 경고")
    shutil.rmtree(tmp)

    # 10) 다른 시험 파일은 이 시험 수거에서 불가침
    tmp, root, dl, inbox, ex, cfg = fresh(exam="gongin")
    write(dl / "법무사2차_오답_2026-09-20.json", '{"b":1}')
    r, w = run(root, "gongin", ex, cfg, dl)
    check(r["copied"] == 0 and r["moved"] == 0 and (dl / "법무사2차_오답_2026-09-20.json").exists(), "⑩ 타 시험 파일 불가침")
    shutil.rmtree(tmp)

    print()
    if FAILS:
        print("❌ ingest_smoke 실패 %d건" % len(FAILS)); return 1
    print("✅ ingest_smoke 통과"); return 0


if __name__ == "__main__":
    sys.exit(main())
