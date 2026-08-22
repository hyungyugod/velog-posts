# G. AI 학습도구의 근거와 지형 — 법무사 수험 설계용 조사

조사일 2026-08-22 / 대상: 한국 법무사 시험(1차 객관식 + 2차 논술형) 수험생, Claude Max + 코딩 가능
원칙: 날조 금지. 확인 안 된 것은 "빈약함"으로 표기. 2차 출처(블로그·요약)는 그렇게 명시.

---

## 1. 학습과학 × AI 근거 (2023~2026)

### 1-1. 긍정 근거

**Kestin, Miller, Klales, Milbourne, Ponti (2025), *Scientific Reports*** — 하버드 Physical Sciences 2, 2023 가을학기, 약 180명 RCT. 학생이 주차별로 (a) 고도로 다듬어진 교실 능동학습 vs (b) 전용 AI 튜터를 교차 경험. **AI 튜터 조건에서 학습이득이 약 2배, 소요 시간은 더 짧았고, 참여도·동기도 높았음.**
- 결정적 단서: 그냥 챗봇이 아니라 **전문가가 작성한 스캐폴드 · 단계적 추론 유도 · 환각 방지 가드레일**을 넣어 설계한 튜터였음. "ChatGPT를 켜놓는 것"과 동일시하면 안 됨.
- https://www.nature.com/articles/s41598-025-97652-6

**LLM 생성 인출연습 문제 (arXiv:2507.05629, 2025)** — 데이터사이언스 강의에서 LLM 생성 retrieval practice 문항 투입. **인출연습이 있던 주 정답률 89% vs 없던 주 73%.** 프로그래밍 강의에서도 LLM 생성 MCQ를 받은 학생이 후속 퀴즈에서 유의하게 높은 점수.
- 저자들이 직접 단 경고: **원본(raw) LLM 생성 MCQ는 환각·약한 오답지(distractor)·자명한 내용·형식 오류가 빈번**하여 배포 전 사람 검수·수정이 반드시 필요.
- https://arxiv.org/abs/2507.05629

**Brookings 리뷰 (생성형 AI 튜터링 연구 종합)** — 다수 RCT에서 학습이득·전이·동기 개선 보고. 다만 인간의 감독(human oversight)이 효과의 공통 조건으로 반복 등장.
- https://www.brookings.edu/articles/what-the-research-shows-about-generative-ai-in-tutoring/

### 1-2. 부정 근거 (설계에 더 중요)

**Bastani, Bastani, Sungu, Ge, Kabakcı, Mariman (2025), *PNAS*, "Generative AI without guardrails can harm learning"** — 터키 고교, 약 1,000명, 9~11학년 50여 학급, 90분 4세션 RCT.
- 연습 중 성적: GPT Base **+48%**, GPT Tutor(교사 설계 힌트 제공형) **+127%**.
- **AI 접근을 회수한 뒤 치른 시험에서 GPT Base 그룹은 AI를 아예 안 쓴 대조군보다 17% 낮았음.**
- 완화 요인: **정답을 주지 말고 교사가 설계한 힌트만 주도록 가드레일을 걸면** 역효과가 사라짐(GPT Tutor 조건).
- 해석: 학생이 GPT-4를 "목발(crutch)"로 쓰면 연습 성과는 오르지만 실전 수행은 떨어진다.
- https://www.pnas.org/doi/10.1073/pnas.2422633122 / https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635/

**Fan et al. (2024/2025), *British Journal of Educational Technology*, "Beware of metacognitive laziness"** — 중국 학생 117명, 읽기→에세이 작성→수정.
- ChatGPT 지원 그룹은 **에세이 품질은 높았으나 사후 지식 검사에서 향상 없음.**
- 자기교정 행동이 적고, 자료를 성찰하는 시간이 유의하게 짧았음 = "메타인지적 게으름".
- 기제: 외부 보조도구가 성찰·검증을 **보완(scaffold)하지 않고 대체(replace)**할 때 발생.
- https://arxiv.org/pdf/2412.09315 / https://www.auckland.ac.nz/en/news/2025/10/02/When-ai-tools-promote-metacognitive-laziness.html
- 관련 보도: https://hechingerreport.org/proof-points-offload-critical-thinking-ai/

### 1-3. 연구의 한계 (과신 금지)

- 표본이 **물리·수학·데이터사이언스·프로그래밍**에 집중. **법학 논술형 시험 도메인의 RCT는 사실상 없음** → 외적 타당도 제한.
- 개입 기간이 짧음(수 주~한 학기). 1~2년짜리 수험 사이클에 대한 장기 증거 없음.
- 성인 자기주도 수험생(동기가 매우 높은 집단)이 아니라 대부분 재학생 대상 → 의존 위험의 크기가 다를 수 있음.
- retrieval practice·spaced repetition·interleaving 자체의 효과는 견고하나(예: Frontiers in Psychology 2025, 초등 현장 인출연습 효과 재확인 https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1632206/full), **"AI로 생성한 인출 자극"이 "사람이 만든 인출 자극"과 동등한지를 직접 비교한 연구는 빈약함.**

---

## 2. 환각 리스크 정량 — 법률 도메인

### 2-1. 범용 LLM (영미법 기준)

**Dahl, Magesh, Suzgun, Ho (2024), *Journal of Legal Analysis* 16(1):64–93, "Large Legal Fictions"** — 80만 건 이상의 검증 가능한 법률 질의.
- **특정·검증가능 질의에서 법률 환각률 69~88%.** 모델별로 **ChatGPT-4 58% ~ Llama 2 88%**.
- 모델이 자기 오류를 인지하지 못하고, 사용자의 잘못된 법적 전제를 오히려 강화하는 경향.
- https://academic.oup.com/jla/article/16/1/64/7699227 / https://arxiv.org/abs/2401.01301
- 요약: https://law.stanford.edu/2024/01/11/hallucinating-law-legal-mistakes-with-large-language-models-are-pervasive/

**Magesh et al. (2025), *Journal of Empirical Legal Studies*, "Hallucination-Free?"** — 상용 RAG 법률 도구 최초의 사전등록 실증 평가(2024-05 테스트).
- **Lexis+ AI 17%, Westlaw AI-Assisted Research 33%, GPT-4 43%** 환각률.
- 핵심: **RAG를 붙여도 환각은 사라지지 않는다.** 벤더의 "hallucination-free" 마케팅은 사실이 아님.
- https://onlinelibrary.wiley.com/doi/full/10.1111/jels.12413 / https://arxiv.org/abs/2405.20362

### 2-2. 한국법 — 가장 직접적인 근거 (필독)

**Oh, Hwang, On (2025-12), "Korean Canonical Legal Benchmark (KCL)", arXiv:2512.24572** — 서울시립대 + LBOX. **한국 변호사시험** 기반.
- 구성: **KCL-MCQA 283문항**(2024·2025년 변시 객관식) + **KCL-Essay 169문항**(2021~2025 사례형 논술). 각 문항에 근거 판례 태깅(문항당 평균 3.9개 / 3.3개).
- 평가 방식: **vanilla(판례 미제공 = 순수 지식 회상)** vs **w/ supporting precedents(근거 판례 제공 = 근거기반 추론)** 비교. 3회 반복 평균.
- 인간 합격선 기준치로 **68.7%** 인용.

| 모델 | MCQA 자료없음 → 판례제공 | Essay 자료없음 → 판례제공 |
|---|---|---|
| Gemini 2.5 Pro | 66.1 → **89.3** | 60.5 → **74.9** |
| Claude Opus 4.1 | 57.2 → 83.3 | 45.5 → 60.3 |
| Claude Sonnet 4.5 | 54.9 → 85.2 | 47.6 → 68.5 |
| GPT-5 | 53.9 → 84.2 | 57.5 → 72.8 |
| Claude 3.7 Sonnet | 50.4 → 82.0 | 43.6 → 63.6 |
| (Large Reasoning 평균) | 51.2 → 81.7 | 46.2 → 64.6 |
| 랜덤 베이스라인 | 20 | — |

- **함의 1 (치명적)**: 자료를 안 주면 Claude Opus 4.1이 한국 변시 객관식에서 **57.2%** — 인간 합격선 68.7%에 **미달**. 즉 **자료 없이 물어보면 대략 40~45%가 틀린다.**
- **함의 2 (활용법)**: 근거 판례를 컨텍스트에 넣으면 **83~85%로 급등**. 저자들의 결론 그대로 — "판례 없이 생기는 오류는 대체로 **지식 부재**에서 온다."
- **함의 3 (논술이 진짜 벽)**: Essay는 근거 자료를 다 줘도 최고가 74.9%, Claude 계열은 60~68% 수준. **논술 채점·모범답안 자동생성은 객관식보다 훨씬 신뢰도가 낮다.**
- **함의 4**: 논술에서는 GPT-5·o3가 Claude 계열을 전 조건에서 상회. 객관식 무자료 회상에서는 Claude Opus 4.1이 GPT-5보다 높음. **용도별로 모델이 갈린다.**
- 저자 명시 한계: LLM-as-a-Judge(Gemini 2.5 Flash) 사용, 고배점 문항에서 인간과 상관 ~0.7로 하락. "판례 제공" 조건은 **완벽한 검색을 가정**한 것이라 실제 RAG의 검색 실패·오순위는 반영 안 됨.
- https://arxiv.org/abs/2512.24572 / 코드·데이터 https://github.com/lbox-kr/kcl

**Lee, Kim, Hwang, Kim, Lee (2025), KoBLEX, EMNLP 2025 Main, arXiv:2509.01324** — 한국 법령 조문 근거 설명형 QA 벤치마크, 226문항, 법률전문가 검수.
- 제안기법 ParSeR가 **표준 검색 + GPT-4o 대비 F1 +37.91, Legal Fidelity +30.81**.
- 함의: **단순 벡터 검색만 붙인 RAG로는 한국 법령의 조문 근거가 크게 부실하다.** 조문 간 다단 위임·연쇄 참조를 따라가는 설계가 필요.
- https://arxiv.org/abs/2509.01324 / https://aclanthology.org/2025.emnlp-main.200/

### 2-3. 수험 콘텐츠 자동생성 시 오류 혼입 추정

- 무자료 생성: **오류율 대략 40~45%** (KCL vanilla, Claude 계열 MCQA 54~57% 정답 기준).
- 조문·판례 원문 첨부: **오류율 대략 15~17%** (KCL w/ precedents 83~85% 기준. Lexis+ AI의 17%와 우연히 유사한 수준).
- 논술 모범답안: **오류·누락률 30~40%** (KCL-Essay 60~68%).
- → 1,000장짜리 자동생성 덱을 무검수로 쓰면 **150~450장에 오류가 섞인다.** 암기는 오류를 그대로 각인시킨다.

**국내 도구 참고**: 법제처 국가법령정보 API를 MCP로 노출해 인용 검증(존재+내용)을 수행하는 오픈소스 존재 — https://github.com/chrisryugj/korean-law-mcp (2차 출처, 성능 벤치마크는 미공개). 자체 검증 파이프라인 설계 시 참고 가치 있음.

---

## 3. 도구 지형 (2026-08 기준)

### ① Anki + FSRS
- **FSRS-6이 Anki 25.07+(2025-07)부터 기본 스케줄러.** 학습 파라미터 17개, FSRS-6에서 w20이 추가되어 개인별 망각곡선 형태를 조정. 이후 6.3(2025-10)에서 가중치 안정화, 6.3.1(2026-03)까지 갱신된 것으로 보고됨. — **주의: 버전 수치는 2차 출처(블로그/포럼) 기반. 실제 적용 전 Anki 공식 매뉴얼로 확인 요망.**
  - https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md
  - https://forums.ankiweb.net/t/fsrs-6-updates-all-difficulties-to-0/64846
- **Optimize는 리뷰 이력이 대략 400~1,000건 이상 쌓여야 기본 파라미터 대비 의미 있는 개선.** 초반엔 기본값으로 그냥 굴려야 한다.
- **AnkiConnect**: Anki 데스크톱 실행 중 `http://localhost:8765`로 HTTP API 노출. 노트 생성, 덱 조회, 동기화 트리거 등. Anki 2.1.x 지원.
  - https://git.sr.ht/~foosoft/anki-connect / https://github.com/ankicommunity/anki-desktop-addon-connect
  - **한계**: 데스크톱이 켜져 있어야만 동작. 서버사이드·모바일 자동화 불가 → 예약작업으로 카드를 밀어넣는 설계라면 PC 상주가 전제.

### ② 손글씨 OCR (한국어)
- 클로바 OCR이 **손글씨에서 구글 드라이브 OCR보다 우수**하다는 국내 비교 리뷰. 곡선/기울어진 문자·필기체 인식 강조, ICDAR 2019 4개 부문 1위 이력.
  - https://didim365.com/blog/네이버-클로바-ocr-vs-구글-드라이브-ocr-비교-리뷰/
- 한국어 OCR 일반 정확도: **인쇄 상태 양호 문서 85~90%, 손글씨·표 구조 포함 시 크게 하락.** (2차 출처)
  - https://www.lido.app/kr/hangugeo-ocr
- **Claude/GPT 비전 vs 클로바 OCR의 한국어 손글씨 직접 비교 벤치마크는 찾지 못함 → 빈약함.** 본인 필기 샘플 20~30장으로 직접 A/B 테스트하는 것이 유일하게 신뢰할 방법.

### ③ TTS (한국어 암기 오디오)
- **Edge-TTS**: 무료, API 키 불필요, MS Azure Neural 기반. 한국어 음성(ko-KR SunHi/InJoon/Hyunsu) 자연스러움 양호, gTTS보다 확연히 우수. 속도 조절·MP3 즉시 출력. **대량 배치 생성에 가장 실용적.**
  - https://tts.travisvn.com/ / https://github.com/kss2002/edge-TTS
- **클로바더빙**: 한국어 발음 정밀도 매우 높음("25살"→"스물다섯 살", "25년도"→"이십오 년도" 식 한국어 읽기 규칙 정확 구현 — 법조문 숫자 낭독에 유리). 단 **무료 이용 시 출처 표기 의무 + 사용량·상업이용 제한.**
  - https://typecast.ai/kr/learn/tts-natural-pronunciation-comparison-2026/ (2차 출처)
- **OpenAI TTS의 한국어 품질을 위 둘과 직접 비교한 자료는 찾지 못함 → 빈약함.**
- 실무 판단: **조문·판례 대량 낭독은 Edge-TTS(무료·무제한·스크립트 가능)**, 발음이 까다로운 핵심 조문만 클로바더빙으로 보강.

### ④ NotebookLM 오디오 오버뷰 — **한국어 지원 O**
- 2025-04 50개 이상 언어로 확대되며 한국어 포함. 이후 80개 이상 언어. 설정의 **Output Language**로 지정.
  - https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-audio-overviews-50-languages/
  - https://workspaceupdates.googleblog.com/2025/04/language-expansion-audio-overviews-notebooklm.html
  - https://support.google.com/notebooklm/answer/16212820?hl=en
- 유의: 오디오 오버뷰는 **요약·대담 형식**이라 조문 축자 암기용이 아님. 이동 중 개념 복습·쟁점 조망용으로만.

### ⑤ 한국 수험가에서 실제 쓰이는 조합
- 2026년 국내 가이드 다수가 **NotebookLM(자료 요약) + ChatGPT(문제 생성) + 클로바노트(강의 녹음 요약)** 조합을 표준으로 제시. (2차 출처, 대학생 대상)
  - https://community.linkareer.com/employment_data/5886590
- **Anki는 한국 전문직 수험가에서 실사용 확인됨** (아래 4번 참조).

---

## 4. 한국 수험생 AI 활용 실사례 (2025~2026) — **빈약함 (정직하게 기록)**

**결론: "AI를 써서 전문직·고시급 시험에 합격했다"는 구체적·검증 가능한 1차 합격 후기는 사실상 찾지 못했다.** 법무사 시험 특정 사례는 전무.

찾은 것:
- **Anki 활용 합격수기는 실재** (AI가 아니라 SRS 도구). 공인노무사 32기 합격자의 Anki 중심 수험기 및 카드 공유, "시험 직전 두문자를 확실히 암기했다는 느낌은 안키 덕분" 진술.
  - https://cafe.daum.net/keedong/4Q79/1382 / https://m.cafe.daum.net/keedong/3Bwv/438
- **Anki + Logseq만으로 세무사 합격**한 국내 사례가 언급됨(코리안키 커뮤니티 운영자) — **2차 출처(나무위키)이며 1차 확인 못 함.**
  - https://namu.wiki/w/Anki
- **실무 변호사의 AI 사용 패턴**(수험 아님, 참고용): 판례 검색은 법률특화 AI, **서면 논리 정교화는 Claude**, 문장 가독성·표현 개선은 ChatGPT 보조.
  - https://www.lawwave.kr/feel/1065
- **로스쿨 제도권 신호**: 6대 로펌(김·장, 광장, 세종, 율촌, 태평양, 화우)이 출제·심사하는 '제1회 로스쿨 AI 챌린지' 개최 — AI 활용 능력 + 법적 추론 역량 평가.
  - https://www.lawtimes.co.kr/news/articleView.html?idxno=219939 / https://www.lawschooltimes.com/news/articleView.html?idxno=11459
- **부작용 측 보도**: 로스쿨에 AI 커리큘럼이 없어 "변시 준비도 벅차다"는 현장 보도(서울신문 2026-02), 대학생 AI 의존 심화 보도(한국일보 2026-03, 유니버시티뉴스 2026 신년기획 "공부는 쉬워지고 사고의 필요성은 줄었다").
  - https://www.seoul.co.kr/news/plan/AI-lawbooks-algorithm/2026/02/06/20260206008006
  - https://news.unn.net/news/articleView.html?idxno=589375
- 교육부·시도교육청이 「수행평가 시 AI 활용 관리 방안」을 확정하며 **할루시네이션을 공식적으로 "지어낸 말, 사실과 다른 말"로 정의하고 학생 지도 대상에 포함**.
  - https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=294&boardSeq=104984&lev=0&m=020402

**시사점**: 벤치마킹할 선례가 없다 = 남의 검증된 레시피를 복사할 수 없다. 자기 데이터(정답률·복습 로그)로 직접 검증하는 루프를 설계에 내장해야 한다.

---

## 5. Claude 최신 기능 중 수험에 유효한 것

### Agent Skills (공식 문서 확인 완료)
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- 구조: `SKILL.md` + YAML frontmatter(`name` 64자 이내 소문자/숫자/하이픈, `description` 1024자 이내).
- **Progressive disclosure — 수험 설계에 핵심적인 성질**:
  | 레벨 | 로딩 시점 | 토큰 비용 |
  |---|---|---|
  | 메타데이터 | 항상(시작 시) | Skill당 ~100토큰 |
  | SKILL.md 본문 | 트리거될 때 | 5k 미만 |
  | 번들 리소스/스크립트 | 참조될 때만 | 접근 전까지 0 |
- → **조문 원문·판례 요지 같은 대용량 참조자료를 Skill에 번들해두면 쓸 때만 컨텍스트를 먹는다.** 스크립트는 코드가 컨텍스트에 안 들어가고 출력만 들어감 → 카드 생성·검증 스크립트를 넣기에 적합.
- 배치: Claude Code는 `~/.claude/skills/`(개인) 또는 `.claude/skills/`(프로젝트). claude.ai는 Settings > Features에서 zip 업로드(Pro/Max/Team/Enterprise, 코드 실행 활성화 필요).
- **주의 1 — 서피스 간 동기화 안 됨**: claude.ai에 올린 Skill은 API/Claude Code에서 안 보이고 그 역도 마찬가지. 각각 따로 관리해야 함.
- **주의 2 — 런타임 네트워크**: Claude Code의 Skill은 네트워크 전면 접근(로컬 프로그램과 동일), API의 Skill은 **네트워크 접근 없음 + 런타임 패키지 설치 불가**. claude.ai는 설정에 따라 가변.
- **주의 3 — 보안**: 신뢰할 수 없는 출처의 Skill 사용 금지. 외부 URL을 가져오는 Skill은 특히 위험(가져온 내용에 악성 지시가 섞일 수 있음).

### Projects / 메모리 / 예약작업 / 긴 컨텍스트 — **2차 출처만 확인 (공식 문서 미확인)**
- Projects(2026-03): 전용 워크스페이스에 지속 메모리 + 커스텀 지시 + 예약작업이 프로젝트 단위로 묶임. 세션마다 컨텍스트를 재설명할 필요가 없음.
- 지속 메모리: 2026-03-02 전 사용자로 확대.
- 예약작업: 2026-08 기준 서버사이드 실행, 기기 상시 접속 불필요.
  - **단, 3-①의 AnkiConnect는 로컬 PC 상주가 필요하므로 "예약작업이 서버에서 돌아 Anki에 카드를 밀어넣는" 구성은 성립하지 않는다.** 예약작업은 카드 초안 생성까지, 주입은 로컬 스크립트로 분리해야 함.
- 긴 컨텍스트: Sonnet 4.6 기준 최대 1M 토큰(베타).
  - https://www.innobu.com/en/articles/claude-ai-2026-new-features.html / https://ryanandmattdatascience.com/claude-cowork-projects/ (모두 2차 출처 — 실제 사용 전 앱 내에서 직접 확인 권장)

### 수험 적용 패턴 (위 근거로부터의 직접 도출)
1. **조문·판례 원문을 항상 컨텍스트에 넣는다** (KCL: 57%→83%). 무자료 질의는 금지 규칙으로 박아둘 것.
2. **Skill에 "출제 규칙 + 검증 절차"를 코드로 고정** — 문항 생성기와 인용 검증기를 스크립트로 분리(출력만 컨텍스트에 들어옴).
3. **가드레일: 답을 주지 말고 힌트만** (Bastani PNAS의 GPT Tutor 조건이 유일하게 역효과가 없던 설계).
4. **긴 컨텍스트는 "한 과목 교재 통째로 넣고 쟁점 지도 뽑기"에 쓰고, 암기 카드는 그 지도에서 파생**시킨다.

---

## 접근 실패 / 미확인 기록
- `arxiv.org/html/2512.24572v1` 직접 fetch는 용량 초과 → 서브에이전트로 전문 독해하여 수치 확보(완료). 단 부록 A~E는 캡처에서 잘림.
- KCL 논문의 EACL 2026 게재 여부: ACL Anthology 검색결과에 `2026.eacl-short.17`로 노출되나 arXiv 원문에는 venue 문자열 없음 → **arXiv 2512.24572 (2025-12-31)로 인용하는 것이 안전.**
- Claude Projects/메모리/예약작업/1M 컨텍스트: docs.claude.com 공식 페이지 미확인, 2차 출처만.
- 한국어 손글씨 OCR의 Claude/GPT 비전 vs 클로바 정량 비교: 없음.
- OpenAI TTS 한국어 품질 정량 비교: 없음.
- 클로바더빙 무료 사용량 구체 수치: 검색 결과에 명시 없음.
