#!/usr/bin/env bash
# HG 무한복습체계 · 퀴즈 파이프라인 E2E 스모크 — 전 케이스 러너
#
#   bash _시험엔진/engine/tests/e2e_smoke_all.sh [ROOT] [BASE_DATE]
#     ROOT       기본 /tmp/e2e/velog-posts   (프로덕션 **복사본**. 없으면 여기서 cp -a 로 만든다)
#     BASE_DATE  기본 오늘(YYYY-MM-DD).  D+0 ~ D+3 네 날짜를 쓴다.
#
# 프로덕션 트리는 읽기만 한다. 모든 산출은 ROOT 아래에서만 생긴다.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE="$(dirname "$HERE")"
PROD="$(dirname "$(dirname "$ENGINE")")"
ROOT="${1:-/tmp/e2e/velog-posts}"
D0="${2:-$(date +%F)}"
d() { python3 -c "import datetime,sys;print((datetime.date.fromisoformat(sys.argv[1])+datetime.timedelta(days=int(sys.argv[2]))).isoformat())" "$D0" "$1"; }
D1=$(d 1); D2=$(d 2); D3=$(d 3)

if [ ! -d "$ROOT" ]; then
  echo "· 복사본 생성: $PROD → $ROOT"
  mkdir -p "$ROOT"
  for x in "_시험엔진" "공인중개사" "법무사"; do
    [ -e "$PROD/$x" ] && cp -a "$PROD/$x" "$ROOT/"
  done
fi

rc=0
run() {
  local name="$1"; shift
  echo; echo "══════ $name ══════"
  python3 "$HERE/e2e_smoke.py" --root "$ROOT" "$@" || rc=1
}

run "1. gongin daily (fixed 50 + 결정론)" --exam gongin --kind daily --date "$D0" --repeat 2
run "2. gongin daily allday (장기 40)"     --exam gongin --kind daily --date "$D1" --stage allday
run "3. gongin retry (듀 상위 20·승격 5)"  --exam gongin --kind retry --date "$D1"
run "4. bupsa2 daily (현행 램프업 단계)"    --exam bupsa2 --kind daily --date "$D1"
run "5. bupsa2 daily S3 합성 15문 (+결정론)" --exam bupsa2 --kind daily --date "$D2" --stage S3 --repeat 2
run "6. bupsa2 retry (전 문항 단답·상한 12·졸업후보 예약)" --exam bupsa2 --kind retry --date "$D2" --stage rebuild-ledger
run "7. bupsa1 daily S2 합성 (5지 40)"      --exam bupsa1 --kind daily --date "$D2" --stage S2
run "8. bupsa1 retry (원장 합성 후 20)"     --exam bupsa1 --kind retry --date "$D2" --stage seed-ledger
run "9. 실패 경로 (문항 1개 누락)"           --exam gongin --kind daily --date "$D3" --fail-mode drop-one
run "10. 실패 경로 (evidence 환각 인용)"     --exam bupsa2 --kind daily --date "$D3" --fail-mode bad-evidence

echo
[ "$rc" -eq 0 ] && echo "✅ E2E 전 케이스 통과 (ROOT=$ROOT)" || echo "❌ 실패한 케이스가 있다 (ROOT=$ROOT)"
exit "$rc"
