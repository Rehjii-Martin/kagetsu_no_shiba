# core/explosion.py
import pygame
import os

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, duration=0.4):
        super().__init__()
        placeholder_path = os.path.join("assets", "fx", "placeholder_explosion.png")

        if os.path.exists(placeholder_path):
            img = pygame.image.load(placeholder_path).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (48, 48))
        else:
            self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 0), (24, 24), 24)

        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.duration = duration

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

    def draw(self, surface, cam_x=0, cam_y=0, zoom=1.0):
        screen_x = int((self.rect.centerx - cam_x) * zoom)
        screen_y = int((self.rect.centery - cam_y) * zoom)
        scaled_image = pygame.transform.rotozoom(self.image, 0, zoom)
        rect = scaled_image.get_rect(center=(screen_x, screen_y))
        surface.blit(scaled_image, rect)
