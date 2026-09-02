#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_조립.py — 코어 엔진 + 도메인 모듈 → 조립완성본 자동 생성 (드리프트 방지)

왜 이 스크립트인가:
  조립완성본을 손으로 다시 합치는 동안 세 파일의 형식이 서로 어긋났고(5·7은 맨 합본,
  9는 헤더+구분선), 코어를 고칠 때마다 세 곳을 수동 동기화해야 했다.
  "반드시 일어나야 하는 일은 프롬프트가 아니라 절차로 보장한다" — 조립도 마찬가지.

사용:
  python3 build_조립.py            # 조립완성본 3개 생성/갱신
  python3 build_조립.py --verify   # 드리프트 검사만 (파일 변경 없음, 어긋나면 exit 1)

규칙:
  - 조립완성본(5·7·9)은 이 스크립트가 만든다. 직접 수정 금지 — 고칠 것은 코어(1) 또는 모듈.
  - 코어 파일은 "1_코어엔진_v*.md" 글롭으로 찾는다 → 버전 올려 파일명이 바뀌어도 동작.
  - 입력 파일이 없거나 코어가 2개 이상이면 시끄럽게 실패한다(exit 2). 무음 실패 금지.
"""
import glob
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# (모듈 파일, 출력 파일, 제목, 추가 안내줄 목록)
ASSEMBLIES = [
    ("2_모듈_공인중개사.md", "5_조립완성본_공인중개사.md", "공인중개사 학습", []),
    ("6_모듈_신체손해사정사.md", "7_조립완성본_신체손해사정사.md", "신체손해사정사 학습", []),
    ("8_모듈_투자재무.md", "9_조립완성본_투자재무.md", "투자·재무 학습",
     ["> 인풋은 Self-OS/투자_질문프롬프트_양식_v1.md(Part 2)를 채워 붙이면 됨."]),
    ("12_모듈_법무사.md", "13_조립완성본_법무사.md", "법무사 학습",
     ["> 지식 파일 6개를 함께 업로드할 것: 14_법무사_과목카드.md · 15_법무사_2차훈련시스템.md · 16_법무사_공식카드_파이프라인.md · 18_법무사_2차답안작성술.md · 19_법무사_개정법워치_v1.md · 23_법무사_실행계획_v7.md"]),
]

SEP_CORE = "==================== [코어 엔진] ===================="
SEP_MODULE = "==================== [도메인 모듈] ===================="


def read(path):
    if not os.path.exists(path):
        sys.exit(f"[FAIL] 입력 파일 없음: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").rstrip() + "\n"


def find_core():
    hits = sorted(glob.glob(os.path.join(BASE, "1_코어엔진_v*.md")))
    if len(hits) != 1:
        sys.exit(f"[FAIL] 코어 파일이 정확히 1개여야 함 — 발견 {len(hits)}개: {hits}")
    return hits[0]


def assemble(core_path, core_text, module_name, title, extra_notes):
    module_text = read(os.path.join(BASE, module_name))
    m = re.search(r"코어 엔진 v[\d.]+", core_text.splitlines()[0])
    core_title = m.group(0) if m else core_text.splitlines()[0].lstrip("# ").strip()
    notes = [
        f"> {title}용 Claude/GPT 프로젝트 지침. **이 파일을 통째로 프로젝트 지침에 붙여넣으면 끝.**",
        f"> ⚙️ 자동 생성 파일({os.path.basename(core_path)} + {module_name}) — 직접 수정 금지,",
        "> 코어나 모듈을 고친 뒤 `python3 build_조립.py`를 실행할 것.",
    ] + extra_notes
    parts = [
        f"# 조립완성본 — {title} ({core_title})",
        "",
        "\n".join(notes),
        "",
        SEP_CORE,
        "",
        core_text.rstrip(),
        "",
        SEP_MODULE,
        "",
        module_text.rstrip(),
        "",
    ]
    return "\n".join(parts)


def main():
    verify = "--verify" in sys.argv
    core_path = find_core()
    core_text = read(core_path)
    drift = []
    for module_name, out_name, title, extra in ASSEMBLIES:
        built = assemble(core_path, core_text, module_name, title, extra)
        out_path = os.path.join(BASE, out_name)
        current = None
        if os.path.exists(out_path):
            with open(out_path, encoding="utf-8") as f:
                current = f.read()
        if verify:
            status = "OK" if current == built else "DRIFT"
            if status == "DRIFT":
                drift.append(out_name)
            print(f"[{status}] {out_name}")
        else:
            if current == built:
                print(f"[SKIP] {out_name} (변경 없음)")
            else:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(built)
                print(f"[BUILD] {out_name} ← {os.path.basename(core_path)} + {module_name}")
    if verify and drift:
        print(f"\n드리프트 {len(drift)}건 — `python3 build_조립.py`로 재조립하세요.")
        sys.exit(1)
    print("완료.")


if __name__ == "__main__":
    main()
