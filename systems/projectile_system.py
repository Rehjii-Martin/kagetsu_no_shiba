import pygame

class ProjectileSystem:
    def __init__(self, walls, enemies, explosion_system, players=None):
        self.projectiles = pygame.sprite.Group()
        self.walls       = walls
        self.enemies     = enemies
        self.players     = players
        self.explosions  = explosion_system.explosions

    def add(self, projectile):
        self.projectiles.add(projectile)

    def update(self, dt):
        self.projectiles.update(
            dt,
            walls_group       = self.walls,
            enemies_group     = self.enemies,
            players_group     = self.players,
            explosions_group  = self.explosions
        )

    def draw(self, surface, camera):
        for p in self.projectiles:
            p.draw(surface,
                   camera.offset_x,
                   camera.offset_y,
                   camera.zoom)
