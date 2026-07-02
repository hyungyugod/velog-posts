# _analytics — 성장 엔진 데이터 (v2 설계 도메인 D, WO-18~20 시드)

- `inbox/` : 현규가 일요일에 IG 인사이트 **스크린샷**을 넣는 곳 (프로페셔널 계정 전환 후부터).
- `metrics.json` : 포스트별 성과 원장 (비파괴·멱등 — 오답 원장과 같은 철학). 레코드:
  `{postId, date, series, format(carousel|reel), hookId, reach, saves, shares, likes, comments, follows, watchTimeSec, screenshot, confidence}`
  판독 불확실 값은 null + confidence:"low" (지어내기 금지 — 정확성 원칙은 지표에도 적용).
- `experiments.md` : 주 1개 단일변수 실험 로그 (가설→설계→결과→채택).
- `hooks.md` : 훅 라이브러리 — ① 벤치마크 수집(현규 인스타 저장폴더 → 주간 정리) ② 자기 훅×성과 태깅.
- `reports/` : 주간 성장 리포트 보관 (WO-19 스케줄이 생성 예정).
- KPI 방법론: 외부 벤치마크 수치와 비교하지 않는다. **첫 4주 자기 기준선 수립 → 이후 기준선 대비 개선**으로만 판정.
