#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오답 누적 원장 빌더 v2 — 닫힌 루프(상태머신 + 간격반복)  · 2026-07-02 (Fable 설계 WO-5)

v1과 달라진 것:
- 결과 JSON schemaVersion 2의 results[](전 문항 정오 기록)를 소화한다.
  → '재도전을 맞혔는지'가 기록되므로 개념의 '졸업'을 확정할 수 있다.
- 개념 상태머신: 재도전중 → 졸업후보(연속정답 2) → 졸업(연속정답 3) / 상습(반복 오답·재도전 실패)
- 간격 사다리 [3, 7, 16, 35]일로 nextReviewDate를 발급하고,
  복습 기한이 온 개념을 dueQueue로 내보낸다(퀴즈 생성 스킬이 재도전 5~8문항의 원천으로 사용).
- 하위호환: schemaVersion 없는 v1 파일은 종전대로 wrong[]만 소화.

유지된 원칙(v1): 비파괴(어떤 파일도 삭제·이동 안 함) · 멱등(매번 전체 재생성) ·
무음실패 불가(원천 0건이면 exit 2로 크게 알림).

사용:  python3 build_ledger.py            (원장 재생성)
       python3 build_ledger.py --ingest  (추가로 _inbox JSON을 _raw로 복사·보존)

[상태머신 규칙]
  오답 발생             -> consecutiveCorrect=0, 다음 복습 +3일
  재도전 정답           -> consecutiveCorrect+1, 다음 복습 = 7 -> 16 -> 35일
  consecutiveCorrect=2  -> 졸업후보 (16일 뒤 마지막 확인 1회)
  consecutiveCorrect>=3 -> 졸업 (듀 큐에서 제외, 시험 전 총복습 리스트엔 포함)
  (미졸업) timesWrong>=2 또는 retryMissed>=1 -> 상습 = 출제 최우선
"""
import json, glob, os, re, sys, datetime, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)                      # claude_ox_오답/
RAW  = os.path.join(BASE, "_raw")
INBOX= os.path.join(BASE, "_inbox")
LADDER = [3, 7, 16, 35]                           # 오답 직후 / 정답 1·2·3회 후 간격(일)

def find_jsons():
    seen = {}
    for d in (RAW, INBOX):
        for f in glob.glob(os.path.join(d, "공인중개사_오답_*.json")):
            base = re.sub(r" \(\d+\)(?=\.json$)", "", os.path.basename(f))
            if base not in seen or os.path.getmtime(f) > os.path.getmtime(seen[base]):
                seen[base] = f
    return list(seen.values())

def dedate(s):  return re.sub(r"^\s*\d{4}-\d{2}-\d{2}\s*", "", s or "").strip()
def deretry(s): return re.sub(r"\s*\(재도전\)\s*$", "", s or "").strip()
def concept_label(src): return deretry(dedate(src))
def norm(s): return re.sub(r"\s+", " ", s or "").strip()
def canon(s): return re.sub(r"[\s/]+", "", norm(s))
def date_prefix(s):
    m = re.match(r"\d{4}-\d{2}-\d{2}", s or "")
    return m.group(0) if m else None

def new_rec(subject, label):
    return {"conceptKey": label, "aliases": [], "subject": subject, "concept": label,
            "status": "재도전중", "timesWrong": 0, "retryMissed": 0, "consecutiveCorrect": 0,
            "firstWrong": None, "lastWrong": None, "lastCorrect": None,
            "lastResult": None, "lastDp": None, "nextReviewDate": None,
            "dates": [], "samples": []}

def main():
    ingest = "--ingest" in sys.argv
    files = find_jsons()
    if not files:
        print("⚠️  접근 실패/0건 — _raw 와 _inbox 에서 채점결과 JSON을 찾지 못했다.")
        print("    (조용히 넘어가지 않는다. 퀴즈 결과 JSON을 _inbox/ 에 넣고 다시 실행.)")
        sys.exit(2)

    if ingest:
        os.makedirs(RAW, exist_ok=True)
        for f in glob.glob(os.path.join(INBOX, "공인중개사_오답_*.json")):
            dst = os.path.join(RAW, os.path.basename(f))
            if not os.path.exists(dst):
                shutil.copy2(f, dst); print("  ↳ 보존:", os.path.basename(f))

    # 1) 파일 -> 시간순 이벤트 스트림
    events = []
    subs = score_sum = tot_sum = perfect = v2files = 0
    dps_all = set()
    for f in sorted(files, key=lambda p: os.path.basename(p)):
        fname = os.path.basename(f)
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print("PARSE FAIL", fname, e); continue
        subs += 1; score_sum += d.get("score", 0); tot_sum += d.get("total", 0)
        if d.get("wrongCount") == 0: perfect += 1
        date_raw = str(d.get("date") or "")
        dp = date_prefix(date_raw) or date_prefix(fname.replace("공인중개사_오답_", "")) or "0000-00-00"
        dps_all.add(dp)
        sv = d.get("schemaVersion", 1)
        if sv >= 2 and isinstance(d.get("results"), list):
            v2files += 1
            for r in d["results"]:
                label = deretry(dedate(str(r.get("conceptKey") or ""))) or concept_label(r.get("src", ""))
                label = norm(label) or norm(str(r.get("cat", "")) + " " + str(r.get("q", ""))[:20])
                retry = bool(r.get("retryOf")) or "(재도전)" in str(r.get("src", ""))
                if r.get("correctAnswered") is False:
                    events.append((dp, fname, "w", canon(label), label, r.get("cat"), date_raw, retry, r))
                elif r.get("correctAnswered") is True and retry:
                    events.append((dp, fname, "c", canon(label), label, r.get("cat"), date_raw, retry, None))
        else:
            for w in d.get("wrong", []):
                label = concept_label(w.get("src", ""))
                label = norm(label) or norm(str(w.get("cat", "")) + " " + str(w.get("q", ""))[:20])
                retry = "(재도전)" in str(w.get("src", ""))
                events.append((dp, fname, "w", canon(label), label, w.get("cat"), date_raw, retry, w))

    # 2) 리플레이: 개념 레코드 갱신
    ledger, subj_wrong = {}, {}
    for dp, fname, kind, ckey, label, subject, date_raw, retry, sample in sorted(events, key=lambda e: (e[0], e[1])):
        r = ledger.setdefault(ckey, new_rec(subject, label))
        if label != r["concept"] and label not in r["aliases"]:
            r["aliases"].append(label)
        if kind == "w":
            r["timesWrong"] += 1
            r["consecutiveCorrect"] = 0
            if retry: r["retryMissed"] += 1
            r["dates"].append(date_raw or dp)
            r["firstWrong"] = r["firstWrong"] or (date_raw or dp)
            r["lastWrong"] = date_raw or dp
            r["lastResult"] = "wrong"; r["lastDp"] = dp
            subj_wrong[subject] = subj_wrong.get(subject, 0) + 1
            if sample is not None and len(r["samples"]) < 3:
                r["samples"].append({"date": date_raw or dp, "type": sample.get("type"), "q": sample.get("q"),
                                     "myAnswer": sample.get("myAnswer"), "correct": sample.get("correct"),
                                     "expl": sample.get("expl")})
        else:
            r["consecutiveCorrect"] += 1
            r["lastCorrect"] = date_raw or dp
            r["lastResult"] = "correct"; r["lastDp"] = dp

    # 3) 상태·다음 복습일 판정
    for r in ledger.values():
        cc = r["consecutiveCorrect"]
        if cc >= 3:
            r["status"] = "졸업"
        elif cc == 2:
            r["status"] = "졸업후보"
        elif r["retryMissed"] > 0 or r["timesWrong"] >= 2:
            r["status"] = "상습"
        else:
            r["status"] = "재도전중"
        try:
            base = datetime.date.fromisoformat(r["lastDp"])
            delta = LADDER[0] if r["lastResult"] == "wrong" else LADDER[min(cc, 3)]
            r["nextReviewDate"] = (base + datetime.timedelta(days=delta)).isoformat()
        except Exception:
            r["nextReviewDate"] = None

    prio = {"상습": 0, "재도전중": 1, "졸업후보": 2, "졸업": 3}
    recs = sorted(ledger.values(), key=lambda r: (prio[r["status"]], -r["retryMissed"], -r["timesWrong"], r["nextReviewDate"] or "9999"))

    # 4) 듀 큐 (퀴즈 생성이 소비)
    today = datetime.date.today().isoformat()
    due = [r for r in recs if r["status"] != "졸업" and r["nextReviewDate"] and r["nextReviewDate"] <= today]
    dueQueue = [{"conceptKey": r["conceptKey"], "subject": r["subject"], "status": r["status"],
                 "timesWrong": r["timesWrong"], "retryMissed": r["retryMissed"],
                 "consecutiveCorrect": r["consecutiveCorrect"],
                 "lastWrong": r["lastWrong"], "nextReviewDate": r["nextReviewDate"]} for r in due]

    status_counts = {}
    for r in recs:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    out = {"ledgerSchema": 2,
           "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
           "sourceFiles": len(files), "v2Files": v2files, "submissions": subs,
           "avgScore": round(score_sum/subs, 1) if subs else None,
           "avgTotal": round(tot_sum/subs) if subs else None, "perfectRuns": perfect,
           "totalWrongItems": sum(r["timesWrong"] for r in recs),
           "uniqueConcepts": len(recs),
           "dateRange": [min(dps_all), max(dps_all)] if dps_all else None,
           "statusCounts": status_counts,
           "subjectWeakness": dict(sorted(subj_wrong.items(), key=lambda x: -x[1])),
           "dueQueue": dueQueue, "ledger": recs}
    json.dump(out, open(os.path.join(HERE, "오답_원장.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # 5) 사람이 읽는 원장(.md)
    L = []
    L.append(f"# 📒 공인중개사 오답 누적 원장 v2  ·  갱신 {out['generatedAt']}")
    L.append("")
    L.append(f"> 기간 {out['dateRange'][0]} ~ {out['dateRange'][1]} · 제출 {subs}회 · 평균 {out['avgScore']}/{out['avgTotal']} · 만점 {perfect}회")
    L.append(f"> 누적 오답 {out['totalWrongItems']}건 · 고유 개념 {out['uniqueConcepts']}개 · 원천 JSON {len(files)}개 (v2 스키마 {v2files}개)")
    L.append(f"> 상태: " + " · ".join(f"{k} {v}" for k, v in status_counts.items()))
    L.append(">")
    if v2files == 0:
        L.append("> ⚠️ 아직 전부 v1 결과(오답만 기록)라 '졸업'은 발생할 수 없다. v2 템플릿(_template.html)으로")
        L.append(">  생성된 퀴즈를 제출하는 시점부터 재도전 정답이 기록되어 졸업이 굴러가기 시작한다.")
        L.append(">")
    L.append(f"## 🗓️ 오늘의 복습 큐 (due — 퀴즈 생성이 여기서 재도전 5~8개를 뽑는다) · {len(dueQueue)}개")
    L.append("")
    if dueQueue:
        L.append("| 우선 | 과목 | 개념 | 상태 | 틀림 | 재도전실패 | 연속정답 | 복습예정일 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for i, q in enumerate(dueQueue, 1):
            L.append(f"| {i} | {q['subject']} | {q['conceptKey']} | {q['status']} | {q['timesWrong']} | {q['retryMissed']} | {q['consecutiveCorrect']} | {q['nextReviewDate']} |")
    else:
        L.append("_오늘 복습 기한이 된 개념 없음_")
    L.append("")
    sections = [("## 🔴 상습 (재도전 실패·반복 오답 — 최우선)", "상습"),
                ("## 🟠 재도전중", "재도전중"),
                ("## 🟡 졸업후보 (연속정답 2 — 마지막 확인 대기)", "졸업후보"),
                ("## 🎓 졸업 (연속정답 3 — 듀 큐 제외, 총복습엔 포함)", "졸업")]
    for title, st in sections:
        L.append(title); L.append("")
        rows = [r for r in recs if r["status"] == st]
        if not rows:
            L.append("_해당 없음_"); L.append(""); continue
        L.append("| 과목 | 개념 | 틀림 | 재도전실패 | 연속정답 | 최근오답 | 최근정답 | 다음복습 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in rows:
            L.append(f"| {r['subject']} | {r['concept']} | {r['timesWrong']} | {r['retryMissed']} | {r['consecutiveCorrect']} | {r['lastWrong'] or '—'} | {r['lastCorrect'] or '—'} | {r['nextReviewDate'] or '—'} |")
        L.append("")
    L.append("## 📊 과목별 약점 (누적 오답 수)")
    L.append("")
    L.append("| 과목 | 오답 |")
    L.append("|---|---|")
    for k, v in out["subjectWeakness"].items():
        L.append(f"| {k} | {v} |")
    L.append("")
    open(os.path.join(HERE, "오답_원장.md"), "w", encoding="utf-8").write("\n".join(L))

    print("✅ 원장 v2 재생성 완료")
    print(f"   원천 {len(files)}개(v2: {v2files}) · 제출 {subs}회 · 누적 오답 {out['totalWrongItems']}건 · 개념 {len(recs)}개")
    print(f"   상태: " + " · ".join(f"{k} {v}" for k, v in status_counts.items()))
    print(f"   🗓️ 듀 큐 {len(dueQueue)}개: " + (", ".join(f"{q['conceptKey']}({q['status']})" for q in dueQueue[:6]) or "없음"))
    print(f"   과목별 약점 TOP3: " + ", ".join(f"{k}({v})" for k, v in list(out['subjectWeakness'].items())[:3]))

if __name__ == "__main__":
    main()
