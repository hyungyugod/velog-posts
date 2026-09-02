---
name: "daily-quiz-gongin"
description: "평일 아침(월~금), 최근 7일 공인중개사 학습노트 신규 30 + 장기복습 10 + 한달전 복원 10 = 50문항 실전형 심화 문제지 v5 (오답 원장 미참조 — 재도전은 오답퀴즈 전담 / 카톡 푸시·정본 템플릿·자동 검산)"
---

> ⚠️ [구본 — 2026-08-25 이후] 정본은 velog-posts/_시험엔진/ 의 베이스+프로파일 체계로 이전됨. 이 파일은 이력 보존용 — 수정 금지, 스케줄러가 더 이상 읽지 않는다.
> ⚙️ 이 본문은 2026-08-24 v5 기준 **참고 사본**. 정본 = `ai-guidelines/50_스케줄-자동화/스케줄_프롬프트_데일리퀴즈_공인중개사_v5.md` — 수정은 정본에서만 하고, 이 사본은 정본 갱신 시 함께 교체.

평일(월~금) 아침에 실행되는 "데일리 문제지 자동 생성" 작업이다. 아래를 순서대로 수행하라.

**[실행 원칙] 이 지침은 실행 모델의 재량을 최소화하도록 쿼터·수열·스크립트로 고정되어 있다. 단계를 건너뛰거나 "비슷하게" 단순화하지 말고, 명시된 숫자와 절차를 그대로 따른다. 품질의 핵심 5가지: ① 노트 전체 정독 ② 과거 문제 회피 ③ 한 끗 차이 보기 ④ 검증 통과까지 반복 ⑤ 장기복습(⏪)·한달전 복원(🔄)은 로그·날짜 기준으로 기계적으로 선정.**

**[v5 변경 요약 — 2026-08-24] 오답 재도전(🔁) 완전 제거. 이 작업은 오답 원장·dueQueue를 출제에 사용하지 않는다 — 재도전은 평일 오답 파이프라인(`daily-wrong-answers-pipeline`)의 '오답 재도전 퀴즈'(`공인중개사/오답퀴즈/`)가 전담한다. 총 50문항 = 본편 40문(신규 30 + 장기복습 10) + 한달전 복원 10문(🔄). 이 문제지에 retryOf·🔁 문항이 있으면 잘못 만든 것이다.**

## 0. 경로·중복 가드 (가장 먼저)
- 이 작업은 **항상 '오늘 하루치 1개'만** 만든다. 밀린 과거 날짜분을 만들지 않는다.
- bash `date +%F`로 오늘 날짜를 구한다. `ROOT=$(find /sessions/*/mnt -maxdepth 2 -type d -name velog-posts 2>/dev/null | head -1)` — 비어 있으면 "velog-posts 마운트 없음"을 명확히 보고하고 종료. `QD=$ROOT/공인중개사/데일리퀴즈`.
- `$QD/{오늘날짜}.html`이 이미 존재하면 → "오늘 문제지는 이미 생성되어 있다"고만 알리고 즉시 종료(덮어쓰기·중복 생성 금지). Read 도구가 괄호 포함 파일명에서 막히면 bash `cat`으로 읽는다.

## 1. 자료 수집
### 1-1. 최근 7일 학습 노트 (신규 출제 원천)
- `find "$ROOT/공인중개사" -maxdepth 1 -name "20*.md" -mtime -7` (claude_ox_오답·데일리퀴즈·오답퀴즈·_지침아카이브 폴더는 자동 제외).
- 발견된 **모든 .md를 처음부터 끝까지 전부 읽는다(발췌·건너뛰기 금지)**. 핵심 개념·규정·숫자·함정·암기코드를 파악한다.
- 최근 7일 노트가 없으면 **종료하지 않는다** — §1-4의 [장기복습 전일 모드]로 전환한다(신규 0문, 그 몫을 전부 장기복습으로).
- ⚠️ **노트 하단 "확인 필요/⚠️" 섹션에 언급된 수치·항목은 출제 금지.**
### 1-2. 과거 출제 회피 목록
- `grep -ho 'q: *"[^"]*"' "$QD"/20*.html | sort -u`로 과거 문제문을 전부 추출해 읽는다.
- 오늘 **본편(신규·장기복습)** 문항은 이 목록과 **같은 개념 + 같은 각도** 반복 금지. 같은 과목이라도 다른 조문·다른 숫자·다른 각도(긍정↔부정, 정의↔사례, 암기↔계산, 방향 뒤집기)로 낸다. 예외 1가지: 1-5의 한달전 복원은 **원문 그대로 재출제가 목적**이므로 회피 대상이 아니다.
### 1-3. 재도전 없음 (v5)
- 오답 원장(`claude_ox_오답/_ledger/오답_원장.json`)과 dueQueue는 **이 작업에서 읽지 않는다**(§5.5의 dueBacklog 숫자 1개만 예외 — 출제 사용 금지). 오답 재도전은 오답퀴즈가 전담한다.
### 1-4. 장기복습 원천 = 옛 노트 로테이션
- 후보: `$ROOT/공인중개사` **최상위**(-maxdepth 1)의 `20*.md` 중 **파일명 날짜**가 오늘−14일 이전인 것 (mtime 아님 — 나중에 수정해도 나이는 파일명 기준. 하위 폴더는 자동 제외).
- 로테이션 로그: `$QD/_장기복습_로그.json` — 형식 `{"파일명.md": {"last": "YYYY-MM-DD", "n": 서빙횟수}}`. 파일이 없으면 빈 객체로 시작한다.
- 나이 버킷과 문항 수:
  | 버킷 | 나이(파일명 기준) | 기본 모드 | 전일 모드 |
  |---|---|---|---|
  | B1 | 14~45일 전 | 3문 | 13문 |
  | B2 | 45~90일 전 | 3문 | 13문 |
  | B3 | 90일+ 전 | 4문 | 14문 |
  - 기본 모드 합계 10문 고정. 전일 모드 합계 40문. 버킷에 후보가 없으면 그 몫은 더 오래된 버킷으로 이월한다.
- 노트 선정(재량 최소화): 버킷마다 ① 로그에 없는(미서빙) 노트 우선, 파일명 날짜 오래된 순 ② 전부 서빙됐으면 `last`가 가장 오래된 순으로 **1~2개**(전일 모드는 3~4개) 뽑는다. 선정된 노트는 **전문 정독** 후 그 노트에서만 출제한다.
- 표기: 문제문 맨 앞 `⏪ `, src 끝에 `(장기복습·N일전)` (N = 오늘 − 노트 파일명 날짜). conceptKey 규칙은 신규와 동일. "확인 필요/⚠️" 출제 금지와 §1-2 과거 출제 회피는 장기복습에도 그대로 적용된다.
- 생성 완료 후 로그 갱신: 선정된 각 노트에 `last=오늘, n+=1`을 기록해 저장한다.
### 1-5. 한달전 복원 원천 = 30일 전 출제분 그대로
- 목적: 딱 한 달 전에 풀었던 문제를 **원문 그대로** 다시 풀어 30일 간격 인출을 완성한다. 변형 금지 — 이 블록만은 "냈던 문제를 그대로" 낸다.
- 후보 창: `$QD/20*.html` 중 파일명 날짜가 **오늘−33일 ~ 오늘−27일** 사이인 파일 전부.
- **폴백**: 창에 파일이 하나도 없으면 → `$QD`에서 **가장 오래된 html의 날짜 D0**를 잡고 **D0 ~ D0+6일(가장 오래된 한 주)** 파일들을 후보로 쓴다. 보고에 "한달전 창 비어있음 → 최고(最古) 주 폴백"을 명시한다.
- 문항 선정 (기계적):
  1. 후보 파일들의 QUESTIONS 배열에서 `retryOf`(🔁)와 `monthlyOf`(🔄) 문항은 **원천에서 제외** (그날의 순수 출제분만 — 과거 v4 파일에는 🔁 문항이 남아 있다).
  2. 남은 문항을 과목(cat)별로 묶고, **과목당 최대 3문**으로 골고루 10문을 뽑는다. 과목 수가 4개 이상이면 과목당 2~3문, 3개 이하면 균등 배분. 같은 과목 안에서는 유형(type)이 겹치지 않게 우선 선택.
  3. 선정 문항은 `q`(단, 맨 앞의 🔁/⏪ 이모지는 제거하고 `🔄 `를 붙인다)·`opts`·`answer`·`expl`·`cat`·`type`·`conceptKey`·`calc`(있으면)를 **그대로 복사**한다. `src`는 원본 src 뒤에 ` (한달전 재출제·원본 YYYY-MM-DD)`를 덧붙인다.
  4. 필드 추가: `monthlyOf: "YYYY-MM-DD"` (원본 파일 날짜).
- 배치: QUESTIONS 배열의 **맨 뒤 41~50번**에 별도 블록으로 넣는다 (블록 안에서는 같은 과목 연속 정렬).

## 2. 출제 계획표 작성 (문항 작성 전 필수 — 건너뛰기 금지)
50행 계획표: `# | 소스(신규/장기/한달전) | 과목 | 출처 소제목 | conceptKey | 개념 + 함정 설계(무엇을 한 끗 바꿀지 — 한달전은 "원문 복사") | type | 정답idx | 🔄 여부`
### 2-1. 과목 배분 (본편 40문 기준)
- 본편 40문항을 발견된 과목 수로 고르게(차이 ≤1). **QUESTIONS 배열에서 같은 과목 문항은 연속 배치** (본편 1~40 안에서. 41~50 한달전 블록은 자체 정렬).
- 소스 구성(합 50): **신규 30 · 장기복습 10 · 한달전 복원 10(고정)**. [전일 모드] 신규 0 · 장기복습 40 · 한달전 10. 유형 쿼터(§2-2)는 **본편 40 기준**으로 유지한다.
### 2-2. 유형 쿼터 (본편 40 기준 — 한달전 10문은 원본 유형 그대로, 쿼터 계산 제외)
| type | 수 | 비고 |
|---|---|---|
| 일반 | 20 | 4지선다 "…옳은 것은?" / "…<b>옳지 않은</b> 것은?" |
| 조합 | 7 | 발문에 정확히 "모두 고른 것은?" + `<br>ㄱ. …<br>ㄴ. …` 나열, 선택지는 조합 4개 |
| 계산 | 4 | **calc:{expr,expected} 필수** — expr은 JS로 평가 가능한 산식 문자열, expected는 그 수치. 소재 부족 시 최소 2, 부족분은 일반으로(일반+계산=24 유지) |
| 사례 | 4 | 갑·을·병 등장 사례에 법리 적용 |
| OX | 5 | opts는 ["O","X"], 한 끗 함정(주체·숫자·방향) |
- 본편 4지선다 35문항 중 **부정형 12~18** (`<b>옳지 않은</b>` 굵게). 단순 정의 확인("…란 무엇인가?") 금지 — 함정 비교·메커니즘·계산·헷갈리는 숫자 적극 활용.
### 2-3. 정답 인덱스 사전 배정 (본편만 — 기계적으로)
- 본편 객관식 35문항: 0,1,2,3을 각 8회씩 적은 32개 수열 + 서로 다른 인덱스 3개 1회씩 = 35개(9·9·9·8). 같은 숫자 3연속 금지로 섞어 계획표 순서대로 배정. 보기를 쓸 때 처음부터 그 위치에 정답을 놓는다.
- 본편 OX 5문항: O 3·X 2 또는 O 2·X 3.
- 한달전 10문은 **원본 answer 그대로** (재배정 금지). 단, 전체 50문 배열에서 같은 정답 인덱스 3연속이 생기면 한달전 블록 **내부의 문항 순서만** 바꿔 해소한다.

## 3. 문항 작성 규칙 — 공인중개사 실전 스타일 (본편에 적용, 한달전은 원문 복사)
- 발문: 실제 시험 형식("…에 관한 설명으로 옳은 것은?" 등). 계산형은 조건 전부 명시 + "(다른 조건은 동일)".
- 보기: 내용만(번호 금지). **오답 보기는 정답과 '한 끗 차이'**(숫자 스왑·주체 교체·기간 교체·원칙↔예외·비슷한 제도 교차). 4개 모두 그럴듯하게, 더미 금지. 정답 보기 길이 티 안 나게. 문자열 안에 큰따옴표(")·백틱 사용 금지(따옴표 필요하면 ' ).
- 해설(expl): `[정답 근거] → [왜 그렇게 설계됐는지 메커니즘 1문장] → [함정 포인트·비교 1문장]` 3문장 250자 이내. OX는 "O." / "X."로 시작. 계산형은 산식 전개 포함.
- src: `YYYY-MM-DD 과목 소제목` — 실제 읽은 노트의 것만. 한달전은 끝에 `(한달전 재출제·원본 YYYY-MM-DD)`.
- **필드 계약 (모든 문항):** `{ type, cat, q, opts, answer, expl, src, conceptKey }` + 한달전 복원이면 `monthlyOf`, 계산형이면 `calc:{expr,expected}`. **retryOf는 쓰지 않는다(v5).**
  - conceptKey 형식: `과목 소제목-요지` 짧게 (예: "부동산세법 2-5 취득시기"). 신규·장기는 src 소제목 기반, 한달전은 원본 conceptKey 그대로.
- 계산형은 작성 직후 node로 expr을 평가해 expected·정답 보기와 일치하는지 확인한다.
- 안티패턴 금지: 노트에 없는 내용 출제 / "확인 필요" 수치 출제 / 과거 문제문 재사용(한달전 제외) / 정답만 조문처럼 길게 / 쿼터 임의 축소 / **한달전 문항 임의 변형** / **오답 원장 참조 출제**.

## 4. HTML 생성 (정본 템플릿)
- **템플릿 = `$QD/_template.html` 고정.** 정본이 채점·저장(buildPayload/downloadResult, 스키마 v2)의 단일 원천이다. (오답퀴즈용 사본 `오답퀴즈/_template.html`과 혼동 금지 — 데일리는 반드시 데일리퀴즈 폴더의 정본.)
- 교체할 것 4가지만:
  1. `{{QUIZ_DATE}}` → 오늘날짜 (title과 JS 상수 두 곳)
  2. `{{META_LINE}}` → "2026년 M월 D일 (요일) · 실전형 50문항(본편 40 + 한달전 복원 10) · 장기복습 10(⏪) · 한달전 10(🔄)"
  3. `{{TAGS_HTML}}` → `<span class="tag">🔥 심화</span><span class="tag">📝 실전 4지선다</span><span class="tag">⏪ 장기복습 10</span><span class="tag">🔄 한달전 복원 10</span><span class="tag">🎯 정답분산</span>` + 오늘 과목명 태그들
  4. `/*__QUESTIONS_START__*/`와 `/*__QUESTIONS_END__*/` **사이**에 50문항 배열 원소 삽입 (1~40 본편, 41~50 한달전 블록)
- **그 외 JS·CSS(buildPayload·downloadResult·클립보드 폴백·보기소거 눈동자(👁) UI 포함) 수정 절대 금지.**
- 저장: `$QD/{오늘날짜}.html`

## 5. 검증 (아래 스크립트를 그대로 실행, 통과까지 반복 — 기준 임의 완화 금지, 통과 전 종료 금지)
FAIL 시: 보기 재배치(정답 위치 이동)·문항 교체·필드 보완 후 재실행. "과거 도입부 중복" FAIL은 발문을 더 구체적 소주제로 좁히거나 다른 개념으로 교체.
```bash
cd "$QD" && node -e '
const fs=require("fs");
const today=process.argv[1];
const html=fs.readFileSync(today+".html","utf8");
const Q=eval(html.match(/const QUESTIONS = (\[[\s\S]*?\n\]);/)[1]);
let fail=[]; const ok=(c,m)=>{ if(!c) fail.push(m); console.log((c?"PASS":"FAIL")+" — "+m); };
const M=Q.filter(q=>q.monthlyOf), B=Q.filter(q=>!q.monthlyOf);
ok(!html.includes("{{"),"템플릿 토큰({{..}}) 잔존 없음");
ok(Q.length===50,"문항 수 50 (현재 "+Q.length+")");
ok(B.length===40,"본편 40 (현재 "+B.length+")");
ok(M.length===10,"한달전 복원 10 (현재 "+M.length+")");
ok(Q.slice(40).every(q=>q.monthlyOf)&&Q.slice(0,40).every(q=>!q.monthlyOf),"한달전 블록은 41~50번에만");
ok(B.every(q=>!q.retryOf&&!q.q.includes("🔁")),"재도전(🔁·retryOf) 없음 — 오답퀴즈 전담(v5)");
ok(M.every(q=>q.q.includes("🔄")&&/\(한달전 재출제·원본 \d{4}-\d{2}-\d{2}\)/.test(q.src)&&/^\d{4}-\d{2}-\d{2}$/.test(q.monthlyOf)),"한달전 표기(🔄·src·monthlyOf) 일관");
const mcats={}; M.forEach(q=>mcats[q.cat]=(mcats[q.cat]||0)+1);
ok(Math.max(...Object.values(mcats))<=3,"한달전 과목 골고루(과목당 ≤3) "+JSON.stringify(mcats));
ok(Q.every(q=>q.answer>=0&&q.answer<q.opts.length),"정답 인덱스 범위");
ok(Q.every(q=>q.q&&q.expl&&q.src&&q.cat&&q.type&&q.conceptKey),"필수 필드(conceptKey 포함)");
ok(Q.every(q=>q.opts.length===4||(q.type==="OX"&&q.opts.length===2)),"보기 수 4 / OX 2");
const T=t=>B.filter(q=>q.type===t).length;
ok(T("OX")===5,"본편 OX 5 (현재 "+T("OX")+")");
ok(T("조합")===7,"본편 조합 7 (현재 "+T("조합")+")");
ok(T("사례")===4,"본편 사례 4 (현재 "+T("사례")+")");
ok(T("계산")>=2&&T("계산")<=4,"본편 계산 2~4 (현재 "+T("계산")+")");
ok(T("일반")+T("계산")===24,"본편 일반+계산=24 (현재 "+(T("일반")+T("계산"))+")");
ok(Q.filter(q=>q.type==="계산").every(q=>q.calc&&q.calc.expr&&isFinite(q.calc.expected)),"계산형 calc{expr,expected} 필수(전체)");
Q.filter(q=>q.type==="계산"&&q.calc&&q.calc.expr).forEach((q,i)=>{ let v; try{ v=Function("return ("+q.calc.expr+")")(); }catch(e){ v=NaN; }
  ok(isFinite(v)&&Math.abs(v-q.calc.expected)<1e-6,"계산 검산 #"+(i+1)+": "+q.calc.expr+" = "+v+" (기대 "+q.calc.expected+")"); });
ok(Q.filter(q=>q.type==="조합").every(q=>q.q.includes("모두 고른")),"조합형 발문 형식(전체)");
const seq=B.map(q=>q.cat); const seen={}; let contiguous=true;
seq.forEach((c,i)=>{ if(!(c in seen)) seen[c]=1; else if(seq[i-1]!==c) contiguous=false; });
ok(contiguous,"본편 같은 과목 연속 배치");
const cats={}; B.forEach(q=>cats[q.cat]=(cats[q.cat]||0)+1); console.log("  본편 과목 분포: "+JSON.stringify(cats));
const mc=B.filter(q=>q.opts.length===4), oxq=B.filter(q=>q.type==="OX");
const o=oxq.filter(q=>q.answer===0).length; ok(o>=2&&o<=3,"본편 OX 비율 O:"+o+" X:"+(oxq.length-o));
const dist=[0,0,0,0]; mc.forEach(q=>dist[q.answer]++); console.log("  본편 객관식 정답 분포 0~3: "+dist.join("/"));
ok(Math.max(...dist)<=10&&Math.min(...dist)>=7,"본편 정답 분산 7~10");
let run=1,maxRun=1; for(let i=1;i<Q.length;i++){run=(Q[i].answer===Q[i-1].answer)?run+1:1;maxRun=Math.max(maxRun,run);}
ok(maxRun<=2,"전체 50문 같은 정답 인덱스 3연속 없음 (최대 "+maxRun+") — 위반 시 한달전 블록 내부 순서만 교체");
const lr=B.filter(q=>q.q.includes("⏪")).length;
ok(lr===10||lr===40,"장기복습(⏪) 10(기본) 또는 40(전일) (현재 "+lr+")");
ok(B.filter(q=>q.q.includes("⏪")).every(q=>/\(장기복습·\d+일전\)/.test(q.src)),"장기복습 표기(⏪·src) 일관");
const neg=mc.filter(q=>/않은|않는|아닌/.test(q.q)).length; ok(neg>=12&&neg<=18,"본편 부정형 12~18 (현재 "+neg+")");
const longest=mc.filter(q=>q.opts[q.answer].length===Math.max(...q.opts.map(x=>x.length))).length;
ok(longest<=Math.ceil(mc.length*0.4),"본편 정답=최장보기 40% 이하 (현재 "+longest+"/"+mc.length+")");
const norm=s=>s.replace(/<[^>]+>/g,"").replace(/[\s🔁🔄⏪]/g,"");
const past=new Set();
fs.readdirSync(".").filter(f=>f.endsWith(".html")&&!f.startsWith(today)&&!f.startsWith("_")).forEach(f=>{
  (fs.readFileSync(f,"utf8").match(/q: *"[^"]*"/g)||[]).forEach(m=>past.add(norm(m.replace(/^q: *"/,"").replace(/"$/,""))));
});
const dup=B.filter(q=>{const n=norm(q.q);return [...past].some(p=>p.slice(0,30)===n.slice(0,30));});
ok(dup.length===0,"본편 과거 문제문과 도입부 중복 없음"+(dup.length?" — "+dup.map(d=>d.q.slice(0,20)).join(" | "):""));
console.log(fail.length? "\n❌ "+fail.length+"건 — 수정 후 재실행":"\n✅ 전체 통과");
process.exit(fail.length?1:0);
' "$(date +%F)"
```

## 5.5 카톡 푸시 페이로드 생성 (검증 통과 후)
- `mkdir -p "$QD/_push"` 후 `$QD/_push/{오늘날짜}.json` 을 아래 스키마 **그대로** 생성한다:
  ```json
  {"date":"YYYY-MM-DD","quizFile":"YYYY-MM-DD.html",
   "counts":{"신규":0,"장기복습":0,"재도전":0,"한달전":10},
   "longRevNotes":["노트 제목 (N일전)"],
   "monthlySrc":"YYYY-MM-DD~YYYY-MM-DD",
   "dueBacklog":0,
   "ox":[{"q":"...","a":"O","exp":"..."}]}
  ```
- 규칙: **`재도전` 키는 kakao_push 스키마 호환용으로 유지하되 값은 항상 0**(v5 — 임의 삭제 금지). `longRevNotes` 최대 3개. `monthlySrc` = 한달전 복원의 원본 날짜 범위(폴백이면 최고 주 범위). `dueBacklog` = 원장 dueQueue 길이 — **출제에는 사용 금지, 푸시 정보용으로 숫자 1개만 읽는다**(원장 읽기 실패 시 null). `ox`는 정확히 3개 — **오늘 퀴즈 50문에 없는 새 OX**를 장기복습 노트 개념에서 만든다. q ≤ 100자, exp ≤ 80자, a는 "O" 또는 "X"(3문 중 O 1~2개), 모든 문자열에 큰따옴표(")와 백틱 금지.
- 생성 후 `python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$QD/_push/{오늘날짜}.json"` 으로 파싱 검증한다. 실패하면 고쳐서 재검증.
- 이 파일은 카톡 푸시 잡(점심 OX·저녁 정답)이 읽는다 — 스키마를 임의 변경하지 말 것.

## 6. 사용자에게 전달
- 완성된 .html을 present_files로 보여준다. 어떤 과목/개념에서 냈는지·장기복습 노트명(N일전)·**한달전 복원의 원본 날짜(또는 폴백 사용 여부)**를 두세 문장으로 요약. 오답 재도전은 별도 오답퀴즈가 담당함을 새 구성 첫 주(2026-08-31까지)에만 한 줄 안내. 장황한 설명 금지. 모든 문구 한국어, 영어 용어는 한글 병기. 추천 질문 3개 포맷은 생략.
