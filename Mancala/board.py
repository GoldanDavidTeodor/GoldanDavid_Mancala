"""
board.py

This defines the main elements of Oware.
It includes the Pit class made for individual pits and the
Board class with its game state and helper functions.
"""

from typing import List, Tuple


class Pit:
    """
    Represents a single pit on the Oware board.

    Attributes:
        stones (int): The current count of seeds in this pit.
    """

    def __init__(self, stones: int = 4):
        """
        Initialize a new Pit.

        Args:
            stones (int, optional): Initial number of stones. Defaults to 4.
        """
        self.stones = stones

    def take_all(self) -> int:
        """
        Remove all stones from the pit and return the count.

        Returns:
            int: The number of stones that were in the pit.
        """
        s = self.stones
        self.stones = 0
        return s

    def add(self, n: int) -> None:
        """
        Add stones to the pit.

        Args:
            n (int): The number of stones to add.
        """
        self.stones += n

    def __repr__(self) -> str:
        """Return a string representation of the Pit."""
        return f"Pit({self.stones})"


class Board:
    """
    Represents the Oware game board.

    Manages the collection of Pits, player scores, and basic board operations.

    Attributes:
        pits_per_side (int): Number of pits per player (default is 6).
        initial_stones (int): Starting stones per pit (default is 4).
        total_pits (int): Total number of pits on the board.
        pits (List[Pit]): The list of Pit objects representing the board.
        scores (List[int]): A two element list tracking scores for Player 0 and Player 1.
    """

    def __init__(self, pits_per_side: int = 6, initial_stones: int = 4):
        """
        Initialize the game board.

        Args:
            pits_per_side (int, optional): Pits per player. Defaults to 6.
            initial_stones (int, optional): Stones per pit. Defaults to 4.
        """
        self.pits_per_side = pits_per_side
        self.initial_stones = initial_stones
        self.total_pits = pits_per_side * 2
        self.pits: List[Pit] = [Pit(initial_stones) for i in range(self.total_pits)]
        self.scores = [0, 0]  

    def clone(self) -> 'Board':
        """
        Create a copy of the current board state.

        Returns:
            Board: A new Board instance with identical state.
        """
        b = Board(self.pits_per_side, self.initial_stones)
        b.pits = [Pit(p.stones) for p in self.pits]
        b.scores = list(self.scores)
        return b

    def pit_owner(self, pit_index: int) -> int:
        """
        Determine which player owns a specific pit.

        Args:
            pit_index (int): The index of the pit.

        Returns:
            int: 0 for Player 0 (bottom), 1 for Player 1 (top).
        """
        if pit_index < self.pits_per_side:
            return 0
        return 1

    def player_pit_indices(self, player: int) -> List[int]:
        """
        Get a list of pit indices belonging to a specific player.

        Args:
            player (int): The player ID (0 or 1).

        Returns:
            List[int]: A list of integer indices.
        """
        if player == 0:
            return list(range(0, self.pits_per_side))
        return list(range(self.pits_per_side, self.total_pits))

    def total_stones_for_player(self, player: int) -> int:
        """
        Calculate the total number of stones currently on a player's side.

        Args:
            player (int): The player ID (0 or 1).

        Returns:
            int: Total sum of stones.
        """
        return sum(self.pits[i].stones for i in self.player_pit_indices(player))

    def is_empty_side(self, player: int) -> bool:
        """
        Check if a player's side of the board is completely empty.

        Args:
            player (int): The player ID (0 or 1).

        Returns:
            bool: True if the player has no stones left, False is the player has stones left.
        """
        return self.total_stones_for_player(player) == 0

    def sow_from(self, pit_index: int) -> Tuple[int, int]:
        """
        Execute the sowing action from a specific pit.

        Removes all seeds from the target pit and distributes them
        counter clockwise +1 seed per pit.

        Args:
            pit_index (int): The index of the pit to sow from.

        Returns:
            Tuple[int, int]: (index of the last pit sown into, stones in that pit).
        """
        seeds = self.pits[pit_index].take_all()
        if seeds == 0:
            return pit_index, 0
        idx = pit_index
        while seeds > 0:
            idx = (idx + 1) % self.total_pits
            self.pits[idx].add(1)
            seeds -= 1
        return idx, self.pits[idx].stones

    def __str__(self) -> str:
        """Return a terminal friendly representation of the board."""
        top = ' '.join(f"[{self.pits[i].stones:2d}]" for i in range(self.total_pits - 1, self.pits_per_side - 1, -1))
        bottom = ' '.join(f"[{self.pits[i].stones:2d}]" for i in range(0, self.pits_per_side))
        return f"P1 score: {self.scores[1]}\n{top}\n{bottom}\nP0 score: {self.scores[0]}"
    