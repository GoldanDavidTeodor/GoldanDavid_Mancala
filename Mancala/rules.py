from typing import List, Tuple
from board import Board

def opponent(p: int) -> int:
    return 1 - p

def _sow_list(pits: List[int], start_idx: int) -> Tuple[int, List[int]]:
    pits = pits.copy()
    seeds = pits[start_idx]
    pits[start_idx] = 0
    idx = start_idx
    while seeds > 0:
        idx = (idx + 1) % len(pits)
        pits[idx] += 1
        seeds -= 1
    return idx, pits

def _owner_of(idx: int, pits_per_side: int) -> int:
    return 0 if idx < pits_per_side else 1

def _capture_on_list(pits: List[int], last_idx: int, mover: int, pits_per_side: int) -> Tuple[int, List[int]]:
    pits = pits.copy()
    captured = 0
    opp = opponent(mover)
    if _owner_of(last_idx, pits_per_side) == opp:
        i = last_idx
        while True:
            stones = pits[i]
            if stones in (2, 3):
                captured += stones
                pits[i] = 0
                i = (i - 1) % len(pits)
                if _owner_of(i, pits_per_side) != opp:
                    break
            else:
                break
    return captured, pits

def legal_moves(board: Board, player: int) -> List[int]:
    candidates = [i for i in board.player_pit_indices(player) if board.pits[i].stones > 0]
    legal = []
    for pit in candidates:
        plain = [p.stones for p in board.pits]
        last_idx, after_sow = _sow_list(plain, pit)
        captured, after_capture = _capture_on_list(after_sow, last_idx, player, board.pits_per_side)
        opp_total = sum(after_capture[i] for i in board.player_pit_indices(opponent(player)))
        if opp_total > 0:
            legal.append(pit)
    return legal if legal else candidates

def apply_move(board: Board, player: int, pit_index: int, simulate_only: bool = False) -> bool:
    if pit_index < 0 or pit_index >= board.total_pits:
        return False
    if board.pit_owner(pit_index) != player:
        return False
    if board.pits[pit_index].stones == 0:
        return False

    plain = [p.stones for p in board.pits]
    last_idx, after_sow = _sow_list(plain, pit_index)
    captured, after_capture = _capture_on_list(after_sow, last_idx, player, board.pits_per_side)

    opp_after_total = sum(after_capture[i] for i in board.player_pit_indices(opponent(player)))
    if opp_after_total == 0:
        alternatives = [i for i in board.player_pit_indices(player) if board.pits[i].stones > 0 and i != pit_index]
        for alt in alternatives:
            plain_alt = [p.stones for p in board.pits]
            last_alt, after_sow_alt = _sow_list(plain_alt, alt)
            _, after_capture_alt = _capture_on_list(after_sow_alt, last_alt, player, board.pits_per_side)
            if sum(after_capture_alt[i] for i in board.player_pit_indices(opponent(player))) > 0:
                return False

    if simulate_only:
        return True

    last_idx_real, _ = board.sow_from(pit_index)
    captured_real = 0
    if board.pit_owner(last_idx_real) == opponent(player):
        i = last_idx_real
        while True:
            stones_here = board.pits[i].stones
            if stones_here in (2, 3):
                captured_real += stones_here
                board.pits[i].stones = 0
                i = (i - 1) % board.total_pits
                if board.pit_owner(i) != opponent(player):
                    break
            else:
                break

    board.scores[player] += captured_real
    return True
