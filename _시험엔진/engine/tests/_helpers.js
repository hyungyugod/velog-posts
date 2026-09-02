// 회귀 테스트 공용 헬퍼 — 템플릿 주입 · jsdom 부팅 · 시나리오 구동 · 차이 비교
'use strict';

const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const ENGINE = path.resolve(__dirname, '..');
const ROOT = path.resolve(ENGINE, '..', '..');
const EXAMS = JSON.parse(fs.readFileSync(path.join(ENGINE, 'exams.json'), 'utf8')).exams;

// 레거시 6벌 (수정 금지 · 읽기 전용)
const LEGACY_DIR = path.join(__dirname, 'legacy_templates');   // 구조 v1 템플릿 6벌(2026-09-02 동결 사본 — payload 회귀 기준)
const LEGACY = {
  gongin_daily: path.join(LEGACY_DIR, 'gongin_daily.html'),
  gongin_retry: path.join(LEGACY_DIR, 'gongin_retry.html'),
  bupsa1_daily: path.join(LEGACY_DIR, 'bupsa1_daily.html'),
  bupsa1_retry: path.join(LEGACY_DIR, 'bupsa1_retry.html'),
  bupsa2_daily: path.join(LEGACY_DIR, 'bupsa2_daily.html'),
  bupsa2_retry: path.join(LEGACY_DIR, 'bupsa2_retry.html'),
};

const RESULT_MSGS = {
  gongin: ['만점','합격권','절반','흔들림','회독'],
  bupsa1: ['만점','합격권','절반','흔들림','회독'],
  bupsa2: ['만점','합격권','절반','흔들림','회독'],
};

function hexRgb(h) {
  h = h.replace('#', '');
  return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
}
function hue(h) {
  const [r, g, b] = hexRgb(h).map(c => c / 255);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  if (!d) return 0;
  let x;
  if (mx === r) x = ((g - b) / d + 6) % 6;
  else if (mx === g) x = (b - r) / d + 2;
  else x = (r - g) / d + 4;
  return x * 60;
}
function warmCool(a, b) {
  const w = h => { const d = Math.abs(h - 45) % 360; return Math.min(d, 360 - d); };
  return w(hue(a)) <= w(hue(b)) ? [a, b] : [b, a];
}
const DERIVED = { '#ffd24a': ['#1a1a1a', '#ffb347', '#26261a'], '#7c9cff': ['#10131c', '#5f7fe8', '#1a2138'] };

/** 새 단일 템플릿을 exam/kind로 토큰 치환 (render_quiz.py의 토큰 규칙과 동일) */
function renderUnified(exam, kind, date) {
  const ex = EXAMS[exam], ui = ex.ui;
  const [warm, cool] = warmCool(ui.accent, ui.accent2);
  const [onAccent, grad2, reveal] = DERIVED[ui.accent.toLowerCase()] || ['#1a1a1a', ui.accent, '#26261a'];
  const t = {
    QUIZ_DATE: date,
    TITLE: ui[kind === 'daily' ? 'title_daily' : 'title_retry'],
    EYEBROW: ui[kind === 'daily' ? 'eyebrow_daily' : 'eyebrow_retry'],
    H1: ui[kind === 'daily' ? 'h1_daily' : 'h1_retry'],
    DESC_HTML: ui[kind === 'daily' ? 'desc_daily' : 'desc_retry'],
    META_LINE: 'TEST META', TAGS_HTML: '', ALERT_HTML: '',
    SUBJECT: ex.payload_subject, RESULT_PREFIX: ex.result_prefix,
    QUIZ_ID_SUFFIX: kind === 'daily' ? '' : '-RQ',
    EXAM_DEFAULT: ui.exam_default || '', INBOX_NOTE: ui.inbox_note || '',
    ACCENT: ui.accent, ACCENT2: ui.accent2, WARM: warm, COOL: cool,
    ON_ACCENT: onAccent, ACCENT_GRAD2: grad2, REVEAL_HOVER: reveal,
    T_MCQ: ui.time_per_mcq_sec, T_SA: ui.time_per_sa_sec,
    RESULT_MSGS: JSON.stringify(RESULT_MSGS[exam]),
  };
  let html = fs.readFileSync(path.join(ENGINE, 'quiz_template.html'), 'utf8');
  for (const [k, v] of Object.entries(t)) html = html.split('{{' + k + '}}').join(String(v));
  return html;
}

function readLegacy(key, date) {
  let html = fs.readFileSync(LEGACY[key], 'utf8');
  return html.split('{{QUIZ_DATE}}').join(date)
    .split('{{META_LINE}}').join('TEST META')
    .split('{{TAGS_HTML}}').join('')
    .split('{{ALERT_HTML}}').join('');
}

function injectQuestions(html, questions) {
  const body = JSON.stringify(questions, null, 1).replace(/^\[\n?/, '').replace(/\n?\]$/, '');
  return html.replace(
    /(\/\*__QUESTIONS_START__\*\/)([\s\S]*?)(\/\*__QUESTIONS_END__\*\/)/,
    (m, a, _b, c) => a + '\n' + body + '\n' + c);
}

function boot(html) {
  const vc = new VirtualConsole();       // jsdom의 미구현 navigation 경고 억제
  const dom = new JSDOM(html, { runScripts: 'dangerously', virtualConsole: vc });
  const win = dom.window;
  win.URL.createObjectURL = () => 'blob:test';
  win.URL.revokeObjectURL = () => {};
  win.Element.prototype.scrollIntoView = function () {};
  win.HTMLAnchorElement.prototype.click = function () {};
  return { dom, win, doc: win.document };
}

function fire(el, type) {
  el.dispatchEvent(new el.ownerDocument.defaultView.Event(type, { bubbles: true }));
}
function click(el) {
  if (!el) throw new Error('click: element not found');
  el.dispatchEvent(new el.ownerDocument.defaultView.MouseEvent('click', { bubbles: true, cancelable: true }));
}
function setVal(el, v) {
  el.value = v;
  fire(el, 'input');
}

// ── 시나리오: payload_questions.js 배열 12문항 기준 ────────────────
//  0 정답 · 1 오답(+진단) · 2 계산 정답 · 3 조합 정답(+O·X 마킹) · 4 🤷 모르겠음
//  5 오답(+진단) · 6 단답 ❌ → 놓친포인트+기타 → 교정 통과 · 7 정답 · 8 오답(+진단)
//  9 정답 · 10 정답(5지) · 11 단답 ⭕
function runScenario(win, questions) {
  const doc = win.document;
  const optOf = (qi, oi) => doc.querySelector(`.opt[data-q="${qi}"][data-o="${oi}"]`);
  const pickCorrect = qi => click(optOf(qi, questions[qi].answer));
  const pickWrong = qi => {
    const n = questions[qi].opts.length;
    click(optOf(qi, (questions[qi].answer + 1) % n));
  };

  pickCorrect(0);
  pickWrong(1);
  pickCorrect(2);
  pickCorrect(3);
  // ㄱㄴㄷ O·X 마킹 (시각 메모 — payload 무관, 회귀에서 부작용 없음을 확인)
  const marks = doc.querySelectorAll('.q .ox-mark');
  if (marks.length) { click(marks[0]); click(marks[0]); click(marks[1]); }
  click(doc.querySelector(`.dk-btn[data-q="4"]`));           // 🤷 모르겠음
  pickWrong(5);

  // 6 · 단답 ❌ → 놓친 포인트 2개 + 기타 → 교정 타이핑 통과
  const c6 = doc.getElementById('card-6');
  setVal(c6.querySelector('.sa-input'), '건설자금이자와 중개보수 정도만 생각남');
  click(c6.querySelector('.sa-reveal'));
  click(c6.querySelectorAll('.sa-grade button')[1]);          // ❌ 틀렸다
  const chips6 = c6.querySelectorAll('.sa-fix .sa-misschips .sa-chip');
  click(chips6[1]);                                          // 채점 포인트 2번째
  click(chips6[chips6.length - 2]);                           // '결론·방향 자체'
  click(chips6[chips6.length - 1]);                           // ＋ 기타
  setVal(c6.querySelector('.sa-etcinput'), '연체료를 통째로 빠뜨림');
  setVal(c6.querySelector('.sa-fixinput'), questions[6].answer);

  pickCorrect(7);
  pickWrong(8);
  pickCorrect(9);
  pickCorrect(10);

  // 11 · 단답 ⭕
  const c11 = doc.getElementById('card-11');
  setVal(c11.querySelector('.sa-input'), '살인죄는 성립하지 않고 현주건조물방화치사죄만 성립한다');
  click(c11.querySelector('.sa-reveal'));
  click(c11.querySelectorAll('.sa-grade button')[0]);         // ⭕ 맞았다

  const submit = doc.getElementById('submitBtn');
  if (submit.disabled) throw new Error('제출 게이트가 열리지 않음 (진행률 미완료)');
  click(submit);

  // 진단 게이트: 틀린 객관식(1·5·8)마다 원인 1개 + 메모 → 진단 저장
  const memos = { 1: '감정평가 시산가액 조정 절차를 몰랐음', 5: '', 8: '용도지구와 혼동' };
  [1, 5, 8].forEach((qi, k) => {
    const d = doc.getElementById('diag-' + qi);
    if (!d) throw new Error('진단 칩이 생성되지 않음: q' + qi);
    click(d.querySelectorAll('.sa-chip')[k % 4]);
    if (memos[qi]) setVal(d.querySelector('.dmemo'), memos[qi]);
  });
  const save = doc.getElementById('diagSave');
  if (!save) throw new Error('진단 저장 버튼 없음');
  if (save.disabled) throw new Error('진단 저장 버튼이 잠겨 있음');
  click(save);

  return JSON.parse(win.eval('JSON.stringify(LAST_PAYLOAD)'));
}

/** 문항 수와 무관한 결정론적 시나리오 — 실제 데이터 스모크용.
 *  객관식: i%5 0/2/4 정답 · 1 오답(+진단) · 3 🤷 무답
 *  단답  : i%3 0 ⭕ · 그 외 ❌ → 놓친 포인트 1개 → 교정 타이핑 통과 */
function runGenericScenario(win, questions) {
  const doc = win.document;
  questions.forEach((q, qi) => {
    if (q.type === '단답') {
      const c = doc.getElementById('card-' + qi);
      setVal(c.querySelector('.sa-input'), '기억나는 만큼 씀 ' + qi);
      click(c.querySelector('.sa-reveal'));
      if (qi % 3 === 0) { click(c.querySelectorAll('.sa-grade button')[0]); return; }
      click(c.querySelectorAll('.sa-grade button')[1]);
      const chips = c.querySelectorAll('.sa-fix .sa-misschips .sa-chip');
      click(chips[0]);
      setVal(c.querySelector('.sa-fixinput'), q.answer);
      return;
    }
    const n = q.opts.length;
    const m = qi % 5;
    if (m === 3) { click(doc.querySelector(`.dk-btn[data-q="${qi}"]`)); return; }
    const oi = (m === 1) ? (q.answer + 1) % n : q.answer;
    click(doc.querySelector(`.opt[data-q="${qi}"][data-o="${oi}"]`));
  });

  const submit = doc.getElementById('submitBtn');
  if (submit.disabled) throw new Error('제출 게이트가 열리지 않음');
  click(submit);

  doc.querySelectorAll('.mcq-diag').forEach((d, k) => {
    click(d.querySelectorAll('.sa-chip')[k % 4]);
  });
  const save = doc.getElementById('diagSave');
  if (save) { if (save.disabled) throw new Error('진단 저장 잠김'); click(save); }
  return JSON.parse(win.eval('JSON.stringify(LAST_PAYLOAD)'));
}

/** 렌더된 HTML에서 QUESTIONS 배열을 뽑는다 */
function extractQuestions(html) {
  const m = html.match(/\/\*__QUESTIONS_START__\*\/([\s\S]*?)\/\*__QUESTIONS_END__\*\//);
  if (!m) throw new Error('QUESTIONS 마커 없음');
  // eslint-disable-next-line no-new-func
  return new Function('return [' + m[1].trim().replace(/,\s*$/, '') + '];')();
}

/** 두 payload의 차이 경로 목록 (generatedAt 제외) */
function diffPaths(a, b, prefix = '', out = []) {
  const skip = new Set(['generatedAt']);
  if (a === b) return out;
  const isObj = v => v && typeof v === 'object';
  if (!isObj(a) || !isObj(b)) {
    if (JSON.stringify(a) !== JSON.stringify(b)) out.push(`${prefix}: ${JSON.stringify(a)} ≠ ${JSON.stringify(b)}`);
    return out;
  }
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of keys) {
    if (skip.has(k)) continue;
    const p = prefix ? `${prefix}.${k}` : k;
    if (!(k in a)) { out.push(`${p}: (없음) ≠ ${JSON.stringify(b[k])}`); continue; }
    if (!(k in b)) { out.push(`${p}: ${JSON.stringify(a[k])} ≠ (없음)`); continue; }
    diffPaths(a[k], b[k], p, out);
  }
  return out;
}

/** 차이 경로에서 필드명만 뽑아 집합으로 (results.8.monthlyOf → monthlyOf) */
function diffFields(paths) {
  return [...new Set(paths.map(p => p.split(':')[0].split('.').pop()))].sort();
}

module.exports = {
  ENGINE, ROOT, EXAMS, LEGACY,
  renderUnified, readLegacy, injectQuestions, boot, click, setVal, fire,
  runScenario, runGenericScenario, extractQuestions, diffPaths, diffFields,
};
