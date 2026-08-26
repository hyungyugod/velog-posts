#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_apkg.py — 카드_YYYY-MM-DD.tsv 를 Anki .apkg 로 굽는 결정론적 빌더.

사용법
    python3 build_apkg.py /경로/카드_2026-08-26.tsv

입력 TSV (헤더 필수, 탭 구분, 따옴표 이스케이프 없음 = QUOTE_NONE)
    deck   type   front   back   tags   src   key
      · deck  : "자격증::공인중개사::세법" 처럼 :: 로 구분한 덱 경로
      · type  : basic | cloze
      · front : 앞면. cloze 는 {{c1::...}} 문법을 반드시 포함
      · back  : 뒷면(basic 필수 / cloze 는 보충설명이라 비어도 경고만)
      · tags  : 공백으로 구분한 태그들
      · src   : 출처 노트 파일명 (카드 하단에 작은 글씨로 박힘)
      · key   : 개념 고유키 — guid 의 씨앗. 같은 key 면 Anki 가 갱신한다

출력
    <TSV 폴더>/출고/YYYY-MM-DD.apkg   (날짜는 TSV 파일명에서 뽑는다)

결정론 보장
    · 모델 ID  : 아래 고정 상수 (랜덤 금지)
    · 덱   ID  : md5(덱 이름) → 정수
    · 노트 guid: md5(key) → base91 (Anki 네이티브 형식)
    ⇒ 같은 TSV 를 몇 번 돌려도 같은 ID 가 나오고, 같은 key 는 새 노트가 아니라
      기존 노트의 갱신으로 들어간다.

의존성
    pip install genanki --break-system-packages
"""

import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict

try:
    import genanki
except ImportError:
    print("오류: genanki 가 설치되어 있지 않다.", file=sys.stderr)
    print("      pip install genanki --break-system-packages", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# 고정 상수 — 절대 바꾸지 말 것. 바꾸면 기존 사용자 덱과 모델이 갈라진다.
# 값 출처: md5("시험엔진::anki::model::basic::v1") 등을 [2^30, 2^31) 로 접은 것
# ─────────────────────────────────────────────────────────────────────────────
MODEL_ID_BASIC = 1773460535
MODEL_ID_CLOZE = 2099921963

MODEL_NAME_BASIC = "시험엔진 기본 v1"
MODEL_NAME_CLOZE = "시험엔진 빈칸 v1"

REQUIRED_COLUMNS = ["deck", "type", "front", "back", "tags", "src", "key"]
VALID_TYPES = {"basic", "cloze"}

# 한국어 가독성 우선 시스템 폰트 스택 + 중앙 정렬 + 정답 강조색
CARD_CSS = """
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
               "Malgun Gothic", "맑은 고딕", "Noto Sans KR",
               "Segoe UI", Roboto, sans-serif;
  font-size: 21px;
  line-height: 1.75;
  text-align: center;
  color: #1c1c1e;
  background-color: #ffffff;
  padding: 18px 14px;
  word-break: keep-all;
}
.card.nightMode, .card.night_mode {
  color: #e6e6e6;
  background-color: #1c1c1e;
}
hr#answer, hr {
  border: none;
  border-top: 1px solid #d8d8dc;
  margin: 18px auto;
  width: 62%;
}
.answer {
  color: #1D9E75;
  font-weight: 700;
}
.cloze {
  color: #1D9E75;
  font-weight: 700;
}
.src {
  margin-top: 22px;
  font-size: 12px;
  color: #9a9aa0;
  letter-spacing: 0.01em;
}
b { font-weight: 700; }
"""

BASIC_QFMT = "<div class=\"front\">{{Front}}</div>"
BASIC_AFMT = (
    "{{FrontSide}}"
    "<hr id=answer>"
    "<div class=\"answer\">{{Back}}</div>"
    "{{#Src}}<div class=\"src\">출처 · {{Src}}</div>{{/Src}}"
)

CLOZE_QFMT = "<div class=\"front\">{{cloze:Text}}</div>"
CLOZE_AFMT = (
    "<div class=\"front\">{{cloze:Text}}</div>"
    "{{#Back}}<hr id=answer><div class=\"answer\">{{Back}}</div>{{/Back}}"
    "{{#Src}}<div class=\"src\">출처 · {{Src}}</div>{{/Src}}"
)


# ─────────────────────────────────────────────────────────────────────────────
# 결정론적 ID / guid
# ─────────────────────────────────────────────────────────────────────────────
_BASE91 = list(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    "!#$%&()*+,-./:;<=>?@[]^_`{|}~"
)


def _md5_int(text):
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)


def deck_id_for(deck_name):
    """덱 이름의 md5 → [2^30, 2^31) 정수. 재실행해도 항상 같다."""
    return (_md5_int(deck_name) % (2 ** 31 - 2 ** 30)) + 2 ** 30


def guid_for_key(key):
    """key 의 md5 앞 8바이트 → base91. 같은 key = 같은 guid = Anki 에서 갱신."""
    digest = hashlib.md5(key.encode("utf-8")).digest()[:8]
    num = int.from_bytes(digest, "big")
    if num == 0:
        return _BASE91[0]
    out = []
    base = len(_BASE91)
    while num > 0:
        num, rem = divmod(num, base)
        out.append(_BASE91[rem])
    return "".join(reversed(out))


# ─────────────────────────────────────────────────────────────────────────────
# 검증
# ─────────────────────────────────────────────────────────────────────────────
CLOZE_RE = re.compile(r"\{\{c(\d+)::(.*?)\}\}", re.DOTALL)


def check_cloze(front):
    """cloze front 문법 점검. 문제 있으면 사유 문자열 리스트를 돌려준다."""
    problems = []
    if "{{c" not in front:
        problems.append("'{{c' 자체가 없다 — cloze 로 선언했는데 빈칸이 하나도 없다")
        return problems
    matches = CLOZE_RE.findall(front)
    if not matches:
        problems.append("'{{cN::내용}}' 형태로 닫히는 빈칸이 없다 (:: 누락이나 }} 미닫힘 의심)")
    # 여는 '{{c' 개수와 실제로 파싱된 빈칸 개수가 다르면 미닫힘
    opens = len(re.findall(r"\{\{c", front))
    if matches and opens != len(matches):
        problems.append(f"'{{{{c' {opens}개 중 {len(matches)}개만 정상으로 닫혔다")
    # 번호가 1부터인지
    for num, _ in matches:
        if int(num) < 1:
            problems.append(f"빈칸 번호 c{num} — 번호는 1 이상이어야 한다")
    # 내용이 빈 빈칸
    for num, body in matches:
        if not body.strip():
            problems.append(f"c{num} 빈칸의 내용이 비어 있다")
    # 중괄호 균형
    if front.count("{{") != front.count("}}"):
        problems.append(f"중괄호 불균형 — '{{{{' {front.count('{{')}개 vs '}}}}' {front.count('}}')}개")
    return problems


def read_tsv(path):
    """TSV 를 읽어 (행 리스트, 경고 리스트, 오류 리스트) 반환."""
    warnings, errors = [], []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        header = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            errors.append(f"헤더에 필수 컬럼이 없다: {', '.join(missing)} (현재 헤더: {header})")
            return [], warnings, errors
        extra = [c for c in header if c not in REQUIRED_COLUMNS]
        if extra:
            warnings.append(f"헤더에 모르는 컬럼이 있다(무시함): {', '.join(extra)}")

        rows = []
        for lineno, raw in enumerate(reader, start=2):
            row = {c: (raw.get(c) or "").strip() for c in REQUIRED_COLUMNS}
            if not any(row.values()):
                continue  # 빈 줄
            row["_line"] = lineno
            rows.append(row)
    return rows, warnings, errors


def validate(rows):
    """입력 검증. (경고, 오류) 반환. 오류가 하나라도 있으면 빌드하지 않는다."""
    warnings, errors = [], []

    # key 중복
    key_lines = defaultdict(list)
    for r in rows:
        if r["key"]:
            key_lines[r["key"]].append(r["_line"])
    for key, lines in sorted(key_lines.items()):
        if len(lines) > 1:
            errors.append(f"key 중복: '{key}' — {len(lines)}행({', '.join(map(str, lines))})에 같은 key 가 있다")

    for r in rows:
        ln = r["_line"]
        # 필수값
        if not r["key"]:
            errors.append(f"{ln}행: key 가 비어 있다")
        if not r["deck"]:
            errors.append(f"{ln}행: deck 이 비어 있다")
        # 타입
        ctype = r["type"].lower()
        if ctype not in VALID_TYPES:
            errors.append(f"{ln}행: type 이 '{r['type']}' 이다 — basic 또는 cloze 만 허용")
            continue
        r["type"] = ctype

        # front / back 빈 값
        if not r["front"]:
            errors.append(f"{ln}행: front 가 비어 있다 (key={r['key']})")
        if not r["back"]:
            if ctype == "basic":
                errors.append(f"{ln}행: back 이 비어 있다 (key={r['key']}) — basic 은 뒷면이 필수")
            else:
                warnings.append(f"{ln}행: cloze 의 back(보충설명)이 비어 있다 (key={r['key']}) — 카드는 만들어진다")

        # cloze 문법
        if ctype == "cloze" and r["front"]:
            for p in check_cloze(r["front"]):
                errors.append(f"{ln}행 cloze 문법 오류 (key={r['key']}): {p}")
        if ctype == "basic" and "{{c" in r["front"]:
            warnings.append(f"{ln}행: basic 인데 front 에 '{{{{c' 가 있다 — cloze 로 넣을 생각이었나 (key={r['key']})")

        # 큰따옴표 / 백틱 — 차단이 아니라 경고
        for field in ("front", "back"):
            val = r[field]
            if '"' in val:
                warnings.append(f"{ln}행 {field}: 큰따옴표(\") 가 있다 — 렌더링은 되지만 확인해 볼 것 (key={r['key']})")
            if "`" in val:
                warnings.append(f"{ln}행 {field}: 백틱(`) 이 있다 — 렌더링은 되지만 확인해 볼 것 (key={r['key']})")

        # 태그 안의 이상 문자
        for t in r["tags"].split():
            if any(ch in t for ch in '"\''):
                warnings.append(f"{ln}행 tags: 태그 '{t}' 에 따옴표가 있다 (key={r['key']})")

    return warnings, errors


# ─────────────────────────────────────────────────────────────────────────────
# 빌드
# ─────────────────────────────────────────────────────────────────────────────
def make_models():
    basic = genanki.Model(
        MODEL_ID_BASIC,
        MODEL_NAME_BASIC,
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Src"}],
        templates=[{"name": "기본", "qfmt": BASIC_QFMT, "afmt": BASIC_AFMT}],
        css=CARD_CSS,
    )
    cloze = genanki.Model(
        MODEL_ID_CLOZE,
        MODEL_NAME_CLOZE,
        fields=[{"name": "Text"}, {"name": "Back"}, {"name": "Src"}],
        templates=[{"name": "빈칸", "qfmt": CLOZE_QFMT, "afmt": CLOZE_AFMT}],
        css=CARD_CSS,
        model_type=genanki.Model.CLOZE,
    )
    return basic, cloze


def build(rows, out_path):
    basic_model, cloze_model = make_models()
    decks = {}
    for r in rows:
        name = r["deck"]
        if name not in decks:
            decks[name] = genanki.Deck(deck_id_for(name), name)
        model = cloze_model if r["type"] == "cloze" else basic_model
        note = genanki.Note(
            model=model,
            fields=[r["front"], r["back"], r["src"]],
            tags=r["tags"].split(),
            guid=guid_for_key(r["key"]),
        )
        decks[name].add_note(note)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # 덱 이름 순으로 고정 정렬 — 재실행 시 패키지 내부 순서도 동일하게
    package = genanki.Package([decks[n] for n in sorted(decks)])
    package.write_to_file(out_path)
    return decks


# ─────────────────────────────────────────────────────────────────────────────
# 산출물 재검증 — 실제로 .apkg 를 열어 확인한다
# ─────────────────────────────────────────────────────────────────────────────
def inspect_apkg(apkg_path):
    """생성된 apkg 를 zipfile+sqlite3 로 열어 (노트수, 카드수, {덱이름: 카드수}) 반환."""
    with zipfile.ZipFile(apkg_path) as z:
        names = z.namelist()
        member = None
        for cand in ("collection.anki21", "collection.anki2"):
            if cand in names:
                member = cand
                break
        if member is None:
            raise RuntimeError(f"apkg 안에 collection.anki2(1) 이 없다: {names}")
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, member)
            with open(db_path, "wb") as fh:
                fh.write(z.read(member))
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            note_count = cur.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            card_count = cur.execute("SELECT COUNT(*) FROM cards").fetchone()[0]

            # 덱 이름 매핑 — 스키마 11(col.decks JSON) / 스키마 18(decks 테이블) 모두 대응
            id2name = {}
            try:
                blob = cur.execute("SELECT decks FROM col").fetchone()[0]
                for did, meta in json.loads(blob).items():
                    id2name[int(did)] = meta["name"]
            except Exception:
                for did, name in cur.execute("SELECT id, name FROM decks"):
                    id2name[int(did)] = name.replace("\x1f", "::")

            per_deck = Counter()
            for did, n in cur.execute("SELECT did, COUNT(*) FROM cards GROUP BY did"):
                per_deck[id2name.get(int(did), f"(알 수 없는 덱 id {did})")] += n
            con.close()
    return note_count, card_count, dict(per_deck)


# ─────────────────────────────────────────────────────────────────────────────
def main(argv):
    if len(argv) != 2:
        print("사용법: python3 build_apkg.py <카드_YYYY-MM-DD.tsv 경로>", file=sys.stderr)
        return 1

    tsv_path = os.path.abspath(argv[1])
    if not os.path.isfile(tsv_path):
        print(f"오류: TSV 파일을 찾을 수 없다 — {tsv_path}", file=sys.stderr)
        return 1

    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(tsv_path))
    if not m:
        print(f"오류: 파일명에서 날짜(YYYY-MM-DD)를 찾을 수 없다 — {os.path.basename(tsv_path)}", file=sys.stderr)
        print("      예: 카드_2026-08-26.tsv", file=sys.stderr)
        return 1
    date_str = m.group(1)

    out_dir = os.path.join(os.path.dirname(tsv_path), "출고")
    out_path = os.path.join(out_dir, f"{date_str}.apkg")

    print("=" * 62)
    print(f"입력  : {tsv_path}")
    print(f"출력  : {out_path}")
    print("=" * 62)

    rows, w1, e1 = read_tsv(tsv_path)
    warnings, errors = list(w1), list(e1)
    if not errors:
        if not rows:
            errors.append("데이터 행이 하나도 없다")
        else:
            w2, e2 = validate(rows)
            warnings += w2
            errors += e2

    # ── 경고 (차단하지 않음)
    if warnings:
        print(f"\n[경고 {len(warnings)}건] — 빌드는 계속한다")
        for w in warnings:
            print(f"  · {w}")

    # ── 오류 (차단)
    if errors:
        print(f"\n[검증 실패] 오류 {len(errors)}건 — .apkg 를 만들지 않았다")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print(f"\n[입력 검증 통과] {len(rows)}행")

    # ── 빌드
    try:
        decks = build(rows, out_path)
    except Exception as exc:
        print(f"\n[빌드 실패] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    # ── 산출물 재검증
    try:
        note_count, card_count, per_deck = inspect_apkg(out_path)
    except Exception as exc:
        print(f"\n[산출물 검증 실패] apkg 를 열 수 없다 — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    type_counts = Counter(r["type"] for r in rows)
    expected_notes = len(rows)
    expected_cards = 0
    for r in rows:
        if r["type"] == "cloze":
            nums = {int(n) for n, _ in CLOZE_RE.findall(r["front"])}
            expected_cards += max(1, len(nums))
        else:
            expected_cards += 1

    print("\n" + "─" * 62)
    print("빌드 결과 검증")
    print("─" * 62)
    print(f"  총 노트 수 : {note_count}장  (기대 {expected_notes}장)")
    print(f"  총 카드 수 : {card_count}장  (기대 {expected_cards}장 — cloze 는 빈칸 번호마다 1장)")
    print(f"  유형별     : basic {type_counts.get('basic', 0)}행 / cloze {type_counts.get('cloze', 0)}행")
    print(f"  덱별 카드 수 ({len(per_deck)}개 덱):")
    for name in sorted(per_deck):
        print(f"    · {name} — {per_deck[name]}장  (덱 id {deck_id_for(name)})")
    print(f"  모델 ID    : basic={MODEL_ID_BASIC} / cloze={MODEL_ID_CLOZE} (고정)")
    print(f"  파일 크기  : {os.path.getsize(out_path):,} 바이트")

    mismatch = []
    if note_count != expected_notes:
        mismatch.append(f"노트 수 불일치 — 기대 {expected_notes}, 실제 {note_count}")
    if card_count != expected_cards:
        mismatch.append(f"카드 수 불일치 — 기대 {expected_cards}, 실제 {card_count}")
    tsv_decks = {r["deck"] for r in rows}
    if set(per_deck) != tsv_decks:
        mismatch.append(f"덱 목록 불일치 — TSV {sorted(tsv_decks)} vs apkg {sorted(per_deck)}")

    if mismatch:
        print(f"\n[산출물 검증 실패] {len(mismatch)}건")
        for msg in mismatch:
            print(f"  ✗ {msg}")
        return 1

    print("\n[검증 통과] 모든 항목 정상")
    print(f"완료: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
