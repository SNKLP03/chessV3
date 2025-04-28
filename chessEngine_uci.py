import chess
import sys
import time

# Piece values and piece-square tables (same as before)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

PAWN_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_PST = KNIGHT_PST
ROOK_PST = KNIGHT_PST
QUEEN_PST = KNIGHT_PST
KING_PST = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

PST_TABLES = {
    chess.PAWN: PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST,
    chess.KING: KING_PST
}

def evaluate_position(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -99999
        else:
            return 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    material = 0
    piece_square_score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        value = PIECE_VALUES[piece.piece_type]
        pst = PST_TABLES[piece.piece_type]
        square_idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
        pst_value = pst[square_idx]
        if piece.color == chess.WHITE:
            material += value
            piece_square_score += pst_value
        else:
            material -= value
            piece_square_score -= pst_value

    total_score = material + piece_square_score
    return total_score if board.turn == chess.WHITE else -total_score

def alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return evaluate_position(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval_score = alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval_score = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth=3, time_limit=2.0):
    start_time = time.time()
    best_move = None
    best_score = float('-inf') if board.turn == chess.WHITE else float('inf')
    legal_moves = list(board.legal_moves)
    
    if not legal_moves:
        return None

    for move in legal_moves:
        if time.time() - start_time > time_limit:
            break
        board.push(move)
        score = alpha_beta(board, depth - 1, float('-inf'), float('inf'), board.turn == chess.BLACK)
        board.pop()
        if board.turn == chess.WHITE:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    return best_move

def uci_loop():
    """Communicate with a chess GUI using UCI protocol."""
    board = chess.Board()
    while True:
        line = input().strip()
        if line == "uci":
            print("id name SimpleChess 1500")
            print("id author xAI")
            print("uciok")
        elif line == "isready":
            print("readyok")
        elif line == "ucinewgame":
            board = chess.Board()
        elif line.startswith("position"):
            parts = line.split()
            if parts[1] == "startpos":
                board = chess.Board()
                moves_start = 3 if parts[2] == "moves" else 2
                if len(parts) > moves_start:
                    for move in parts[moves_start:]:
                        board.push_uci(move)
            elif parts[1] == "fen":
                fen = " ".join(parts[2:parts.index("moves") if "moves" in parts else -1])
                board = chess.Board(fen)
                if "moves" in parts:
                    moves_start = parts.index("moves") + 1
                    for move in parts[moves_start:]:
                        board.push_uci(move)
        elif line.startswith("go"):
            move = find_best_move(board, depth=3, time_limit=2.0)
            if move:
                print(f"bestmove {move.uci()}")
            else:
                print("bestmove (none)")
        elif line == "quit":
            break

if __name__ == "__main__":
    uci_loop()