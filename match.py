#!/usr/bin/env python3
"""Head-to-head match runner: our engine vs. the house sunfish-4k baseline.

Our engine speaks the make.fun env protocol over HTTP, but for LOCAL matches we
wrap it as a UCI-ish engine by importing its source and calling choose(fen,
legal).  Sunfish runs as its own UCI subprocess (pst_entry.py).

Usage: match.py <our_engine.py> <n_games> [sunfish_nodes]
The house baseline searches 50,000 nodes a move.
"""
import sys, os, subprocess, time
import chess

OUR = sys.argv[1] if len(sys.argv) > 1 else '/tmp/engine_v2.py'
NGAMES = int(sys.argv[2]) if len(sys.argv) > 2 else 6
SUN_NODES = int(sys.argv[3]) if len(sys.argv) > 3 else 50000
SUNFISH = '/tmp/sunfish/nnue_4k/pst_entry.py'

src = open(OUR).read().split("if __name__")[0]
ns = {}
exec(src, ns)
our_choose, our_parse, our_uci, our_moves = ns['choose'], ns['parse'], ns['uci'], ns['moves']


class Sunfish:
    def __init__(self):
        self.p = subprocess.Popen(['python3', SUNFISH], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1)
        self._send('uci'); self._read_until('uciok')
        self._send(f'setoption name TableMemory value {SUN_NODES}')

    def _send(self, s):
        self.p.stdin.write(s + '\n'); self.p.stdin.flush()

    def _read_until(self, tok):
        while True:
            line = self.p.stdout.readline()
            if not line:
                return None
            if line.strip() == tok or tok in line:
                return line

    def best(self, moves_uci):
        self._send('position startpos moves' + (' ' + ' '.join(moves_uci) if moves_uci else ''))
        self._send('go nodes %d' % SUN_NODES)
        while True:
            line = self.p.stdout.readline()
            if not line:
                return None
            if line.startswith('bestmove'):
                return line.split()[1]
            if line.startswith('info') and 'nodes' in line:
                # sunfish aborts at the node cap via info string
                pass


def our_best(fen, legal_uci):
    return our_choose(fen, legal_uci)


def play_game(sun, our_is_white, opening_uci=None):
    board = chess.Board()
    if opening_uci:
        for m in opening_uci:
            board.push_uci(m)
    while not board.is_game_over(claim_draw=True):
        if board.is_game_over(claim_draw=True):
            break
        turn_white = (board.turn == chess.WHITE)
        # our engine moves on its colour; sunfish on the other
        if turn_white == our_is_white:
            legal = [m.uci() for m in board.legal_moves]
            mv = our_best(board.fen(), legal)
            if mv is None:
                return 'loss', board
            board.push_uci(mv)
        else:
            moves_uci = [m.uci() for m in board.move_stack]
            mv = sun.best(moves_uci)
            if mv is None:
                return 'win', board
            board.push_uci(mv)
        if board.can_claim_fifty_moves() or board.is_repetition(3):
            break
    r = board.result(claim_draw=True)
    if r == '1-0':
        return ('win' if our_is_white else 'loss'), board
    if r == '0-1':
        return ('loss' if our_is_white else 'win'), board
    return 'draw', board


# A few well-known openings (8 plies each) so games differ.
OPENINGS = [
    ['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5a4', 'g8f6'],
    ['d2d4', 'd7d5', 'c2c4', 'e7e6', 'b1c3', 'g8f6', 'c4d5', 'e6d5'],
    ['e2e4', 'c7c5', 'g1f3', 'd7d6', 'd2d4', 'c5d4', 'f3d4', 'g8f6'],
    ['d2d4', 'g8f6', 'c2c4', 'g7g6', 'b1c3', 'f8g7', 'e2e4', 'd7d6'],
    ['e2e4', 'e7e6', 'd2d4', 'd7d5', 'b1c3', 'g8f6', 'e4e5', 'f6d7'],
    ['g1f3', 'd7d5', 'g2g3', 'g8f6', 'f1g2', 'e7e6', 'e1g1', 'f8e7'],
    ['e2e4', 'e7e5', 'g1f3', 'g8f6', 'f3e5', 'd7d6', 'e5f3', 'f6e4'],
    ['d2d4', 'd7d5', 'g1f3', 'g8f6', 'c2c4', 'e7e6', 'b1c3', 'f8e7'],
]

res = {'win': 0, 'loss': 0, 'draw': 0}
t0 = time.time()
for g in range(NGAMES):
    our_is_white = (g % 2 == 0)
    op = OPENINGS[g % len(OPENINGS)]
    sun = Sunfish()
    outcome, board = play_game(sun, our_is_white, op)
    sun.p.terminate()
    res[outcome] += 1
    print(f"game {g+1}: our={'white' if our_is_white else 'black':5} {outcome:5} "
          f"in {len(board.move_stack)} plies  ({res})", flush=True)

pts = res['win'] + 0.5 * res['draw']
print(f"\nTOTAL: +{res['win']} ={res['draw']} -{res['loss']}  score {pts}/{NGAMES} "
      f"({pts/NGAMES*100:.0f}%)  {time.time()-t0:.0f}s")
