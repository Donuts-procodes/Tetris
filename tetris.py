import sys
import os
import json
import random
import pygame
from datetime import datetime

# ----------------------- Settings -----------------------
GRID_W, GRID_H = 10, 20
VISIBLE_NEXT = 3
LINES_PER_LEVEL = 10
INITIAL_FALL_MS = 800
LEVEL_SPEEDUP_MS = 60
MIN_FALL_MS = 70
FPS = 60
FONT_NAME = "consolas"
SCORE_FILE = "tetris_scores.json"
MAX_SAVED_SCORES = 20

SAFE_MARGIN_RATIO = 0.04
MIN_BLOCK = 14
MAX_BLOCK = 52

TITLE_TOP_PAD_RATIO = 0.015
TITLE_MIN_SCALE = 0.65

# Colors
COLORS = {
    "I": (0, 240, 240),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
    "O": (240, 240, 0),
    "S": (0, 240, 0),
    "T": (160, 0, 240),
    "Z": (240, 0, 0),
    "ghost": (150, 150, 155),
    "bg": (12, 14, 20),
    "panel": (20, 24, 32),
    "frame": (85, 100, 130),
    "grid": (45, 55, 70),
    "text": (230, 235, 240),
    "subtext": (160, 170, 185),
    "accent": (255, 205, 90),
    "ok": (110, 220, 160),
    "danger": (255, 115, 115),
    "button_bg": (45, 55, 75),
    "button_hover": (70, 90, 120),
    "button_text": (240, 245, 250),
}

# Shapes (rotations)
SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    "O": [[(1, 0), (2, 0), (1, 1), (2, 1)]] * 4,
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
}


# SRS kicks
def build_srs_kicks():
    kicks_jlstz = {
        (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    }
    kicks_i = {
        (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
    }
    return kicks_jlstz, kicks_i


KICKS_JLSTZ, KICKS_I = build_srs_kicks()


def new_bag():
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ----------------------- Scoreboard persistence -----------------------
def load_scores():
    if not os.path.exists(SCORE_FILE):
        return {"high": 0, "history": []}
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "high" not in data or "history" not in data:
                return {"high": 0, "history": []}
            return data
    except Exception:
        return {"high": 0, "history": []}


def save_scores(data):
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ----------------------- Core classes -----------------------
class Piece:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.rot = 0
        self.x = x
        self.y = y

    def blocks(self, ox=0, oy=0, rot=None):
        r = self.rot if rot is None else rot
        for cx, cy in SHAPES[self.kind][r]:
            yield self.x + cx + ox, self.y + cy + oy

    def clone(self):
        p = Piece(self.kind, self.x, self.y)
        p.rot = self.rot
        return p


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.score = 0
        self.lines = 0
        self.level = 0
        self.game_over = False
        self.tetris_banner_timer = 0
        self.last_clear_rows = 0

    def inside(self, x, y):
        return 0 <= x < GRID_W and y < GRID_H

    def collides(self, piece):
        for x, y in piece.blocks():
            if y < 0:
                continue
            if not self.inside(x, y) or (y >= 0 and self.grid[y][x] is not None):
                return True
        return False

    def lock_piece(self, piece):
        for x, y in piece.blocks():
            if y < 0:
                self.game_over = True
                return []
            self.grid[y][x] = COLORS[piece.kind]
        cleared = self.clear_lines()
        self.update_score_and_level(len(cleared))
        self.last_clear_rows = len(cleared)
        if self.last_clear_rows == 4:
            self.tetris_banner_timer = 1200
        return cleared

    def clear_lines(self):
        full = [
            r
            for r in range(GRID_H)
            if all(self.grid[r][c] is not None for c in range(GRID_W))
        ]
        for r in full:
            del self.grid[r]
            self.grid.insert(0, [None for _ in range(GRID_W)])
        return full

    def update_score_and_level(self, nrows):
        if nrows == 0:
            return
        add = {1: 100, 2: 300, 3: 500, 4: 800}.get(nrows, 0)
        self.score += add * (self.level + 1)
        self.lines += nrows
        new_level = self.lines // LINES_PER_LEVEL
        if new_level > self.level:
            self.level = new_level


# ----------------------- Game -----------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris (Fullscreen Safe)")
        self.clock = pygame.time.Clock()

        # Fullscreen
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        info = pygame.display.Info()
        self.SW, self.SH = info.current_w, info.current_h

        self.compute_layout_and_fonts()

        self.reset()
        self.scores = load_scores()
        self.buttons = {}
        self.build_buttons()

    def compute_layout_and_fonts(self):
        self.margin = int(self.SH * SAFE_MARGIN_RATIO)
        usable_h = self.SH - 2 * self.margin
        block = clamp(usable_h // GRID_H, MIN_BLOCK, MAX_BLOCK)

        def layout_for(block_size, title_scale_guess=1.0):
            base = clamp(block_size, 16, 32)
            font_big = pygame.font.SysFont(FONT_NAME, int(base * 1.6), bold=True)
            font_huge = pygame.font.SysFont(
                FONT_NAME, int(base * 2.2 * title_scale_guess), bold=True
            )

            play_w_px = block_size * GRID_W
            play_h_px = block_size * GRID_H
            panel_w = clamp(int(self.SW * 0.16), 180, 340)
            total_w = panel_w * 2 + play_w_px + self.margin * 2

            title_surface = font_huge.render("TETRIS", True, COLORS["accent"])
            title_h = title_surface.get_height()
            title_top_pad = int(self.SH * TITLE_TOP_PAD_RATIO)

            play_top = self.margin + title_h + title_top_pad
            total_height_needed = play_top + play_h_px + self.margin

            return {
                "block": block_size,
                "play_w_px": play_w_px,
                "play_h_px": play_h_px,
                "panel_w": panel_w,
                "total_w": total_w,
                "title_surface": title_surface,
                "title_h": title_h,
                "play_top": play_top,
                "total_height_needed": total_height_needed,
                "font_base": base,
                "font_big": font_big,
                "font_huge": font_huge,
            }

        title_scale = 1.0
        L = layout_for(block, title_scale)

        def fits(L):
            return L["total_w"] <= self.SW and L["total_height_needed"] <= self.SH

        while L["total_w"] > self.SW and block > MIN_BLOCK:
            block -= 1
            L = layout_for(block, title_scale)
        while L["total_height_needed"] > self.SH and block > MIN_BLOCK:
            block -= 1
            L = layout_for(block, title_scale)
        while L["total_height_needed"] > self.SH and title_scale > TITLE_MIN_SCALE:
            title_scale *= 0.95
            L = layout_for(block, title_scale)
        while not fits(L) and block > MIN_BLOCK:
            block -= 1
            L = layout_for(block, max(title_scale, TITLE_MIN_SCALE))

        self.block = L["block"]
        self.play_w_px = L["play_w_px"]
        self.play_h_px = L["play_h_px"]
        self.panel_w = L["panel_w"]
        self.title_surface = L["title_surface"]

        total_w = self.panel_w * 2 + self.play_w_px + self.margin * 2
        extra_x = max(0, (self.SW - total_w) // 2)
        self.left_panel_x = self.margin + extra_x
        self.play_x = self.left_panel_x + self.panel_w + self.margin
        self.right_panel_x = self.play_x + self.play_w_px + self.margin

        self.top_y = L["play_top"]
        self.title_top = self.margin

        self.font = pygame.font.SysFont(FONT_NAME, clamp(self.block, 16, 32))
        self.font_small = pygame.font.SysFont(
            FONT_NAME, int(clamp(self.block, 16, 32) * 0.7)
        )
        self.font_big = L["font_big"]
        self.font_huge = L["font_huge"]

    def reset(self):
        self.board = Board()
        self.bag = new_bag()
        self.queue = []
        while len(self.queue) < VISIBLE_NEXT:
            self.refill_bag()
        self.current = self.spawn_piece()
        self.hold = None
        self.hold_locked = False
        self.drop_timer = 0
        self.fall_ms = INITIAL_FALL_MS
        self.paused = False
        self.floaters = []

    def build_buttons(self):
        pad = int(self.block * 0.6)
        btn_w = self.panel_w - 2 * pad
        btn_h = int(self.block * 1.3)
        spacing = int(self.block * 0.45)
        max_bottom = self.top_y + self.play_h_px - pad

        y2 = max_bottom - btn_h
        y1 = y2 - spacing - btn_h
        x = self.right_panel_x + pad

        min_y = self.top_y + pad
        if y1 < min_y:
            available = max_bottom - min_y
            btn_h = max(22, (available - spacing) // 2)
            y1 = min_y
            y2 = y1 + btn_h + spacing

        self.buttons = {
            "restart": pygame.Rect(x, y1, btn_w, btn_h),
            "exit": pygame.Rect(x, y2, btn_w, btn_h),
        }

    def refill_bag(self):
        if not self.bag:
            self.bag = new_bag()
        self.queue.append(self.bag.pop())

    def spawn_piece(self):
        if not self.queue:
            self.refill_bag()
        kind = self.queue.pop(0)
        while len(self.queue) < VISIBLE_NEXT:
            self.refill_bag()
        p = Piece(kind, x=3, y=-2)
        if self.board.collides(p):
            self.board.game_over = True
        return p

    # ---------------- Input ----------------
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.quit_game()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.quit_game()
                if self.board.game_over:
                    if e.key == pygame.K_r:
                        self.end_run_record()
                        self.reset()
                        self.build_buttons()
                    continue
                if e.key == pygame.K_p:
                    self.paused = not self.paused
                    continue
                if self.paused:
                    continue
                if e.key == pygame.K_LEFT:
                    self.try_move(-1, 0)
                elif e.key == pygame.K_RIGHT:
                    self.try_move(1, 0)
                elif e.key == pygame.K_DOWN:
                    self.soft_drop()
                elif e.key in (pygame.K_UP, pygame.K_x):
                    self.rotate(+1)
                elif e.key == pygame.K_z:
                    self.rotate(-1)
                elif e.key == pygame.K_SPACE:
                    self.hard_drop()
                elif e.key == pygame.K_c:
                    self.hold_piece()

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.buttons["restart"].collidepoint(mouse_pos):
                    self.end_run_record()
                    self.reset()
                    self.build_buttons()
                elif self.buttons["exit"].collidepoint(mouse_pos):
                    self.quit_game()

    def try_move(self, dx, dy):
        t = self.current.clone()
        t.x += dx
        t.y += dy
        if not self.board.collides(t):
            self.current = t

    def rotate(self, direction):
        p = self.current
        r_from = p.rot
        r_to = (p.rot + direction) % 4
        kicks = KICKS_I if p.kind == "I" else KICKS_JLSTZ
        for dx, dy in kicks.get((r_from, r_to), [(0, 0)]):
            t = p.clone()
            t.rot = r_to
            t.x += dx
            t.y += dy
            if not self.board.collides(t):
                self.current = t
                return

    def soft_drop(self):
        self.try_move(0, 1)

    def hard_drop(self):
        dist = 0
        t = self.current.clone()
        while not self.board.collides(t):
            t.y += 1
            dist += 1
        dist -= 1
        if dist > 0:
            self.current.y += dist
        self.lock_current()

    def lock_current(self):
        self.board.lock_piece(self.current)
        if self.board.last_clear_rows > 0:
            text = {1: "+100", 2: "DOUBLE! +300", 3: "TRIPLE! +500", 4: "TETRIS! +800"}[
                self.board.last_clear_rows
            ]
            self.spawn_floater(
                text,
                color=(
                    COLORS["ok"] if self.board.last_clear_rows < 4 else COLORS["accent"]
                ),
            )
        self.update_speed()
        self.hold_locked = False
        if not self.board.game_over:
            self.current = self.spawn_piece()
        else:
            self.end_run_record()

    def update_speed(self):
        self.fall_ms = max(
            MIN_FALL_MS, INITIAL_FALL_MS - self.board.level * LEVEL_SPEEDUP_MS
        )

    def hold_piece(self):
        if self.hold_locked:
            return
        if self.hold is None:
            self.hold = self.current.kind
            self.current = self.spawn_piece()
        else:
            self.hold, self.current.kind = self.current.kind, self.hold
            self.current.rot = 0
            self.current.x, self.current.y = 3, -2
            if self.board.collides(self.current):
                self.board.game_over = True
                self.end_run_record()
        self.hold_locked = True

    # Floaters
    def spawn_floater(self, text, color):
        cx = self.play_x + self.play_w_px // 2
        cy = self.top_y + self.play_h_px // 3
        self.floaters.append(
            {
                "text": text,
                "x": cx,
                "y": cy,
                "vy": -0.08 * self.block,
                "life": 1000,
                "color": color,
            }
        )

    def update_floaters(self, dt):
        self.floaters = [
            {**f, "y": f["y"] + f["vy"] * dt, "life": f["life"] - dt}
            for f in self.floaters
            if f["life"] - dt > 0
        ]

    # Gravity
    def tick_gravity(self, dt):
        if self.board.game_over or self.paused:
            return
        self.drop_timer += dt
        while self.drop_timer >= self.fall_ms:
            self.drop_timer -= self.fall_ms
            t = self.current.clone()
            t.y += 1
            if self.board.collides(t):
                self.lock_current()
                break
            else:
                self.current = t

        if self.board.tetris_banner_timer > 0:
            self.board.tetris_banner_timer = max(0, self.board.tetris_banner_timer - dt)

    # ---------------- Rendering helpers ----------------
    def draw_panel(self, rect):
        pygame.draw.rect(self.screen, COLORS["panel"], rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["frame"], rect, width=2, border_radius=12)

    def draw_cell(self, gx, gy, color, alpha=255):
        x = self.play_x + gx * self.block
        y = self.top_y + gy * self.block
        r = pygame.Rect(x + 1, y + 1, self.block - 2, self.block - 2)
        surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        surf.fill((*color, alpha))
        pygame.draw.rect(surf, (255, 255, 255, 40), (0, 0, r.width, 3))
        pygame.draw.rect(surf, (0, 0, 0, 50), (0, r.height - 3, r.width, 3))
        self.screen.blit(surf, (r.x, r.y))

    def draw_grid(self):
        frame = pygame.Rect(
            self.play_x - 3, self.top_y - 3, self.play_w_px + 6, self.play_h_px + 6
        )
        pygame.draw.rect(self.screen, COLORS["frame"], frame, width=3, border_radius=10)
        for x in range(GRID_W + 1):
            px = self.play_x + x * self.block
            pygame.draw.line(
                self.screen,
                COLORS["grid"],
                (px, self.top_y),
                (px, self.top_y + self.play_h_px),
            )
        for y in range(GRID_H + 1):
            py = self.top_y + y * self.block
            pygame.draw.line(
                self.screen,
                COLORS["grid"],
                (self.play_x, py),
                (self.play_x + self.play_w_px, py),
            )

    def draw_board(self):
        for y in range(GRID_H):
            for x in range(GRID_W):
                c = self.board.grid[y][x]
                if c is not None:
                    self.draw_cell(x, y, c)

    def draw_piece(self, piece, ghost=False):
        color = COLORS["ghost"] if ghost else COLORS[piece.kind]
        alpha = 110 if ghost else 255
        for x, y in piece.blocks():
            if y >= 0:
                self.draw_cell(x, y, color, alpha)

    def draw_ghost(self):
        g = self.current.clone()
        while not self.board.collides(g):
            g.y += 1
        g.y -= 1
        if g.y >= self.current.y:
            self.draw_piece(g, ghost=True)

    def blit_label(self, text, x, y, color):
        surf = self.font_small.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def blit_value(self, text, x, y, color=COLORS["text"]):
        surf = self.font_big.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def blit_text(self, text, x, y, color=COLORS["text"]):
        surf = self.font_small.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def draw_title(self):
        self.screen.blit(self.title_surface, (self.left_panel_x, self.title_top))

    def draw_left_panel(self):
        rect = pygame.Rect(self.left_panel_x, self.top_y, self.panel_w, self.play_h_px)
        self.draw_panel(rect)
        pad = int(self.block * 0.6)
        x = rect.x + pad
        y = rect.y + pad

        self.blit_label("SCORE", x, y, COLORS["subtext"])
        y += int(self.block * 0.8)
        self.blit_value(str(self.board.score), x, y)
        y += int(self.block * 1.2)

        self.blit_label("LEVEL", x, y, COLORS["subtext"])
        y += int(self.block * 0.8)
        self.blit_value(str(self.board.level), x, y)
        y += int(self.block * 1.2)

        self.blit_label("LINES", x, y, COLORS["subtext"])
        y += int(self.block * 0.8)
        self.blit_value(str(self.board.lines), x, y)
        y += int(self.block * 1.3)

        self.blit_label("CONTROLS", x, y, COLORS["subtext"])
        y += int(self.block * 0.8)
        for line in [
            "←/→ Move",
            "↓ Soft drop",
            "↑/X Rotate CW",
            "Z Rotate CCW",
            "Space Hard drop",
            "C Hold",
            "P Pause",
            "R Restart",
            "Esc Quit",
        ]:
            self.blit_text(line, x, y)
            y += int(self.block * 0.85)

        y += int(self.block * 0.6)
        self.blit_label("HOLD", x, y, COLORS["subtext"])
        y += int(self.block * 0.6)
        self.draw_mini_box(x, y, kind=self.hold)

    def draw_right_panel(self):
        rect = pygame.Rect(self.right_panel_x, self.top_y, self.panel_w, self.play_h_px)
        self.draw_panel(rect)
        pad = int(self.block * 0.6)
        x = rect.x + pad
        y = rect.y + pad

        # NEXT header
        self.blit_label("NEXT", x, y, COLORS["subtext"])
        y += int(self.block * 0.6)
        next_top = y
        next_box_w = self.panel_w - int(self.block * 1.2)

        # Reserve space for scoreboard + buttons
        btn_h = int(self.block * 1.3)
        spacing = int(self.block * 0.45)
        buttons_reserved = pad + (btn_h * 2 + spacing) + pad
        sb_h_target = int(self.play_h_px * 0.28)

        # Compute max height available for the next box
        max_next_area_h = (
            self.play_h_px - (next_top - self.top_y) - buttons_reserved - sb_h_target
        )
        max_next_area_h = max(max_next_area_h, int(self.block * 2.6))

        # Slot height for exactly 3 items (smaller size)
        slot_h = int(self.block * 2.8)
        total_next_h = slot_h * VISIBLE_NEXT
        if total_next_h > max_next_area_h:
            scale = max_next_area_h / float(total_next_h)
            slot_h = max(22, int(slot_h * scale))
            total_next_h = slot_h * VISIBLE_NEXT

        self.draw_next_list(x, next_top, next_box_w, slot_h, size_scale=0.55)

        # Scoreboard sits above buttons; flex height
        sb_y = self.top_y + self.play_h_px - buttons_reserved - sb_h_target
        sb_h = sb_h_target
        min_sb_h = int(self.block * 3.2)
        if sb_y < next_top + total_next_h + pad:
            sb_y = next_top + total_next_h + pad
            sb_h = max(
                min_sb_h, (self.top_y + self.play_h_px - buttons_reserved) - sb_y
            )

        self.draw_scoreboard(rect.x + pad, sb_y, rect.width - 2 * pad, sb_h)

        self.build_buttons()
        self.draw_buttons()

    def draw_mini_box(self, x, y, kind=None):
        box_w = self.panel_w - int(self.block * 1.2)
        box_h = int(self.block * 3.0)
        rect = pygame.Rect(x, y, box_w, box_h)
        pygame.draw.rect(self.screen, COLORS["frame"], rect, width=2, border_radius=8)
        if kind:
            self.draw_mini_piece(
                kind,
                rect.x + int(self.block * 0.45),
                rect.y + int(self.block * 0.45),
                size_scale=0.6,
            )

    def draw_next_list(self, x, y, box_w, slot_h, size_scale=0.55):
        rect = pygame.Rect(x, y, box_w, slot_h * VISIBLE_NEXT)
        pygame.draw.rect(self.screen, COLORS["frame"], rect, width=2, border_radius=8)
        yy = y + int(self.block * 0.35)
        for kind in self.queue[:VISIBLE_NEXT]:
            self.draw_mini_piece(
                kind, x + int(self.block * 0.45), yy, size_scale=size_scale
            )
            yy += slot_h

    def draw_mini_piece(self, kind, x, y, size_scale=0.65):
        cells = SHAPES[kind][0]
        minx = min(cx for cx, cy in cells)
        miny = min(cy for cx, cy in cells)
        norm = [(cx - minx, cy - miny) for cx, cy in cells]
        size = int(self.block * size_scale)
        for cx, cy in norm:
            r = pygame.Rect(x + cx * size, y + cy * size, size - 3, size - 3)
            pygame.draw.rect(self.screen, COLORS[kind], r, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), r, width=1, border_radius=5)

    def draw_scoreboard(self, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        sub = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(sub, (255, 255, 255, 20), (0, 0, w, h), border_radius=8)
        pygame.draw.rect(sub, COLORS["frame"], (0, 0, w, h), width=2, border_radius=8)

        title = self.font_small.render("SCOREBOARD", True, COLORS["subtext"])
        sub.blit(title, (int(self.block * 0.3), int(self.block * 0.3)))

        hs = self.scores.get("high", 0)
        hs_surf = self.font_small.render(f"High: {hs}", True, COLORS["text"])
        sub.blit(hs_surf, (int(self.block * 0.3), int(self.block * 1.2)))

        line_h = int(self.block * 0.9)
        start_y = int(self.block * 2.0)
        max_rows = max(1, (h - start_y - int(self.block * 0.3)) // line_h)
        hist = self.scores.get("history", [])[-max_rows:][::-1]

        yy = start_y
        for item in hist:
            sc = item.get("score", 0)
            lv = item.get("level", 0)
            line = f"L{lv}  {sc}"
            txt = self.font_small.render(line, True, COLORS["text"])
            sub.blit(txt, (int(self.block * 0.3), yy))
            yy += line_h

        self.screen.blit(sub, (x, y))

    def draw_banner(self):
        if self.board.tetris_banner_timer <= 0:
            return
        t = self.board.tetris_banner_timer / 1200.0
        alpha = int(255 * clamp(t, 0.2, 1.0))
        surf = self.font_huge.render("TETRIS!", True, COLORS["accent"])
        banner = surf.convert_alpha()
        banner.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        x = self.play_x + (self.play_w_px - banner.get_width()) // 2
        y = self.top_y + int(self.play_h_px * 0.12)
        self.screen.blit(banner, (x, y))

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for key, label in (("restart", "Restart"), ("exit", "Exit")):
            rect = self.buttons[key]
            hover = rect.collidepoint(mouse_pos)
            color = COLORS["button_hover"] if hover else COLORS["button_bg"]
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(
                self.screen, COLORS["frame"], rect, width=2, border_radius=10
            )

            txt = self.font_big.render(label, True, COLORS["button_text"])
            self.screen.blit(
                txt,
                (
                    rect.x + (rect.w - txt.get_width()) // 2,
                    rect.y + (rect.h - txt.get_height()) // 2,
                ),
            )

    def draw_center_messages(self):
        if self.paused and not self.board.game_over:
            txt = self.font_big.render("PAUSED", True, COLORS["subtext"])
            self.screen.blit(
                txt,
                (
                    self.play_x + (self.play_w_px - txt.get_width()) // 2,
                    self.top_y + (self.play_h_px - txt.get_height()) // 2,
                ),
            )
        if self.board.game_over:
            overlay = pygame.Surface((self.play_w_px, self.play_h_px), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (self.play_x, self.top_y))
            t1 = self.font_huge.render("GAME OVER", True, COLORS["danger"])
            t2 = self.font_big.render("Press R or click Restart", True, COLORS["text"])
            cx = self.play_x + (self.play_w_px - t1.get_width()) // 2
            cy = self.top_y + int(self.play_h_px * 0.35)
            self.screen.blit(t1, (cx, cy))
            self.screen.blit(
                t2,
                (
                    self.play_x + (self.play_w_px - t2.get_width()) // 2,
                    cy + t1.get_height() + int(self.block * 0.8),
                ),
            )

    def render(self):
        self.screen.fill(COLORS["bg"])
        self.draw_title()
        self.draw_left_panel()
        self.draw_right_panel()
        self.draw_grid()
        self.draw_board()
        if not self.board.game_over:
            self.draw_ghost()
            self.draw_piece(self.current)
        self.draw_banner()
        for f in self.floaters:
            s = self.font_big.render(f["text"], True, f["color"])
            alpha = clamp(int(255 * (f["life"] / 1000.0)), 0, 255)
            s2 = s.convert_alpha()
            s2.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(s2, (int(f["x"] - s2.get_width() / 2), int(f["y"])))
        self.draw_center_messages()
        pygame.display.flip()

    def end_run_record(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {"time": now, "score": self.board.score, "level": self.board.level}
        data = load_scores()
        data["high"] = max(data.get("high", 0), self.board.score)
        hist = data.get("history", [])
        hist.append(entry)
        if len(hist) > MAX_SAVED_SCORES:
            hist = hist[-MAX_SAVED_SCORES:]
        data["history"] = hist
        save_scores(data)
        self.scores = data

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.tick_gravity(dt)
            self.update_floaters(dt)
            self.render()


if __name__ == "__main__":
    Game().run()
