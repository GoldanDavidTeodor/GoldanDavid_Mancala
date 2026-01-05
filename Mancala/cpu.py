"""
cpu.py

This implements the AI opponent for the Oware game.
It includes the CPUPlayer class which uses Minimax (with Alpha-Beta pruning)
to determine the best moves.
"""

import random
from typing import List, Optional, Tuple
from board import Board
from rules import legal_moves, apply_move


class CPUPlayer:
    """
    An AI player that calculates moves based on selected difficulty.

    Attributes:
        player_id (int): The AI player index (1).
        difficulty (str): 'Easy', 'Medium', or 'Hard'.
        max_depth (int): Depth limit for the Minimax algorithm.
    """

    def __init__(self, player_id: int = 1, difficulty: str = "Medium"):
        """
        Initialize the CPU Player.

        Args:
            player_id (int, optional): ID of the AI player. Default is 1.
            difficulty (str, optional): 'Easy', 'Medium', or 'Hard'. Default is "Medium".
        """
        self.player_id = player_id
        self.difficulty = difficulty
        self.max_depth = 4 if difficulty == "Hard" else 1

    def set_difficulty(self, difficulty: str) -> None:
        """
        Update the difficulty level and adjust search depth.

        Args:
            difficulty (str): New difficulty level.
        """
        self.difficulty = difficulty
        self.max_depth = 4 if difficulty == "Hard" else 1
    
    def get_move(self, board: Board) -> int:
        """
        Calculate the best move for the current board state.

        Args:
            board (Board): The current game board.

        Returns:
            int: The index of the selected pit to move, or -1 if no moves exist.
        """
        legal = legal_moves(board, self.player_id)
        if not legal:
            return -1

        if self.difficulty == "Easy":
            return random.choice(legal)

        elif self.difficulty == "Medium":
            # 30% chance to make a random move 70% chance to make a greedy move
            if random.random() < 0.3:
                return random.choice(legal)
            else:
                return self._get_smart_move(board, legal)

        elif self.difficulty == "Hard":
            # first move doesn't matter that much
            if sum(p.stones for p in board.pits) == board.total_pits * 4:
                 return random.choice(legal)
            
            _, move = self._minimax(board, self.max_depth, float('-inf'), float('inf'), True)
            return move if move is not None else random.choice(legal)

        return random.choice(legal)
    
    def has_legal_moves(self, board: Board) -> bool:
        """
        Check if the AI has any legal moves available.

        Args:
            board (Board): Current board.

        Returns:
            bool: True if legal moves exist, False if not.
        """
        return len(legal_moves(board, self.player_id)) > 0


    def _get_smart_move(self, board: Board, legal: List[int]) -> int:
        """
        Find a move that maximizes immediate score gain (Greedy).

        Args:
            board (Board): Current board.
            legal (List[int]): List of legal move indices.

        Returns:
            int: The index of the best greedy move.
        """
        best_move = legal[0]
        max_score = -1
        
        for move in legal:
            temp_board = board.clone()
            apply_move(temp_board, self.player_id, move, simulate_only=True)
            score_gain = temp_board.scores[self.player_id] - board.scores[self.player_id]
            
            if score_gain > max_score:
                max_score = score_gain
                best_move = move
        return best_move

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[float, Optional[int]]:
        """
        Execute Minimax algorithm with Alpha-Beta pruning.

        Args:
            board (Board): The board state to evaluate.
            depth (int): Remaining depth to search.
            alpha (float): Best value for maximizer so far.
            beta (float): Best value for minimizer so far.
            maximizing (bool): True if it's the AI's turn (maximize).

        Returns:
            Tuple[float,Optional[int]]: (Best Score, Best Move Index).
        """
        current_player = self.player_id if maximizing else (1 - self.player_id)
        legal = legal_moves(board, current_player)

        #end conditions
        if depth == 0 or not legal or board.scores[0] > 24 or board.scores[1] > 24:
            return (board.scores[self.player_id] - board.scores[1 - self.player_id]), None

        best_move = None
        
        if maximizing:
            max_eval = float('-inf')
            for move in legal:
                sim_board = board.clone()
                apply_move(sim_board, current_player, move)
                
                eval_score, _ = self._minimax(sim_board, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal:
                sim_board = board.clone()
                apply_move(sim_board, current_player, move)
                
                eval_score, _ = self._minimax(sim_board, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return min_eval, best_move