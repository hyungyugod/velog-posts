#!/usr/bin/env bash
# HG 무한복습체계 · build_apkg.py 스모크 (2026-09-03 신설 — 주간 공급 소프트 상한)
#   사용: bash _시험엔진/engine/tests/apkg_smoke.sh
#   픽스처·산출물은 velog-posts 바깥(TEST_HOME, 기본 /tmp/hg-tests)에만 만든다.
#   genanki 가 없으면 설치를 한 번 시도하고, 그래도 없으면 SKIP + exit 0 (회귀 러너를 깨지 않는다).
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILDER="$HERE/../build_apkg.py"
TEST_HOME="${TEST_HOME:-/tmp/hg-tests}"
WORK="$TEST_HOME/apkg"

echo "── apkg 스모크 (build_apkg.py)"

command -v python3 >/dev/null || { echo "SKIP python3 없음 — apkg 스모크 건너뜀"; exit 0; }
[ -f "$BUILDER" ] || { echo "❌ 빌더를 찾을 수 없다: $BUILDER"; exit 1; }

if ! python3 -c "import genanki" >/dev/null 2>&1; then
  pip install genanki --break-system-packages >/dev/null 2>&1 \
    || pip3 install genanki --break-system-packages >/dev/null 2>&1 || true
fi
if ! python3 -c "import genanki" >/dev/null 2>&1; then
  echo "SKIP genanki 없음 — apkg 스모크 건너뜀"
  exit 0
fi

rm -rf "$WORK"
mkdir -p "$WORK"

# 픽스처 3행: basic 1 + cloze 1빈칸 1 + cloze 2빈칸 1 = 카드 4장
write_fixture() {  # $1 = TSV 경로
  {
    printf 'deck\ttype\tfront\tback\ttags\tsrc\tkey\n'
    printf '자격증::테스트::스모크\tbasic\t스모크 앞면 — 사실 1은?\t스모크 뒷면 1\t테스트 스모크\t스모크노트.md\tsmoke-basic-1\n'
    printf '자격증::테스트::스모크\tcloze\t스모크 신고기한은 {{c1::60일}} 이내\t보충 설명 1\t테스트 스모크\t스모크노트.md\tsmoke-cloze-1\n'
    printf '자격증::테스트::스모크\tcloze\t스모크 동의요건 토지면적 {{c1::3분의 2}} 이상 + 총수 {{c2::2분의 1}} 이상\t보충 설명 2\t테스트 스모크\t스모크노트.md\tsmoke-cloze-2\n'
  } > "$1"
}

fail=0
assert_has() {      # $1=라벨 $2=출력 $3=기대 문자열
  if printf '%s' "$2" | grep -qF -- "$3"; then
    echo "  ✓ $1"
  else
    echo "  ✗ $1 — 기대 문자열이 없다: $3"; fail=1
  fi
}
assert_absent() {   # $1=라벨 $2=출력 $3=없어야 할 문자열
  if printf '%s' "$2" | grep -qF -- "$3"; then
    echo "  ✗ $1 — 없어야 할 문자열이 있다: $3"; fail=1
  else
    echo "  ✓ $1"
  fi
}
assert_rc() {       # $1=라벨 $2=실제 rc $3=기대 rc
  if [ "$2" -eq "$3" ]; then echo "  ✓ $1"; else echo "  ✗ $1 — exit $2 (기대 $3)"; fail=1; fi
}

# ── 1) 정규 덱 — 검증 통과 + 카드 4장 + 주간 상한 정보 1줄
REG="$WORK/카드_2026-01-01.tsv"
write_fixture "$REG"
out="$(python3 "$BUILDER" "$REG" 2>&1)"; rc=$?
assert_rc  "정규 덱 exit 0"            "$rc" 0
assert_has "정규 덱 [검증 통과]"        "$out" "[검증 통과]"
assert_has "정규 덱 카드 4장"           "$out" "총 카드 수 : 4장"
assert_has "정규 덱 주간 상한 표기"      "$out" "주간 상한 :"

# ── 2) 특집 덱 — 상한 밖(주간 상한 줄이 없어야 한다)
SP="$WORK/카드_2026-01-01-테스트특집.tsv"
write_fixture "$SP"
out2="$(python3 "$BUILDER" "$SP" 2>&1)"; rc2=$?
assert_rc     "특집 덱 exit 0"          "$rc2" 0
assert_has    "특집 덱 [검증 통과]"      "$out2" "[검증 통과]"
assert_absent "특집 덱 상한 제외"        "$out2" "주간 상한 :"

# ── 3) 상한 초과 — 경고만 내고 exit 0 (테스트 전용 환경변수로 상한을 3장으로 낮춘다)
out3="$(HG_ANKI_CEILING_OVERRIDE=3 python3 "$BUILDER" "$REG" 2>&1)"; rc3=$?
assert_rc  "상한 초과 exit 0(차단 없음)" "$rc3" 0
assert_has "상한 초과 경고"              "$out3" "[경고] 총 카드 4장 > 주간 소프트 상한 3장"
assert_has "상한 초과에도 [검증 통과]"    "$out3" "[검증 통과]"

echo
if [ "$fail" -eq 0 ]; then
  echo "✅ apkg 스모크 통과 (10건)"
else
  echo "❌ apkg 스모크 실패"
fi
exit "$fail"
