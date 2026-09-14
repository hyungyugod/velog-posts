#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HG 무한복습체계 · extract_anki_candidates.py 스모크 (2026-09-14 신설)
  사용: python3 _시험엔진/engine/tests/candidates_smoke.py
  픽스처·산출물은 velog-posts 바깥(TEST_HOME, 기본 /tmp/hg-tests)에만 만든다.

검사 항목
  1 창 계산: 파일명 날짜 기준(창 밖 노트 제외)
  2 표식 카운트: ★★/★/n:/{} (인라인 {}·!! 원표기 포함)
  3 금지 3경로: ⓐ 줄 안 ⚠️ ⓑ 하단 표 위치·키워드 역참조 + (⚠️ N) 인라인 참조(행 없으면 금지) + 범위=전체는 일반 주의문 ⓒ 백지보고서 ⑦
  4 혼동 카드 머리 ⚠️는 경고가 아님
  5 기출고 key·원장 상습(기출고 제외·실수 전용 표시)
  6 직전 검수리포트 이월(상단 N행 소진 건너뜀)·보류(대기 주수 +1, 3주 표면화) 파싱
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
SCRIPT = ENGINE / "extract_anki_candidates.py"
TEST_HOME = Path(os.environ.get("TEST_HOME", "/tmp/hg-tests"))
ROOT = TEST_HOME / "cand_root"

fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


def w(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    (ROOT / "_시험엔진" / "engine").mkdir(parents=True)
    shutil.copy(ENGINE / "exams.json", ROOT / "_시험엔진" / "engine" / "exams.json")
    # 노트 1 — 신양식 표 + 인라인 참조 + 혼동 카드
    w(ROOT / "공인중개사" / "2026-09-10-부동산공법-(스모크 노트).md", """# 📌 1. 스모크

## 1-1. 대제목
### 1) 소제목
- ★★ 정상 항목 하나 — 편입되어야 한다
- ★ 오피스텔 "3000 이하일 때 가능" — 하단 표 #1이 지목(범위 항목)
- ★ 인라인 참조 항목 (⚠️ 2)
- ★★ 표에 없는 행을 가리키는 항목 (⚠️ 9)
- n: 신고는 7일 이내에 한다
- 세율은 {반일제고}다 — 인라인 중괄호
### 2) 다른 소제목
- ★ 같은 소제목 아님 — 오피스텔 언급해도 1)만 지목이므로 여기는 살아야 한다: 오피스텔 3000
- ⚠️ 혼동 카드: A vs B — 이 줄의 ⚠️는 경고가 아니다 {판별식}

## ⚠️ 확인 필요
| # | 위치 | 원문 표현 | 확인 포인트 | 범위 |
|---|---|---|---|---|
| 1 | 1-1 1) | "3000 이하일 때 가능" | 미만/이하 | 항목 |
| 2 | 1-1 1) | 인라인 참조 항목 | 확인 | 항목 |
| 3 | 전체 | 세율·수치 | 개정 가능성 | 전체 |

■ 백지시트 (1단계) — 스모크
- ★ 백지시트 안의 표식은 세지 않는다
""")
    # 노트 2 — 구양식(번호 불릿) + 창 밖 노트
    w(ROOT / "공인중개사" / "2026-09-08-민법-(구양식).md", """# 📌 1. 구양식

## 1-4. 비진의표시
### 1) 소제목
- ★ 대리권 남용은 무권대리에 해당한다
- !! 원표기 느낌표 항목
- ! 원표기 느낌표 하나

## ⚠️ 확인 필요

1. **대리권 남용 (1-4)** — 메모는 "무권대리에 해당한다"로 되어 있다. 원문 확인 필요.
""")
    w(ROOT / "공인중개사" / "2026-08-30-민법-(창 밖).md", "- ★★ 창 밖이라 세지 않는다\n")
    # 법무사 2차 노트 (트랙 스위치)
    w(ROOT / "법무사" / "2026-09-12-형법-2차-(스모크).md", "## 1-1. 절도\n### 1) 소제목\n- ★★ 법무사 2차 항목\n")
    w(ROOT / "법무사" / "2026-09-12-헌법-(1차 스모크).md", "- ★★ 1차 항목 — bupsa1로만 잡혀야 한다\n")
    # 백지복습 보고서 ⑦ → 노트1의 '정상 항목 하나'를 지목
    w(ROOT / "공인중개사" / "백지복습" / "2026-09-11-부동산공법-(백지복습_스모크 노트).md", """---
type: 백지복습보고서
exam: 공인중개사
subject: 부동산공법
topic: 스모크 노트
source: 2026-09-10-부동산공법-(스모크 노트).md
rounds: 1
recall: [50]
last_stage: 1
status: 열림
updated: 2026-09-11
---
## ③ 남은 구멍 (최우선 재출제)
| 우선순위 | 덩어리 | 개념 | 정답 |
|---|---|---|---|
| 1 | ① | 구멍 개념 | 구멍 정답 |
## ⑦ ⚠️ 확인 필요 (정리본에서 승계 — 출제 금지 유지)
| # | 필기 내용 | 확인 포인트 | 상태 |
|---|---|---|---|
| 1 | "정상 항목 하나" | 사실은 의심 | 미확인 |
""")
    # 기출고 key
    w(ROOT / "_시험엔진" / "anki" / "카드_2026-09-07.tsv",
      "deck\ttype\tfront\tback\ttags\tsrc\tkey\n자격증::공인중개사::민법\tbasic\tq\ta\tt\ts\t민법 1-1\n")
    # 원장
    w(ROOT / "공인중개사" / "claude_ox_오답" / "_ledger" / "오답_원장.json", json.dumps({"ledger": [
        {"conceptKey": "민법 1-1", "subject": "민법", "timesWrong": 3, "retryMissed": 2, "errorCauses": {}, "samples": []},
        {"conceptKey": "공법 2-2", "subject": "부동산공법", "timesWrong": 2, "retryMissed": 0, "errorCauses": {"실수": 2}, "samples": [{"q": "q", "expl": "e"}]},
        {"conceptKey": "공법 3-3", "subject": "부동산공법", "timesWrong": 1, "retryMissed": 0, "errorCauses": {}, "samples": []},
    ]}, ensure_ascii=False))
    # 직전 검수리포트
    w(ROOT / "_시험엔진" / "anki" / "출고" / "검수_2026-09-07.md", """# 검수리포트

## 이월 (다음 주 우선)

> ✅ 소진 — 아래 상단 2행은 특집으로 소진됐다.

| 원천 | 레인 | 항목 | 이월 횟수 | 사유 |
|---|---|---|---|---|
| 소진된 노트 | ★★ | 소진 1 | 1 | 특집 |
| 소진된 노트 | ★ | 소진 2 | 1 | 특집 |
| 백지 A | 백지구멍 | 살아 있는 이월 | 1 | 상한 |

| 노트 | 표 | 두번째 | 표는 | 안읽는다 |
|---|---|---|---|---|
| x | y | z | w | v |

## 보류 (사용자 확정 대기)

| 원천 | 항목 | 지목 근거 | 대기 주수 | 해소 조건 |
|---|---|---|---|---|
| 노트 X | 오래된 보류 | 하단 #1 | 2 | 정리본 확정 |
| 노트 Y | 새 보류 | 백지 ⑦ | 1 | 정리본 확정 |
""")


def main():
    print("── 후보 추출기 스모크 (extract_anki_candidates.py)")
    if not SCRIPT.exists():
        print("❌ 스크립트 없음:", SCRIPT)
        return 1
    build_fixture()
    out = TEST_HOME / "cand_out" / "후보_2026-09-14.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "--date", "2026-09-14", "--root", str(ROOT), "--out", str(out), "--json"],
                       capture_output=True, text=True)
    check(r.returncode == 0, f"exit 0 (stderr: {r.stderr.strip()[:200]})")
    if r.returncode != 0:
        return 1
    d = json.loads(out.read_text(encoding="utf-8"))
    check(out.with_suffix(".md").exists(), ".md 요약 생성")
    notes = {n["file"]: n for n in d["notes"]}
    # 1 창 계산 · 트랙 스위치
    check("2026-08-30-민법-(창 밖).md" not in notes, "창 밖 노트 제외")
    check(any(n["exam"] == "bupsa2" and "형법-2차" in n["file"] for n in d["notes"]), "법무사 2차 노트는 bupsa2")
    check(all(not (n["exam"] == "bupsa1" and "-2차-" in n["file"]) for n in d["notes"]), "bupsa1에 -2차- 노트 없음")
    check(any(n["exam"] == "bupsa1" and "헌법" in n["file"] for n in d["notes"]), "1차 노트는 bupsa1")
    # 2 표식 카운트
    n1 = notes["2026-09-10-부동산공법-(스모크 노트).md"]
    check(n1["marks"] == {"★★": 2, "★": 3, "n:": 1, "{}": 2}, f"노트1 표식 {n1['marks']} == ★★2 ★3 n:1 {{}}2 (백지시트 이후 제외)")
    n2 = notes["2026-09-08-민법-(구양식).md"]
    check(n2["marks"]["★★"] == 1 and n2["marks"]["★"] == 2, f"!!/! 원표기 승계 {n2['marks']}")
    # 3 금지 경로
    b1 = {b["line"]: b["reasons"] for b in n1["banned"]}
    check(any("하단 ⚠️표 #1" in x for x in b1.get(6, [])), "표 #1 위치+따옴표 키워드 → L6 금지")
    check(7 in b1 and any("인라인 참조" in x for x in b1[7]), "(⚠️ 2) 인라인 참조 → L7 금지")
    check(8 in b1 and any("해당 행 없음" in x for x in b1[8]), "(⚠️ 9) 표에 행 없음 → L8 안전 쪽 금지")
    check(12 not in b1, "다른 소제목의 '오피스텔 3000' 줄(L12)은 위치가 달라 금지되지 않음")
    check(13 not in b1, "혼동 카드 머리 ⚠️(L13)는 경고 아님")
    check(len(n1["general_notices"]) == 1, "범위=전체 행 → 일반 주의문 1건(금지 아님)")
    check(n1["warn_format"] == "v3.11", "신양식 표 인식")
    check(5 in b1 and any("백지보고서 ⑦" in x for x in b1[5]), "백지보고서 ⑦ → L5 '정상 항목 하나' 금지")
    check(9 not in b1 and 10 not in b1, "키워드 미매칭 행이 소제목 전체를 금지하지 않음(L9·L10 생존)")
    items_ok = [it for it in n1["items"] if not it["banned"]]
    check(any(it["braces"] == ["반일제고"] for it in n1["items"]), "인라인 {반일제고} 추출")
    check(any(it["braces"] == ["판별식"] and not it["banned"] for it in n1["items"]), "혼동 카드 줄의 {판별식}은 살아 있음")
    b2 = {b["line"]: b["reasons"] for b in n2["banned"]}
    check(5 in b2 and any("하단 ⚠️표" in x for x in b2[5]), "구양식 번호 불릿 (1-4)+키워드 → L5 금지")
    check(n2["warn_format"] == "legacy", "구양식 인식")
    # 5 기출고 · 상습
    check(d["existing_keys"] == 1, "기출고 key 1개")
    hab = d["habitual"]["gongin"]
    check(any(h["conceptKey"] == "민법 1-1" and h["already_issued"] for h in hab), "상습: 기출고 key 표시")
    check(any(h["conceptKey"] == "공법 2-2" and h["only_slip"] for h in hab), "상습: 실수 전용 표시")
    check(all(h["conceptKey"] != "공법 3-3" for h in hab), "tw1 rm0은 상습 아님")
    # 6 직전 리포트
    pv = d["prev_report"]
    check(pv["file"] == "검수_2026-09-07.md", "직전 정규 검수리포트 선택")
    check(len(pv["carry"]) == 1 and pv["carry"][0]["항목"] == "살아 있는 이월", f"이월: 상단 2행 소진 건너뜀·두 번째 표 무시 → 1행 ({[c['항목'] for c in pv['carry']]})")
    hold = {h["항목"]: h for h in pv["hold"]}
    check(hold.get("오래된 보류", {}).get("대기 주수") == 3 and hold["오래된 보류"]["표면화"], "보류: 대기 주수 2→3, 3주 표면화")
    check(hold.get("새 보류", {}).get("대기 주수") == 2 and not hold["새 보류"]["표면화"], "보류: 대기 주수 1→2")
    # n:
    check(len(n1["n_lines"]) == 1 and n1["n_lines"][0]["line"] == 9, "n: 줄 수집")
    print()
    if fails:
        print(f"❌ 후보 추출기 스모크 실패 {len(fails)}건")
        return 1
    print("✅ 후보 추출기 스모크 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
