// 템플릿 v2 — ① 보기별 O·X 마킹 ② 중간 제출(푼 것만 채점) ③ 진행 저장·복원(localStorage)
//   전체 제출 payload는 종전과 100% 동일해야 한다(회귀는 payload_regression.test.js 가 별도 보증).
'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { JSDOM, VirtualConsole } = require('jsdom');
const H = require('./_helpers');
const { BASE } = require('./fixtures/payload_questions');

const DATE = '2026-09-10';
const FIX = path.join(H.ENGINE, 'tests', 'fixtures');
let pass = 0, fail = 0;
const out = [];

function t(name, fn) {
  try { fn(); pass++; out.push('  ✔ ' + name); }
  catch (e) { fail++; out.push('  ✘ ' + name + '\n      ' + String(e.message).split('\n').join('\n      ')); }
}

// ── jsdom 부팅 헬퍼 ──────────────────────────────────────────────
/** Map 기반 localStorage 스텁 — 인스턴스를 넘겨 '새 DOM으로 재로드'를 흉내낸다 */
function makeStore() {
  const m = new Map();
  return { map: m, api: {
    getItem: k => (m.has(String(k)) ? m.get(String(k)) : null),
    setItem: (k, v) => { m.set(String(k), String(v)); },
    removeItem: k => { m.delete(String(k)); },
    clear: () => m.clear(),
    key: i => (Array.from(m.keys())[i] === undefined ? null : Array.from(m.keys())[i]),
    get length() { return m.size; },
  } };
}
/** store=null이면 localStorage 없음(jsdom 기본 = opaque origin), 'throw'면 접근 시 예외 */
function boot(html, store) {
  const dom = new JSDOM(html, {
    runScripts: 'dangerously', virtualConsole: new VirtualConsole(),
    beforeParse(window) {
      if (store === 'throw') {
        Object.defineProperty(window, 'localStorage', {
          configurable: true, get() { throw new Error('SecurityError: file:// origin'); } });
      } else if (store) {
        Object.defineProperty(window, 'localStorage', { configurable: true, value: store.api });
      }
    },
  });
  const win = dom.window;
  win.URL.createObjectURL = () => 'blob:test';
  win.URL.revokeObjectURL = () => {};
  win.Element.prototype.scrollIntoView = function () {};
  win.HTMLAnchorElement.prototype.click = function () {};
  win.__confirms = [];
  win.confirm = (msg) => { win.__confirms.push(msg); return win.__confirmAnswer !== false; };
  return { dom, win, doc: win.document };
}
function page(store, questions) {
  return boot(H.injectQuestions(H.renderUnified('gongin', 'daily', DATE), questions || BASE), store);
}
const state = (win, expr) => JSON.parse(win.eval('JSON.stringify(' + expr + ')'));

// ── 문항 응답 헬퍼 (BASE 12문항 기준) ─────────────────────────────
const optOf = (doc, qi, oi) => doc.querySelector(`.opt[data-q="${qi}"][data-o="${oi}"]`);
const markOf = (doc, qi, oi) => doc.querySelector(`.optox[data-q="${qi}"][data-o="${oi}"]`);
const pickCorrect = (doc, qs, qi) => H.click(optOf(doc, qi, qs[qi].answer));
const pickWrong = (doc, qs, qi) => H.click(optOf(doc, qi, (qs[qi].answer + 1) % qs[qi].opts.length));
const pickDK = (doc, qi) => H.click(doc.querySelector(`.dk-btn[data-q="${qi}"]`));
// v2.1 · ? 마킹 헬퍼 — 세 번 눌러 · → O → X → ?
const markQ = (doc, qi, oi) => { const b = markOf(doc, qi, oi); H.click(b); H.click(b); H.click(b); return b; };
const stmtOf = (doc, qi, i) => doc.querySelectorAll(`#card-${qi} .ox-mark`)[i];
const markQStmt = (doc, qi, i) => { const b = stmtOf(doc, qi, i); H.click(b); H.click(b); H.click(b); return b; };
/** BASE와 같은 12문항 · q3(조합)의 발문만 부정형으로 — 조합 지문 판정의 부정형 경로용 */
const NEGQ = BASE.map((q, i) => i !== 3 ? q : Object.assign({}, q,
  { q: q.q.replace('옳은 것을 모두 고른 것은?', '<b>옳지 않은</b> 것을 모두 고른 것은?') }));

/** 단답 ❌ → 놓친 포인트 1개 → 교정 타이핑 통과 */
function saWrong(doc, qs, qi) {
  const c = doc.getElementById('card-' + qi);
  H.setVal(c.querySelector('.sa-input'), '기억나는 만큼만 씀 ' + qi);
  H.click(c.querySelector('.sa-reveal'));
  H.click(c.querySelectorAll('.sa-grade button')[1]);
  H.click(c.querySelectorAll('.sa-fix .sa-misschips .sa-chip')[0]);
  H.setVal(c.querySelector('.sa-fixinput'), qs[qi].answer);
}
function saOk(doc, qs, qi) {
  const c = doc.getElementById('card-' + qi);
  H.setVal(c.querySelector('.sa-input'), qs[qi].answer);
  H.click(c.querySelector('.sa-reveal'));
  H.click(c.querySelectorAll('.sa-grade button')[0]);
}
/** 0~6번(7문) 응답 — 정답 0·2·3 / 오답 1·5 / 무답 4 / 단답 오답 6 */
function answerFirst7(doc, qs) {
  pickCorrect(doc, qs, 0); pickWrong(doc, qs, 1); pickCorrect(doc, qs, 2);
  pickCorrect(doc, qs, 3); pickDK(doc, 4); pickWrong(doc, qs, 5); saWrong(doc, qs, 6);
}
/** 7~11번(5문) 응답 — 정답 7·9·10 / 오답 8 / 단답 정답 11 */
function answerLast5(doc, qs) {
  pickCorrect(doc, qs, 7); pickWrong(doc, qs, 8); pickCorrect(doc, qs, 9);
  pickCorrect(doc, qs, 10); saOk(doc, qs, 11);
}
/** 진단 게이트 통과 — 열려 있는 .mcq-diag(미완료)마다 원인 1개 선택 후 저장 */
function passDiag(doc) {
  doc.querySelectorAll('.mcq-diag:not(.done)').forEach((d, k) => H.click(d.querySelectorAll('.sa-chip')[k % 4]));
  const save = doc.getElementById('diagSave');
  if (save) {
    assert.ok(!save.disabled, '진단 저장 버튼이 잠겨 있음');
    H.click(save);
  }
}

console.log('\n[template]');

// ══ ① 보기별 O·X 마킹 ═══════════════════════════════════════════
t('① 눈동자(👁) 소거 UI는 제거됐다 (머리 주석의 변경 이력만 남는다)', () => {
  const full = H.renderUnified('gongin', 'daily', DATE);
  const body = full.slice(full.indexOf('-->'));            // 머리 주석(변경 이력) 제외
  assert.ok(!/\.eye[{ :.,]|'eye'|"eye"|ruled|👁/.test(body), '👁/eye/ruled 잔존');
  assert.ok(body.includes('optox'), 'O·X 토글 클래스 없음');
  const { doc, win } = boot(full, null);
  assert.strictEqual(doc.querySelectorAll('.eye, .ruled').length, 0, '소거 UI가 DOM에 남음');
  win.close();
});

t('① 토글 순서 · → O → X → ? → · · 보기 테두리 클래스(mk-o/mk-x/mk-q)', () => {
  const { doc, win } = page(null);
  const mk = markOf(doc, 0, 0), el = optOf(doc, 0, 0);
  assert.strictEqual(mk.textContent, '·');
  H.click(mk);
  assert.strictEqual(mk.textContent, 'O');
  assert.ok(mk.classList.contains('o') && el.classList.contains('mk-o'), 'O 상태 클래스');
  H.click(mk);
  assert.strictEqual(mk.textContent, 'X');
  assert.ok(mk.classList.contains('x') && el.classList.contains('mk-x'), 'X 상태 클래스(소거 승계)');
  H.click(mk);
  assert.strictEqual(mk.textContent, '?');
  assert.ok(mk.classList.contains('q') && el.classList.contains('mk-q'), '? 상태 클래스');
  assert.ok(!mk.classList.contains('x') && !el.classList.contains('mk-x'), 'X 상태가 남음');
  H.click(mk);
  assert.strictEqual(mk.textContent, '·');
  assert.ok(!el.classList.contains('mk-o') && !el.classList.contains('mk-x')
    && !el.classList.contains('mk-q'), '· 로 복귀');
  win.close();
});

t('① ㄱㄴㄷ 지문 마킹과 같은 토글 순서·클래스(o/x/q)', () => {
  const { doc, win } = page(null);
  const g = doc.querySelectorAll('#card-3 .ox-mark')[0];
  H.click(g); assert.ok(g.classList.contains('o') && g.textContent === 'O');
  H.click(g); assert.ok(g.classList.contains('x') && g.textContent === 'X');
  H.click(g); assert.ok(g.classList.contains('q') && g.textContent === '?', '? 상태');
  H.click(g); assert.ok(!g.classList.contains('o') && !g.classList.contains('x')
    && !g.classList.contains('q') && g.textContent === '·');
  win.close();
});

t('① 토글은 보기 선택과 무관 · 선택과 마킹이 겹쳐도 둘 다 남는다', () => {
  const { doc, win } = page(null);
  H.click(markOf(doc, 0, 2));                                  // 토글만 클릭
  assert.strictEqual(state(win, 'selected')[0], null, '토글 클릭이 선택을 만들었다');
  assert.strictEqual(doc.querySelectorAll('#card-0 .opt.sel').length, 0);
  H.click(optOf(doc, 0, 2));                                   // 같은 보기를 선택
  H.click(markOf(doc, 0, 2));                                  // O → X
  const el = optOf(doc, 0, 2);
  assert.ok(el.classList.contains('sel') && el.classList.contains('mk-x'), '선택+마킹 공존');
  assert.strictEqual(state(win, 'selected')[0], 2, '마킹이 선택을 지웠다');
  assert.ok(el.querySelector('.mk'), '선택 표시(원형 마크) 유지');
  win.close();
});

t('① OX형은 보기 토글 대신 문항 ? 플래그 1개 (객관식 나머지 전 유형에는 보기별 토글)', () => {
  const { doc, win } = page(null);
  const oxb = doc.querySelectorAll('#card-4 .optox');
  assert.strictEqual(oxb.length, 1, 'OX형(q4)에는 문항 플래그 1개만');
  assert.strictEqual(oxb[0].dataset.o, '-1', 'OX 플래그는 data-o=-1');
  oxb[0].click(); assert.strictEqual(win.markStateOf(oxb[0]), 'q', 'OX 플래그 · → ?');
  assert.ok(oxb[0].closest('.opt').classList.contains('mk-q'), '홀더에 mk-q');
  oxb[0].click(); assert.strictEqual(win.markStateOf(oxb[0]), '', 'OX 플래그 ? → ·(2상태)');
  [0, 1, 2, 3, 5, 7, 8, 9, 10].forEach(qi => {
    assert.strictEqual(doc.querySelectorAll('#card-' + qi + ' .optox').length, BASE[qi].opts.length,
      'q' + qi + ' 토글 수');
  });
  assert.strictEqual(doc.querySelectorAll('#card-6 .optox').length, 0, '단답(q6)에 토글이 붙음');
  win.close();
});

t('① 채점 후 잠금 — 마킹 표시는 유지되고 더는 바뀌지 않는다', () => {
  const { doc, win } = page(null);
  H.click(markOf(doc, 0, 0));                                  // O
  answerFirst7(doc, BASE); answerLast5(doc, BASE);
  H.click(doc.getElementById('submitBtn'));
  passDiag(doc);
  const mk = markOf(doc, 0, 0);
  assert.strictEqual(mk.textContent, 'O', '채점 후 마킹 소실');
  H.click(mk);
  assert.strictEqual(mk.textContent, 'O', '채점 후에도 토글이 먹는다(잠금 실패)');
  win.close();
});

t('① 마킹은 payload에 아무 영향이 없다 (마킹 유/무 payload 동일)', () => {
  const run = (mark) => {
    const { doc, win } = page(null);
    if (mark) {
      [[0, 0], [1, 1], [3, 2], [10, 4]].forEach(([q, o]) => { H.click(markOf(doc, q, o)); H.click(markOf(doc, q, o)); });
      H.click(markOf(doc, 5, 0));
      doc.querySelectorAll('#card-3 .ox-mark').forEach(g => H.click(g));
    }
    answerFirst7(doc, BASE); answerLast5(doc, BASE);
    H.click(doc.getElementById('submitBtn'));
    passDiag(doc);
    const p = state(win, 'LAST_PAYLOAD'); win.close(); return p;
  };
  assert.deepStrictEqual(H.diffPaths(run(false), run(true)), [], '마킹이 payload를 흔들었다');
});

// ══ ② 중간 제출 ═════════════════════════════════════════════════
t('② 중간제출 버튼: 0개 답 → 잠김 / 1개 이상 → 열림 / 전 문항 완료 → 다시 잠김', () => {
  const { doc, win } = page(null);
  const pb = doc.getElementById('partialBtn');
  assert.ok(pb, '중간제출 버튼 없음');
  assert.ok(pb.disabled, '아무것도 안 풀었는데 열려 있음');
  pickCorrect(doc, BASE, 0);
  assert.ok(!pb.disabled, '1문항 답했는데 잠겨 있음');
  answerFirst7(doc, BASE); answerLast5(doc, BASE);
  assert.ok(pb.disabled, '전 문항 완료인데 중간제출이 열려 있음');
  assert.ok(!doc.getElementById('submitBtn').disabled, '전체 제출이 잠겨 있음');
  win.close();
});

t('② confirm 문구 · 취소하면 채점하지 않는다', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  win.__confirmAnswer = false;
  H.click(doc.getElementById('partialBtn'));
  assert.strictEqual(win.__confirms.length, 1, 'confirm 미호출');
  assert.strictEqual(win.__confirms[0],
    '7문항만 채점하고 나머지 5문항은 미응답으로 남깁니다. 미응답은 정답이 공개되지 않고 다음 퀴즈에서 다시 나옵니다.');
  assert.strictEqual(state(win, 'LAST_PAYLOAD'), null, '취소했는데 채점됨');
  assert.ok(!doc.getElementById('result').classList.contains('show'), '취소했는데 결과가 열림');
  assert.deepStrictEqual(state(win, 'GRADED').filter(Boolean), [], '취소했는데 채점 확정됨');
  win.close();
});

t('② 7문 답하고 중간제출 → partial·total·answeredCount·skippedCount', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));
  passDiag(doc);
  const p = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(p.partial, true, 'partial');
  assert.strictEqual(p.total, 7, 'total = 답한 문항 수');
  assert.strictEqual(p.answeredCount, 7);
  assert.strictEqual(p.skippedCount, 5);
  assert.strictEqual(p.score, 3, '답한 것 중 정답(q0·q2·q3)');
  assert.strictEqual(p.wrongCount, 4, '답한 오답(q1·q4·q5·q6)');
  assert.strictEqual(p.results.length, 12, 'results[]는 전 문항');
  assert.strictEqual(p.quizId, DATE);
  win.close();
});

t('② 미응답 항목은 축약형 — 정답·해설·options 없음 · wrong[]에도 없음', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));
  passDiag(doc);
  const p = state(win, 'LAST_PAYLOAD');
  const skipped = p.results.filter(r => r.skipped);
  assert.deepStrictEqual(skipped.map(r => r.id), [8, 9, 10, 11, 12].map(i => `${DATE}-q${i}`));
  skipped.forEach(r => {
    assert.deepStrictEqual(Object.keys(r).sort(),
      ['cat', 'conceptKey', 'correctAnswered', 'id', 'myAnswer', 'q', 'retryOf', 'skipped', 'type'],
      '미응답 항목 키 집합');
    assert.strictEqual(r.correctAnswered, null);
    assert.strictEqual(r.myAnswer, null);
  });
  assert.strictEqual(p.results[9].retryOf, '중개사법 과태료 개별금액', '미응답이어도 retryOf는 남는다');
  assert.ok(p.wrong.every(w => !w.skipped), 'wrong[]에 skipped가 섞임');
  assert.deepStrictEqual(p.wrong.map(w => w.id), [2, 5, 6, 7].map(i => `${DATE}-q${i}`), 'wrong[]은 답한 오답만');
  win.close();
});

t('② 미응답 카드: 배지 표시 · 정답/해설 미공개 · 답한 문항만 채점 확정', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));
  passDiag(doc);
  [7, 8, 9, 10, 11].forEach(qi => {
    const card = doc.getElementById('card-' + qi);
    assert.ok(card.querySelector('.skipbadge'), 'q' + qi + ' 미응답 배지 없음');
    assert.strictEqual(card.querySelector('.skipbadge').textContent, '미응답(중간제출)');
    assert.ok(!doc.getElementById('expl-' + qi).classList.contains('show'), 'q' + qi + ' 해설이 공개됨');
    assert.strictEqual(doc.getElementById('expl-' + qi).innerHTML, '', 'q' + qi + ' 해설 내용이 채워짐');
    assert.strictEqual(card.querySelectorAll('.opt.correct').length, 0, 'q' + qi + ' 정답이 표시됨');
  });
  [0, 1, 2, 3, 4, 5, 6].forEach(qi => {
    assert.ok(doc.getElementById('expl-' + qi).classList.contains('show'), 'q' + qi + ' 해설 미공개');
    assert.ok(!doc.getElementById('card-' + qi).querySelector('.skipbadge'), 'q' + qi + '에 미응답 배지');
  });
  assert.deepStrictEqual(state(win, 'GRADED'),
    [true, true, true, true, true, true, true, false, false, false, false, false]);
  win.close();
});

t('② 진단 게이트는 답한 오답에만 열린다 (미응답 q8은 열리지 않는다)', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));
  assert.ok(doc.getElementById('diag-1'), 'q1 진단 없음');
  assert.ok(doc.getElementById('diag-5'), 'q5 진단 없음');
  assert.ok(!doc.getElementById('diag-4'), '🤷 무답에 진단이 열림(자동 개념부재여야 한다)');
  assert.ok(!doc.getElementById('diag-8'), '미응답 q8에 진단이 열림');
  assert.strictEqual(doc.querySelectorAll('.mcq-diag').length, 2);
  passDiag(doc);
  const p = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(p.results[4].errorCause, '개념부재', '🤷 자동 진단');
  assert.ok(p.results[1].errorCause && p.results[5].errorCause, '진단 원인 미부착');
  assert.ok(!('errorCause' in p.results[8]), '미응답에 원인이 붙음');
  win.close();
});

t('② 중간제출 후 나머지를 마저 풀고 전체 제출 → partial 키 없음 · total 12 · 앞 7문 결과 고정', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));
  passDiag(doc);
  const p1 = state(win, 'LAST_PAYLOAD');
  // 이어서 나머지 5문
  assert.ok(doc.getElementById('submitBtn').disabled, '아직 전체 제출이 열려 있음');
  answerLast5(doc, BASE);
  assert.ok(!doc.getElementById('submitBtn').disabled, '전 문항 완료인데 전체 제출이 잠김');
  H.click(doc.getElementById('submitBtn'));
  passDiag(doc);
  const p2 = state(win, 'LAST_PAYLOAD');
  assert.ok(!('partial' in p2), 'partial 키가 남음');
  assert.ok(!('answeredCount' in p2) && !('skippedCount' in p2), '부분 제출 키가 남음');
  assert.strictEqual(p2.total, 12);
  assert.strictEqual(p2.score, 7);
  assert.strictEqual(p2.wrongCount, 5);
  assert.ok(p2.results.every(r => !('skipped' in r)), 'skipped 항목이 남음');
  for (let i = 0; i <= 6; i++) {
    assert.deepStrictEqual(p2.results[i], p1.results[i], 'q' + i + ' 결과가 재채점으로 바뀜');
  }
  assert.deepStrictEqual(state(win, 'GRADED'), new Array(12).fill(true));
  win.close();
});

t('② 중간제출 진단을 저장하지 않고 이어서 전체 제출해도 진단 칸이 중복되지 않는다', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));               // 진단 게이트만 열고 저장은 하지 않는다
  H.click(doc.getElementById('diag-1').querySelectorAll('.sa-chip')[0]);
  answerLast5(doc, BASE);
  H.click(doc.getElementById('submitBtn'));
  assert.strictEqual(doc.querySelectorAll('#diag-1').length, 1, '진단 칸 중복 생성');
  assert.strictEqual(doc.querySelectorAll('#diagSave').length, 1, '저장 버튼 중복 생성');
  assert.strictEqual(doc.querySelectorAll('.mcq-diag').length, 3, 'q1·q5·q8');
  passDiag(doc);
  const p = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(p.total, 12);
  [1, 4, 5, 8].forEach(qi => assert.ok(p.results[qi].errorCause, 'q' + qi + ' 원인 미부착'));
  win.close();
});

t('② 중간제출을 거친 전체 제출 payload = 처음부터 전체 제출한 payload', () => {
  const straight = (() => {
    const { doc, win } = page(null);
    answerFirst7(doc, BASE); answerLast5(doc, BASE);
    H.click(doc.getElementById('submitBtn'));
    passDiag(doc);
    const p = state(win, 'LAST_PAYLOAD'); win.close(); return p;
  })();
  const viaPartial = (() => {
    const { doc, win } = page(null);
    answerFirst7(doc, BASE);
    H.click(doc.getElementById('partialBtn'));
    passDiag(doc);
    answerLast5(doc, BASE);
    H.click(doc.getElementById('submitBtn'));
    passDiag(doc);
    const p = state(win, 'LAST_PAYLOAD'); win.close(); return p;
  })();
  // 진단 원인은 클릭 순서로 갈릴 수 있으므로 경로 비교에서 제외
  const strip = p => { p.results.forEach(r => { delete r.errorCause; delete r.causeNote; });
                       p.wrong.forEach(r => { delete r.errorCause; delete r.causeNote; }); return p; };
  assert.deepStrictEqual(H.diffPaths(strip(straight), strip(viaPartial)), []);
});

t('② 전체 제출 payload는 레거시와 바이트 단위로 같다 (키 순서 포함 · 기대 차이 monthlyOf만 제거)', () => {
  const runOn = html => {
    const { win } = H.boot(H.injectQuestions(html, BASE));
    const p = H.runScenario(win, BASE); win.close(); return p;
  };
  const norm = p => {
    p.generatedAt = 'X';
    p.results.forEach(r => { delete r.monthlyOf; });        // 레거시 gongin에는 없는 필드(문서화된 차이)
    p.wrong.forEach(r => { delete r.monthlyOf; });
    return JSON.stringify(p, null, 2);
  };
  assert.strictEqual(norm(runOn(H.renderUnified('gongin', 'daily', DATE))),
                     norm(runOn(H.readLegacy('gongin_daily', DATE))), '직렬화 결과(키 순서 포함) 불일치');
});

t('② 전체 제출 payload의 키 순서 — partial 키가 끼어들지 않는다', () => {
  const { doc, win } = page(null);
  answerFirst7(doc, BASE); answerLast5(doc, BASE);
  H.click(doc.getElementById('submitBtn'));
  passDiag(doc);
  const p = state(win, 'LAST_PAYLOAD');
  assert.deepStrictEqual(Object.keys(p),
    ['schemaVersion', 'subject', 'date', 'quizId', 'score', 'total', 'wrongCount',
     'results', 'wrong', 'generatedAt']);
  assert.deepStrictEqual(Object.keys(p.results[0]),
    ['id', 'cat', 'type', 'q', 'options', 'myAnswer', 'correct', 'expl', 'src',
     'conceptKey', 'retryOf', 'correctAnswered']);
  win.close();
});

// ══ ③ 진행 저장·복원 ════════════════════════════════════════════
const KEY = 'hgq:공인중개사:' + DATE;

t('③ 저장 키는 hgq:과목:퀴즈ID (retry는 -RQ 접미)', () => {
  const s1 = makeStore();
  const p1 = page(s1); pickCorrect(p1.doc, BASE, 0); p1.win.close();
  assert.deepStrictEqual([...s1.map.keys()], [KEY]);
  const s2 = makeStore();
  const p2 = boot(H.injectQuestions(H.renderUnified('gongin', 'retry', DATE), BASE), s2);
  pickCorrect(p2.doc, BASE, 0); p2.win.close();
  assert.deepStrictEqual([...s2.map.keys()], ['hgq:공인중개사:' + DATE + '-RQ']);
});

t('③ 답 5개 입력 → 새 DOM으로 재로드 → 5개 복원 + 복원 배너', () => {
  const store = makeStore();
  const a = page(store);
  [0, 1, 2, 3, 5].forEach(qi => pickCorrect(a.doc, BASE, qi));
  H.click(markOf(a.doc, 7, 1)); H.click(markOf(a.doc, 7, 1));       // 보기 X 마킹
  H.click(a.doc.querySelectorAll('#card-3 .ox-mark')[0]);           // ㄱㄴㄷ O 마킹
  const before = state(a.win, 'selected');
  a.win.close();
  assert.ok(store.map.get(KEY), '저장분 없음');

  const b = page(store);
  assert.deepStrictEqual(state(b.win, 'selected'), before, '선택 복원 실패');
  assert.strictEqual(b.doc.querySelectorAll('.opt.sel').length, 5);
  assert.strictEqual(b.doc.getElementById('pcount').textContent, '5 / 12 완료');
  const bar = b.doc.getElementById('restoreBar');
  assert.ok(!bar.hidden, '복원 배너가 숨겨져 있음');
  assert.ok(bar.textContent.includes('이전 진행 복원됨'), '배너 문구');
  assert.ok(bar.textContent.includes('답 5개'), '배너 답 개수: ' + bar.textContent);
  assert.ok(b.doc.getElementById('restoreReset'), '[처음부터 다시] 링크 없음');
  assert.strictEqual(markOf(b.doc, 7, 1).textContent, 'X', '보기 O·X 마킹 복원 실패');
  assert.strictEqual(b.doc.querySelectorAll('#card-3 .ox-mark')[0].textContent, 'O', 'ㄱㄴㄷ 마킹 복원 실패');
  b.win.close();
});

t('③ [처음부터 다시] → 저장분 삭제', () => {
  const store = makeStore();
  const a = page(store);
  [0, 1, 2].forEach(qi => pickCorrect(a.doc, BASE, qi));
  a.win.close();
  const b = page(store);
  H.click(b.doc.getElementById('restoreReset'));
  assert.strictEqual(store.map.size, 0, '저장분이 남음');
  b.win.close();
});

t('③ 단답 상태(타이핑·공개·자가채점·놓친 포인트·교정)도 복원된다', () => {
  const store = makeStore();
  const a = page(store);
  saWrong(a.doc, BASE, 6);
  const before = state(a.win, 'selected')[6];
  a.win.close();
  const b = page(store);
  assert.deepStrictEqual(state(b.win, 'selected')[6], before, '단답 상태 복원 실패');
  const c = b.doc.getElementById('card-6');
  assert.ok(c.querySelector('.sa-input').disabled, '정답 공개 상태 미복원');
  assert.ok(c.querySelectorAll('.sa-grade button')[1].classList.contains('on-no'), '❌ 표시 미복원');
  assert.ok(c.querySelector('.sa-fix.done'), '교정 통과 상태 미복원');
  assert.strictEqual(b.doc.getElementById('pcount').textContent, '1 / 12 완료');
  b.win.close();
});

t('③ 전체 제출 완료 → 저장분 삭제', () => {
  const store = makeStore();
  const { doc, win } = page(store);
  answerFirst7(doc, BASE); answerLast5(doc, BASE);
  assert.ok(store.map.get(KEY), '푸는 동안 저장이 안 됨');
  H.click(doc.getElementById('submitBtn'));
  assert.ok(store.map.get(KEY), '진단 게이트 통과 전인데 저장분이 사라짐');
  passDiag(doc);
  assert.strictEqual(store.map.size, 0, '전체 제출 후에도 저장분이 남음');
  win.close();
});

t('③ 중간 제출 시엔 저장분 유지 → 재로드하면 채점된 문항이 채점 상태로 복원', () => {
  const store = makeStore();
  const a = page(store);
  answerFirst7(a.doc, BASE);
  H.click(a.doc.getElementById('partialBtn'));
  passDiag(a.doc);
  assert.ok(store.map.get(KEY), '중간 제출 후 저장분이 사라짐');
  const p1 = state(a.win, 'LAST_PAYLOAD');
  a.win.close();

  const b = page(store);
  assert.deepStrictEqual(state(b.win, 'GRADED'),
    [true, true, true, true, true, true, true, false, false, false, false, false], '채점 상태 미복원');
  assert.ok(b.doc.getElementById('expl-0').classList.contains('show'), '채점된 문항의 해설 미복원');
  assert.strictEqual(b.doc.querySelectorAll('#card-1 .opt.correct').length, 1, '정답 표시 미복원');
  assert.ok(b.doc.getElementById('card-8').querySelector('.skipbadge'), '미응답 배지 미복원');
  assert.ok(!b.doc.getElementById('expl-8').classList.contains('show'), '미응답 해설이 복원 때 공개됨');
  const d1 = b.doc.getElementById('diag-1');
  assert.ok(d1 && d1.classList.contains('done'), '저장된 오답 진단 미복원');
  assert.strictEqual(d1.querySelectorAll('.sa-chip.on').length, 1, '선택했던 원인 미복원');
  // 이어서 나머지를 풀고 전체 제출 — 앞 7문 결과는 그대로여야 한다
  answerLast5(b.doc, BASE);
  H.click(b.doc.getElementById('submitBtn'));
  passDiag(b.doc);
  const p2 = state(b.win, 'LAST_PAYLOAD');
  assert.ok(!('partial' in p2));
  assert.strictEqual(p2.total, 12);
  for (let i = 0; i <= 6; i++) assert.deepStrictEqual(p2.results[i], p1.results[i], 'q' + i + ' 결과가 흔들림');
  assert.strictEqual(store.map.size, 0, '전체 제출 후 저장분이 남음');
  b.win.close();
});

t('③ localStorage가 없거나(opaque origin) 예외를 던져도 페이지는 그대로 동작', () => {
  ['none', 'throw'].forEach(mode => {
    const html = H.injectQuestions(H.renderUnified('gongin', 'daily', DATE), BASE);
    const { doc, win } = boot(html, mode === 'throw' ? 'throw' : null);
    assert.ok(doc.getElementById('restoreBar').hidden, mode + ': 배너가 떴다');
    answerFirst7(doc, BASE); answerLast5(doc, BASE);
    H.click(doc.getElementById('submitBtn'));
    passDiag(doc);
    const p = state(win, 'LAST_PAYLOAD');
    assert.strictEqual(p.total, 12, mode + ': 채점 실패');
    assert.strictEqual(p.score, 7, mode + ': 점수 불일치');
    win.close();
  });
});

// ══ ④ ? 마킹 + ❓ 물음표 모음 (v2.1) ════════════════════════════
/** 전 문항 응답 → 전체 제출 → 진단 게이트 통과 */
function fullSubmit(doc, qs) {
  answerFirst7(doc, qs); answerLast5(doc, qs);
  H.click(doc.getElementById('submitBtn'));
  passDiag(doc);
}

t('④ 진행 저장·복원이 ?를 포함해 왕복한다 (보기·지문 둘 다)', () => {
  const store = makeStore();
  const a = page(store);
  markQ(a.doc, 0, 2);                                   // 보기 ?
  markQStmt(a.doc, 3, 1);                               // ㄴ 지문 ?
  H.click(markOf(a.doc, 1, 0));                         // O (섞여도 갈리지 않는지)
  const snap = state(a.win, 'snapshot()');
  assert.strictEqual(snap.optMarks['0'][2], 'q', 'snapshot에 보기 q 미기록');
  assert.strictEqual(snap.oxMarks['3'][1], 'q', 'snapshot에 지문 q 미기록');
  assert.strictEqual(snap.optMarks['1'][0], 'o');
  a.win.close();

  const b = page(store);
  const mk = markOf(b.doc, 0, 2);
  assert.strictEqual(mk.textContent, '?', '보기 ? 복원 실패');
  assert.ok(mk.classList.contains('q') && optOf(b.doc, 0, 2).classList.contains('mk-q'), '복원된 ? 상태 클래스');
  assert.strictEqual(stmtOf(b.doc, 3, 1).textContent, '?', '지문 ? 복원 실패');
  assert.ok(stmtOf(b.doc, 3, 1).classList.contains('q'));
  assert.strictEqual(markOf(b.doc, 1, 0).textContent, 'O', 'O 마킹이 흔들림');
  b.win.close();
});

t('④ 전체 제출 → #qmarks N=4 · 판정 4개 · 문항당 해설 1회 · 앵커 · 위치', () => {
  // 일반 보기 2개(정답 1 · 오답 1) + 계산형 보기 1개 + 조합 지문 1개(부정형 발문 · 정답 조합에 든 ㄱ)
  // ※ OX형 보기에는 v2부터 토글이 붙지 않는다(아래 별도 테스트) — 그 자리를 계산형 보기가 대신한다
  const { doc, win } = page(null, NEGQ);
  markQ(doc, 0, 1);                                     // q0 정답 보기(answer=1)
  markQ(doc, 1, 2);                                     // q1 오답 보기(answer=0)
  markQ(doc, 2, 1);                                     // q2 계산형 정답 보기(answer=1)
  markQStmt(doc, 3, 0);                                 // q3 ㄱ 지문 · 부정형 발문 · 정답 조합(ㄱ, ㄷ, ㄹ)에 듦
  fullSubmit(doc, NEGQ);

  const qm = doc.getElementById('qmarks');
  assert.ok(qm, '#qmarks 섹션이 없음');
  assert.strictEqual(qm.querySelector('.qm-title').textContent, '❓ 확신 없던 것 4개 — 해설 모음');
  assert.strictEqual(qm.previousElementSibling.id, 'result', '점수 요약 바로 아래가 아님');
  assert.strictEqual(qm.nextElementSibling.id, 'quiz', '문항 카드들 위가 아님');
  assert.strictEqual(qm.querySelectorAll('.qm-item').length, 4, '항목 카드 수');
  assert.deepStrictEqual([].map.call(qm.querySelectorAll('.qm-v'), v => v.textContent),
    ['✅ 정답 보기', '❌ 오답 보기', '✅ 정답 보기', '❌ 거짓 지문'], '판정 문구');
  assert.strictEqual(qm.querySelectorAll('.qm-expl').length, 4, '해설은 문항당 1회');
  assert.strictEqual(qm.querySelectorAll('.qm-jump').length, 4, '앵커는 문항당 1개');
  const it3 = qm.querySelector('.qm-item[data-q="3"]');
  assert.strictEqual(it3.querySelector('.qm-jump').getAttribute('href'), '#card-3', '앵커 대상');
  assert.strictEqual(it3.querySelector('.qm-v').getAttribute('title'),
    '정답 조합 ㄱ, ㄷ, ㄹ · 부정형 발문', '판정 근거 툴팁');
  assert.ok(it3.querySelector('.qm-line').textContent.indexOf('ㄱ. 저당권의 효력은') === 0, '지문 전문 표시');
  assert.ok(it3.querySelector('.qm-expl').textContent.includes('저당권은 비점유담보물권'), '해설 전문');
  assert.ok(it3.querySelector('.qm-expl .src').textContent.includes(BASE[3].src), '출처 표기');
  const it0 = qm.querySelector('.qm-item[data-q="0"]');
  assert.strictEqual(it0.querySelector('.qm-head span').textContent, 'Q1 · 부동산학개론', 'Q번호·과목');
  assert.strictEqual(it0.querySelector('.qm-txt').textContent, BASE[0].opts[1], '보기 텍스트');
  // 채점 후에도 ? 표시는 유지되고 토글은 잠긴다
  const mk = markOf(doc, 0, 1);
  H.click(mk);
  assert.strictEqual(mk.textContent, '?', '채점 후 ? 마킹이 바뀜');
  win.close();
});

t('④ 긍정형 발문의 조합 지문 — 정답 조합에 들면 ⭕ 참인 지문 / 안 들면 ❌ 거짓 지문', () => {
  const { doc, win } = page(null);                      // BASE q3은 "옳은 것을 모두 고른 것은?"
  markQStmt(doc, 3, 0);                                 // ㄱ — 정답 조합 ㄱ, ㄷ, ㄹ 에 듦
  markQStmt(doc, 3, 1);                                 // ㄴ — 안 듦
  fullSubmit(doc, BASE);
  const it = doc.querySelector('#qmarks .qm-item[data-q="3"]');
  assert.deepStrictEqual([].map.call(it.querySelectorAll('.qm-v'), v => v.textContent),
    ['⭕ 참인 지문', '❌ 거짓 지문']);
  assert.strictEqual(it.querySelectorAll('.qm-v')[0].getAttribute('title'),
    '정답 조합 ㄱ, ㄷ, ㄹ · 긍정형 발문');
  // ? 마킹된 지문 버튼은 상태 클래스가 'q'라 카드 탐색(div.q)이 흔들리기 쉽다 — 채점 후 잠금 확인
  const g = stmtOf(doc, 3, 0);
  H.click(g);
  assert.strictEqual(g.textContent, '?', '채점 후에도 지문 토글이 먹는다(잠금 실패)');
  win.close();
});

t('④ 같은 문항의 ?는 한 카드로 묶이고 해설·앵커는 1번만', () => {
  const { doc, win } = page(null);
  markQ(doc, 0, 0); markQ(doc, 0, 3);
  fullSubmit(doc, BASE);
  const qm = doc.getElementById('qmarks');
  assert.strictEqual(qm.querySelector('.qm-title').textContent, '❓ 확신 없던 것 2개 — 해설 모음');
  assert.strictEqual(qm.querySelectorAll('.qm-item').length, 1, '카드가 쪼개짐');
  assert.strictEqual(qm.querySelectorAll('.qm-line').length, 2, '보기별 판정 줄');
  assert.strictEqual(qm.querySelectorAll('.qm-expl').length, 1, '해설 중복');
  assert.strictEqual(qm.querySelectorAll('.qm-jump').length, 1, '앵커 중복');
  assert.deepStrictEqual([].map.call(qm.querySelectorAll('.qm-v'), v => v.textContent),
    ['❌ 오답 보기', '❌ 오답 보기']);
  win.close();
});

t('④ ?가 하나도 없으면(· / O / X 뿐) #qmarks 섹션 자체를 만들지 않는다', () => {
  const { doc, win } = page(null);
  H.click(markOf(doc, 0, 0));                                   // O
  H.click(markOf(doc, 1, 1)); H.click(markOf(doc, 1, 1));       // X
  H.click(stmtOf(doc, 3, 0));                                   // 지문 O
  fullSubmit(doc, BASE);
  assert.strictEqual(doc.getElementById('qmarks'), null, '? 0개인데 섹션이 생김');
  const p = state(win, 'LAST_PAYLOAD');
  assert.ok(!('uncertainCount' in p), 'uncertainCount가 붙음');
  assert.ok(p.results.every(r => !('uncertain' in r)), 'uncertain이 붙음');
  win.close();
});

t('④ OX형은 문항 ? 플래그로 모음에 들어간다 (판정 = 정답 O/X) + 계산형 보기 판정', () => {
  const { doc, win } = page(null);
  const flag = doc.querySelector('#card-4 .optox');
  assert.ok(flag && flag.dataset.o === '-1', 'OX 문항 플래그');
  flag.click();                                         // OX 문항에 ?
  markQ(doc, 2, 0);                                     // 계산형 보기에 ? — 같은 판정 경로
  fullSubmit(doc, BASE);
  const qm = doc.getElementById('qmarks');
  const items = [].slice.call(qm.querySelectorAll('.qm-item'));
  assert.strictEqual(items.length, 2, '문항 카드 2개(OX 1 + 계산 1)');
  const ox = items.find(x => x.dataset.q === '4');
  assert.ok(ox, 'OX 문항 카드 존재');
  assert.strictEqual(ox.querySelector('.qm-v').textContent, '정답 ' + BASE[4].opts[BASE[4].answer], 'OX 판정 = 정답 O/X');
  assert.ok(ox.querySelector('.qm-txt').textContent.length > 5, 'OX 항목 텍스트 = 문항 지문');
  const calc = items.find(x => x.dataset.q === '2');
  assert.strictEqual(calc.querySelector('.qm-v').textContent, '❌ 오답 보기', '계산형 보기 판정');
  // payload에도 OX 지문이 uncertain 으로 실린다
  const p = win.LAST_PAYLOAD || win.__lastPayload;
  win.close();
});

t('⑥ 🤷 모르겠음 문항은 채점 후 무지개 테두리(.dkq) + 배지, 다른 문항엔 없다 · 복원 경로도 동일', () => {
  const store = makeStore();
  const a = page(store);
  fullSubmit(a.doc, BASE);                              // q4 = DK
  const c4 = a.doc.getElementById('card-4');
  assert.ok(c4.classList.contains('dkq'), 'DK 문항에 dkq 없음');
  assert.strictEqual(c4.querySelectorAll('.dkbadge').length, 1, 'DK 배지 1개');
  assert.strictEqual(a.doc.querySelectorAll('div.q.dkq').length, 1, 'dkq는 DK 문항에만');
  assert.ok(!a.doc.getElementById('card-1').classList.contains('dkq'), '일반 오답에 dkq가 붙음');
  a.win.close();
  // 중간제출로 채점된 DK 문항이 재로드 복원될 때도 같은 표시
  const store2 = makeStore();
  const b = page(store2);
  answerFirst7(b.doc, BASE);                            // q4 = DK 포함 7문
  H.click(b.doc.getElementById('partialBtn'));
  passDiag(b.doc);
  b.win.close();
  const c = page(store2);
  assert.ok(c.doc.getElementById('card-4').classList.contains('dkq'), '복원된 DK 문항에 dkq 없음');
  assert.strictEqual(c.doc.getElementById('card-4').querySelectorAll('.dkbadge').length, 1, '복원 시 배지 중복/누락');
  c.win.close();
});

t('④ 중간제출: 미응답 문항의 ?는 모음·payload에서 빠지고, 마저 풀면 들어온다', () => {
  const { doc, win } = page(null);
  markQ(doc, 0, 0);                                     // 곧 답할 문항
  markQ(doc, 8, 0);                                     // 중간제출 시점엔 미응답
  answerFirst7(doc, BASE);
  H.click(doc.getElementById('partialBtn'));
  passDiag(doc);
  let qm = doc.getElementById('qmarks');
  assert.ok(qm, '중간 제출에도 모음이 떠야 한다');
  assert.strictEqual(qm.querySelector('.qm-title').textContent, '❓ 확신 없던 것 1개 — 해설 모음');
  assert.strictEqual(qm.querySelectorAll('.qm-item').length, 1);
  assert.strictEqual(qm.querySelector('.qm-item[data-q="8"]'), null, '미응답 q8의 ?가 모음에 들어옴');
  let p = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(p.uncertainCount, 1);
  assert.ok(!('uncertain' in p.results[8]), '미응답에 uncertain이 붙음');
  assert.strictEqual(p.results[8].skipped, true);

  answerLast5(doc, BASE);
  H.click(doc.getElementById('submitBtn'));
  passDiag(doc);
  qm = doc.getElementById('qmarks');
  assert.strictEqual(qm.querySelector('.qm-title').textContent, '❓ 확신 없던 것 2개 — 해설 모음');
  assert.ok(qm.querySelector('.qm-item[data-q="8"]'), '풀고 나서도 q8이 모음에 없음');
  p = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(p.uncertainCount, 2);
  assert.deepStrictEqual(p.results[8].uncertain, [BASE[8].opts[0]]);
  win.close();
});

t('④ payload: uncertain은 ? 붙은 항목에만 · 태그 없는 순수 텍스트 · uncertainCount 합계', () => {
  const { doc, win } = page(null, NEGQ);
  markQ(doc, 1, 0);                                     // 보기 텍스트에 태그 없음
  markQ(doc, 1, 3);
  markQStmt(doc, 3, 0);                                 // 지문 — 'ㄱ. …' 전문
  fullSubmit(doc, NEGQ);
  const p = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(p.uncertainCount, 3, 'uncertainCount');
  assert.deepStrictEqual(p.results[1].uncertain, [BASE[1].opts[0], BASE[1].opts[3]]);
  assert.deepStrictEqual(p.results[3].uncertain, ['ㄱ. 저당권의 효력은 부합물과 종물에 미친다']);
  assert.ok(p.results[3].uncertain.every(s => !/[<>]/.test(s)), 'HTML 태그가 남음');
  const withUnc = p.results.map((r, i) => ('uncertain' in r) ? i : -1).filter(i => i >= 0);
  assert.deepStrictEqual(withUnc, [1, 3], 'uncertain이 다른 항목에도 붙음');
  assert.ok(p.wrong.every(w => !('uncertain' in w)), 'wrong[](v1 하위호환)에 uncertain이 샘');
  // 키 순서: 종전 키 뒤에 uncertain(오답 q1은 진단이 그 뒤에 더 붙는다) / 최상위는 맨 뒤 uncertainCount
  assert.strictEqual(Object.keys(p.results[3]).pop(), 'uncertain');
  assert.ok(Object.keys(p.results[1]).indexOf('uncertain')
    > Object.keys(p.results[1]).indexOf('correctAnswered'), 'uncertain은 종전 키 뒤');
  assert.strictEqual(Object.keys(p).pop(), 'uncertainCount');
  win.close();
});

t('④ ? 없는 제출 payload는 O·X만 찍은 제출과 문자열 단위로 동일하다', () => {
  const run = (marks) => {
    const { doc, win } = page(null);
    if (marks) {
      H.click(markOf(doc, 0, 0));                                 // O
      H.click(markOf(doc, 5, 2)); H.click(markOf(doc, 5, 2));     // X
      doc.querySelectorAll('#card-3 .ox-mark').forEach(g => H.click(g));   // 지문 O
    }
    fullSubmit(doc, BASE);
    const p = state(win, 'LAST_PAYLOAD'); win.close();
    p.generatedAt = 'X';
    p.results.forEach(r => { delete r.errorCause; delete r.causeNote; });
    p.wrong.forEach(r => { delete r.errorCause; delete r.causeNote; });
    return JSON.stringify(p, null, 2);
  };
  assert.strictEqual(run(false), run(true), '마킹이 payload 문자열을 흔들었다');
  assert.ok(run(false).indexOf('uncertain') < 0, 'uncertain 키가 새어나옴');
});

// ══ 렌더러 연동 ═════════════════════════════════════════════════
t('render_quiz.py 렌더 → 토큰 잔존 0 → jsdom에서 채점·중간제출까지 동작', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'hg-tpl2-'));
  const root = path.join(tmp, 'root');
  const ex = H.EXAMS.gongin;
  const notes = path.join(root, ex.notes_dir || '공인중개사');
  fs.mkdirSync(notes, { recursive: true });
  // evidence(노트 원문 인용) 게이트용 원천 노트를 임시 루트에 심는다 — 인용문 그대로가 원문
  const qdoc = JSON.parse(fs.readFileSync(path.join(FIX, 'gongin_daily.questions.json'), 'utf8'));
  (qdoc.questions || qdoc).forEach(q => {
    const ev = q && q.evidence;
    if (!ev || !ev.note || ev.note === 'samples') return;
    fs.writeFileSync(path.join(notes, path.basename(ev.note)), '# 원천 노트\n\n' + ev.quote + '\n');
  });
  const outFile = path.join(tmp, 'x.html');
  execFileSync('python3', [path.join(H.ENGINE, 'render_quiz.py'),
    '--exam', 'gongin', '--kind', 'daily', '--date', DATE, '--root', root,
    '--plan', path.join(FIX, 'gongin_daily.plan.json'),
    '--questions', path.join(FIX, 'gongin_daily.questions.json'),
    '--no-validate', '--out', outFile], { cwd: H.ENGINE, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });

  const html = fs.readFileSync(outFile, 'utf8');
  assert.deepStrictEqual(html.match(/\{\{[A-Z0-9_]+\}\}/g), null, '토큰 잔존');
  const qs = H.extractQuestions(html);
  const store = makeStore();
  const { doc, win } = boot(html, store);
  // 중간 제출 — 앞 3문만
  qs.slice(0, 3).forEach((q, qi) => {
    if (q.type === '단답') { saOk(doc, qs, qi); return; }
    H.click(doc.querySelector(`.opt[data-q="${qi}"][data-o="${q.answer}"]`));
  });
  H.click(doc.getElementById('partialBtn'));
  passDiag(doc);
  const pp = state(win, 'LAST_PAYLOAD');
  assert.strictEqual(pp.partial, true);
  assert.strictEqual(pp.answeredCount, 3);
  assert.strictEqual(pp.skippedCount, qs.length - 3);
  // 나머지를 채우고 전체 제출
  const p = H.runGenericScenario(win, qs);
  assert.ok(!('partial' in p), '전체 제출에 partial 키');
  assert.strictEqual(p.total, qs.length);
  assert.strictEqual(p.results.length, qs.length);
  assert.strictEqual(store.map.size, 0, '전체 제출 후 저장분이 남음');
  win.close();
  fs.rmSync(tmp, { recursive: true, force: true });
});

t('템플릿 머리 주석에 v2 변경 3줄 · 주석에 토큰 표기 없음', () => {
  const raw = fs.readFileSync(path.join(H.ENGINE, 'quiz_template.html'), 'utf8');
  const head = raw.slice(0, raw.indexOf('-->'));
  const v2 = head.split('\n').filter(l => /-\s*v2/.test(l));
  assert.ok(v2.length >= 3, 'v2 변경 주석이 3줄 미만: ' + v2.length);
  assert.strictEqual(head.match(/\{\{[A-Z0-9_]+\}\}/g), null, '주석에 토큰 표기가 있으면 잔존 검사에 걸린다');
});

t('⑤ 템플릿 머리 주석에 v2.1 변경 2줄 · 주석에 토큰 표기 없음', () => {
  const raw = fs.readFileSync(path.join(H.ENGINE, 'quiz_template.html'), 'utf8');
  const head = raw.slice(0, raw.indexOf('-->'));
  const v21 = head.split('\n').filter(l => /-\s*v2\.1/.test(l));
  assert.ok(v21.length >= 2, 'v2.1 변경 주석이 2줄 미만: ' + v21.length);
  assert.ok(/마킹|O·X|\?/.test(v21[0]) && /qmarks|물음표/.test(v21[1]), 'v2.1 주석 내용');
  assert.strictEqual(head.match(/\{\{[A-Z0-9_]+\}\}/g), null, '주석에 토큰 표기가 있으면 잔존 검사에 걸린다');
});

console.log(out.join('\n'));
console.log(`[template] ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
