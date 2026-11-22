import os
import unittest

try:
    import engine_src as engine
except ImportError:
    import engine_src_v3 as engine


START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def legal_ucis(fen):
    position = engine.parse(fen)
    side = position[1]
    result = []
    for move in engine.moves(position):
        child = engine.play(position, move)
        king = child[0].index(6 * side)
        if not engine.attacked(child[0], king, -side):
            result.append(engine.uci(move))
    return result


class EngineTests(unittest.TestCase):
    def test_parse_start_fen_returns_board(self):
        board, side, castling, ep, halfmove = engine.parse(START_FEN)
        self.assertEqual(len(board), 128)
        self.assertEqual(side, 1)
        self.assertEqual(castling, "KQkq")
        self.assertEqual(ep, -1)
        self.assertEqual(halfmove, 0)
        self.assertEqual(board[engine.square("e1")], 6)
        self.assertEqual(board[engine.square("e8")], -6)
        self.assertEqual(board[engine.square("a1")], 4)
        self.assertEqual(board[engine.square("h8")], -4)

    def test_choose_returns_legal_move(self):
        allowed = legal_ucis(START_FEN)
        move = engine.choose(START_FEN, allowed)
        self.assertRegex(move, r"^[a-h][1-8][a-h][1-8][nbrq]?$")
        self.assertIn(move, allowed)

    def test_main_is_at_most_4096_bytes(self):
        self.assertTrue(os.path.isfile("main.py"))
        self.assertLessEqual(os.path.getsize("main.py"), 4096)


if __name__ == "__main__":
    unittest.main()
