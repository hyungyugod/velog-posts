#!/usr/bin/env bash
# HG 무한복습체계 · 퀴즈 엔진 회귀 테스트 러너
#   사용: bash _시험엔진/engine/tests/run.sh
#   jsdom은 velog-posts 바깥(TEST_HOME, 기본 /tmp/hg-tests)에만 설치한다.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_HOME="${TEST_HOME:-/tmp/hg-tests}"

command -v node >/dev/null || { echo "node가 필요합니다"; exit 2; }
command -v python3 >/dev/null || { echo "python3이 필요합니다"; exit 2; }

if [ ! -d "$TEST_HOME/node_modules/jsdom" ]; then
  echo "· jsdom 설치 → $TEST_HOME"
  mkdir -p "$TEST_HOME"
  npm --prefix "$TEST_HOME" install jsdom@24 --silent || { echo "jsdom 설치 실패"; exit 2; }
fi
export NODE_PATH="$TEST_HOME/node_modules"

rc=0
for f in "$HERE"/*.test.js; do
  node "$f" || rc=1
done

echo
if [ "$rc" -eq 0 ]; then echo "✅ 전체 통과"; else echo "❌ 실패한 테스트가 있습니다"; fi
exit "$rc"
