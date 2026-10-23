# -*- coding: utf-8 -*-
"""특별판 데이터 DSL — 정리본·TSV·검수리포트의 단일 원천."""

CHAPTERS = []


class Item:
    def __init__(self, text, src, ex=None, trap=None, mem=None, why=None, chip=False, extra_src=None):
        self.text = text          # {정답} 또는 {정답::힌트} 가 빈칸
        self.src = src            # ["0930:7", ...] — 카드·정리본이 기대는 원문 줄
        self.ex = ex              # 예) — 원문 노트의 예) 줄 (뒷면)
        self.trap = trap          # 함정 — 원문 줄 (뒷면)
        self.mem = mem            # 기억(두문자 등) — 원문 줄 (뒷면)
        self.why = why            # 왜 — 원문 줄 (뒷면)
        self.chip = chip          # 현행 기준 확인 칩
        self.extra_src = extra_src or []   # 뒷면 칸의 원천 줄


class Sub:
    def __init__(self, title, items, card=True):
        self.title = title
        self.items = items
        self.card = card


class Sec:
    def __init__(self, no, title, tip, subs):
        self.no, self.title, self.tip, self.subs = no, title, tip, subs


class Chap:
    def __init__(self, no, title, short, part, secs):
        self.no, self.title, self.short, self.part, self.secs = no, title, short, part, secs


def C(no, title, short, part, secs):
    ch = Chap(no, title, short, part, secs)
    CHAPTERS.append(ch)
    return ch


S = Sec
U = Sub
I = Item
