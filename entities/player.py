import pygame
import os

# ▶ Compute your project root exactly once:
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAYER_ASSET_DIR = os.path.join(PROJECT_ROOT,
                                "assets", "characters", "players")

# ▶ Debug: show where we’re looking and what’s actually there
print(">> PLAYER_ASSET_DIR =", PLAYER_ASSET_DIR)
print(">> Contents:", os.listdir(PLAYER_ASSET_DIR))

import os, pygame

class Player:
    FRAME_WIDTH  = 64
    FRAME_HEIGHT = 64
    # how many frames per direction you actually want
    FRAMES_PER_DIR = 3
    # row-order in the sheet
    DIRECTIONS = ["up", "left", "down", "right"]

    def __init__(self, x, y):
        # compute the absolute path once
        project_root    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sheet_path      = os.path.join(project_root,
                                       "assets", "characters", "players",
                                       "walksheet_1.png")
        self.spritesheet = pygame.image.load(sheet_path).convert_alpha()

        # build animations for each direction
        self.animations = {
            dir_name: self._load_frames(row_idx)
            for row_idx, dir_name in enumerate(self.DIRECTIONS)
        }

        # state
        self.direction   = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 0.30  # seconds between frames

        # starting image
        self.image = self.animations[self.direction][0]
        self.rect  = pygame.Rect(x, y, self.FRAME_WIDTH, self.FRAME_HEIGHT)
        self.speed = 30

    def _load_frames(self, row):
        """Grab FRAMES_PER_DIR frames from the given row."""
        frames = []
        for col in range(self.FRAMES_PER_DIR):
            rect = pygame.Rect(
                col * self.FRAME_WIDTH,
                row * self.FRAME_HEIGHT,
                self.FRAME_WIDTH,
                self.FRAME_HEIGHT
            )
            frames.append(self.spritesheet.subsurface(rect))
        return frames

    def update(self, keys, dt):
        dx = dy = 0
        moving = False

        if keys[pygame.K_w]:
            dy, self.direction, moving = -self.speed * dt, "up",    True
        if keys[pygame.K_s]:
            dy, self.direction, moving =  self.speed * dt, "down",  True
        if keys[pygame.K_a]:
            dx, self.direction, moving = -self.speed * dt, "left",  True
        if keys[pygame.K_d]:
            dx, self.direction, moving =  self.speed * dt, "right", True

        self.rect.x += dx
        self.rect.y += dy

        if moving:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_duration:
                self.frame_index  = (self.frame_index + 1) % self.FRAMES_PER_DIR
                self.frame_timer  = 0
        else:
            self.frame_index = 0

        # pick the correct frame-list based on current direction
        self.image = self.animations[self.direction][self.frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
