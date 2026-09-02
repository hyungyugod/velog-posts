// 렌더 테스트 — 정답 분산 · 3연속 금지 · 조합 셔플 비율 · 표기 부착 · 토큰 잔존 0
//              · 결정론 · 한달전 블록 위치 · 실패 시 draft 저장 · 실제 데이터 스모크
'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const H = require('./_helpers');

const FIX = path.join(H.ENGINE, 'tests', 'fixtures');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'hg-render-'));
let pass = 0, fail = 0;
const out = [];

function t(name, fn) {
  try { fn(); pass++; out.push('  ✔ ' + name); }
  catch (e) { fail++; out.push('  ✘ ' + name + '\n      ' + String(e.message).split('\n').join('\n      ')); }
}

/** 픽스처 plan 이 가리키는 원천 노트를 임시 root 에 깐다.
 *  evidence(노트 원문 인용) 게이트가 실제 파일과 대조하므로, 픽스처 quote 를 본문에 넣는다.
 *  키 = plan 의 path(루트 상대). 값 = 그 노트에서 인용되는 문장들. */
const FIXTURE_NOTES = {
  '공인중개사/2026-09-05-부동산학개론-(부동산학개론 지대이론).md': [
    '★★ 수익방식으로 구한 시산가액을 수익가액이라 한다.'],
  '공인중개사/2026-09-06-민법-(민법 물권·채권 총정리).md': ['- n: 물권은 절대권이고 채권은 상대권이다.'],
  '공인중개사/백지복습/2026-09-01-부동산세법-백지.md': [
    '남은 구멍: 법인에만 인정되는 간접비용은 건설자금이자, 할부·연부이자 및 연체료, 중개보수 세 가지다.'],
  '공인중개사/2026-06-07-부동산세법-(부동산세법 취득세 기초).md': ['★ 취득세 과세표준은 사실상 취득가격이다.'],
  '법무사/2026-09-05-민법-(민법 총칙 정리).md': ['★★ 법률행위의 목적은 확정·가능·적법·사회적 타당성을 갖추어야 한다.'],
  '법무사/2026-09-06-부동산등기법-(부등 신청주의).md': ['★ 등기는 신청 또는 촉탁에 의하여 실행함이 원칙이다.'],
  '법무사/백지복습/2026-09-01-부동산등기법-백지.md': [
    '남은 구멍: 단독신청이 허용되는 대표적 사유는 판결에 의한 등기, 상속에 의한 등기, 등기명의인 표시변경등기다.'],
  '법무사/2026-06-20-부동산등기법-(부동산등기법 가등기).md': ['★ 가등기는 순위보전의 효력만 가진다.'],
  '법무사/2026-09-05-2차-형법-(형법 위법성조각사유).md': [
    '★★ 긴급피난은 현재의 위난을 피하기 위한 상당한 이유 있는 행위여야 한다.',
    '★ 결과범과 형식범은 구성요건적 결과의 발생을 요구하는가에 따라 구별된다.',
    '- n: 부진정 결과적 가중범은 중한 결과를 고의로 야기한 경우에도 성립한다.'],
  '법무사/2026-06-25-2차-민사집행법-(민사집행법 배당절차).md': [
    '★★ 배당요구 종기는 배당재단의 범위를 확정하여 절차의 안정을 도모하기 위한 것이다.'],
  '법무사/백지복습/2026-09-01-2차-민사집행법-백지.md': [
    '남은 구멍: 집행권원이란 사법상 급부청구권의 존재와 범위를 표시하고 집행력이 부여된 공정증서를 말한다.'],
};

function seedNotes(root) {
  for (const [rel, lines] of Object.entries(FIXTURE_NOTES)) {
    const p = path.join(root, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, '# ' + path.basename(rel, '.md') + '\n\n' + lines.join('\n') + '\n', 'utf8');
  }
  return root;
}

function render(exam, kind, date, opts = {}) {
  const root = opts.root || seedNotes(fs.mkdtempSync(path.join(TMP, 'root-')));
  const cwd = opts.cwd || H.ENGINE;
  const args = [path.join(cwd, 'render_quiz.py'), '--exam', exam, '--kind', kind, '--date', date,
    '--plan', opts.plan || path.join(FIX, `${exam}_${kind}.plan.json`),
    '--questions', opts.questions || path.join(FIX, `${exam}_${kind}.questions.json`),
    '--root', root];
  if (!opts.validate) args.push('--no-validate');
  if (opts.seed !== undefined) args.push('--seed', String(opts.seed));
  let stdout = '', code = 0, stderr = '';
  try {
    stdout = execFileSync('python3', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (e) {
    code = e.status; stdout = e.stdout || ''; stderr = e.stderr || '';
  }
  const dir = exam === 'gongin' ? '공인중개사' : (exam === 'bupsa1' ? path.join('법무사', '1차') : path.join('법무사', '2차'));
  const file = path.join(root, dir, kind === 'daily' ? '데일리퀴즈' : '오답퀴즈', `${date}.html`);
  return { root, code, stdout, stderr, file, dir,
    html: fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null };
}

console.log('\n[render]');

// ── 1. 기본 렌더 4종 ─────────────────────────────────────────────
const R = {};
for (const [exam, kind, date] of [['gongin', 'daily', '2026-09-10'], ['gongin', 'retry', '2026-09-11'],
                                  ['bupsa1', 'daily', '2026-09-10'], ['bupsa2', 'daily', '2026-09-10'],
                                  ['bupsa2', 'retry', '2026-09-11']]) {
  R[`${exam}_${kind}`] = render(exam, kind, date);
}

t('5종(gongin daily/retry · bupsa1 daily · bupsa2 daily/retry) 렌더 성공', () => {
  for (const [k, r] of Object.entries(R)) {
    assert.strictEqual(r.code, 0, `${k} exit=${r.code}\n${r.stderr}`);
    assert.ok(r.html, `${k} 출력 파일 없음`);
  }
});

t('토큰 잔존 0', () => {
  for (const [k, r] of Object.entries(R)) {
    const left = [...new Set((r.html.match(/\{\{[A-Z0-9_]+\}\}/g) || []))];
    assert.deepStrictEqual(left, [], `${k}: ${left.join(', ')}`);
  }
});

// ── 2. 정답 분산 · 3연속 금지 ────────────────────────────────────
function mcqAnswers(html) {
  return H.extractQuestions(html).filter(q => q.type !== '단답' && q.type !== 'OX').map(q => q.answer);
}

t('정답 분산 (최대−최소 ≤ 3) · 인덱스 범위 준수', () => {
  for (const [k, r] of Object.entries(R)) {
    const qs = H.extractQuestions(r.html);
    const a = mcqAnswers(r.html);
    if (!a.length) continue;
    const range = k.startsWith('bupsa1') ? 5 : 4;
    qs.filter(q => q.type !== '단답' && q.type !== 'OX')
      .forEach(q => assert.ok(q.answer >= 0 && q.answer < q.opts.length && q.opts.length === range,
        `${k}: opts=${q.opts.length} answer=${q.answer} (기대 ${range}지)`));
    const c = Array.from({ length: range }, (_, i) => a.filter(x => x === i).length);
    assert.ok(Math.max(...c) - Math.min(...c) <= 3, `${k}: 분산 ${c}`);
  }
});

t('같은 인덱스 3연속 금지 (한달전 블록 포함 최종 배열)', () => {
  for (const [k, r] of Object.entries(R)) {
    const a = mcqAnswers(r.html);
    for (let i = 0; i + 2 < a.length; i++) {
      assert.ok(!(a[i] === a[i + 1] && a[i + 1] === a[i + 2]), `${k}: ${i}번째부터 3연속 (${a})`);
    }
  }
});

t('정답이 항상 최장 보기는 아니다 (배정이 길이와 무관)', () => {
  const qs = H.extractQuestions(R.gongin_daily.html).filter(q => q.opts && q.opts.length === 4);
  const longest = qs.filter(q => q.opts.indexOf(q.opts.slice().sort((x, y) => y.length - x.length)[0]) === q.answer);
  assert.ok(longest.length / qs.length <= 0.6, `최장=정답 비율 ${longest.length}/${qs.length}`);
});

// ── 3. 조합형 ────────────────────────────────────────────────────
function combos(html) { return H.extractQuestions(html).filter(q => q.type === '조합'); }

t('조합형: 지문 나열 부착 · 라벨 조합 보기 · opt 규격', () => {
  const g = combos(R.gongin_daily.html);
  assert.ok(g.length >= 4, '조합 문항 4개 이상');
  g.forEach(q => {
    assert.ok(/<br>ㄱ\. /.test(q.q), 'ㄱ. 지문 나열 부착: ' + q.q.slice(0, 40));
    assert.strictEqual(q.opts.length, 4, 'gongin 조합 opts 4');
    q.opts.forEach(o => assert.ok(/^[ㄱ-ㅎ](, [ㄱ-ㅎ])*$/.test(o), '조합 보기 형식: ' + o));
    assert.strictEqual(new Set(q.opts).size, q.opts.length, '보기 중복 없음');
  });
  const b = combos(R.bupsa1_daily.html);
  assert.ok(b.length >= 3, 'bupsa1 조합 3개 이상');
  b.forEach(q => {
    assert.strictEqual(q.opts.length, 5, 'bupsa1 조합 opts 5');
    q.opts.forEach(o => assert.strictEqual(o.split(', ').length, 3, 'bupsa1 opt_size 3: ' + o));
  });
});

t('조합형: 오답 보기는 정답과 원소 1개 차이(근접 조합)', () => {
  for (const html of [R.gongin_daily.html, R.bupsa1_daily.html]) {
    combos(html).forEach(q => {
      const set = s => new Set(s.split(', '));
      const corr = set(q.opts[q.answer]);
      q.opts.forEach((o, i) => {
        if (i === q.answer) return;
        const d = set(o);
        const only = [...corr].filter(x => !d.has(x)).length + [...d].filter(x => !corr.has(x)).length;
        assert.ok(only <= 2 && only >= 1, `근접 조합 아님: ${q.opts[q.answer]} vs ${o}`);
      });
    });
  }
});

t('조합형 세트 규격: ㄱ·ㄴ 정답 포함 비율 25~75% · ㄱ 거짓 문항 ≥2 (gongin, ≥4문)', () => {
  const g = combos(R.gongin_daily.html);
  assert.ok(g.length >= 4);
  for (const lab of ['ㄱ', 'ㄴ']) {
    const ratio = g.filter(q => q.opts[q.answer].split(', ').includes(lab)).length / g.length;
    assert.ok(ratio >= 0.25 && ratio <= 0.75, `${lab} 포함 비율 ${ratio}`);
  }
  // ㄱ이 거짓인 문항 — 발문이 '옳은 것을 모두'면 ㄱ∉정답, '옳지 않은 것을 모두'면 ㄱ∈정답
  const firstFalse = g.filter(q => {
    const inAns = q.opts[q.answer].split(', ').includes('ㄱ');
    const negative = /않은|않는|아닌/.test(q.q.split('<br>')[0]);
    return negative ? inAns : !inAns;
  }).length;
  assert.ok(firstFalse >= 2, `ㄱ 거짓 문항 ${firstFalse}개 (기대 ≥2)`);
});

// ── 4. 표기 부착 ─────────────────────────────────────────────────
t('⏪ 장기복습 표기: q 접두 + src 접미(N일전)', () => {
  const qs = H.extractQuestions(R.gongin_daily.html);
  const lr = qs.filter(q => q.q.startsWith('⏪ '));
  assert.strictEqual(lr.length, 2, '장기복습 2문항');
  lr.forEach(q => assert.ok(/\(장기복습·95일전\)$/.test(q.src), 'src 접미: ' + q.src));
  const b2 = H.extractQuestions(R.bupsa2_daily.html).filter(q => q.q.startsWith('⏪ '));
  assert.strictEqual(b2.length, 1);
  assert.ok(/\(장기복습·77일전\)$/.test(b2[0].src), 'note 경로 불일치 시 과목 폴백: ' + b2[0].src);
});

t('🔁 재도전 표기: q 접두 + retryOf + src 접미(재도전) · src 비면 "오답원장 (재도전)"', () => {
  for (const key of ['gongin_retry', 'bupsa2_retry']) {
    const qs = H.extractQuestions(R[key].html);
    assert.ok(qs.every(q => q.q.startsWith('🔁 ')), key + ': 전 문항 🔁 접두');
    assert.ok(qs.every(q => q.retryOf === q.conceptKey), key + ': retryOf = conceptKey');
    assert.ok(qs.every(q => /\(재도전\)$/.test(q.src)), key + ': src 접미');
  }
  const g = H.extractQuestions(R.gongin_retry.html);
  assert.strictEqual(g.find(q => q.conceptKey === '공인중개사법 1 상가임대차').src, '오답원장 (재도전)');
  const b = H.extractQuestions(R.bupsa2_retry.html);
  assert.ok(b.every(q => q.type === '단답' && q.exam === '2차' && q.sub), 'bupsa2 retry는 sub 있는 단답 전용');
  assert.ok(/오답 재도전 3문항 · 듀 잔여 6개/.test(R.bupsa2_retry.html), 'bupsa2 retry meta');
});

t('🔄 한달전 블록은 배열 맨 뒤 · 블록 안 과목 연속 · monthlyOf(원본 날짜) 계약 유지', () => {
  const qs = H.extractQuestions(R.gongin_daily.html);
  const mo = qs.map((q, i) => (q.monthlyOf ? i : -1)).filter(i => i >= 0);
  assert.strictEqual(mo.length, 3);
  assert.deepStrictEqual(mo, [qs.length - 3, qs.length - 2, qs.length - 1], '맨 뒤 연속');
  mo.forEach(i => {
    assert.ok(qs[i].q.startsWith('🔄 '));
    assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(qs[i].monthlyOf), 'monthlyOf 날짜: ' + qs[i].monthlyOf);
    assert.ok(/\(한달전 재출제·원본 \d{4}-\d{2}-\d{2}\)$/.test(qs[i].src), 'src 접미: ' + qs[i].src);
  });
  const cats = mo.map(i => qs[i].cat);
  assert.deepStrictEqual(cats, ['부동산공법', '부동산공법', '부동산공시법'], '블록 안 과목 연속');
});

t('한달전 블록 계약 위반(monthlyOf가 날짜가 아님·src 접미 없음)을 렌더가 잡는다', () => {
  const bad = path.join(TMP, 'bad-plan.json');
  const p = JSON.parse(fs.readFileSync(path.join(FIX, 'gongin_daily.plan.json'), 'utf8'));
  p.monthly_block[0].monthlyOf = '공법 용도지역-중복지정 불가';
  p.monthly_block[1].src = '2026-08-11 부동산공법 개발행위허가';
  fs.writeFileSync(bad, JSON.stringify(p));
  const r = render('gongin', 'daily', '2026-09-10', { plan: bad });
  assert.strictEqual(r.code, 1);
  assert.ok(/monthlyOf는 원본 문제지 날짜/.test(r.stderr), r.stderr);
  assert.ok(/한달전 재출제·원본/.test(r.stderr), r.stderr);
});

t('장기복습 age_days를 못 찾으면 실패 (src 접미 계약 보증)', () => {
  const bad = path.join(TMP, 'bad-lr.json');
  const p = JSON.parse(fs.readFileSync(path.join(FIX, 'gongin_daily.plan.json'), 'utf8'));
  p.longrev_picks = [];                                     // 나이 출처 전부 제거
  fs.writeFileSync(bad, JSON.stringify(p));
  const r = render('gongin', 'daily', '2026-09-10', { plan: bad });
  assert.strictEqual(r.code, 1);
  assert.ok(/age_days를 찾을 수 없음/.test(r.stderr), r.stderr);
});

t('본편 과목 연속 배치 (과목 블록 순서 = 첫 등장 순)', () => {
  const qs = H.extractQuestions(R.gongin_daily.html);
  const seen = [];
  qs.forEach(q => { if (seen[seen.length - 1] !== q.cat) seen.push(q.cat); });
  assert.strictEqual(new Set(seen).size, seen.length, '같은 과목이 두 번 끊겨 등장: ' + seen.join(' > '));
  assert.deepStrictEqual(seen, ['부동산학개론', '민법', '부동산세법', '부동산공법', '부동산공시법']);
});

// ── 5. META / TAGS / ALERT ───────────────────────────────────────
t('META_LINE · TAGS_HTML · ALERT_HTML 생성', () => {
  assert.ok(/2026년 9월 10일 \(목\)/.test(R.gongin_daily.html), 'gongin 날짜·요일');
  assert.ok(/장기복습 2\(⏪\)/.test(R.gongin_daily.html));
  assert.ok(/단답 2\(자가채점\)/.test(R.gongin_daily.html));
  assert.ok(/듀 잔여 25개/.test(R.gongin_retry.html), 'retry 듀 잔여');
  assert.ok(/S2 객관식 8문항\(단답 1 포함\)/.test(R.bupsa1_daily.html), 'bupsa1 STAGE·SA_SUFFIX');
  assert.ok(/미니답안 1/.test(R.bupsa2_daily.html), 'bupsa2 MINI');
  assert.ok(/<div class="alertbanner">⚠ 최근 2회 미제출/.test(R.bupsa1_daily.html), 'ALERT 배너');
  assert.ok(/<div class="alertbanner"><\/div>/.test(R.gongin_daily.html), 'gongin ALERT 빈값');
});

// ── 6. 결정론 ────────────────────────────────────────────────────
t('결정론: 같은 입력 + 같은 시드 → 같은 HTML', () => {
  const a = render('gongin', 'daily', '2026-09-10', { seed: 12345 });
  const b = render('gongin', 'daily', '2026-09-10', { seed: 12345 });
  assert.strictEqual(a.html, b.html, '같은 시드인데 결과가 다름');
  const c = render('gongin', 'daily', '2026-09-10', { seed: 999 });
  assert.notStrictEqual(a.html, c.html, '시드가 다른데 결과가 같음(시드 미반영 의심)');
  const d = render('gongin', 'daily', '2026-09-10');       // 기본 시드도 재현되어야
  assert.strictEqual(d.html, R.gongin_daily.html, '기본 시드 비결정적');
});

// ── 7. 부수 산출 ─────────────────────────────────────────────────
t('부수 산출: _장기복습_로그 갱신 · _push(gongin daily) · _runs.log', () => {
  const r = R.gongin_daily;
  const log = JSON.parse(fs.readFileSync(path.join(r.root, '공인중개사', '데일리퀴즈', '_장기복습_로그.json'), 'utf8'));
  const key = '2026-06-07-부동산세법-(부동산세법 취득세 기초).md';
  assert.strictEqual(log[key].last, '2026-09-10');
  assert.strictEqual(log[key].n, 1);
  const push = JSON.parse(fs.readFileSync(path.join(r.root, '공인중개사', '데일리퀴즈', '_push', '2026-09-10.json'), 'utf8'));
  assert.strictEqual(push.counts['한달전'], 3);
  assert.strictEqual(push.counts['장기복습'], 2);
  assert.strictEqual(push.counts['재도전'], 0);
  assert.strictEqual(push.monthlySrc, '2026-08-08~2026-08-14');
  assert.strictEqual(push.dueBacklog, 42);
  assert.strictEqual(push.ox.length, 3, 'push_ox 3문');
  assert.deepStrictEqual(push.longRevNotes, ['부동산세법 취득세 기초 (95일전)']);
  const runs = fs.readFileSync(path.join(r.root, '_시험엔진', '_runs.log'), 'utf8').trim().split('\n');
  const cols = runs[runs.length - 1].split('\t');
  assert.strictEqual(cols.length, 5, '_runs.log 5칼럼');
  assert.strictEqual(cols[3], 'OK');
  assert.ok(!fs.existsSync(path.join(R.gongin_retry.root, '공인중개사', '오답퀴즈', '_push')), 'retry는 push 없음');
});

// ── 8. 실패 경로 ─────────────────────────────────────────────────
t('실패 시: draft 저장 + exit 1 + _runs.log FAIL', () => {
  const bad = path.join(TMP, 'bad.questions.json');
  const doc = JSON.parse(fs.readFileSync(path.join(FIX, 'gongin_daily.questions.json'), 'utf8'));
  delete doc.questions[0].conceptKey;                       // 필수 필드 제거
  doc.questions[1].calc.expected = 99;                      // 계산 불일치
  fs.writeFileSync(bad, JSON.stringify(doc));
  const r = render('gongin', 'daily', '2026-09-10', { questions: bad });
  assert.strictEqual(r.code, 1, 'exit 1');
  assert.ok(!r.html, '실패했는데 최종 경로에 파일이 생김');
  assert.ok(/conceptKey/.test(r.stderr) && /calc\.expr/.test(r.stderr), '실패 항목 출력: ' + r.stderr);
  const draft = path.join(r.root, '공인중개사', '데일리퀴즈', '_work', '2026-09-10.draft.html');
  assert.ok(fs.existsSync(draft), 'draft 미저장');
  assert.ok(/conceptKey/.test(fs.readFileSync(draft, 'utf8')), 'draft에 실패 항목 없음');
  const runs = fs.readFileSync(path.join(r.root, '_시험엔진', '_runs.log'), 'utf8').trim().split('\n');
  assert.strictEqual(runs[runs.length - 1].split('\t')[3], 'FAIL');
});

t('실패 시: 조합 opt_size 불일치 · plan.date 불일치도 잡는다', () => {
  const bad = path.join(TMP, 'bad2.questions.json');
  const doc = JSON.parse(fs.readFileSync(path.join(FIX, 'bupsa1_daily.questions.json'), 'utf8'));
  doc.questions[2].items[2].truth = true;                   // 참 4개 → opt_size 3 위반
  fs.writeFileSync(bad, JSON.stringify(doc));
  const r = render('bupsa1', 'daily', '2026-09-10', { questions: bad });
  assert.strictEqual(r.code, 1);
  assert.ok(/opt_size/.test(r.stderr), r.stderr);
  const r2 = render('gongin', 'daily', '2026-09-12');       // plan.date=2026-09-10
  assert.strictEqual(r2.code, 1);
  assert.ok(/plan\.date 불일치/.test(r2.stderr), r2.stderr);
});

t('retry: conceptKey가 plan.picks에 없으면 실패', () => {
  const bad = path.join(TMP, 'bad3.questions.json');
  const doc = JSON.parse(fs.readFileSync(path.join(FIX, 'gongin_retry.questions.json'), 'utf8'));
  doc.questions[0].conceptKey = '없는 개념';
  fs.writeFileSync(bad, JSON.stringify(doc));
  const r = render('gongin', 'retry', '2026-09-11', { questions: bad });
  assert.strictEqual(r.code, 1);
  assert.ok(/plan\.picks에 없음/.test(r.stderr), r.stderr);
});

// ── 8-1. evidence(노트 원문 인용) 게이트 ─────────────────────────
t('evidence 통과: 노트 원문에 있는 quote → 렌더 성공 · HTML에는 evidence 미포함', () => {
  for (const key of ['gongin_daily', 'bupsa1_daily', 'bupsa2_daily', 'bupsa2_retry']) {
    assert.strictEqual(R[key].code, 0, key + ' exit=' + R[key].code + '\n' + R[key].stderr);
    assert.ok(!/evidence/.test(R[key].html), key + ': HTML에 evidence가 실렸다(비대화)');
    H.extractQuestions(R[key].html).forEach(q =>
      assert.ok(!('evidence' in q), key + ': QUESTIONS 항목에 evidence 잔존'));
  }
  // 픽스처 단답에는 실제로 evidence가 붙어 있다(게이트가 무력화된 통과가 아님을 보증)
  const src = JSON.parse(fs.readFileSync(path.join(FIX, 'bupsa2_daily.questions.json'), 'utf8'));
  assert.ok(src.questions.every(q => q.type !== '단답' || (q.evidence && q.evidence.quote)),
    '픽스처 단답에 evidence 없음 — 통과 테스트가 공회전');
});

t('evidence 실패: 노트에 없는 quote → 렌더 FAIL(문항·노트·quote 앞 40자 열거)', () => {
  const bad = path.join(TMP, 'bad-ev.questions.json');
  const doc = JSON.parse(fs.readFileSync(path.join(FIX, 'bupsa2_daily.questions.json'), 'utf8'));
  doc.questions[0].evidence.quote = '노트에 존재하지 않는 문장을 지어낸 인용이다 환각 게이트가 잡아야 한다';
  fs.writeFileSync(bad, JSON.stringify(doc));
  const r = render('bupsa2', 'daily', '2026-09-10', { questions: bad });
  assert.strictEqual(r.code, 1, 'exit 1');
  assert.ok(!r.html, '실패했는데 최종 경로에 파일이 생김');
  assert.ok(/노트 원문에 없음/.test(r.stderr), r.stderr.slice(0, 400));
  assert.ok(/형법 위법성조각사유/.test(r.stderr), '어느 노트인지 미출력: ' + r.stderr.slice(0, 400));
  assert.ok(/노트에 존재하지 않는 문장을/.test(r.stderr), 'quote 앞부분 미출력');
});

t('evidence 실패: daily 단답 evidence 누락 · quote 길이 미달 · 못 찾는 note', () => {
  const mk = (mut, name) => {
    const p = path.join(TMP, name);
    const doc = JSON.parse(fs.readFileSync(path.join(FIX, 'gongin_daily.questions.json'), 'utf8'));
    mut(doc);
    fs.writeFileSync(p, JSON.stringify(doc));
    return render('gongin', 'daily', '2026-09-10', { questions: p });
  };
  const r1 = mk(d => { delete d.questions[3].evidence; }, 'ev-missing.json');
  assert.strictEqual(r1.code, 1);
  assert.ok(/단답 evidence 누락/.test(r1.stderr), r1.stderr.slice(0, 300));

  const r2 = mk(d => { d.questions[3].evidence.quote = '수익가액'; }, 'ev-short.json');
  assert.strictEqual(r2.code, 1);
  assert.ok(/quote 길이/.test(r2.stderr), r2.stderr.slice(0, 300));

  const r3 = mk(d => { d.questions[3].evidence.note = '없는-노트.md'; }, 'ev-nonote.json');
  assert.strictEqual(r3.code, 1);
  assert.ok(/evidence\.note 를 찾지 못함/.test(r3.stderr), r3.stderr.slice(0, 300));
});

t('evidence(retry): note="samples"는 plan.picks[].samples 의 q·expl과 대조한다', () => {
  const bad = path.join(TMP, 'bad-ev-samples.questions.json');
  const doc = JSON.parse(fs.readFileSync(path.join(FIX, 'bupsa2_retry.questions.json'), 'utf8'));
  doc.questions[1].evidence.quote = '샘플 어디에도 없는 문장을 근거라고 우기는 인용이다 잡혀야 한다';
  fs.writeFileSync(bad, JSON.stringify(doc));
  const r = render('bupsa2', 'retry', '2026-09-11', { questions: bad });
  assert.strictEqual(r.code, 1);
  assert.ok(/samples\(q·expl\)에 없음/.test(r.stderr), r.stderr.slice(0, 400));
  // daily 문항에 note="samples"를 쓰면 그것도 실패
  const bad2 = path.join(TMP, 'bad-ev-samples2.questions.json');
  const d2 = JSON.parse(fs.readFileSync(path.join(FIX, 'bupsa2_daily.questions.json'), 'utf8'));
  d2.questions[0].evidence.note = 'samples';
  fs.writeFileSync(bad2, JSON.stringify(d2));
  const r2 = render('bupsa2', 'daily', '2026-09-10', { questions: bad2 });
  assert.strictEqual(r2.code, 1);
  assert.ok(/재도전 문항에서만/.test(r2.stderr), r2.stderr.slice(0, 300));
});

// ── 8-2. validate_quiz.js 연동 ───────────────────────────────────
t('⑦ validate_quiz.js가 실제로 호출되고, FAIL이면 최종 경로에 쓰지 않는다', () => {
  const r = render('gongin', 'daily', '2026-09-10', { validate: true });
  // 테스트 픽스처는 15문항(프로덕션 50문항 규격 미달)이라 검사기가 FAIL하는 것이 정상
  assert.strictEqual(r.code, 1, '검사기 FAIL인데 통과함');
  assert.ok(/validate_quiz\.js 실패/.test(r.stderr), '검사기 미호출 의심: ' + r.stderr.slice(0, 200));
  assert.ok(/FAIL — 문항 수 50/.test(r.stderr), '검사기 출력 전달 안 됨');
  assert.ok(!r.html, 'FAIL인데 최종 경로에 파일이 생김');
  assert.ok(!fs.existsSync(path.join(r.root, '공인중개사', '데일리퀴즈', '_work', '2026-09-10.render.tmp.html')),
    'tmp 파일이 남음');
  assert.ok(fs.existsSync(path.join(r.root, '공인중개사', '데일리퀴즈', '_work', '2026-09-10.draft.html')));
});

t('validate_quiz.js가 없으면 렌더를 중단한다 (무검증 문제지 금지 — 2026-09-02 정책)', () => {
  const eng = path.join(TMP, 'engine-noval');
  fs.mkdirSync(eng, { recursive: true });
  for (const f of ['render_quiz.py', 'exams.json', 'quiz_template.html']) {
    fs.copyFileSync(path.join(H.ENGINE, f), path.join(eng, f));
  }
  const r = render('gongin', 'daily', '2026-09-10', { cwd: eng, validate: true });
  assert.notStrictEqual(r.code, 0, '검사기 부재인데 성공 종료');
  assert.ok(/validate_quiz\.js 부재/.test(r.stdout + r.stderr), r.stdout + r.stderr);
  assert.ok(!r.html, '검사기 없이 최종 산출이 생김');
});

// ── 9. 렌더 결과가 실제로 채점되는가 ─────────────────────────────
t('렌더 산출 HTML이 jsdom에서 채점·payload 생성까지 동작', () => {
  const qs = H.extractQuestions(R.gongin_daily.html);
  const { win } = H.boot(R.gongin_daily.html);
  const p = H.runGenericScenario(win, qs);
  assert.strictEqual(p.total, qs.length);
  assert.strictEqual(p.subject, '공인중개사');
  assert.strictEqual(p.quizId, '2026-09-10');
  assert.ok(p.results.every(r => !('exam' in r)), 'gongin exam 키 없음');
  win.close();
  const b2 = H.extractQuestions(R.bupsa2_daily.html);
  const { win: w2 } = H.boot(R.bupsa2_daily.html);
  const p2 = H.runGenericScenario(w2, b2);
  assert.strictEqual(p2.subject, '법무사2차');
  assert.ok(p2.results.every(r => r.exam === '2차'), 'bupsa2 exam=2차');
  assert.ok(p2.results.every(r => r.selfGraded === true), '2차는 전부 단답');
  w2.close();
});

// ── 10. 실제 데이터 스모크 ───────────────────────────────────────
t('실제 데이터 스모크: 2026-09-01 원본 vs 새 템플릿 재렌더 채점 payload 동일(기대 차이 monthlyOf)', () => {
  const src = path.join(H.ROOT, '공인중개사', '데일리퀴즈', '2026-09-01.html');
  const orig = fs.readFileSync(src, 'utf8');
  const qs = H.extractQuestions(orig);
  assert.ok(qs.length >= 45, '원본 문항 ' + qs.length);

  const { win: w1 } = H.boot(orig);
  const pOrig = H.runGenericScenario(w1, qs); w1.close();

  const fresh = H.injectQuestions(H.renderUnified('gongin', 'daily', '2026-09-01'), qs);
  const { win: w2 } = H.boot(fresh);
  const pNew = H.runGenericScenario(w2, qs); w2.close();

  const paths = H.diffPaths(pOrig, pNew);
  assert.deepStrictEqual(H.diffFields(paths), ['monthlyOf'],
    '차이:\n' + paths.slice(0, 12).map(x => '  - ' + x).join('\n'));
  assert.strictEqual(pOrig.score, pNew.score, 'score');
  assert.strictEqual(pOrig.wrongCount, pNew.wrongCount, 'wrongCount');
  assert.strictEqual(paths.length, 10, '한달전 10문항의 monthlyOf만 차이');
});

for (const [label, rel, exam, kind, date, expect] of [
  ['법무사 2차 데일리', ['법무사', '2차', '데일리퀴즈', '2026-08-31.html'], 'bupsa2', 'daily', '2026-08-31', []],
  ['공인중개사 오답', ['공인중개사', '오답퀴즈', '2026-09-02.html'], 'gongin', 'retry', '2026-09-02', []],
  ['법무사 2차 오답', ['법무사', '2차', '오답퀴즈', '2026-09-01.html'], 'bupsa2', 'retry', '2026-09-01', []],
]) {
  t(`실제 데이터 스모크: ${label} 원본(${date}) 재렌더 채점 payload 동일`, () => {
    const orig = fs.readFileSync(path.join(H.ROOT, ...rel), 'utf8');
    const qs = H.extractQuestions(orig);
    const { win: w1 } = H.boot(orig);
    const p1 = H.runGenericScenario(w1, qs); w1.close();
    const { win: w2 } = H.boot(H.injectQuestions(H.renderUnified(exam, kind, date), qs));
    const p2 = H.runGenericScenario(w2, qs); w2.close();
    const paths = H.diffPaths(p1, p2);
    assert.deepStrictEqual(H.diffFields(paths), expect,
      '차이:\n' + paths.slice(0, 10).map(x => '  - ' + x).join('\n'));
  });
}

console.log(out.join('\n'));
console.log(`[render] ${pass} passed, ${fail} failed`);
try { fs.rmSync(TMP, { recursive: true, force: true }); } catch (e) { /* noop */ }
process.exit(fail ? 1 : 0);
