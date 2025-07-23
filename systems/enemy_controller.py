class EnemyController:
    def __init__(self, enemies, collision_rects, map_rect):
        self.enemies = enemies
        self.collision_rects = collision_rects
        self.map_rect = map_rect
    def update(self, dt, player):
        for e in self.enemies:
            e.update(dt, player, self.collision_rects, self.map_rect)
        for e in self.enemies:
            if player.rect.colliderect(e.rect):
                cd = getattr(e, '_hit_cooldown', 0.0)
                if cd <= 0.0:
                    player.health -= 10
                    e._hit_cooldown = 0.5
                else:
                    e._hit_cooldown = cd - dt
    def draw(self, surface, camera):
        for e in self.enemies:
            e.draw(surface, camera)