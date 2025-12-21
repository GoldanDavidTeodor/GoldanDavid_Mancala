import random
from typing import List
from board import Board
from rules import legal_moves

class CPUPlayer:
    
    def __init__(self, player_id: int = 1):
        self.player_id = player_id
    
    def get_move(self, board: Board) -> int:
        moves = legal_moves(board, self.player_id)
        if not moves:
            return -1
        return random.choice(moves)
    
    def has_legal_moves(self, board: Board) -> bool:
        return len(legal_moves(board, self.player_id)) > 0
