import tkinter as tk
from tkinter import messagebox
from board import Board
import rules

PIT_RADIUS = 56          
PIT_SPACING = 22
CANVAS_PAD_X = 28
FLASH_MS = 140  


class SimpleOwareGUI:
    def __init__(self, root):
        self.root = root
        root.title("Oware - Simple GUI")

        self.board = Board()  
        self.player = 0
        self.animating = False

        self.top_score = tk.Label(root, text="P1: 0", font=("Helvetica", 14, "bold"))
        self.top_score.pack(pady=(6, 0))

        n = self.board.pits_per_side
        width = (PIT_RADIUS * 2 + PIT_SPACING) * n + CANVAS_PAD_X * 2
        height = 320
        self.canvas = tk.Canvas(root, width=width, height=height, bg="#f8f8fb")
        self.canvas.pack(padx=8, pady=8)

        self.bottom_score = tk.Label(root, text="P0: 0", font=("Helvetica", 14, "bold"))
        self.bottom_score.pack(pady=(0, 6))

        self.status = tk.Label(root, text="Player 0's turn", font=("Helvetica", 10))
        self.status.pack()

        self.pit_map = {}  

        self._build_board_graphics()
        self.canvas.tag_bind("pit", "<Button-1>", self._on_pit_click)
        self._draw_board()

    def _build_board_graphics(self):
        n = self.board.pits_per_side
        pit_d = PIT_RADIUS * 2
        total_width = n * pit_d + (n - 1) * PIT_SPACING
        start_x = (int(self.canvas['width']) - total_width) // 2 + PIT_RADIUS

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
        self.status.config(text=f"Player {self.player}'s turn")

        legal = rules.legal_moves(self.board, self.player)
        for idx, (pit, _, _, _) in self.pit_map.items():
            if idx in legal:
                self.canvas.itemconfigure(pit, width=4, outline="#2e8b57")
            else:
                owner = self.board.pit_owner(idx)
                outline = "#653" if owner == 0 else "#345"
                self.canvas.itemconfigure(pit, width=3, outline=outline)

    def _on_pit_click(self, event):
        if self.animating:
            return
        item = self.canvas.find_withtag("current")
        if not item:
            return
        tags = self.canvas.gettags(item)
        pit_tag = next((t for t in tags if t.startswith("pit") and t != "pit"), None)
        if not pit_tag:
            return
        pit_idx = int(pit_tag[3:])
        legal = rules.legal_moves(self.board, self.player)
        if pit_idx not in legal:
            pit, _, _, _ = self.pit_map[pit_idx]
            old = self.canvas.itemcget(pit, "outline")
            self.canvas.itemconfigure(pit, outline="#ff0000", width=4)
            self.root.after(220, lambda: self.canvas.itemconfigure(pit, outline=old, width=3))
            return
        self._animate_and_apply(pit_idx)

    def _animate_and_apply(self, pit_index):
        seeds = self.board.pits[pit_index].stones
        seq = []
        idx = pit_index
        for _ in range(seeds):
            idx = (idx + 1) % self.board.total_pits
            seq.append(idx)

        self.animating = True
        self.canvas.config(cursor="watch")

        self._flash_sequence(seq, 0, pit_index)

    def _flash_sequence(self, seq, pos, source_pit):
        if pos >= len(seq):
            ok = rules.apply_move(self.board, self.player, source_pit)
            if not ok:
                messagebox.showerror("Illegal move", "Move rejected by rules.")
            else:
                if self.board.is_empty_side(0) or self.board.is_empty_side(1):
                    self._endgame_sweep()
                    return
                self.player = 1 - self.player
            self.animating = False
            self.canvas.config(cursor="")
            self._draw_board()
            return

        pit_idx = seq[pos]
        pit, _, _, _ = self.pit_map[pit_idx]
        old_fill = self.canvas.itemcget(pit, "fill")
        self.canvas.itemconfigure(pit, fill="#fff3c6")
        self.root.after(FLASH_MS, lambda: self._unflash_and_continue(pit, old_fill, seq, pos, source_pit))

    def _unflash_and_continue(self, pit, old_fill, seq, pos, source_pit):
        self.canvas.itemconfigure(pit, fill=old_fill)
        self.root.after(60, lambda: self._flash_sequence(seq, pos + 1, source_pit))

    def _endgame_sweep(self):
        p0 = sum(self.board.pits[i].stones for i in self.board.player_pit_indices(0))
        p1 = sum(self.board.pits[i].stones for i in self.board.player_pit_indices(1))
        if p0 > 0:
            self.board.scores[0] += p0
            for i in self.board.player_pit_indices(0):
                self.board.pits[i].stones = 0
        if p1 > 0:
            self.board.scores[1] += p1
            for i in self.board.player_pit_indices(1):
                self.board.pits[i].stones = 0
        self._draw_board()
        if self.board.scores[0] > self.board.scores[1]:
            msg = f"Player 0 wins {self.board.scores[0]} - {self.board.scores[1]}"
        elif self.board.scores[1] > self.board.scores[0]:
            msg = f"Player 1 wins {self.board.scores[1]} - {self.board.scores[0]}"
        else:
            msg = f"Draw: {self.board.scores[0]} - {self.board.scores[1]}"
        messagebox.showinfo("Game Over", msg)
        self.animating = True

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleOwareGUI(root)
    root.mainloop()