# core/explosion.py
import pygame
import os

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frame_duration=0.05):
        super().__init__()
        # load the full strip
        sheet_path = os.path.join("assets", "fx", "Explosion1.png")
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()

        # assume square frames laid out side-by-side:
        frame_count = sheet_w // sheet_h
        self.frames = []
        for i in range(frame_count):
            rect = pygame.Rect(i * sheet_h, 0, sheet_h, sheet_h)
            # subsurface + .copy() to get an independent Surface
            self.frames.append(sheet.subsurface(rect).copy())

        # animation state
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = frame_duration

        # start image & rect
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return
            self.image = self.frames[self.frame_index]

    def draw(self, surface, cam_x=0, cam_y=0, zoom=1.0):
        # scale + position just like before
        sx = int((self.rect.centerx - cam_x) * zoom)
        sy = int((self.rect.centery - cam_y) * zoom)
        img = pygame.transform.rotozoom(self.image, 0, zoom)
        r = img.get_rect(center=(sx, sy))
        surface.blit(img, r)
