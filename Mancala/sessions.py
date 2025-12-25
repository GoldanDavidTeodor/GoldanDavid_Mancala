import json
import datetime
from typing import List, Dict, Optional


class SessionManager:
    def __init__(self, autosave_path: Optional[str] = None):
        self.history: List[Dict] = []
        self.cumulative = {"games_played": 0, "wins": {"0": 0, "1": 0}, "draws": 0}
        self.autosave_path = autosave_path

    def record_match(self, scores: List[int]) -> None:
        s0, s1 = int(scores[0]), int(scores[1])
        if s0 > s1:
            winner = "0"
        elif s1 > s0:
            winner = "1"
        else:
            winner = "draw"
        entry = {"timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                 "winner": winner,
                 "scores": [s0, s1]}
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
        payload = {"history": self.history, "cumulative": self.cumulative}
        if current_state is not None:
            payload["current"] = current_state
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self, filepath: str) -> Optional[Dict]:
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.history = payload.get("history", [])
        self.cumulative = payload.get("cumulative", self.cumulative)
        return payload.get("current")

    def stats_summary(self) -> Dict:
        return {
            "games_played": self.cumulative.get("games_played", 0),
            "wins_p0": self.cumulative.get("wins", {}).get("0", 0),
            "wins_p1": self.cumulative.get("wins", {}).get("1", 0),
            "draws": self.cumulative.get("draws", 0),
        }
