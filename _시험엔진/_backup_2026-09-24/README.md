# HG Infinite Recall System (HG 무한복습체계) — 엔진 정본 (구조 v2, 2026-09-02)

> 이 폴더가 모든 퀴즈·오답·Anki 자동화의 **단일 정본**이다. 학습 메커니즘은 `공부루틴_OS_v1.md`, 절차는 `spec/`, 파라미터는 `engine/exams.json`, 코드는 `engine/`. 이력은 `CHANGELOG.md`에만 쓴다(실행자는 이력을 읽지 않는다).
> 정본을 velog-posts 안에 두는 이유: 스케줄 세션은 태스크 생성 시점에 연결된 폴더만 마운트한다 — 모든 작업이 velog-posts를 쓰므로 의존 폴더가 1개다.

## 구조

```
_시험엔진/
├── README.md                ← 이 파일 (구조·실행 규칙)
├── CHANGELOG.md             ← 전 이력 (사고·교훈 포함)
├── 공부루틴_OS_v1.md         ← 학습 메커니즘·루프 정본 (4계층·표식 규약·Anki 운영·강의청취법)
├── spec/                    ← 절차 (실행자가 읽는 산문 — 각 ≤80줄)
│   ├── 데일리퀴즈.md · 오답퀴즈.md · 주간리포트.md · 앙키덱.md
│   ├── 문항작성.md          ← questions.json 계약 + 문항 규칙 (전 시험 공통)
│   ├── 프로파일_공인중개사.md · 프로파일_법무사1차.md · 프로파일_법무사2차.md  (특칙만)
│   └── 참조_법무사1차_기출문형.md · 참조_법무사2차_문형사전.md  (형식 사전)
├── engine/                  ← 코드 (시험 폴더에는 데이터만 남는다)
│   ├── exams.json           ← 시험별 파라미터 단일 정본
│   ├── prepare_quiz.py      ← 수거·원장 갱신·원천 선정·플랜 (daily/retry/weekly)
│   ├── render_quiz.py       ← questions.json → 정답 배정·렌더·검증·부수 산출
│   ├── validate_quiz.js     ← 검증 (exam×kind 분기, 레거시 6벌 통합)
│   ├── quiz_template.html   ← 퀴즈 템플릿 단일본 v2.2 (토큰 렌더 · O/X/? 마킹 · 중간제출 · 진행저장 · ❓ 해설 모음 · 💬 단답 코멘트)
│   ├── build_ledger.py      ← 오답 원장 (FSRS-6, --exam) + fsrs_vendor/
│   ├── build_dashboard.py   ← 퀘스트 보드 (gongin)
│   ├── build_apkg.py        ← Anki 덱 빌더 (anki/에서 이동)
│   ├── extract_anki_candidates.py ← Anki 후보 추출기(2026-09-14) — 창·표식·금지 3경로·기출고·상습·이월/보류 표 → anki/_work/후보_<date>.json (문안은 쓰지 않는다)
│   ├── rerender_quiz.py     ← 기존 문제지를 현재 템플릿으로 재렌더 (템플릿 업그레이드용, 결과 수거된 것은 건너뜀)
│   └── tests/               ← 회귀(run.sh) · E2E(e2e_smoke_all.sh)
├── anki/                    ← 카드_*.tsv · 출고/{*.apkg, 검수_*.md}
└── _runs.log                ← 실행 로그 (ISO시각·exam·kind·결과·요약) — 주간리포트가 미실행일 집계
```

시험 폴더: `공인중개사/`, `법무사/1차/`, `법무사/2차/` — 각각 `데일리퀴즈/{YYYY-MM-DD.html, _work/, _push/, _장기복습_로그.json}`, `오답퀴즈/{YYYY-MM-DD.html, _work/}`, `claude_ox_오답/{_inbox/, _ledger/{오답_원장.json, 오답_원장.md}, _work/, YYYY-MM-DD-claude_oxquize.md}`. 노트는 `공인중개사/`·`법무사/` 최상위(`YYYY-MM-DD-과목-(제목).md`), 백지복습 보고서는 `<노트폴더>/백지복습/`. 법무사 1차/2차는 노트 폴더만 공유 — 파일명 `-2차-` 유무가 트랙 스위치.

## 실행 흐름 (문제지 1개 = 3단계)

```
prepare_quiz.py  → plan.json   (수거·원장·원천·쿼터·장기복습·한달전·과거색인 — 기계적)
(AI)             → questions.json  (문항 작성만 — 정답 위치 없음)
render_quiz.py   → HTML         (정답 배정·조합 셔플·검증·로그·푸시 — 기계적)
```
결과 JSON은 되돌아와 원장이 된다: 풀면서 단답에 적은 💬 코멘트(`results[].comment`)가 원장 `comments`(+`dueQueue[].lastComment`)로 쌓여 다음 plan(`picks[].comments`·`recent_comments`·`comments_week`)의 조준 각도가 된다 — 주석 전용이라 FSRS 스케줄·상태에는 영향이 없다.

실행자(스케줄러·스킬)는 `spec/<절차>.md` + `spec/프로파일_<시험>.md`(+ 참조)만 읽는다. 우선순위: 프로파일 > 문항작성 > 절차 > 위임문. **엔진·템플릿·스크립트는 실행 중 수정 금지.**

## 스케줄러 (사이클 독립 — 시험 1개 = 3개 + 시험 횡단 1개)

> **하루 1문제지 원칙 (2026-09-19, OS v2.9)**: 월·수·금 **공인 데일리 50** / 화·토 **공인 오답 25** / 목 **법무사 2차 데일리 ≤15** / 일 **없음**. 법무사 2차 오답은 스케줄 서빙 정지(온디맨드 스킬만 — 듀는 계속 쌓인다), 법무사 1차 2개는 노트 0이라 문제지를 만들지 않는다(스킵·DUE0 보고). 근거: 최근 14일 생성 30개·제출 9개 — 공급을 실소화량에 맞춘다(종전 09-16 하루 2문제지). 요일 정본은 `exams.json` `schedule_days_daily/retry`(주간리포트 미실행일 집계가 읽는다) — 스케줄드 태스크의 요일도 같아야 한다.

| 작업 | 공인중개사 | 법무사 1차 | 법무사 2차 |
|---|---|---|---|
| 오답 파이프라인 | `gongin-odap-quiz` **화·토** 08:40 | `bupsa-1cha-odap-quiz` 평일 08:55 (듀 0 — 문제지 없음) | `bupsa-2cha-odap-quiz` **일시정지** (09-19 — 삭제 금지) |
| 데일리퀴즈 | `gongin-daily-quiz` **월·수·금** 09:00 | `bupsa-1cha-daily-quiz` 화·목 09:20 (노트 0 — 스킵) | `bupsa-2cha-daily-quiz` **목** 09:15 |
| 주간리포트(월) | `gongin-weekly-report` 07:00 | `bupsa-1cha-weekly-report` 07:40 | `bupsa-2cha-weekly-report` 07:30 |

+ `anki-weekly-deck` 월 08:00 (`spec/앙키덱.md`). 법무사 2차는 **목요일 데일리 1개**(≤15 — 서술형 인출 한계 10~15문), 오답 재도전은 09-19 스케줄 서빙 정지(듀는 계속 쌓인다 — 11/2 이후 토요일 1개로 재개, OS §7 국면 3). ⚠️ `anki-weekly-deck` 실제 태스크 프롬프트는 위임문 정본(09-19 개정: '목표 280' → `card_target` 참조)으로 교체해야 한다. 위임문 정본은 `spec/스케줄러_위임문.md`. 온디맨드 스킬: `daily-quiz-gongin`·`daily-quiz-bupsa`·`odap-quiz-gongin`·`odap-quiz-bupsa`·`baekji-chaejeom`(백지채점).
스케줄러는 맥이 켜져 있을 때 실행되며 놓친 회차는 다음 기동 시 몰아서 돈다 — 실제 실행 시각은 `_runs.log`가 정본.

## 규칙

1. **정확성 > 절차**: 노트에 없는 내용·⚠️/확인 필요 항목 출제 금지, 검증 통과 전 종료 금지. Downloads 는 **엔진(prepare)만 만진다** — `cp -n` 수거 + 동명이본 가드(같은 이름·다른 내용 → `_inbox` ` (N).json`) + `_inbox` 사본과 바이트 일치가 확인된 원본만 `Downloads/_오답_수거완료/`로 이동(rename, 다른 파일 불변). AI 실행자는 Downloads 에 쓰지 않는다. 수거완료 폴더는 사용자가 비운다(원장 원천은 `_inbox`).
2. 시험·트랙 간 파일 교차 금지. 항상 오늘 하루치 1개(밀린 날짜 생성 금지).
3. 파라미터 변경 → `engine/exams.json`만. 절차 변경 → `spec/`. 코드 변경 → `engine/tests/run.sh` + `e2e_smoke_all.sh` 통과 후. 모든 변경은 `CHANGELOG.md`에 1줄.
4. 새 시험 추가 = `exams.json`에 항목 1개 + 시험 폴더 스캐폴드(`데일리퀴즈/`, `오답퀴즈/`, `claude_ox_오답/_inbox/`) + 프로파일 md 1장 + 스케줄러 3개(velog-posts 연결 세션에서 생성, 첫 1회 Run now로 도구 승인).
5. 시험 종료 = 스케줄러 3개 disable(삭제 금지) + `exams.json`에 `"status":"closed"` + 외부 잡(카톡푸시) disable. 폴더·원장은 보존.
