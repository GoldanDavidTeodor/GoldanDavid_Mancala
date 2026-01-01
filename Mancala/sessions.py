"""
sessions.py

This manages game session persistence.
It handles saving/loading game history, statistics (wins/losses),
and saving/restoring interrupted game states to JSON files.
"""

import json
import datetime
from typing import List, Dict, Optional


class SessionManager:
    """
    Manages the recording and retrieval of game sessions and statistics.

    Attributes:
        history (List[Dict]): A list of past match records.
        cumulative (Dict): Full game stats (wins, draws, games played).
        autosave_path (Optional[str]): File path for automatic saving.
    """

    def __init__(self, autosave_path: Optional[str] = None):
        """
        Initialize the SessionManager.

        Args:
            autosave_path (Optional[str], optional): Path to autosave file. Defaults to None.
        """
        self.history: List[Dict] = []
        self.cumulative = {"games_played": 0, "wins": {"0": 0, "1": 0}, "draws": 0}
        self.autosave_path = autosave_path

    def record_match(self, scores: List[int]) -> None:
        """
        Record the result of a finished match.

        Updates history and cumulative stats, then triggers an autosave.

        Args:
            scores (List[int]): Final scores [Player 0, Player 1].
        """
        s0, s1 = int(scores[0]), int(scores[1])
        if s0 > s1:
            winner = "0"
        elif s1 > s0:
            winner = "1"
        else:
            winner = "draw"
            
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "winner": winner,
            "scores": [s0, s1]
        }
        self.history.append(entry)
        self.cumulative["games_played"] += 1
        
        if winner == "draw":
            self.cumulative["draws"] += 1
        else:
            self.cumulative["wins"][winner] += 1
            
        if self.autosave_path:
            try:
                self.save(self.autosave_path)
            except Exception:
                pass

    def save(self, filepath: str, current_state: Optional[Dict] = None) -> None:
        """
        Save the entire session (history + current game) to a JSON file.

        Args:
            filepath (str): Target file path.
            current_state (Optional[Dict], optional): Current board state to save. Default is None.
        """
        payload = {"history": self.history, "cumulative": self.cumulative}
        if current_state is not None:
            payload["current"] = current_state
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self, filepath: str) -> Optional[Dict]:
        """
        Load session history and return the current game state if present.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            Optional[Dict]: The interrupted game state, or None if not present.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.history = payload.get("history", [])
        self.cumulative = payload.get("cumulative", self.cumulative)
        return payload.get("current")

    def stats_summary(self) -> Dict:
        """
        Return a summary dictionary of win/loss statistics.

        Returns:
            Dict: Keys include 'games_played', 'wins_p0', 'wins_p1', 'draws'.
        """
        return {
            "games_played": self.cumulative.get("games_played", 0),
            "wins_p0": self.cumulative.get("wins", {}).get("0", 0),
            "wins_p1": self.cumulative.get("wins", {}).get("1", 0),
            "draws": self.cumulative.get("draws", 0),
        }
