import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
d = json.load(open(f"{HERE}/카드메타_2026-10-19.json", encoding="utf-8"))
cards = d["cards"]
for i, c in enumerate(cards, 1): c["no"] = i
FOLDER = {"B": "법무사"}
G = {"G1": lambda c: c["note"] in ("G", "N4", "P", "N5"),
     "G2": lambda c: c["note"] in ("N1", "N2", "K1", "K2"),
     "G3": lambda c: c["note"] in ("N3", "J", "S"),
     "G4": lambda c: c["lane"] == "구노트",
     "G5": lambda c: c["note"] == "B"}
for g, fn in G.items():
    sel = [c for c in cards if fn(c)]
    srcs = sorted(set((FOLDER.get(c["note"], "공인중개사"), c["src"]) for c in sel))
    out = [f"# 검증 입력 {g} — 2026-10-19 정규 덱 ({len(sel)}행 · {sum(c['ncards'] for c in sel)}장)\n"]
    out.append("## A. 원문 정리본 (줄 번호 = 카드의 lines)\n")
    for folder, s in srcs:
        lines = open(f"{ROOT}/{folder}/{s}", encoding="utf-8").read().split("\n")
        used = sorted(set(n for c in sel if c["src"] == s for n in c["lines"]))
        if any(c["lane"] == "구노트" and c["src"] == s for c in sel):
            keep = sorted(set(k for n in used for k in range(max(1, n - 3), min(len(lines), n + 3) + 1)))
            tail = [k for k in range(1, len(lines) + 1) if re.search(r"확인 필요", lines[k-1])]
            keep = sorted(set(keep) | set(k for t in tail for k in range(t, min(len(lines), t + 12) + 1)))
            out.append(f"### {folder}/{s} (구노트 — 인용 줄 ±3 + 하단 확인 필요 섹션)\n```")
            prev = 0
            for k in keep:
                if k != prev + 1: out.append("   …")
                out.append(f"{k:4d}\t{lines[k-1]}"); prev = k
        else:
            out.append(f"### {folder}/{s} (전문)\n```")
            out += [f"{k:4d}\t{t}" for k, t in enumerate(lines, 1)]
        out.append("```\n")
    out.append("## B. 카드 (TSV 사본 — `<style>…</style>`는 `<style/>`로 치환. 앞면의 `{{cN::답}}`이 빈칸)\n")
    for c in sel:
        back = re.sub(r"<style>.*?</style>", "<style/>", c["back"]); front = re.sub(r"<style>.*?</style>", "<style/>", c["front"])
        out.append(f"### #{c['no']} · key `{c['key']}` · {c['kind']} · 레인 {c['lane']} · 원문 {c['src'][:10]} L{','.join(map(str,c['lines']))}\n- 앞면: {front}\n- 뒷면: {back or '(비어 있음)'}\n- 도식 원천: {c['dsrc'] or '—'}\n")
    open(f"{HERE}/검증입력_{g}_2026-10-19.md", "w", encoding="utf-8").write("\n".join(out))
    print(g, len(sel), sum(c['ncards'] for c in sel))
