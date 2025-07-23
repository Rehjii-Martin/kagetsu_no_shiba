# File: systems/projectile_system.py
import pygame


class ProjectileSystem:
    def __init__(self, walls, enemies, explosion_system):
        self.projectiles = pygame.sprite.Group()
        self.walls       = walls
        self.enemies     = enemies
        self.explosions  = explosion_system.explosions

    # external API
    def add(self, projectile):
        self.projectiles.add(projectile)

    # frame update
    def update(self, dt):
        self.projectiles.update(
            dt,
            walls_group       = self.walls,
            enemies_group     = self.enemies,
            explosions_group  = self.explosions
        )

    # draw all
    def draw(self, surface, camera):
        for p in self.projectiles:
            p.draw(surface,
                   camera.offset_x,
                   camera.offset_y,
                   camera.zoom)
