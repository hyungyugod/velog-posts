[오답 인박스]  ← 여기에 채점결과 JSON을 넣는다
- 퀴즈 제출 시 브라우저가 Downloads에 저장하는 공인중개사_오답_YYYY-MM-DD.json 을 이 폴더로 복사(끌어다 놓기).
- 그 다음:  python3 ../_ledger/build_ledger.py --ingest
  → _inbox의 새 JSON을 _raw로 보존하고, 누적 원장(_ledger/오답_원장.md/.json)을 다시 만든다.
- 왜 이 폴더인가: 기존 루프는 'Downloads 접근 + 최근 7일 창'에 의존해 6/15~7/01 무음 실패했다.
  이 폴더는 저장소 안에 있어 세션이 항상 접근 가능하고, 원장은 전체 이력을 반영해 한 주 걸러도 데이터가 새지 않는다.
