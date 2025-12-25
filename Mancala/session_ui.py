import json
import os
from tkinter import messagebox, filedialog


def save_session_dialog(gui):
    path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if not path:
        return
    current = {
        "board_pits": [p.stones for p in gui.board.pits],
        "scores": list(gui.board.scores),
        "player": gui.player,
        "vs_ai": gui.vs_ai,
    }
    try:
        gui.session.save(path, current_state=current)
        messagebox.showinfo("Saved", f"Session saved to {path}")
    except Exception as e:
        messagebox.showerror("Save Error", str(e))


def load_session_dialog(gui):
    path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not path:
        return
    return load_from_path(gui, path)


def load_from_path(gui, path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as e:
        messagebox.showerror("Load Error", str(e))
        return

    current = None
    if isinstance(payload, dict) and ("history" in payload or "cumulative" in payload):
        try:
            current = gui.session.load(path)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return
    elif isinstance(payload, dict) and ("board_pits" in payload or "scores" in payload):
        current = payload
    else:
        messagebox.showinfo("Loaded", "Unrecognized JSON format.")
        return

    if current:
        try:
            pits = current.get("board_pits")
            if pits and len(pits) == gui.board.total_pits:
                for i, v in enumerate(pits):
                    gui.board.pits[i].stones = int(v)
            scores = current.get("scores")
            if scores and len(scores) == 2:
                gui.board.scores = [int(scores[0]), int(scores[1])]
            gui.player = int(current.get("player", 0))
            gui.vs_ai = bool(current.get("vs_ai", False))
            if gui.vs_ai:
                from cpu import CPUPlayer
                gui.cpu_player = CPUPlayer(player_id=1)
            else:
                gui.cpu_player = None
            try:
                gui.menu_frame.destroy()
            except Exception:
                pass
            gui._setup_game_ui()
            gui._draw_board()
            messagebox.showinfo("Loaded", f"Loaded board state from {path}")
            return
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return


def show_stats(gui):
    s = gui.session.stats_summary()
    txt = f"Games: {s['games_played']}\nP0 wins: {s['wins_p0']}\nP1 wins: {s['wins_p1']}\nDraws: {s['draws']}"
    last = gui.session.history[-5:]
    if last:
        txt += "\n\nLast matches:\n"
        for e in reversed(last):
            w = e.get("winner")
            sc = e.get("scores")
            ts = e.get("timestamp")
            txt += f"{ts}: {w} {sc}\n"
    messagebox.showinfo("Session Stats", txt)
