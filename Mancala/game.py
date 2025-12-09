from board import Board
from rules import legal_moves, apply_move

def game_end_sweep(board: Board, last_player: int):
    p0_total = sum(board.pits[i].stones for i in board.player_pit_indices(0))
    p1_total = sum(board.pits[i].stones for i in board.player_pit_indices(1))
    if p0_total == 0 or p1_total == 0:
        if p0_total > 0:
            board.scores[0] += p0_total
            for i in board.player_pit_indices(0):
                board.pits[i].stones = 0
        if p1_total > 0:
            board.scores[1] += p1_total
            for i in board.player_pit_indices(1):
                board.pits[i].stones = 0

        print("\nFinal board:")
        print(board)
        if board.scores[0] > board.scores[1]:
            print(f"Player 0 wins {board.scores[0]} - {board.scores[1]}")
        elif board.scores[1] > board.scores[0]:
            print(f"Player 1 wins {board.scores[1]} - {board.scores[0]}")
        else:
            print(f"Draw: {board.scores[0]} - {board.scores[1]}")
        return True
    return False

def simple_cli():
    b = Board()
    player = 0
    while True:
        print("\n" + str(b))
        if b.is_empty_side(0) or b.is_empty_side(1):
            if game_end_sweep(b, player):
                break

        lm = legal_moves(b, player)
        if not lm:
            print(f"Player {player} has no legal moves. Ending game.")
            if game_end_sweep(b, player):
                break
            else:
                break

        print(f"Player {player} legal moves: {lm}")
        raw = input(f"Choose pit for player {player} or q: ")
        if raw.lower() == "q":
            print("Quit by user.")
            break
        try:
            chosen = int(raw)
        except:
            print("Please enter a number.")
            continue
        if chosen not in lm:
            print("Illegal choice; pick one of:", lm)
            continue
        ok = apply_move(b, player, chosen)
        if not ok:
            print("Move was found illegal by rules. Try another.")
            continue
        player = 1 - player

if __name__ == "__main__":
    simple_cli()
