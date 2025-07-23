import pygame
class ExplosionSystem:
    def __init__(self):
        self.explosions = pygame.sprite.Group()
    def update(self, dt):
        self.explosions.update(dt)
    def draw(self, surface, camera):
        for ex in self.explosions:
            ex.draw(surface, camera.offset_x, camera.offset_y, camera.zoom)
