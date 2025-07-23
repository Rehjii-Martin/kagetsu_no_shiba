import pygame
class PlayerController:
    
    def __init__(self, player, collision_rects, map_rect):
        self.player = player
        self.collision_rects = collision_rects
        self.map_rect = map_rect
    
    def update(self, dt, keys, projectile_system, chat_active):
        if not chat_active:
            self.player.update(keys, dt, self.map_rect, self.collision_rects)
        
        if not chat_active and keys[pygame.K_SPACE]:
            proj = self.player.try_shoot(keys)
            if proj:
                projectile_system.add(proj)
                self.player.energy = max(0, self.player.energy - 5)
        
        if not chat_active and keys[pygame.K_q]:
            self.player.try_dash(dt, self.collision_rects, self.map_rect)
    
    def draw(self, surface, camera):
        self.player.draw(surface, camera)