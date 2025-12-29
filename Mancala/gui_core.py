import os
import tkinter as tk
from tkinter import messagebox, filedialog
from board import Board
import rules
from cpu import CPUPlayer
from sessions import SessionManager
import session_ui

PIT_RADIUS = 56          
PIT_SPACING = 22
CANVAS_PAD_X = 28
FLASH_MS = 140  

N_PITS = 6 
WINDOW_WIDTH = (PIT_RADIUS * 2 + PIT_SPACING) * N_PITS + CANVAS_PAD_X * 2
WINDOW_HEIGHT = 580 

class SimpleOwareGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Oware")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.board = Board()  
        self.player = 0
        self.animating = False
        self.vs_ai = False
        self.ai_difficulty = "Medium" 
        self.cpu_player = None 
        
        self.history_stack = []
        self.redo_stack = []
        
        base = os.path.dirname(__file__)
        session_file = os.path.join(base, "last_session.json")
        self.session = SessionManager(autosave_path=session_file)

        self.show_menu()

    def show_menu(self):
        self.menu_frame = tk.Frame(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#f0f0f0")
        self.menu_frame.pack_propagate(False) 
        self.menu_frame.pack()

        tk.Label(self.menu_frame, text="OWARE", font=("Helvetica", 32, "bold"), bg="#f0f0f0").pack(pady=(60, 20))
        
        btn_style = {"font": ("Helvetica", 12), "width": 20, "pady": 10}
        
        tk.Button(self.menu_frame, text="1vs1", command=lambda: self.start_game(False), **btn_style).pack(pady=5)
        
        ai_frame = tk.Frame(self.menu_frame, bg="#f0f0f0")
        ai_frame.pack(pady=5)
        
        tk.Button(ai_frame, text="vs AI", command=lambda: self.start_game(True), **btn_style).pack(side="top")
        
        self.diff_var = tk.StringVar(value="Medium")
        diff_menu = tk.OptionMenu(ai_frame, self.diff_var, "Easy", "Medium", "Hard")
        diff_menu.config(width=21, font=("Helvetica", 10))
        diff_menu.pack(side="bottom", pady=2)

        tk.Button(self.menu_frame, text="Load Session", command=self._load_session_dialog, **btn_style).pack(pady=6)
        tk.Button(self.menu_frame, text="Save Session", command=self._save_session_dialog, **btn_style).pack(pady=6)
        tk.Button(self.menu_frame, text="View Stats", command=self._show_stats, **btn_style).pack(pady=6)
        
        tk.Label(self.menu_frame, text="Select a game mode to begin", bg="#f0f0f0", fg="gray").pack(side="bottom", pady=20)

    def start_game(self, vs_ai):
        self.vs_ai = vs_ai
        self.ai_difficulty = self.diff_var.get()

        if vs_ai:
            self.cpu_player = CPUPlayer(player_id=1, difficulty=self.ai_difficulty) 
        
        self.history_stack = []
        self.redo_stack = []

        self.menu_frame.destroy() 
        self._setup_game_ui()
        self._draw_board()

    def _setup_game_ui(self):
        self.top_score = tk.Label(self.root, text="P1: 0", font=("Helvetica", 14, "bold"))
        self.top_score.pack(pady=(6, 0))

        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=300, bg="#f8f8fb", highlightthickness=0)
        self.canvas.pack(padx=8, pady=8)

        self.bottom_score = tk.Label(self.root, text="P0: 0", font=("Helvetica", 14, "bold"))
        self.bottom_score.pack(pady=(0, 6))

        self.status = tk.Label(self.root, text="Player 0's turn", font=("Helvetica", 10))
        self.status.pack()

        self.undo_frame = tk.Frame(self.root)
        self.undo_frame.pack(pady=(5, 5))
        
        self.btn_undo = tk.Button(self.undo_frame, text="Undo", command=self.perform_undo, state="disabled", width=8)
        self.btn_undo.pack(side="left", padx=5)
        
        self.btn_redo = tk.Button(self.undo_frame, text="Redo", command=self.perform_redo, state="disabled", width=8)
        self.btn_redo.pack(side="left", padx=5)

        self.endgame_btn = tk.Button(self.root, text="Trigger Endgame", font=("Helvetica", 10),
                         command=self._trigger_endgame)
        self.endgame_btn.pack(pady=(6, 2))
        self.save_match_btn = tk.Button(self.root, text="Save Match (JSON)", font=("Helvetica", 10),
                        command=self._save_match)
        self.save_match_btn.pack(pady=(2, 6))
        self.save_session_btn = tk.Button(self.root, text="Save Session (JSON)", font=("Helvetica", 10),
                command=self._save_session_dialog)
        self.save_session_btn.pack(pady=(2, 6))

        self.pit_map = {} 
        self._build_board_graphics()
        self.canvas.tag_bind("pit", "<Button-1>", self._on_pit_click)
        self._draw_board()

    def save_state(self):
        state = {
            'board': self.board.clone(),
            'player': self.player,
            'scores': list(self.board.scores)
        }
        self.history_stack.append(state)
        self.redo_stack.clear()
        self._update_undo_buttons()

    def perform_undo(self):
        if not self.history_stack or self.animating: return
        
        steps = 2 if (self.vs_ai and self.player == 0 and len(self.history_stack) >= 2) else 1
        if self.vs_ai and self.player == 1: steps = 1

        for _ in range(steps):
            if not self.history_stack: break
            
            current = {
                'board': self.board.clone(),
                'player': self.player,
                'scores': list(self.board.scores)
            }
            self.redo_stack.append(current)

            prev = self.history_stack.pop()
            self.board = prev['board']
            self.player = prev['player']
            self.board.scores = prev['scores']

        self._draw_board()
        self._update_undo_buttons()

    def perform_redo(self):
        if not self.redo_stack or self.animating: return

        current = {
            'board': self.board.clone(),
            'player': self.player,
            'scores': list(self.board.scores)
        }
        self.history_stack.append(current)

        next_state = self.redo_stack.pop()
        self.board = next_state['board']
        self.player = next_state['player']
        self.board.scores = next_state['scores']

        self._draw_board()
        self._update_undo_buttons()

    def _update_undo_buttons(self):
        self.btn_undo.config(state="normal" if self.history_stack else "disabled")
        self.btn_redo.config(state="normal" if self.redo_stack else "disabled")

    def _build_board_graphics(self):
        n = self.board.pits_per_side
        pit_d = PIT_RADIUS * 2
        total_width = n * pit_d + (n - 1) * PIT_SPACING
        start_x = (WINDOW_WIDTH - total_width) // 2 + PIT_RADIUS

        for row, y in [(1, 80), (0, 220)]:
            for i in range(n):
                pit_idx = (self.board.total_pits - 1 - i) if row == 1 else i
                x = start_x + i * (pit_d + PIT_SPACING)
                fill = "#e6f0ff" if row == 1 else "#fff9e6"
                outline = "#345" if row == 1 else "#653"
                pit = self.canvas.create_oval(
                    x - PIT_RADIUS, y - PIT_RADIUS, x + PIT_RADIUS, y + PIT_RADIUS,
                    fill=fill, outline=outline, width=3, tags=("pit", f"pit{pit_idx}")
                )
                text = self.canvas.create_text(x, y, text="0", font=("Helvetica", 14, "bold"),
                                               tags=("pit", f"pit{pit_idx}"))
                self.pit_map[pit_idx] = (pit, text, x, y)

    def _draw_board(self):
        for idx, (pit, text, cx, cy) in self.pit_map.items():
            count = self.board.pits[idx].stones
            self.canvas.itemconfigure(text, text=str(count))
            owner = self.board.pit_owner(idx)
            fill = "#fff9e6" if owner == 0 else "#e6f0ff"
            outline = "#653" if owner == 0 else "#345"
            self.canvas.itemconfigure(pit, fill=fill, outline=outline, width=3)

        self.top_score.config(text=f"P1: {self.board.scores[1]}")
        self.bottom_score.config(text=f"P0: {self.board.scores[0]}")
        
        mode_text = f" (vs AI - {self.ai_difficulty})" if self.vs_ai else ""
        self.status.config(text=f"Player {self.player}'s turn{mode_text}")

        legal = rules.legal_moves(self.board, self.player)
        for idx, (pit, _, _, _) in self.pit_map.items():
            if idx in legal:
                self.canvas.itemconfigure(pit, width=4, outline="#2e8b57")
            else:
                owner = self.board.pit_owner(idx)
                outline = "#653" if owner == 0 else "#345"
                self.canvas.itemconfigure(pit, width=3, outline=outline)
        
        if hasattr(self, 'btn_undo'):
            self._update_undo_buttons()

    def _on_pit_click(self, event):
        if self.animating: return
        
        if self.vs_ai and self.player == 1: return

        item = self.canvas.find_withtag("current")
        if not item: return
        tags = self.canvas.gettags(item)
        pit_tag = next((t for t in tags if t.startswith("pit") and t != "pit"), None)
        if not pit_tag: return
        pit_idx = int(pit_tag[3:])
        legal = rules.legal_moves(self.board, self.player)
        if pit_idx not in legal:
            pit, _, _, _ = self.pit_map[pit_idx]
            old = self.canvas.itemcget(pit, "outline")
            self.canvas.itemconfigure(pit, outline="#ff0000", width=4)
            self.root.after(220, lambda: self.canvas.itemconfigure(pit, outline=old, width=3))
            return
        
        self.save_state()
        self._animate_and_apply(pit_idx)

    def _animate_and_apply(self, pit_index):
        seeds = self.board.pits[pit_index].stones
        seq = [pit_index]  
        idx = pit_index
        for _ in range(seeds):
            idx = (idx + 1) % self.board.total_pits
            seq.append(idx)

        self.animating = True
        self.canvas.config(cursor="watch")
        
        if hasattr(self, 'btn_undo'):
            self.btn_undo.config(state="disabled")
            self.btn_redo.config(state="disabled")

        self._flash_sequence(seq, 0, pit_index)

    def _flash_sequence(self, seq, pos, source_pit):
        if pos >= len(seq):
            ok = rules.apply_move(self.board, self.player, source_pit)
            if not ok:
                messagebox.showerror("Illegal move", "Move rejected by rules.")
                self.animating = False
                self.canvas.config(cursor="")
                self._draw_board()
                return
            
            if self.board.is_empty_side(0) or self.board.is_empty_side(1):
                self.animating = False
                self.canvas.config(cursor="")
                self._endgame_sweep()
                return
            
            self.player = 1 - self.player
            self.animating = False
            self.canvas.config(cursor="")
            self._draw_board()
            
            if self.vs_ai and self.player == self.cpu_player.player_id:
                self.root.after(500, self._execute_cpu_turn)
            return

        pit_idx = seq[pos]
        pit, text, _, _ = self.pit_map[pit_idx]
        old_fill = self.canvas.itemcget(pit, "fill")
        
        if pos == 0:
            self.canvas.itemconfigure(text, text="0")
        
        self.canvas.itemconfigure(pit, fill="#fff3c6")
        self.root.after(FLASH_MS, lambda: self._unflash_and_continue(pit, text, old_fill, seq, pos, source_pit))

    def _unflash_and_continue(self, pit, text, old_fill, seq, pos, source_pit):
        self.canvas.itemconfigure(pit, fill=old_fill)
        
        if pos > 0: 
            dest_count = self.board.pits[seq[pos]].stones + 1
            self.canvas.itemconfigure(text, text=str(dest_count))
        
        self.root.after(60, lambda: self._flash_sequence(seq, pos + 1, source_pit))

    def _execute_cpu_turn(self):
        """Execute a CPU turn with animation."""
        if not self.vs_ai or self.player != self.cpu_player.player_id:
            return
        
        self.save_state()

        move = self.cpu_player.get_move(self.board)
        
        if move == -1:
            self.player = 1 - self.player
            self._draw_board()
            return
        
        self._animate_and_apply(move)

    def _trigger_endgame(self):
        if self.animating:
            return
        self._endgame_sweep()

    def _endgame_sweep(self):
        p0 = sum(self.board.pits[i].stones for i in self.board.player_pit_indices(0))
        p1 = sum(self.board.pits[i].stones for i in self.board.player_pit_indices(1))
        self.board.scores[0] += p0
        self.board.scores[1] += p1
        for i in range(self.board.total_pits): self.board.pits[i].stones = 0
        self._draw_board()
        
        try:
            self.session.record_match([self.board.scores[0], self.board.scores[1]])
        except Exception:
            pass

        msg = f"Draw: {self.board.scores[0]} - {self.board.scores[1]}"
        if self.board.scores[0] > self.board.scores[1]:
            msg = f"Player 0 wins {self.board.scores[0]} - {self.board.scores[1]}"
        elif self.board.scores[1] > self.board.scores[0]:
            msg = f"Player 1 wins {self.board.scores[1]} - {self.board.scores[0]}"

        messagebox.showinfo("Game Over", msg)
        for name in ("top_score", "canvas", "bottom_score", "status", "endgame_btn", "save_match_btn", "undo_frame"):
            w = getattr(self, name, None)
            if w:
                try:
                    w.destroy()
                except Exception:
                    pass

        try:
            if hasattr(self, "save_session_btn") and self.save_session_btn:
                self.save_session_btn.destroy()
        except Exception:
            pass
        self.pit_map = {}
        self.board = Board()
        self.player = 0
        self.animating = False
        self.vs_ai = False
        self.cpu_player = None
        self.show_menu()
        return

    def _save_session_dialog(self):
        return session_ui.save_session_dialog(self)

    def _load_session_dialog(self):
        return session_ui.load_session_dialog(self)

    def _save_match(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        match = {
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "scores": [int(self.board.scores[0]), int(self.board.scores[1])],
            "board_pits": [int(p.stones) for p in self.board.pits],
            "player": int(self.player),
            "vs_ai": bool(self.vs_ai),
        }
        try:
            import json
            with open(path, "w", encoding="utf-8") as f:
                json.dump(match, f, indent=2)
            try:
                base = os.path.dirname(__file__)
                quick = os.path.join(base, "last_match.json")
                with open(quick, "w", encoding="utf-8") as qf:
                    json.dump(match, qf, indent=2)
            except Exception:
                pass
            messagebox.showinfo("Saved", f"Match saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _show_stats(self):
        return session_ui.show_stats(self)


def main():
    import tkinter as tk
    root = tk.Tk()
    app = SimpleOwareGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()