#!/usr/bin/env python3
"""In-process head-to-head: engine A vs engine B (both our engines).
Much faster than driving a subprocess, and deterministic.

Usage: duel.py <A.py> <B.py> [ngames] [movetime]
A plays white on even games.
"""
import sys, time, subprocess, os
import chess

A = sys.argv[1]; B = sys.argv[2]
NG = int(sys.argv[3]) if len(sys.argv) > 3 else 2
MT = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0

def load(path):
    src = open(path).read().split("if __name__")[0]
    ns = {}
    exec(src, ns)
    return ns

EA, EB = load(A), load(B)

def pick(E, fen, allowed, mt):
    E['nodes'] = 0
    E['deadline'] = time.monotonic() + mt
    E['seen'] = {}
    E['TT'] = {}
    E['kill'] = {}
    E['history'] = {}
    return E['choose'](fen, allowed)

OPENINGS = [
    ['e2e4','e7e5','g1f3','b8c6','f1b5','a7a6','b5a4','g8f6'],
    ['d2d4','d7d5','c2c4','e7e6','b1c3','g8f6','c4d5','e6d5'],
    ['e2e4','c7c5','g1f3','d7d6','d2d4','c5d4','f3d4','g8f6'],
    ['d2d4','g8f6','c2c4','g7g6','b1c3','f8g7','e2e4','d7d6'],
]

res = {'A': 0, 'B': 0, 'draw': 0}
t0 = time.time()
for g in range(NG):
    b = chess.Board()
    for m in OPENINGS[g % len(OPENINGS)]:
        b.push_uci(m)
    A_white = (g % 2 == 0)
    while not b.is_game_over(claim_draw=True):
        turn_white = (b.turn == chess.WHITE)
        eng = EA if (turn_white == A_white) else EB
        legal = [m.uci() for m in b.legal_moves]
        try:
            mv = pick(eng, b.fen(), legal, MT)
        except Exception as e:
            print(f"  crash ({e}); other side wins")
            mv = None
        if mv is None or mv not in legal:
            res['B' if eng is EA else 'A'] += 1
            print(f"game {g+1}: ILLEGAL move -> loss", flush=True)
            break
        b.push_uci(mv)
    else:
        r = b.result(claim_draw=True)
        if r == '1-0':
            res['A' if A_white else 'B'] += 1
        elif r == '0-1':
            res['B' if A_white else 'A'] += 1
        else:
            res['draw'] += 1
    print(f"game {g+1}: A={'white' if A_white else 'black'} "
          f"{b.result(claim_draw=True)} ({len(b.move_stack)} plies)  A={res['A']} B={res['B']} ={res['draw']}",
          flush=True)

print(f"\nA={os.path.basename(A)} wins {res['A']}, B={os.path.basename(B)} wins {res['B']}, draws {res['draw']}  ({time.time()-t0:.0f}s)")
