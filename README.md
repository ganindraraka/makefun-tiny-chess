# makefun-tiny-chess

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/ganindraraka/makefun-tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/ganindraraka/makefun-tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A tiny chess engine for the [make.fun **tiny-chess-01** bounty](https://make.fun/bounty/tiny-chess-01):
the strongest chess engine that fits in 4 KB of Python.

## How it plays

`main.py` is a self-contained chess engine that talks to the grading environment over HTTP:

- Read `MAKEFUN_ENV_URL`, `POST <base>/game` to get a position, then loop: on `status == "your_move"`
  compute a move and `POST <base>/move` with `{"game": ..., "move": "<uci>"}`.

Its search is an iterative-deepening negamax with alpha-beta pruning. It keeps the best move from
the last fully completed depth and stops on a node cap or wall-clock deadline. At the leaves it runs
a capture-only quiescence search so it does not blunder on the horizon.

- **Null-move pruning:** in non-check nodes at depth 3 or more (and with enough material left), it
  gives the opponent a free move and searches with a reduced depth; if the resulting score still
  fails high, the node is cut off.
- **Futility pruning:** at depth 2 or less, if the static evaluation plus a depth-scaled margin is
  already below alpha, quiet moves are discarded and the static score is returned.
- **Late-move reductions (LMR):** late quiet, non-capture moves in non-check nodes at depth 3 or
  more are searched one ply shallower, then re-searched at full depth if they beat alpha.
- **Move ordering:** the previous iteration's best move first, then MVV-LVA captures and promotions,
  then **killer moves**, then the history heuristic.
- **Transposition table:** positions are cached by board, side, castling and en-passant key, with
  depth, score, bound flag and best move, subject to repetition and 50-move safeguards.
- **Evaluation:** material, piece-square tables, the bishop pair, rook activity, pawn structure and
  mobility.

The readable source lives in `engine_src.py` (kept out of the commit) and is packed into `main.py`
byte-for-byte with the kit's own `makefun compress`.

## Performance

On the reference box the search settles around 8,000-10,500 nodes/second depending on the position.
Each move has a ~2.5 s budget and a hard cap of 50,000 nodes; the clock is deliberately short so a
full 6-game match fits inside the grading wall clock.

## Run it locally

```
MAKEFUN_ENV_URL=http://127.0.0.1:PORT python3 main.py
```

## Built by

An autonomous coding agent session (Codex), on a remote box, for the make.fun tiny-chess-01 bounty:
<https://make.fun/bounty/tiny-chess-01>.

## License

MIT — see [LICENSE](LICENSE).
