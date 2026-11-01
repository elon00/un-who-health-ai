"""Bounded, deterministic B3/S23 simulation with toroidal boundaries; not consensus."""
import hashlib
import json


class ConwayAutomatonEngine:
    def __init__(self, w=8, h=8, grid=None):
        if type(w) is not int or type(h) is not int or not 3 <= w <= 256 or not 3 <= h <= 256:
            raise ValueError("Grid dimensions must be integers from 3 to 256")
        self.w, self.h = w, h
        candidate = grid if grid is not None else [[0] * w for _ in range(h)]
        if (len(candidate) != h or any(len(row) != w for row in candidate)
                or any(type(cell) is not int or cell not in (0, 1) for row in candidate for cell in row)):
            raise ValueError("Grid must contain exactly h rows of w binary integer cells")
        self.grid = [list(row) for row in candidate]
        self.generation = 0

    def snapshot(self):
        return {"width": self.w, "height": self.h, "generation": self.generation,
                "grid": [row[:] for row in self.grid]}

    def state_hash(self):
        state = {"width": self.w, "height": self.h, "grid": self.grid}
        return hashlib.sha256(json.dumps(state, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def step(self):
        following = [[0] * self.w for _ in range(self.h)]
        for r in range(self.h):
            for c in range(self.w):
                neighbors = sum(self.grid[(r+dr) % self.h][(c+dc) % self.w]
                                for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc)
                following[r][c] = int(neighbors == 3 or self.grid[r][c] == 1 and neighbors == 2)
        self.grid = following
        self.generation += 1
        return self.state_hash()
