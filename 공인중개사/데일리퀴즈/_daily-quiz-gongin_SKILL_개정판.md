---
name: daily-quiz-gongin
description: 평일 아침(월~금), 최근 7일 공인중개사 학습노트로 40문항 실전형(일반·조합·계산·사례·OX) 심화 문제지 자동 생성 v2 (원장 듀 큐 재도전·정본 템플릿·자동 검산)
---

> ⚙️ 설치: 설정 > 기능(Capabilities)에서 기존 daily-quiz-gongin 스킬 본문을 이 파일 내용으로 교체.


토·일요일에 실행되는 "데일리 문제지 자동 생성" 작업이다. 아래를 순서대로 수행하라.

**[실행 원칙] 이 지침은 실행 모델의 재량을 최소화하도록 쿼터·수열·스크립트로 고정되어 있다. 단계를 건너뛰거나 "비슷하게" 단순화하지 말고, 명시된 숫자와 절차를 그대로 따른다. 품질의 핵심 4가지: ① 노트 전체 정독 ② 과거 문제 회피 ③ 한 끗 차이 보기 ④ 검증 통과까지 반복.**

## 0. 경로·중복 가드 (가장 먼저)
- 이 작업은 **항상 '오늘 하루치 1개'만** 만든다. 밀린 과거 날짜분을 만들지 않는다.
- bash `date +%F`로 오늘 날짜를 구한다. `ROOT=$(find /sessions/*/mnt -maxdepth 2 -type d -name velog-posts 2>/dev/null | head -1)` — 비어 있으면 "velog-posts 마운트 없음"을 명확히 보고하고 종료. `QD=$ROOT/공인중개사/데일리퀴즈`.
- `$QD/{오늘날짜}.html`이 이미 존재하면 → "오늘 문제지는 이미 생성되어 있다"고만 알리고 즉시 종료(덮어쓰기·중복 생성 금지). Read 도구가 괄호 포함 파일명에서 막히면 bash `cat`으로 읽는다.

## 1. 자료 수집
### 1-1. 최근 7일 학습 노트 (출제 원천)
- `find "$ROOT/공인중개사" -name "*.md" -mtime -7` (claude_ox_오답·데일리퀴즈 폴더 제외).
- 발견된 **모든 .md를 처음부터 끝까지 전부 읽는다(발췌·건너뛰기 금지)**. 핵심 개념·규정·숫자·함정·암기코드를 파악한다.
- 노트가 하나도 없으면 "최근 7일 새 노트가 없어 오늘은 건너뛴다"고만 알리고 종료한다.
- ⚠️ **노트 하단 "확인 필요/⚠️" 섹션에 언급된 수치·항목은 출제 금지.**
### 1-2. 과거 출제 회피 목록
- `grep -ho 'q: *"[^"]*"' "$QD"/20*.html | sort -u`로 과거 문제문을 전부 추출해 읽는다.
- 오늘 문항은 이 목록과 **같은 개념 + 같은 각도** 반복 금지. 같은 과목이라도 다른 조문·다른 숫자·다른 각도(긍정↔부정, 정의↔사례, 암기↔계산, 방향 뒤집기)로 낸다. 예외: 1-3의 재도전 개념은 의도적 반복 OK(단, 각도·숫자는 변형).
### 1-3. 재도전 원천 = 오답 원장 듀 큐 (v2 변경)
- `$ROOT/공인중개사/claude_ox_오답/_ledger/오답_원장.json`을 읽고 `dueQueue`(이미 상습 우선으로 정렬됨)에서 **상위 5~8개**를 재도전 개념으로 편성한다.
- 각 재도전 문항에 네 가지 모두 표기: 문제문 맨 앞 `🔁 `, `conceptKey` = 듀 항목의 conceptKey 그대로, `retryOf` = 같은 값, src 끝 `(재도전)`.
- 재도전도 과거 문항 복사 금지 — 같은 개념을 **다른 각도·다른 숫자**로.
- 원장 파일이 없거나 dueQueue가 비어 있으면: 폴백으로 `claude_ox_오답/`의 최신 오답노트 .md에서 5~8개(기존 방식) + 보고에 "원장 미사용(사유)"를 명시한다.

## 2. 출제 계획표 작성 (문항 작성 전 필수 — 건너뛰기 금지)
40행 계획표: `# | 과목 | 출처 소제목 | conceptKey | 개념 + 함정 설계(무엇을 한 끗 바꿀지) | type | 정답idx | 🔁여부`
### 2-1. 과목 배분
- 40문항을 발견된 과목 수로 고르게(차이 ≤1, 재도전 몰린 과목만 +2 허용). **QUESTIONS 배열에서 같은 과목 문항은 연속 배치.**
### 2-2. 유형 쿼터 (합계 40 — type 필드 값은 아래 표기 그대로)
| type | 수 | 비고 |
|---|---|---|
| 일반 | 20 | 4지선다 "…옳은 것은?" / "…<b>옳지 않은</b> 것은?" |
| 조합 | 7 | 발문에 정확히 "모두 고른 것은?" + `<br>ㄱ. …<br>ㄴ. …` 나열, 선택지는 조합 4개 |
| 계산 | 4 | **calc:{expr,expected} 필수** — expr은 JS로 평가 가능한 산식 문자열, expected는 그 수치. 소재 부족 시 최소 2, 부족분은 일반으로(일반+계산=24 유지) |
| 사례 | 4 | 갑·을·병 등장 사례에 법리 적용 |
| OX | 5 | opts는 ["O","X"], 한 끗 함정(주체·숫자·방향) |
- 4지선다 35문항 중 **부정형 12~18** (`<b>옳지 않은</b>` 굵게). 단순 정의 확인("…란 무엇인가?") 금지 — 함정 비교·메커니즘·계산·헷갈리는 숫자 적극 활용.
### 2-3. 정답 인덱스 사전 배정 (기계적으로)
- 객관식 35문항: 0,1,2,3을 각 8회씩 적은 32개 수열 + 서로 다른 인덱스 3개 1회씩 = 35개(9·9·9·8). 같은 숫자 3연속 금지로 섞어 계획표 순서대로 배정. 보기를 쓸 때 처음부터 그 위치에 정답을 놓는다.
- OX 5문항: O 3·X 2 또는 O 2·X 3.

## 3. 문항 작성 규칙 — 공인중개사 실전 스타일 (원본 규칙 전부 유지)
- 발문: 실제 시험 형식("…에 관한 설명으로 옳은 것은?" 등). 계산형은 조건 전부 명시 + "(다른 조건은 동일)".
- 보기: 내용만(번호 금지). **오답 보기는 정답과 '한 끗 차이'**(숫자 스왑·주체 교체·기간 교체·원칙↔예외·비슷한 제도 교차). 4개 모두 그럴듯하게, 더미 금지. 정답 보기 길이 티 안 나게. 문자열 안에 큰따옴표(")·백틱 사용 금지(따옴표 필요하면 ' ').
- 해설(expl): `[정답 근거] → [왜 그렇게 설계됐는지 메커니즘 1문장] → [함정 포인트·비교 1문장]` 3문장 250자 이내. OX는 "O." / "X."로 시작. 계산형은 산식 전개 포함.
- src: `YYYY-MM-DD 과목 소제목` — 실제 읽은 노트의 것만. 재도전은 끝에 `(재도전)`.
- **필드 계약 v2 (모든 문항):** `{ type, cat, q, opts, answer, expl, src, conceptKey }` + 재도전이면 `retryOf`, 계산형이면 `calc:{expr,expected}`.
  - conceptKey 형식: `과목 소제목-요지` 짧게 (예: "부동산세법 2-5 취득시기"). 재도전은 듀 큐 값을 **그대로 복사**(변형 금지 — 원장 매칭 키다), 신규는 src 소제목 기반.
- 계산형은 작성 직후 node로 expr을 평가해 expected·정답 보기와 일치하는지 확인한다.
- 안티패턴 금지: 노트에 없는 내용 출제 / "확인 필요" 수치 출제 / 과거 문제문 재사용(재도전 제외) / 정답만 조문처럼 길게 / 쿼터 임의 축소.

## 4. HTML 생성 (정본 템플릿 — v2 변경)
- **템플릿 = `$QD/_template.html` 고정.** "최신 날짜 파일 복제"는 폐기됐다 — 정본이 채점·저장(buildPayload/downloadResult, 스키마 v2)의 단일 원천이다.
- 교체할 것 4가지만:
  1. `{{QUIZ_DATE}}` → 오늘날짜 (title과 JS 상수 두 곳)
  2. `{{META_LINE}}` → "2026년 M월 D일 (요일) · 실전형 40문항 · 오답 재도전 N문항(🔁) 포함"
  3. `{{TAGS_HTML}}` → `<span class="tag">🔥 심화</span><span class="tag">📝 실전 4지선다</span><span class="tag">🔁 오답 재도전 N</span><span class="tag">🎯 정답분산</span>` + 오늘 과목명 태그들
  4. `/*__QUESTIONS_START__*/`와 `/*__QUESTIONS_END__*/` **사이**에 40문항 배열 원소 삽입
- **그 외 JS·CSS(buildPayload·downloadResult·클립보드 폴백 포함) 수정 절대 금지.**
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
ok(!html.includes("{{"),"템플릿 토큰({{..}}) 잔존 없음");
ok(Q.length===40,"문항 수 40 (현재 "+Q.length+")");
ok(Q.every(q=>q.answer>=0&&q.answer<q.opts.length),"정답 인덱스 범위");
ok(Q.every(q=>q.q&&q.expl&&q.src&&q.cat&&q.type&&q.conceptKey),"필수 필드(conceptKey 포함)");
ok(Q.every(q=>q.opts.length===4||(q.type==="OX"&&q.opts.length===2)),"보기 수 4 / OX 2");
const T=t=>Q.filter(q=>q.type===t).length;
ok(T("OX")===5,"OX 5 (현재 "+T("OX")+")");
ok(T("조합")===7,"조합 7 (현재 "+T("조합")+")");
ok(T("사례")===4,"사례 4 (현재 "+T("사례")+")");
ok(T("계산")>=2&&T("계산")<=4,"계산 2~4 (현재 "+T("계산")+")");
ok(T("일반")+T("계산")===24,"일반+계산=24 (현재 "+(T("일반")+T("계산"))+")");
ok(Q.filter(q=>q.type==="계산").every(q=>q.calc&&q.calc.expr&&isFinite(q.calc.expected)),"계산형 calc{expr,expected} 필수");
Q.filter(q=>q.type==="계산"&&q.calc&&q.calc.expr).forEach((q,i)=>{ let v; try{ v=Function("return ("+q.calc.expr+")")(); }catch(e){ v=NaN; }
  ok(isFinite(v)&&Math.abs(v-q.calc.expected)<1e-6,"계산 검산 #"+(i+1)+": "+q.calc.expr+" = "+v+" (기대 "+q.calc.expected+")"); });
ok(Q.filter(q=>q.type==="조합").every(q=>q.q.includes("모두 고른")),"조합형 발문 형식");
const seq=Q.map(q=>q.cat); const seen={}; let contiguous=true;
seq.forEach((c,i)=>{ if(!(c in seen)) seen[c]=1; else if(seq[i-1]!==c) contiguous=false; });
ok(contiguous,"같은 과목 연속 배치");
const cats={}; Q.forEach(q=>cats[q.cat]=(cats[q.cat]||0)+1); console.log("  과목 분포: "+JSON.stringify(cats));
const mc=Q.filter(q=>q.opts.length===4), oxq=Q.filter(q=>q.type==="OX");
const o=oxq.filter(q=>q.answer===0).length; ok(o>=2&&o<=3,"OX 비율 O:"+o+" X:"+(oxq.length-o));
const dist=[0,0,0,0]; mc.forEach(q=>dist[q.answer]++); console.log("  객관식 정답 분포 0~3: "+dist.join("/"));
ok(Math.max(...dist)<=10&&Math.min(...dist)>=7,"정답 분산 7~10");
let run=1,maxRun=1; for(let i=1;i<Q.length;i++){run=(Q[i].answer===Q[i-1].answer)?run+1:1;maxRun=Math.max(maxRun,run);}
ok(maxRun<=2,"같은 정답 인덱스 3연속 없음 (최대 "+maxRun+")");
const re=Q.filter(q=>q.retryOf).length; ok(re>=5&&re<=8,"재도전(retryOf) 5~8 (현재 "+re+")");
ok(Q.filter(q=>q.retryOf).every(q=>q.q.includes("🔁")&&/\(재도전\)/.test(q.src)),"재도전 표기(🔁·src) 일관");
const neg=mc.filter(q=>/않은|않는|아닌/.test(q.q)).length; ok(neg>=12&&neg<=18,"부정형 12~18 (현재 "+neg+")");
const longest=mc.filter(q=>q.opts[q.answer].length===Math.max(...q.opts.map(x=>x.length))).length;
ok(longest<=Math.ceil(mc.length*0.4),"정답=최장보기 40% 이하 (현재 "+longest+"/"+mc.length+")");
const norm=s=>s.replace(/<[^>]+>/g,"").replace(/[\s🔁]/g,"");
const past=new Set();
fs.readdirSync(".").filter(f=>f.endsWith(".html")&&!f.startsWith(today)&&!f.startsWith("_")).forEach(f=>{
  (fs.readFileSync(f,"utf8").match(/q: *"[^"]*"/g)||[]).forEach(m=>past.add(norm(m.replace(/^q: *"/,"").replace(/"$/,""))));
});
const dup=Q.filter(q=>!q.retryOf).filter(q=>{const n=norm(q.q);return [...past].some(p=>p.slice(0,30)===n.slice(0,30));});
ok(dup.length===0,"과거 문제문과 도입부 중복 없음"+(dup.length?" — "+dup.map(d=>d.q.slice(0,20)).join(" | "):""));
console.log(fail.length? "\n❌ "+fail.length+"건 — 수정 후 재실행":"\n✅ 전체 통과");
process.exit(fail.length?1:0);
' "$(date +%F)"
```

## 6. 사용자에게 전달
- 완성된 .html을 present_files로 보여준다. 어떤 과목/개념에서 냈는지·재도전 문항 수를 한두 문장으로 요약. 장황한 설명 금지. 모든 문구 한국어, 영어 용어는 한글 병기. 추천 질문 3개 포맷은 생략.
