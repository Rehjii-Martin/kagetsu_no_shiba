# core/projectile.py
import os, math, pygame
from core.explosion import Explosion  

class Projectile(pygame.sprite.Sprite):
    def __init__(self, *groups, start_pos=None, direction=None, speed=800, max_range=800, image_path=None, **kwargs):
        super().__init__()
        if start_pos is None or direction is None:
            raise ValueError("start_pos and direction must be provided")
        self.x, self.y = start_pos
        self.dx, self.dy = direction
        self.speed = speed
        self.max_range = max_range
        self.travelled = 0
        self.is_circle = False

        if image_path is None:
            image_path = os.path.join("assets", "projectiles", "default_blast.png")

        if os.path.exists(image_path):
            raw_image = pygame.image.load(image_path).convert_alpha()
            raw_image = pygame.transform.smoothscale(raw_image, (40, 32))
            angle = math.degrees(math.atan2(-self.dy, self.dx))
            rotated_image = pygame.transform.rotate(raw_image, angle)
            self.base_image = rotated_image
            self.image = rotated_image
            tip_offset = 12
            shift_x = -self.dx * tip_offset
            shift_y = -self.dy * tip_offset
            self.rect = self.image.get_rect(center=(self.x + shift_x, self.y + shift_y))
        else:
            self.radius = 8
            self.is_circle = True
            self.color = (255, 220, 50)
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt, walls_group=None, enemies_group=None, explosions_group=None):
        dx_pixels = self.dx * self.speed * dt
        dy_pixels = self.dy * self.speed * dt
        self.x += dx_pixels
        self.y += dy_pixels
        self.travelled += math.hypot(dx_pixels, dy_pixels)

        if not self.is_circle:
            tip_offset = 12
            shift_x = -self.dx * tip_offset
            shift_y = -self.dy * tip_offset
            self.rect.center = (int(self.x + shift_x), int(self.y + shift_y))
        else:
            self.rect.center = (int(self.x), int(self.y))

        if self.travelled >= self.max_range:
            if explosions_group is not None:
                explosions_group.add(Explosion(self.x, self.y))
            self.kill()
            return

        if walls_group:
            for wall in walls_group:
                if self.rect.colliderect(wall.rect):
                    print(f"[COLLISION] Projectile hit wall at {wall.rect}")
                    if explosions_group is not None:
                        # if you want a slower/faster animation, pass it as the 3rd positional arg:
                        # e.g. frame_duration=0.1 would be Explosion(x, y, 0.1)
                        explosions_group.add(Explosion(self.rect.centerx,
                                                      self.rect.centery,
                                                      0.08))
                    self.kill()
                    return
            else:
                print(f"[DEBUG] Projectile at {self.rect.center} did not collide with any wall.")

      
        if enemies_group:
            hit = pygame.sprite.spritecollide(self, enemies_group, False)
            for enemy in hit:
                enemy.take_damage(10)
                if explosions_group is not None:
                    explosions_group.add(Explosion(self.rect.centerx, self.rect.centery))
                self.kill()
                return

    def draw(self, screen, cam_x=0, cam_y=0, zoom=1.0):
        screen_x = int((self.x - cam_x) * zoom)
        screen_y = int((self.y - cam_y) * zoom)

        if self.is_circle:
            radius = max(1, int(self.radius * zoom))
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), radius)
        else:
            scaled_image = pygame.transform.rotozoom(self.base_image, 0, zoom)
            rect = scaled_image.get_rect(center=(screen_x, screen_y))
            screen.blit(scaled_image, rect)
