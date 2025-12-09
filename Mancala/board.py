from typing import List, Tuple

class Pit:
    def __init__(self, stones: int = 4):
        self.stones = stones

    def take_all(self) -> int:
        s = self.stones
        self.stones = 0
        return s

    def add(self, n: int) -> None:
        self.stones += n

    def __repr__(self):
        return f"Pit({self.stones})"


class Board:
    def __init__(self, pits_per_side: int = 6, initial_stones: int = 4):
        self.pits_per_side = pits_per_side
        self.initial_stones = initial_stones
        self.total_pits = pits_per_side * 2
        self.pits: List[Pit] = [Pit(initial_stones) for _ in range(self.total_pits)]
        self.scores = [0, 0]  

    def clone(self):
        b = Board(self.pits_per_side, self.initial_stones)
        b.pits = [Pit(p.stones) for p in self.pits]
        b.scores = list(self.scores)
        return b

    def pit_owner(self, pit_index: int) -> int:
        if pit_index < self.pits_per_side:
            return 0
        return 1

    def player_pit_indices(self, player: int) -> List[int]:
        if player == 0:
            return list(range(0, self.pits_per_side))
        return list(range(self.pits_per_side, self.total_pits))

    def total_stones_for_player(self, player: int) -> int:
        return sum(self.pits[i].stones for i in self.player_pit_indices(player))

    def is_empty_side(self, player: int) -> bool:
        return self.total_stones_for_player(player) == 0

    def sow_from(self, pit_index: int) -> Tuple[int, int]:
        seeds = self.pits[pit_index].take_all()
        if seeds == 0:
            return pit_index, 0
        idx = pit_index
        while seeds > 0:
            idx = (idx + 1) % self.total_pits
            self.pits[idx].add(1)
            seeds -= 1
        return idx, self.pits[idx].stones

    def __str__(self):
        top = ' '.join(f"[{self.pits[i].stones:2d}]" for i in range(self.total_pits - 1, self.pits_per_side - 1, -1))
        bottom = ' '.join(f"[{self.pits[i].stones:2d}]" for i in range(0, self.pits_per_side))
        return f"P1 score: {self.scores[1]}\n{top}\n{bottom}\nP0 score: {self.scores[0]}"
