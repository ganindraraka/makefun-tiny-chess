# tiny-chess-01 — a tiny chess engine

A single-file Python chess engine for the make.fun `tiny-chess-01` bounty: a legal-move
generator, an alpha-beta search with iterative deepening, a transposition table and killer
moves, and a simple material + piece-square evaluation.

`main.py` is the packed entrypoint (the kit's `makefun compress` packs `engine_src.py`);
`engine_src.py` is the readable source it is packed from.
