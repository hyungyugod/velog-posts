import sys
def patch(fn, pairs):
    s = open(fn, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:90], s.count(old))
        s = s.replace(old, new)
    open(fn, "w", encoding="utf-8").write(s)
