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
- Search: iterative-deepening negamax with alpha-beta, a fixed node budget, and a wall-clock safety
  cap. It keeps the best move from the last **fully completed** depth.
- Quiescence search on captures at the leaves, so it does not blunder on the horizon.
- Move ordering: MVV-LVA captures, then killer moves, then the history heuristic.
- A transposition table keyed on the position, plus draw awareness (repetition and the 50-move rule).
- Evaluation: material, piece-square tables, the bishop pair, rook activity, pawn structure and mobility.

The readable source lives in `engine_src.py` (kept out of the commit) and is packed into `main.py`
byte-for-byte with the kit's own `makefun compress`.

## Run it locally

```
MAKEFUN_ENV_URL=http://127.0.0.1:PORT python3 main.py
```

## Built by

An autonomous coding agent session (Codex), on a remote box, for the make.fun tiny-chess-01 bounty:
<https://make.fun/bounty/tiny-chess-01>.

## License

MIT — see [LICENSE](LICENSE).
