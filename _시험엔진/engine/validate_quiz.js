#!/usr/bin/env node
'use strict';
/**
 * validate_quiz.js — HG 무한복습체계 퀴즈 검증기 (통합 정본, 2026-09-02)
 *
 * 마크다운 프로파일에 흩어져 있던 6벌 인라인 검증 스크립트를 한 파일로 통합했다.
 *   1) 공인중개사 데일리      (구 프로파일_공인중개사_v1 §데일리퀴즈 — 현행 spec/프로파일_공인중개사.md)
 *   2) 법무사1차 데일리        (구 프로파일_법무사1차_v1 §데일리퀴즈 — 현행 spec/프로파일_법무사1차.md)
 *   3) 법무사1차 오답(완결본)  (구 프로파일_법무사1차_v1 §오답퀴즈)
 *   4) 법무사2차 데일리        (구 프로파일_법무사2차_v1 §데일리퀴즈 — 현행 spec/프로파일_법무사2차.md)
 *   5) 법무사2차 오답 추가검증 (구 프로파일_법무사2차_v1 §오답퀴즈)
 *   6) 오답 공통 베이스        (구 베이스_오답파이프라인_v1 §3-4 — 현행 spec/오답퀴즈.md)
 * 검사 항목은 6벌의 합집합이며 exam×kind 로 분기해 전부 보존한다.
 * 모든 수치 상수는 engine/exams.json 에서 읽는다.
 *
 * 사용법:
 *   node validate_quiz.js --exam gongin|bupsa1|bupsa2 --kind daily|retry \
 *        --file <html 경로> [--date YYYY-MM-DD] [--root <velog-posts 루트>] [--json]
 *
 *   --date  기본 = 파일명의 날짜(YYYY-MM-DD.html), 없으면 오늘
 *   --root  기본 = 이 스크립트 위치의 두 단계 위 (velog-posts)
 *   --json  {pass, checks:[{id,ok,msg}], summary:{...}} 를 stdout 에 JSON 으로
 *   exit 0 = 전체 통과 / 1 = 1건 이상 FAIL
 */

const fs = require('fs');
const path = require('path');

/* ────────────────────────────────── CLI ────────────────────────────────── */

function parseArgs(argv) {
  const a = { json: false };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--json') a.json = true;
    else if (t === '--exam') a.exam = argv[++i];
    else if (t === '--kind') a.kind = argv[++i];
    else if (t === '--file') a.file = argv[++i];
    else if (t === '--date') a.date = argv[++i];
    else if (t === '--root') a.root = argv[++i];
    else if (t === '-h' || t === '--help') a.help = true;
    else if (!a.file && !t.startsWith('-')) a.file = t;
  }
  return a;
}

const USAGE =
  'usage: node validate_quiz.js --exam gongin|bupsa1|bupsa2 --kind daily|retry ' +
  '--file <html> [--date YYYY-MM-DD] [--root <velog-posts>] [--json]';

const ARGS = parseArgs(process.argv.slice(2));
if (ARGS.help) { console.log(USAGE); process.exit(0); }

function die(msg) {
  if (ARGS.json) {
    process.stdout.write(JSON.stringify({ pass: false, checks: [{ id: 'cli', ok: false, msg: msg }], summary: { error: msg } }, null, 2) + '\n');
  } else {
    console.error('FAIL — ' + msg);
  }
  process.exit(1);
}

if (!ARGS.exam || !ARGS.kind || !ARGS.file) die('인자 부족. ' + USAGE);
if (!['gongin', 'bupsa1', 'bupsa2'].includes(ARGS.exam)) die('--exam 은 gongin|bupsa1|bupsa2');
if (!['daily', 'retry'].includes(ARGS.kind)) die('--kind 는 daily|retry');

/* ─────────────────────────────── exams.json ────────────────────────────── */

const EXAMS_PATH = path.join(__dirname, 'exams.json');
let CFG;
try { CFG = JSON.parse(fs.readFileSync(EXAMS_PATH, 'utf8')); }
catch (e) { die('exams.json 읽기 실패: ' + EXAMS_PATH + ' — ' + e.message); }

const EX = CFG.exams[ARGS.exam];
if (!EX) die('exams.json 에 ' + ARGS.exam + ' 없음');
const V = CFG._validate || {};
const KIND = ARGS.kind;
const KCFG = EX[KIND] || {};
const DCFG = EX.daily || {};
const PATHS = CFG._paths || {};

/** kind 블록 → daily 블록 → 시험 블록 순으로 값 해석 (retry 가 daily 계약을 상속) */
function cf(key, dflt) {
  if (KCFG[key] !== undefined) return KCFG[key];
  if (DCFG[key] !== undefined) return DCFG[key];
  if (EX[key] !== undefined) return EX[key];
  return dflt;
}
function rx(pat, flags) { return new RegExp(pat, flags); }

/* ──────────────────────────── 경로 · 날짜 해석 ─────────────────────────── */

const ROOT = path.resolve(ARGS.root || path.resolve(__dirname, '..', '..'));
const FILE = path.resolve(ARGS.file);
const QDIR = path.dirname(FILE);
const BASENAME = path.basename(FILE);

function todayLocal() {
  const d = new Date();
  const p = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}
const mDate = BASENAME.match(/^(\d{4}-\d{2}-\d{2})\.html$/);
const TODAY = ARGS.date || (mDate ? mDate[1] : todayLocal());

const NOTES_DIR = path.join(ROOT, EX.notes_dir);
const EXAM_DIR = path.join(ROOT, EX.dir);
const LEDGER = path.join(
  EXAM_DIR,
  PATHS.ledger_dir || 'claude_ox_오답',
  PATHS.ledger_subdir || '_ledger',
  '오답_원장.json'
);

const day = s => Math.round((new Date(TODAY) - new Date(s)) / 864e5);
const onOrAfter = iso => !!iso && TODAY >= iso;

/* ─────────────────────────── 문항 추출 · 결과 수집 ─────────────────────── */

let HTML;
try { HTML = fs.readFileSync(FILE, 'utf8'); }
catch (e) { die('문제지 읽기 실패: ' + FILE + ' — ' + e.message); }

const QRE = rx(V.questions_regex || 'const QUESTIONS = (\\[[\\s\\S]*?\\n\\]);');
const qm = HTML.match(QRE);
if (!qm) die('QUESTIONS 배열을 찾지 못함: ' + FILE);
let Q;
try { Q = JSON.parse(qm[1]); }               // 순수 JSON 이면 그대로
catch (e) { Q = eval(qm[1]); }               // 아니면 기존과 동일하게 eval 폴백  // eslint-disable-line no-eval
if (!Array.isArray(Q)) die('QUESTIONS 가 배열이 아님');

const checks = [];
const info = [];
const OUT = [];
function ok(id, cond, msg) {
  const v = !!cond;
  checks.push({ id: id, ok: v, msg: msg });
  OUT.push((v ? 'PASS' : 'FAIL') + ' — ' + msg);
  return v;
}
function note(line) { info.push(line); OUT.push(line); }

/* ───────────────────────────── 공통 헬퍼 (1벌) ─────────────────────────── */

const EM = V.emoji || { longrev: '⏪', monthly: '🔄', retry: '🔁' };
const SRC = V.src_marks || {};
const RE_LONGREV_SRC = rx(SRC.longrev || '\\(장기복습·\\d+일전\\)');
const RE_MONTHLY_SRC = rx(SRC.monthly || '\\(한달전 재출제·원본 \\d{4}-\\d{2}-\\d{2}\\)');
const RE_RETRY_SRC = rx(SRC.retry || '\\(재도전\\)');
const RE_MONTHLY_OF = rx(V.monthly_of_regex || '^\\d{4}-\\d{2}-\\d{2}$');
const TOKEN = V.token_leftover || '{{';

// 해설↔보기 2-gram 정합 휴리스틱 (6벌 공통 · 1벌로 통합)
const nrmE = s => String(s || '').replace(/<[^>]*>/g, ' ').replace(/\[[^\]]*\]/g, ' ')
  .replace(/[\s.,·()「」\x27!?~-]/g, '').toLowerCase();
const grmE = s => { const m = new Map(); for (let i = 0; i < s.length - 1; i++) { const k = s.slice(i, i + 2); m.set(k, (m.get(k) || 0) + 1); } return m; };
const dicE = (a, b) => {
  a = nrmE(a); b = nrmE(b);
  if (a.length < 2 || b.length < 2) return 0;
  const ga = grmE(a), gb = grmE(b);
  let it = 0, na = 0, nb = 0;
  ga.forEach(v => na += v); gb.forEach(v => nb += v);
  ga.forEach((v, k) => { it += Math.min(v, gb.get(k) || 0); });
  return 2 * it / (na + nb);
};
const EMC = V.expl_match || {};
const EM_MIN_OPTS = EMC.min_opts !== undefined ? EMC.min_opts : 3;
const EM_DICE = EMC.dice_min !== undefined ? EMC.dice_min : 0.28;
const EM_RATIO = EMC.ratio_over_answer !== undefined ? EMC.ratio_over_answer : 1.6;
const EM_SPLIT = rx(EMC.first_sentence_split || '(?<=다)\\.\\s');

function explMatchChecks(list) {
  list.filter(q => q.opts && q.opts.length >= EM_MIN_OPTS).forEach((q, i) => {
    const first = String(q.expl || '').split(EM_SPLIT)[0];
    const sc = q.opts.map(o => dicE(first, o));
    const b = sc.indexOf(Math.max(...sc));
    ok('expl_match#' + (i + 1),
      !(b !== q.answer && sc[b] >= EM_DICE && sc[b] >= sc[q.answer] * EM_RATIO),
      '정답-해설 정합 의심 — 해설 첫 문장이 ' + String.fromCharCode(65 + b) +
      '를 서술하는데 answer=' + String.fromCharCode(65 + q.answer) +
      ' (' + (q.q || '').replace(/<[^>]*>/g, '').slice(0, 30) +
      '). answer 오배정이면 answer 교정, 오탐이면 [정답 근거] 첫 문장을 정답 보기 기준으로 재서술');
  });
}

// 같은 정답 3연속 없음
function maxRunOf(seq) { let run = 1, mx = 1; for (let i = 1; i < seq.length; i++) { run = (seq[i] === seq[i - 1]) ? run + 1 : 1; mx = Math.max(mx, run); } return mx; }

// 같은 과목 연속 배치
function contiguousCat(list) {
  const seq = list.map(q => q.cat), seen = {};
  let contig = true;
  seq.forEach((c, i) => { if (!(c in seen)) seen[c] = 1; else if (seq[i - 1] !== c) contig = false; });
  return contig;
}

// 조합형 ㄱ·ㄴ 정답 포함 비율 (위치-참거짓 무상관)
function comboRatioChecks(CB, minCount, comboCfg) {
  if (CB.length < minCount) return;
  const pr = (comboCfg || {}).position_truth_ratio || [0.25, 0.75];
  const labels = ((comboCfg || {}).label_set || ['ㄱ', 'ㄴ']).slice(0, 2);
  labels.forEach(L => {
    const r = CB.filter(q => q.opts[q.answer].includes(L)).length / CB.length;
    ok('combo_ratio_' + L, r >= pr[0] && r <= pr[1],
      '조합형 ' + L + ' 정답 포함 ' + Math.round(pr[0] * 100) + '~' + Math.round(pr[1] * 100) +
      '% — 위치·참거짓 무상관 (현재 ' + Math.round(r * 100) + '%)');
  });
}

// 단답 계약 (answer 문자열 · keywords 2~4 · opts 없음)
function saContract(q) {
  const kc = cf('keywords_count', [2, 4]);
  return typeof q.answer === 'string' && Array.isArray(q.keywords) &&
    q.keywords.length >= kc[0] && q.keywords.length <= kc[1] && !q.opts;
}

// 과거 문제문 도입부 중복
const DUP_LEN = V.dup_prefix_len || 30;
const PAST_Q_RE = rx(V.past_q_regex || 'q: *"[^"]*"', 'g');
function normQ(s) { return String(s).replace(/<[^>]+>/g, '').replace(new RegExp('[\\s' + EM.retry + EM.monthly + EM.longrev + ']', 'g'), ''); }
function pastQuestionTexts(html) {
  // 새 엔진 산출(순수 JSON, "q": "…")과 레거시(q: "…") 모두에서 문제문을 뽑는다.
  // ① QUESTIONS 배열 파싱(JSON → eval 폴백) ② 실패 시 레거시 정규식.
  const m = html.match(QRE);
  if (m) {
    let arr = null;
    try { arr = JSON.parse(m[1]); } catch (e) { try { arr = eval(m[1]); } catch (e2) { arr = null; } }  // eslint-disable-line no-eval
    if (Array.isArray(arr)) return arr.map(q => (q && typeof q === 'object') ? String(q.q || '') : '').filter(Boolean);
  }
  return (html.match(PAST_Q_RE) || []).map(s => s.replace(/^"?q"? *: *"/, '').replace(/"$/, ''));
}
/* ── 최근 N일 데일리 문제지와의 conceptKey 중복 (2026-09-02 신설) ──
 * 신규 문항(⏪ 장기복습 · 🔄 한달전 · 🔁 재도전이 아닌 것)의 conceptKey 가 같은 폴더의
 * 최근 N일 데일리 문제지(오늘 제외)에 그대로 있으면 FAIL. 단답 치환이 백지복습 '남은 구멍'을
 * 다시 겨냥하는 것은 N일이 지나면 허용한다는 뜻이다. N = _validate.recent_concept_days. */
function recentConceptDupCheck(B) {
  const days = cf('recent_concept_days', V.recent_concept_days);   // 시험별 override 가능
  if (!days) return;
  const qfile = rx(V.quiz_file_regex || '^20\\d{2}-\\d{2}-\\d{2}\\.html$');
  const seen = new Map();                      // conceptKey → 최근 출처 파일명
  let files = [];
  try { files = fs.readdirSync(QDIR); } catch (e) { files = []; }
  files.filter(f => qfile.test(f) && f !== BASENAME && !f.startsWith(TODAY))
    .filter(f => { const d = day(f.slice(0, 10)); return d > 0 && d <= days; })
    .sort()
    .forEach(f => {
      let html = '';
      try { html = fs.readFileSync(path.join(QDIR, f), 'utf8'); } catch (e) { return; }
      const m = html.match(QRE);
      if (!m) return;
      let arr = null;
      try { arr = JSON.parse(m[1]); } catch (e) { try { arr = eval(m[1]); } catch (e2) { arr = null; } }  // eslint-disable-line no-eval
      if (!Array.isArray(arr)) return;
      arr.forEach(q => { if (q && q.conceptKey) seen.set(String(q.conceptKey), f); });
    });
  const isNew = q => !(q.q || '').includes(EM.longrev) && !(q.q || '').includes(EM.monthly) &&
    !(q.q || '').includes(EM.retry) && !q.monthlyOf && !q.retryOf;
  const dup = B.filter(isNew).filter(q => seen.has(String(q.conceptKey)));
  ok('recent_concept_dup', dup.length === 0,
    '신규 문항 conceptKey가 최근 ' + days + '일 데일리와 중복 없음' +
    (dup.length ? ' — ' + dup.map(q => q.conceptKey + ' ← ' + seen.get(String(q.conceptKey))).join(' | ') : ''));
}

function pastDupCheck(B) {
  const past = new Set();
  fs.readdirSync(QDIR)
    .filter(f => f.endsWith('.html') && !f.startsWith(TODAY) && !f.startsWith('_') && f !== BASENAME)
    .forEach(f => {
      pastQuestionTexts(fs.readFileSync(path.join(QDIR, f), 'utf8')).forEach(t => past.add(normQ(t)));
    });
  const pastArr = [...past];
  const dup = B.filter(q => { const n = normQ(q.q); return pastArr.some(p => p.slice(0, DUP_LEN) === n.slice(0, DUP_LEN)); });
  ok('past_dup', dup.length === 0,
    '과거 문제문과 도입부 중복 없음' + (dup.length ? ' — ' + dup.map(d => d.q.slice(0, 20)).join(' | ') : ''));
}

/* ── 램프업 단계 판정 (법무사 1·2차 공용 — 레거시 사다리 그대로, 경로만 exams.json) ── */
function countNotes() {
  const trk = EX.track || {};
  const notePat = rx(PATHS.note_pattern || '^20\\d{2}-\\d{2}-\\d{2}.*\\.md$');
  let files = [];
  try { files = fs.readdirSync(NOTES_DIR); } catch (e) { files = []; }
  const mds = files.filter(f => notePat.test(f) &&
    (trk.token ? (trk.include ? f.includes(trk.token) : !f.includes(trk.token)) : true) &&
    fs.statSync(path.join(NOTES_DIR, f)).size > 0);
  const w = cf('new_note_window_days', 7);
  const nNew = mds.filter(f => { const d = day(f.slice(0, 10)); return d >= 0 && d < w; }).length;
  const nLong = mds.filter(f => day(f.slice(0, 10)) >= w).length;
  const mw = cf('monthly_window', [27, 33]);
  const qfile = rx(V.quiz_file_regex || '^20\\d{2}-\\d{2}-\\d{2}\\.html$');
  let qfiles = [];
  try { qfiles = fs.readdirSync(QDIR); } catch (e) { qfiles = []; }
  const nMon = qfiles.filter(f => qfile.test(f) && day(f.slice(0, 10)) >= mw[0] && day(f.slice(0, 10)) <= mw[1]).length;
  return { nNew: nNew, nLong: nLong, nMon: nMon };
}
function evalExpr(expr, ctx) {
  if (typeof expr === 'number') return expr;
  const src = String(expr).replace(/\bnew\b/g, 'new_').replace(/\blong\b/g, 'long_').replace(/\bmonthly_window\b/g, 'mon_');
  return Function('new_', 'long_', 'mon_', 'return (' + src + ');')(ctx.nNew, ctx.nLong, ctx.nMon);
}
function resolveStage(ctx) {
  const ladder = DCFG.rampup || [];
  for (const s of ladder) {
    if (evalExpr(s.when, ctx)) return { stage: s.stage, exp: evalExpr(s.total, ctx), def: s };
  }
  return { stage: '스킵', exp: 0, def: {} };
}

/* ══════════════════════════════ 데일리 검증 ═══════════════════════════════ */

function validateGonginDaily() {
  const M = Q.filter(q => q.monthlyOf), B = Q.filter(q => !q.monthlyOf);
  const SA = Q.filter(q => q.type === '단답'), MCQ = Q.filter(q => q.type !== '단답');
  const SAB = B.filter(q => q.type === '단답');

  const total = DCFG.total, monthly = DCFG.monthly, main = total - monthly;
  const optsN = DCFG.opts_count, ansR = DCFG.answer_range;
  const TQ = DCFG.type_quota_main40 || {};
  const saCap = onOrAfter(DCFG.sa_swap_zero_from) ? 0 : DCFG.sa_swap_max;
  const kc = cf('keywords_count', [2, 4]);
  const saStem = rx(DCFG.sa_stem_regex);
  const saForbid = DCFG.sa_answer_forbid_regex || {};
  const negRx = rx(DCFG.negative_regex);

  ok('token_leftover', !HTML.includes(TOKEN), '템플릿 토큰({{..}}) 잔존 없음');
  ok('total_count', Q.length === total, '문항 수 ' + total + ' (현재 ' + Q.length + ')');
  ok('main_count', B.length === main, '본편 ' + main + ' (현재 ' + B.length + ')');
  ok('monthly_count', M.length === monthly, '한달전 복원 ' + monthly + ' (현재 ' + M.length + ')');
  ok('monthly_block_tail',
    Q.slice(main).every(q => q.monthlyOf) && Q.slice(0, main).every(q => !q.monthlyOf),
    '한달전 블록은 ' + (main + 1) + '~' + total + '번에만');
  ok('no_retry_in_main', B.every(q => !q.retryOf && !q.q.includes(EM.retry)),
    '재도전(' + EM.retry + '·retryOf) 없음 — 오답퀴즈 전담(v5)');
  ok('monthly_marks',
    M.every(q => q.q.includes(EM.monthly) && RE_MONTHLY_SRC.test(q.src) && RE_MONTHLY_OF.test(q.monthlyOf)),
    '한달전 표기(' + EM.monthly + '·src·monthlyOf) 일관');
  const mcats = {}; M.forEach(q => mcats[q.cat] = (mcats[q.cat] || 0) + 1);
  ok('monthly_cat_max', Math.max(...Object.values(mcats)) <= DCFG.monthly_per_cat_max,
    '한달전 과목 골고루(과목당 ≤' + DCFG.monthly_per_cat_max + ') ' + JSON.stringify(mcats));
  ok('mcq_answer_range', MCQ.every(q => q.answer >= 0 && q.answer < q.opts.length), '객관식 정답 인덱스 범위');
  ok('required_fields', Q.every(q => q.q && q.expl && q.src && q.cat && q.type && q.conceptKey), '필수 필드(conceptKey 포함)');
  ok('mcq_opts_count', MCQ.every(q => q.opts.length === optsN || (q.type === 'OX' && q.opts.length === 2)),
    '객관식 보기 수 ' + optsN + ' / OX 2');
  ok('sa_cap_daily', SAB.length <= saCap, '단답 치환 ≤' + saCap + '·본편 신규 몫 (현재 ' + SAB.length + ')');
  ok('sa_contract', SA.every(q => saContract(q) && q.answer.length >= 2),
    '단답 계약(answer 문자열·keywords ' + kc[0] + '~' + kc[1] + '·opts 없음)');
  ok('sa_not_longrev', SAB.every(q => !q.q.includes(EM.longrev)), '단답은 신규에만(' + EM.longrev + ' 치환 금지)');
  ok('sa_stem', SA.every(q => saStem.test(String(q.q))), '단답 발문(쓰시오체)');
  ok('sa_answer_tags',
    SA.every(q => !rx(saForbid.tag_other_than_br, 'i').test(String(q.answer)) && !rx(saForbid.quote_backtick).test(String(q.answer))),
    '단답 answer: br 외 태그·백틱·큰따옴표 금지');

  const T = t => B.filter(q => q.type === t).length;
  ok('type_ox', T('OX') === TQ['OX'][0], '본편 OX ' + TQ['OX'][0] + ' (현재 ' + T('OX') + ')');
  ok('type_combo', T('조합') === TQ['조합'][0], '본편 조합 ' + TQ['조합'][0] + ' (현재 ' + T('조합') + ')');
  comboRatioChecks(B.filter(q => q.type === '조합'), (DCFG.combo || {}).check_min_count || 4, DCFG.combo);
  ok('type_case', T('사례') === TQ['사례'][0], '본편 사례 ' + TQ['사례'][0] + ' (현재 ' + T('사례') + ')');
  ok('type_calc', T('계산') >= TQ['계산'][0] && T('계산') <= TQ['계산'][1],
    '본편 계산 ' + TQ['계산'][0] + '~' + TQ['계산'][1] + ' (현재 ' + T('계산') + ')');
  const sum24 = T('일반') + T('계산') + T('단답');
  ok('type_sum24', sum24 === 24, '본편 일반+계산+단답=24 (현재 ' + sum24 + ')');
  const calcFields = DCFG.calc_required_fields || ['expr', 'expected'];
  ok('calc_fields', Q.filter(q => q.type === '계산').every(q => q.calc && q.calc[calcFields[0]] && isFinite(q.calc[calcFields[1]])),
    '계산형 calc{' + calcFields.join(',') + '} 필수(전체)');
  Q.filter(q => q.type === '계산' && q.calc && q.calc.expr).forEach((q, i) => {
    let v; try { v = Function('return (' + q.calc.expr + ')')(); } catch (e) { v = NaN; }
    ok('calc_verify#' + (i + 1), isFinite(v) && Math.abs(v - q.calc.expected) < 1e-6,
      '계산 검산 #' + (i + 1) + ': ' + q.calc.expr + ' = ' + v + ' (기대 ' + q.calc.expected + ')');
  });
  ok('combo_stem', Q.filter(q => q.type === '조합').every(q => q.q.includes((DCFG.combo || {}).stem_contains)),
    '조합형 발문 형식(전체)');
  explMatchChecks(MCQ);
  ok('cat_contiguous', contiguousCat(B), '본편 같은 과목 연속 배치');
  const cats = {}; B.forEach(q => cats[q.cat] = (cats[q.cat] || 0) + 1);
  note('  본편 과목 분포: ' + JSON.stringify(cats));

  const mc = B.filter(q => q.opts && q.opts.length === optsN), oxq = B.filter(q => q.type === 'OX');
  const oxO = oxq.filter(q => q.answer === 0).length;
  const oxR = (DCFG.ox_balance || {}).O || [2, 3];
  ok('ox_balance', oxO >= oxR[0] && oxO <= oxR[1], '본편 OX 비율 O:' + oxO + ' X:' + (oxq.length - oxO));
  const dist = new Array(ansR).fill(0); mc.forEach(q => dist[q.answer]++);
  note('  본편 객관식 정답 분포 0~' + (ansR - 1) + ': ' + dist.join('/'));
  const ad = DCFG.answer_dist_main;
  ok('answer_dist_main', Math.max(...dist) <= ad[1] && Math.min(...dist) >= ad[0],
    '본편 정답 분산 ' + ad[0] + '~' + ad[1]);
  let run = 1, maxRun = 1;
  for (let i = 1; i < Q.length; i++) {
    run = (Number.isInteger(Q[i].answer) && Q[i].answer === Q[i - 1].answer) ? run + 1 : 1;
    maxRun = Math.max(maxRun, run);
  }
  ok('no_triple_run', maxRun <= 2,
    '전체 ' + total + '문 같은 정답 인덱스 3연속 없음 (최대 ' + maxRun + ') — 위반 시 한달전 블록 내부 순서만 교체');

  const lr = B.filter(q => q.q.includes(EM.longrev)).length;
  const lrA = DCFG.longrev, lrB = (DCFG.allday_mode || {}).longrev;
  ok('longrev_count', lr === lrA || lr === lrB,
    '장기복습(' + EM.longrev + ') ' + lrA + '(기본) 또는 ' + lrB + '(전일) (현재 ' + lr + ')');
  ok('longrev_marks', B.filter(q => q.q.includes(EM.longrev)).every(q => RE_LONGREV_SRC.test(q.src)),
    '장기복습 표기(' + EM.longrev + '·src) 일관');
  const nr = DCFG.negative_ratio_mcq, nrR = DCFG.negative_ratio_round || ['round', 'round'];
  const neg = mc.filter(q => negRx.test(q.q)).length;
  ok('negative_ratio', neg >= Math[nrR[0]](mc.length * nr[0]) && neg <= Math[nrR[1]](mc.length * nr[1]),
    '본편 부정형 ' + Math.round(nr[0] * 100) + '~' + Math.round(nr[1] * 100) + '% (현재 ' + neg + '/' + mc.length + ')');
  const lmax = DCFG.longest_is_answer_max;
  const longest = mc.filter(q => q.opts[q.answer].length === Math.max(...q.opts.map(x => x.length))).length;
  ok('longest_is_answer', longest <= Math.ceil(mc.length * lmax),
    '본편 정답=최장보기 ' + Math.round(lmax * 100) + '% 이하 (현재 ' + longest + '/' + mc.length + ')');
  pastDupCheck(B);
  recentConceptDupCheck(B);

  return { main: B.length, monthly: M.length, sa: SA.length, longrev: lr, cats: cats, answerDist: dist };
}

function validateBupsaDaily() {
  const ctx = countNotes();
  const st = resolveStage(ctx);
  const stage = st.stage, exp = st.exp;
  note('단계=' + stage + ' 기대문항=' + exp + ' (신규 ' + ctx.nNew + '·장기 ' + ctx.nLong + '·한달전창 ' + ctx.nMon + ')');

  const M = Q.filter(q => q.monthlyOf), B = Q.filter(q => !q.monthlyOf);
  const confirmRx = rx((DCFG.forbid_regex || {}).confirm_tag || V.confirm_needed_regex ||
    '\\((원문|판례 번호|예규 번호|현행 예규) 확인 필요\\)');
  const monExp = st.def.monthly || 0;
  const examTag = (EX.track || {}).front_matter_exam;

  ok('token_leftover', !HTML.includes(TOKEN), '토큰 잔존 없음');
  ok('confirm_tag', !confirmRx.test(HTML), '태그 위생: 확인-필요류 잔존 0');
  ok('total_count', Q.length === exp, '문항 수 ' + exp + ' (현재 ' + Q.length + ')');
  ok('monthly_count', M.length === monExp, '한달전 ' + monExp + ' (현재 ' + M.length + ')');
  if (M.length) {
    ok('monthly_block_tail',
      Q.slice(-M.length).every(q => q.monthlyOf) && Q.slice(0, Q.length - M.length).every(q => !q.monthlyOf),
      '한달전 블록 맨 뒤');
  }
  ok('required_fields', Q.every(q => q.q && q.expl && q.src && q.cat && q.type && q.conceptKey && q.exam), '필수 필드(exam·conceptKey)');

  if (ARGS.exam === 'bupsa1') {
    /* ── 법무사 1차 데일리 (객관식 5지) ── */
    const SA = Q.filter(q => q.type === '단답'), MCQ = Q.filter(q => q.type !== '단답');
    const optsN = DCFG.opts_count, kc = cf('keywords_count', [2, 4]);
    const saCap = onOrAfter(DCFG.sa_swap_zero_from) ? 0 : DCFG.sa_swap_max;
    const saForbid = DCFG.sa_answer_forbid_regex || {};
    const fb = DCFG.forbid_regex || {};

    ok('exam_field', Q.every(q => q.exam === examTag), '전 문항 exam ' + examTag);
    ok('sa_cap_daily', SA.length <= saCap, '단답 치환 ≤' + saCap + ' (현재 ' + SA.length + ')');
    ok('sa_contract', SA.every(q => saContract(q) && q.answer.length >= 2),
      '단답 계약(answer 문자열·keywords ' + kc[0] + '~' + kc[1] + '·opts 없음)');
    ok('sa_stem', SA.every(q => rx(DCFG.sa_stem_regex).test(String(q.q))), '단답 발문(쓰시오체)');
    ok('sa_answer_tags',
      SA.every(q => !rx(saForbid.tag_other_than_br, 'i').test(String(q.answer)) && !rx(saForbid.quote_backtick).test(String(q.answer))),
      '단답 answer: br 외 태그·백틱·큰따옴표 금지');
    ok('mcq_contract', MCQ.every(q => Number.isInteger(q.answer) && q.opts && q.opts.length === optsN && q.answer >= 0 && q.answer < optsN),
      '객관식 계약(' + optsN + '지선다·정답 0~' + (optsN - 1) + ')');
    ok('no_ox', Q.every(q => q.type !== 'OX'), 'OX 없음 (기출 미출제 유형)');
    ok('no_calc', Q.every(q => q.type !== '계산' && !q.calc), '계산형 없음');
    const STEM = rx(DCFG.stem_whitelist_regex);
    ok('mcq_stem_whitelist', MCQ.every(q => STEM.test(String(q.q))), '객관식 발문 기출 상투구 (기출문형 §1-1)');
    const pq = rx(fb.precedent_quote), cn = rx(fb.case_number);
    ok('precedent_plain', Q.every(q => !pq.test(String(q.q) + (q.opts || []).join(' ') + (q.type === '단답' ? String(q.answer) : ''))),
      '판례 평서화 (지문 내 인용구 금지)');
    ok('no_case_number', Q.every(q => !cn.test(String(q.q) + (q.opts || []).join(' ') + (q.type === '단답' ? String(q.answer) : ''))),
      '지문에 판결번호 없음');
    ok('combo_marker', Q.filter(q => q.type === '조합').every(q => rx((DCFG.combo || {}).marker_regex).test(q.q)),
      '조합형 지문 마커(<br>ㄱ. 형)');
    const ct = DCFG.count_type || {};
    const cnt = Q.filter(q => q.type === '개수');
    ok('count_type_max', cnt.length <= ct.max_per_set, '개수형 ' + ct.max_per_set + '문 이하 (현재 ' + cnt.length + ')');
    ok('count_type_stem', cnt.every(q => rx(ct.stem_regex).test(q.q)), '개수형 발문');
    const pe = rx(DCFG.precedent_expl_regex);
    Q.filter(q => q.type === '판례').forEach((q, i) =>
      ok('precedent_expl#' + (i + 1), pe.test(q.expl), '판례결론형 해설에 결론 가른 변수 명시 #' + (i + 1)));
    explMatchChecks(MCQ);
    ok('combo_stem', Q.filter(q => q.type === '조합').every(q => q.q.includes((DCFG.combo || {}).stem_contains)), '조합형 발문 형식');
    comboRatioChecks(Q.filter(q => q.type === '조합'), (DCFG.combo || {}).check_min_count || 4, DCFG.combo);
  } else {
    /* ── 법무사 2차 데일리 (전 문항 단답) ── */
    const kc = cf('keywords_count', [2, 4]);
    const SUBS = DCFG.sub_types || [];
    const fb = DCFG.forbid_regex || {};
    ok('all_sa_exam', Q.every(q => q.type === DCFG.type && q.exam === examTag),
      '전 문항 ' + DCFG.type + '·exam ' + examTag + ' (혼입 금지)');
    ok('sa_answer_string', Q.every(q => typeof q.answer === 'string' && q.answer.length >= 2 && !q.opts), '단답: answer 문자열·opts 없음');
    ok('sa_keywords', Q.every(q => Array.isArray(q.keywords) && q.keywords.length >= kc[0] && q.keywords.length <= kc[1]),
      '단답: keywords ' + kc[0] + '~' + kc[1] + '개');
    ok('no_calc', Q.every(q => !q.calc), '계산형 없음');
    ok('sub_valid', B.every(q => SUBS.includes(q.sub)), '본편 sub 소유형 유효 (' + SUBS.length + '종)');
    const mac = DCFG.mini_answer_counts || { maintain: 0, total_gte: 12, high: 2, low: 1 };
    const mini = B.filter(q => q.sub === '미니답안');
    const miniExp = (stage === '유지') ? mac.maintain : (exp >= mac.total_gte ? mac.high : mac.low);
    const mlen = DCFG.mini_answer_len || [150, 500];
    ok('mini_count', mini.length === miniExp, '미니답안 ' + miniExp + '문 (현재 ' + mini.length + ')');
    ok('mini_skeleton', mini.every(q => q.answer.includes('<br>') && q.answer.length >= mlen[0] && q.answer.length <= mlen[1] && rx(DCFG.mini_answer_stem_regex).test(q.q)),
      '미니답안 골격(br 문단·' + mlen[0] + '~' + mlen[1] + '자·배점 표기)');
    ok('answer_maxlen', B.filter(q => q.sub !== '미니답안').every(q => q.answer.length <= DCFG.answer_max_len),
      '일반 정답 ' + DCFG.answer_max_len + '자 이내');
    ok('br_only', Q.every(q => !rx(fb.tag_other_than_br, 'i').test(String(q.q) + String(q.answer) + String(q.expl))), '태그는 br만 (그 외 < 금지)');
    ok('no_bracket_quote', Q.every(q => !rx(fb.quote_brackets).test(String(q.answer))), '조문 인용 괄호형 (낫표 금지)');
    ok('stem_style', B.every(q => rx(DCFG.stem_regex).test(q.q)), '발문 기출체 (하시오체 포함)');
  }

  const re = B.filter(q => q.retryOf || String(q.q).includes(EM.retry)).length;
  ok('no_retry_in_main', re === 0, '재도전 0 — 오답퀴즈 전담 (현재 ' + re + ')');
  const lr = B.filter(q => q.q.includes(EM.longrev)).length;
  if (stage === 'S2' || stage === 'S3') ok('longrev_count', lr === st.def.longrev, '장기복습 ' + st.def.longrev + ' (현재 ' + lr + ')');
  if (stage === '유지') ok('longrev_maintain', lr === B.length, '유지 모드: 전부 장기복습 (현재 ' + lr + '/' + B.length + ')');
  ok('longrev_marks', B.filter(q => q.q.includes(EM.longrev)).every(q => RE_LONGREV_SRC.test(q.src)), '장기복습 표기 일관');
  if (M.length) {
    ok('monthly_marks', M.every(q => q.q.includes(EM.monthly) && RE_MONTHLY_SRC.test(q.src) && RE_MONTHLY_OF.test(q.monthlyOf)), '한달전 표기 일관');
    const mc = {}; M.forEach(q => mc[q.cat] = (mc[q.cat] || 0) + 1);
    ok('monthly_cat_max', Math.max(...Object.values(mc)) <= DCFG.monthly_per_cat_max,
      '한달전 과목 골고루(≤' + DCFG.monthly_per_cat_max + ') ' + JSON.stringify(mc));
  }
  ok('cat_contiguous', contiguousCat(B), '같은 과목 연속 배치');

  let dist = null;
  if (ARGS.exam === 'bupsa1') {
    const mc5 = B.filter(q => q.type !== '단답');
    const minN = DCFG.answer_dist_min_n || 10;
    if (mc5.length >= minN) {
      dist = new Array(DCFG.answer_range).fill(0); mc5.forEach(q => dist[q.answer]++);
      note('  객관식 정답 분포 0~' + (DCFG.answer_range - 1) + ': ' + dist.join('/'));
      ok('answer_dist_maxdiff', Math.max(...dist) - Math.min(...dist) <= DCFG.answer_dist_max_diff,
        '정답 분산(최대-최소 ≤' + DCFG.answer_dist_max_diff + ')');
      const nr = DCFG.negative_ratio_mcq, negRx = rx(DCFG.negative_regex);
      const nrR = DCFG.negative_ratio_round || ['floor', 'ceil'];
      const neg = mc5.filter(q => negRx.test(q.q)).length;
      ok('negative_ratio', neg >= Math[nrR[0]](mc5.length * nr[0]) && neg <= Math[nrR[1]](mc5.length * nr[1]),
        '부정형 ' + Math.round(nr[0] * 100) + '~' + Math.round(nr[1] * 100) + '% (현재 ' + neg + '/' + mc5.length + ')');
      const mx = maxRunOf(B.filter(q => Number.isInteger(q.answer)).map(q => q.answer));
      ok('no_triple_run', mx <= 2, '같은 정답 3연속 없음 (최대 ' + mx + ')');
    }
  }
  const cats = {}; B.forEach(q => cats[q.cat] = (cats[q.cat] || 0) + 1);
  note('  과목 분포: ' + JSON.stringify(cats));
  pastDupCheck(B);
  recentConceptDupCheck(B);

  return {
    stage: stage, expected: exp, newNotes: ctx.nNew, longNotes: ctx.nLong, monthlyWindow: ctx.nMon,
    main: B.length, monthly: M.length, longrev: lr, cats: cats, answerDist: dist
  };
}

/* ══════════════════════════════ 오답 검증 ═════════════════════════════════ */

function validateRetry() {
  let led;
  try { led = JSON.parse(fs.readFileSync(LEDGER, 'utf8')); }
  catch (e) { ok('ledger_load', false, '원장 읽기 실패: ' + LEDGER + ' — ' + e.message); return { error: 'ledger' }; }
  const due = led.dueQueue || [];
  // 주의: 상위 N 집합이 아니라 "dueQueue 어디든 존재" 로 판정한다(레거시 keys.has 유지).
  const keys = new Set(due.map(d => d.conceptKey));
  const dmap = new Map(due.map(d => [d.conceptKey, d]));

  const cap = KCFG.cap;
  const exp = Math.min(cap, due.length);
  const saCapRaw = KCFG.sa_promote_unlimited ? Infinity
    : (KCFG.sa_promote_cap === null || KCFG.sa_promote_cap === undefined ? 0 : KCFG.sa_promote_cap);
  const SA_CAP = onOrAfter(KCFG.sa_promote_zero_from) ? 0 : saCapRaw;

  const SA = Q.filter(q => q.type === '단답'), MCQ = Q.filter(q => q.type !== '단답');
  const kc = cf('keywords_count', [2, 4]);
  const excl = V.missedtop_exclude || ['결론·방향 자체', '^기타:'];

  const missedTopOK = q => {
    const d = dmap.get(q.conceptKey);
    const mt = ((d && d.missedTop) || []).filter(k => k !== excl[0] && !rx(excl[1]).test(k));
    return !mt.length || (q.keywords || []).some(k => mt.includes(k));
  };
  const promoteOK = q => { const d = dmap.get(q.conceptKey); return d && (d.status === '상습' || d.retryMissed >= 1 || d.timesWrong >= 3); };

  ok('token_leftover', !HTML.includes(TOKEN), '토큰 잔존 없음');
  ok('total_count', Q.length === exp, '문항 수 = min(' + cap + ',듀) = ' + exp + ' (현재 ' + Q.length + ')');
  ok('retry_marks', Q.every(q => q.retryOf && q.retryOf === q.conceptKey && q.q.includes(EM.retry) && RE_RETRY_SRC.test(q.src)),
    '전 문항 재도전 표기(retryOf·' + EM.retry + '·src)');
  ok('conceptkey_in_due', Q.every(q => keys.has(q.conceptKey)), 'conceptKey 전부 듀큐에 존재');
  ok('required_fields', Q.every(q => q.q && q.expl && q.src && q.cat && q.type), '필수 필드');

  if (ARGS.exam === 'bupsa1') {
    /* ── 법무사1차 오답 — 베이스 공통 대신 실행하는 완결 검증 ── */
    const optsN = KCFG.opts_count;
    const examTag = (EX.track || {}).front_matter_exam;
    ok('exam_field_nocalc', Q.every(q => q.exam === examTag && !q.calc), '전 문항 ' + examTag + '·계산 금지');
    ok('no_ox', MCQ.every(q => q.type !== 'OX'), 'OX 금지');
    ok('mcq_contract', MCQ.every(q => Number.isInteger(q.answer) && q.opts && q.opts.length === optsN && q.answer >= 0 && q.answer < optsN),
      '객관식 계약(' + optsN + '지선다·정답 0~' + (optsN - 1) + ')');
    comboRatioChecks(MCQ.filter(q => q.type === '조합'), (KCFG.combo || {}).check_min_count || 4, KCFG.combo);
    explMatchChecks(MCQ);
    ok('sa_cap_retry', SA.length <= SA_CAP, '단답 승격 상한 ≤' + SA_CAP + ' (현재 ' + SA.length + ')');
    ok('sa_contract_retry', SA.every(saContract), '단답 계약(answer 문자열·keywords ' + kc[0] + '~' + kc[1] + '·opts 없음)');
    ok('sa_stem', SA.every(q => rx(cf('sa_stem_regex')).test(String(q.q))), '단답 발문(쓰시오체)');
    if (MCQ.length > 0) ok('sa_promote_cond', SA.every(promoteOK), '단답 승격 조건(상습∨재도전실패≥1∨틀림≥3)');
    ok('sa_missedtop', SA.every(missedTopOK), '단답 missedTop 조준(있다면 keywords에 반영 — 결론·방향/기타는 문구 검사 제외)');
    const STEM = rx(cf('stem_whitelist_regex'));
    ok('mcq_stem_whitelist', MCQ.every(q => STEM.test(String(q.q))), '객관식 발문 기출 상투구');
    const fb = cf('forbid_regex', {});
    ok('precedent_plain', Q.every(q => !rx(fb.precedent_quote).test(String(q.q) + (q.opts || []).join(' ') + String(q.answer || ''))), '판례 평서화 (인용구 금지)');
    ok('no_case_number', Q.every(q => !rx(fb.case_number).test(String(q.q) + (q.opts || []).join(' ') + String(q.answer || ''))), '판결번호 없음');
    const minN = KCFG.answer_dist_min_n || 10;
    if (MCQ.length >= minN) {
      const dist = new Array(KCFG.answer_range).fill(0); MCQ.forEach(q => dist[q.answer]++);
      note('  정답 분포 0~' + (KCFG.answer_range - 1) + ': ' + dist.join('/'));
      ok('answer_dist_maxdiff', Math.max(...dist) - Math.min(...dist) <= KCFG.answer_dist_max_diff,
        '정답 분산(최대-최소 ≤' + KCFG.answer_dist_max_diff + ')');
    }
    const mx = maxRunOf(MCQ.map(q => q.answer));
    ok('no_triple_run', mx <= 2, '같은 정답 3연속 없음 (최대 ' + mx + ')');
  } else {
    /* ── 오답 공통 베이스 (gongin: 상한 20·SA_CAP 5 / bupsa2: 상한 8·SA_CAP Infinity) ── */
    ok('sa_contract_retry', SA.every(saContract), '단답 계약(있다면 — exam 검사는 트랙 추가 검증 몫)');
    ok('sa_cap_retry', SA.length <= SA_CAP, '단답 승격 상한 ≤' + SA_CAP + ' (현재 ' + SA.length + ')');
    if (MCQ.length > 0) ok('sa_promote_cond', SA.every(promoteOK), '단답 승격 조건(상습∨재도전실패≥1∨틀림≥3)');
    ok('sa_missedtop', SA.every(missedTopOK), '단답 missedTop 조준(있다면 keywords에 반영 — 결론·방향/기타는 문구 검사 제외)');
    const optsN = cf('opts_count', 4);
    ok('mcq_contract', MCQ.every(q => Number.isInteger(q.answer) && q.opts && (q.opts.length === optsN || (q.type === 'OX' && q.opts.length === 2)) && q.answer >= 0 && q.answer < q.opts.length),
      '객관식 계약');
    const oxr = cf('ox_max_ratio', 0.3);
    const ox = MCQ.filter(q => q.type === 'OX');
    ok('ox_ratio', ox.length <= Math.ceil(Q.length * oxr), 'OX ≤' + Math.round(oxr * 100) + '%');
    comboRatioChecks(MCQ.filter(q => q.type === '조합'), (cf('combo', {}) || {}).check_min_count || 4, cf('combo', {}));
    const mc4 = MCQ.filter(q => q.opts && q.opts.length === optsN);
    const minN = cf('answer_dist_min_n', 8);
    if (mc4.length >= minN) {
      const d = new Array(cf('answer_range', 4)).fill(0); mc4.forEach(q => d[q.answer]++);
      note('  정답 분포: ' + d.join('/'));
      ok('answer_dist_maxdiff', Math.max(...d) - Math.min(...d) <= cf('answer_dist_max_diff', 3),
        '정답 분산(최대-최소 ≤' + cf('answer_dist_max_diff', 3) + ')');
    }
    const mx = maxRunOf(MCQ.map(q => q.answer));
    ok('no_triple_run', mx <= 2, '같은 정답 3연속 없음 (최대 ' + mx + ')');
    explMatchChecks(MCQ);

    if (ARGS.exam === 'bupsa2') {
      /* ── 법무사2차 오답 전용 추가검증 (베이스 통과 + 이것도 통과가 규칙) ── */
      const examTag = (EX.track || {}).front_matter_exam;
      const SUBS = cf('sub_types', []);
      const fb = cf('forbid_regex', {});
      const mlen = cf('mini_answer_len', [150, 500]);
      ok('all_sa_exam', Q.every(q => q.type === cf('type') && q.exam === examTag && !q.opts), '전 문항 ' + cf('type') + '·' + examTag);
      ok('sub_valid', Q.every(q => SUBS.includes(q.sub)), 'sub 소유형 유효 (' + SUBS.length + '종)');
      const mini = Q.filter(q => q.sub === '미니답안');
      ok('mini_max', mini.length <= KCFG.mini_answer_max, '미니답안 ' + KCFG.mini_answer_max + '문 이하 (현재 ' + mini.length + ')');
      ok('mini_skeleton', mini.every(q => q.answer.includes('<br>') && q.answer.length >= mlen[0] && q.answer.length <= mlen[1] && rx(cf('mini_answer_stem_regex')).test(q.q)),
        '미니답안 골격(br 문단·' + mlen[0] + '~' + mlen[1] + '자·배점 표기)');
      ok('answer_maxlen', Q.filter(q => q.sub !== '미니답안').every(q => q.answer.length <= cf('answer_max_len')),
        '일반 정답 ' + cf('answer_max_len') + '자 이내');
      ok('br_only', Q.every(q => !rx(fb.tag_other_than_br, 'i').test(String(q.q) + String(q.answer) + String(q.expl))), '태그는 br만 (그 외 < 금지)');
      ok('no_bracket_quote', Q.every(q => !rx(fb.quote_brackets).test(String(q.answer))), '조문 인용 괄호형 (낫표 금지)');
      ok('stem_style', Q.every(q => rx(cf('stem_regex')).test(q.q)), '발문 기출체 (하시오체 포함)');
    }
  }

  return {
    cap: cap, expected: exp, dueLen: due.length, dueRest: Math.max(0, due.length - Q.length),
    sa: SA.length, saCap: SA_CAP === Infinity ? 'Infinity' : SA_CAP, mcq: MCQ.length
  };
}

/* ═════════════════════════════════ main ═══════════════════════════════════ */

let extra = {};
try {
  if (KIND === 'daily') extra = (ARGS.exam === 'gongin') ? validateGonginDaily() : validateBupsaDaily();
  else extra = validateRetry();
} catch (e) {
  ok('runtime', false, '검증 중 예외: ' + e.message);
}

const fails = checks.filter(c => !c.ok);
const pass = fails.length === 0;

const summary = Object.assign({
  exam: ARGS.exam, kind: KIND, file: FILE, date: TODAY, root: ROOT,
  total: Q.length, checks: checks.length, failed: fails.length,
  final_format: onOrAfter(EX.final_format_from),
  sa_swap_zero: onOrAfter(DCFG.sa_swap_zero_from),
  sa_promote_zero: onOrAfter((EX.retry || {}).sa_promote_zero_from)
}, extra);

if (ARGS.json) {
  process.stdout.write(JSON.stringify({
    pass: pass,
    checks: checks.map(c => ({ id: c.id, ok: c.ok, msg: c.msg })),
    summary: summary
  }, null, 2) + '\n');
} else {
  OUT.forEach(l => console.log(l));
  console.log(fails.length ? '\n❌ ' + fails.length + '건 — 수정 후 재실행' : '\n✅ 전체 통과');
}
process.exit(pass ? 0 : 1);
