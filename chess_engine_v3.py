import chess
import time

# Piece values for evaluation (in centipawns)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-square tables to encourage good piece placement (for white; mirrored for black)
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
    """Score the position. Positive means white is better; negative means black is better."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
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
    """Search for the best score using Minimax with Alpha-Beta pruning."""
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
    """Find the best move using a board copy."""
    start_time = time.time()
    search_board = board.copy()
    legal_moves = list(search_board.legal_moves)
    
    if not legal_moves:
        print("No legal moves available!")
        return None

    move_scores = []
    
    for move in legal_moves:
        if time.time() - start_time > time_limit:
            print("Time limit reached")
            break
        search_board.push(move)
        score = alpha_beta(search_board, depth - 1, float('-inf'), float('inf'), search_board.turn == chess.BLACK)
        search_board.pop()
        print(f"Evaluated move {move.uci()} with score {score}")
        move_scores.append((move, score))

    if not move_scores:
        print("No moves evaluated, selecting first legal move")
        return legal_moves[0] if legal_moves else None

    if board.turn == chess.WHITE:
        best_move, best_score = max(move_scores, key=lambda x: x[1])
    else:
        best_move, best_score = min(move_scores, key=lambda x: x[1])

    if best_move not in board.legal_moves:
        print(f"Error: Selected move {best_move.uci()} is not legal")
        print(f"Legal moves: {[m.uci() for m in board.legal_moves]}")
        return legal_moves[0] if legal_moves else None

    print(f"Selected move {best_move.uci()} with score {best_score}")
    return best_move

def play_game():
    """Play a game in the console. You are White; engine is Black."""
    board = chess.Board()
    print("Welcome to Chess! You play White. Enter moves like 'e2e4' or 'Nf3'.")
    print(board)

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            while True:
                try:
                    move = input("Your move: ")
                    move = board.parse_san(move)
                    if move in board.legal_moves:
                        board.push(move)
                        break
                    else:
                        print("Illegal move. Try again.")
                except ValueError:
                    print("Invalid move format. Use algebraic notation (e.g., 'e2e4' or 'Nf3').")
        else:
            print("Engine thinking...")
            print(f"Board FEN before engine move: {board.fen()}")
            print(f"Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
            move = find_best_move(board, depth=5, time_limit=3.0)
            if move:
                legal_moves = list(board.legal_moves)
                if move in legal_moves:
                    # Display move before pushing
                    move_san = board.san(move)
                    board.push(move)
                    print(f"Engine move: {move_san}")
                else:
                    print(f"Error: Engine selected invalid move {move.uci()}")
                    print(f"Legal moves: {[m.uci() for m in legal_moves]}")
                    break
            else:
                print("Engine has no moves!")
                break
        print("\n" + str(board) + "\n")

    result = board.result()
    print(f"Game over! Result: {result}")

if __name__ == "__main__":
    play_game()