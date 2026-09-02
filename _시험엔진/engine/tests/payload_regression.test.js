// payload 회귀 — 레거시 6벌 각각 vs 새 단일 템플릿(같은 exam/kind)에 동일 QUESTIONS 주입,
// 동일 시나리오(정답·오답·🤷·진단+메모·단답 교정 게이트·계산·조합)를 jsdom에서 돌려 payload 비교.
'use strict';

const assert = require('assert');
const H = require('./_helpers');
const { BASE, withExam } = require('./fixtures/payload_questions');

const DATE = '2026-09-10';
let pass = 0, fail = 0;
const results = [];

function t(name, fn) {
  try { fn(); pass++; results.push('  ✔ ' + name); }
  catch (e) { fail++; results.push('  ✘ ' + name + '\n      ' + String(e.message).split('\n').join('\n      ')); }
}

function payloadOf(html, questions) {
  const { win } = H.boot(H.injectQuestions(html, questions));
  const p = H.runScenario(win, questions);
  win.close();
  return p;
}

// 레거시 6벌 ↔ 새 템플릿 짝 / 사용할 문항 세트 / 기대 차이 필드
const PAIRS = [
  { legacy: 'gongin_daily', exam: 'gongin', kind: 'daily', qs: () => BASE,        expect: ['monthlyOf'] },
  { legacy: 'gongin_retry', exam: 'gongin', kind: 'retry', qs: () => BASE,        expect: ['monthlyOf'] },
  { legacy: 'bupsa1_daily', exam: 'bupsa1', kind: 'daily', qs: () => withExam('1차'), expect: ['calc'] },
  { legacy: 'bupsa1_retry', exam: 'bupsa1', kind: 'retry', qs: () => withExam('1차'), expect: ['calc'] },
  { legacy: 'bupsa2_daily', exam: 'bupsa2', kind: 'daily', qs: () => withExam('2차'), expect: ['calc'] },
  { legacy: 'bupsa2_retry', exam: 'bupsa2', kind: 'retry', qs: () => withExam('2차'), expect: ['calc'] },
];

console.log('\n[payload_regression]');

for (const p of PAIRS) {
  t(`${p.legacy} ↔ 새 템플릿(${p.exam}/${p.kind}) payload 동일 (기대 차이: ${p.expect.join(', ') || '없음'})`, () => {
    const questions = p.qs();
    const legacy = payloadOf(H.readLegacy(p.legacy, DATE), questions);
    const unified = payloadOf(H.renderUnified(p.exam, p.kind, DATE), questions);
    const paths = H.diffPaths(legacy, unified);
    const fields = H.diffFields(paths);
    assert.deepStrictEqual(fields, p.expect.slice().sort(),
      '차이 필드가 기대와 다름\n실제 차이:\n' + paths.map(x => '  - ' + x).join('\n'));
  });
}

// 시나리오가 실제로 전 기능을 밟았는지 (payload 자체의 내용 검증)
t('시나리오 payload 내용 검증 (점수·무답·진단·단답 교정)', () => {
  const p = payloadOf(H.renderUnified('gongin', 'daily', DATE), BASE);
  assert.strictEqual(p.total, 12, 'total');
  assert.strictEqual(p.score, 7, 'score(정답 7 = q0,2,3,7,9,10,11)');
  assert.strictEqual(p.wrongCount, 5, 'wrongCount(q1,4,5,6,8)');
  assert.strictEqual(p.schemaVersion, 2);
  assert.strictEqual(p.subject, '공인중개사');
  assert.strictEqual(p.quizId, DATE);
  assert.strictEqual(p.results[4].myAnswer, '모르겠음', '🤷 무답');
  assert.strictEqual(p.results[4].errorCause, '개념부재', '🤷 원인 자동 진단');
  assert.strictEqual(p.results[1].errorCause, '개념부재');
  assert.ok(p.results[1].causeNote, '진단 메모');
  assert.ok(!('causeNote' in p.results[5]), '메모 미입력이면 causeNote 없음');
  assert.strictEqual(p.results[6].selfGraded, true, '단답 selfGraded');
  assert.ok(p.results[6].missedKeys.length >= 3, '놓친 포인트 칩 + 기타');
  assert.ok(p.results[6].missedKeys.some(k => k.startsWith('기타: ')), '기타 입력');
  assert.strictEqual(p.results[6].fixTyped, BASE[6].answer, '교정 타이핑 원문');
  assert.deepStrictEqual(p.results[2].calc, { expr: '1500/5000*100', expected: 30 }, '계산형 calc');
  assert.strictEqual(p.results[9].retryOf, '중개사법 과태료 개별금액', '🔁 retryOf');
  assert.strictEqual(p.results[8].monthlyOf, '2026-08-10', '🔄 monthlyOf(원본 문제지 날짜)');
  assert.strictEqual(p.results[0].retryOf, null);
  assert.ok(!('exam' in p.results[0]), '공인중개사는 exam 키 없음');
  // wrong[]는 v1 하위호환 — id로 역참조 가능해야 한다
  assert.deepStrictEqual(p.wrong.map(w => w.id),
    [1, 4, 5, 6, 8].map(i => `${DATE}-q${i + 1}`), 'wrong[] v1 하위호환');
});

t('retry 템플릿의 quizId·결과 파일명 접미(-RQ)', () => {
  const p = payloadOf(H.renderUnified('gongin', 'retry', DATE), BASE);
  assert.strictEqual(p.quizId, DATE + '-RQ');
  const html = H.renderUnified('gongin', 'retry', DATE);
  assert.ok(html.includes('${RESULT_PREFIX}${QUIZ_DATE}${QUIZ_ID_SUFFIX}.json'), '다운로드 파일명 템플릿');
  assert.ok(html.includes('const RESULT_PREFIX = "공인중개사_오답_"'));
  assert.ok(html.includes('const QUIZ_ID_SUFFIX = "-RQ"'));
});

t('법무사 payload에는 exam 키가 실린다 / 공인중개사에는 없다', () => {
  const b1 = payloadOf(H.renderUnified('bupsa1', 'daily', DATE), BASE);   // exam 미기재 문항
  assert.strictEqual(b1.results[0].exam, '1차', 'EXAM_DEFAULT 폴백');
  assert.strictEqual(b1.results[6].exam, '1차', '단답도 EXAM_DEFAULT(레거시는 "2차" — 의도적 수정)');
  const b2 = payloadOf(H.renderUnified('bupsa2', 'daily', DATE), BASE);
  assert.strictEqual(b2.results[0].exam, '2차');
  const g = payloadOf(H.renderUnified('gongin', 'daily', DATE), BASE);
  assert.ok(g.results.every(r => !('exam' in r)));
});

t('기대 차이 문서화: 레거시 bupsa1은 단답 exam을 "2차"로 강제한다', () => {
  const questions = BASE;                                  // exam 필드 없음
  const legacy = payloadOf(H.readLegacy('bupsa1_daily', DATE), questions);
  const unified = payloadOf(H.renderUnified('bupsa1', 'daily', DATE), questions);
  assert.strictEqual(legacy.results[6].exam, '2차', '레거시: isSA면 무조건 2차');
  assert.strictEqual(unified.results[6].exam, '1차', '신규: item.exam || EXAM_DEFAULT');
  assert.deepStrictEqual(H.diffFields(H.diffPaths(legacy, unified)), ['calc', 'exam']);
});

console.log(results.join('\n'));
console.log(`[payload_regression] ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
