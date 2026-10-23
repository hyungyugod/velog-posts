# -*- coding: utf-8 -*-
"""data_*.py 편집 도구 — I(...) 호출을 첫 인자 접두로 찾아 통째로 바꾼다(정확히 1개일 때만)."""
import ast


def _line_starts(b):
    starts = [0]
    for i, ch in enumerate(b):
        if ch == 0x0A:
            starts.append(i + 1)
    return starts


def find_call(fn, prefix):
    src = open(fn, encoding="utf-8").read()
    tree = ast.parse(src)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "I" and node.args \
                and isinstance(node.args[0], ast.Constant) and node.args[0].value.startswith(prefix):
            hits.append(node)
    return src, hits


def replace_call(fn, prefix, new_src):
    src, hits = find_call(fn, prefix)
    assert len(hits) == 1, (fn, prefix, len(hits))
    n = hits[0]
    b = src.encode("utf-8")
    ls = _line_starts(b)
    s = ls[n.lineno - 1] + n.col_offset
    e = ls[n.end_lineno - 1] + n.end_col_offset
    if new_src == "":
        # 줄 전체 삭제: 앞 들여쓰기 ~ 뒤 ",\n"
        s0 = ls[n.lineno - 1]
        e0 = e
        if b[e0:e0 + 2] == b",\n":
            e0 += 2
        nb = b[:s0] + b[e0:]
    else:
        nb = b[:s] + new_src.encode("utf-8") + b[e:]
    out = nb.decode("utf-8")
    compile(out, fn, "exec")
    open(fn, "w", encoding="utf-8").write(out)


def insert_after(fn, prefix, new_src):
    """prefix로 찾은 I(...) 호출 뒤(같은 들여쓰기 새 줄)에 new_src 호출을 넣는다."""
    src, hits = find_call(fn, prefix)
    assert len(hits) == 1, (fn, prefix, len(hits))
    n = hits[0]
    b = src.encode("utf-8")
    ls = _line_starts(b)
    e = ls[n.end_lineno - 1] + n.end_col_offset
    assert b[e:e + 2] == b",\n", b[e:e + 10]
    indent = b" " * n.col_offset
    nb = b[:e + 2] + indent + new_src.encode("utf-8") + b",\n" + b[e + 2:]
    out = nb.decode("utf-8")
    compile(out, fn, "exec")
    open(fn, "w", encoding="utf-8").write(out)


def sreplace(fn, old, new):
    s = open(fn, encoding="utf-8").read()
    c = s.count(old)
    assert c == 1, (fn, c, old[:80])
    s = s.replace(old, new)
    compile(s, fn, "exec")
    open(fn, "w", encoding="utf-8").write(s)
