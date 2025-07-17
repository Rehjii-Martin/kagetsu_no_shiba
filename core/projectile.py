# core/projectile.py
import os, math, pygame
from core.explosion import Explosion  

class Projectile(pygame.sprite.Sprite):
    def __init__(self, *groups, start_pos=None, direction=None, speed=800, max_range=800, image_path=None, **kwargs):
        """
        start_pos   = (x, y) center where the blast spawns
        direction   = (dx, dy) should be normalized (length 1)
        speed       = pixels per second
        max_range   = how many pixels it can travel before disappearing
        image_path  = optional path to a sprite; if None, draws a circle
        """
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

        # Always shift the rect to match the tip of the image
        if not self.is_circle:
            tip_offset = 12
            shift_x = -self.dx * tip_offset
            shift_y = -self.dy * tip_offset
            self.rect.center = (int(self.x + shift_x), int(self.y + shift_y))
        else:
            self.rect.center = (int(self.x), int(self.y))

        if self.travelled >= self.max_range:
            if explosions_group:
                explosions_group.add(Explosion(self.x, self.y))
            self.kill()
            return

        if walls_group and any(self.rect.colliderect(r) for r in walls_group):
            if explosions_group:
                explosions_group.add(Explosion(self.x, self.y))
            self.kill()
            return

        if enemies_group:
            hit = pygame.sprite.spritecollide(self, enemies_group, False)
            for enemy in hit:
                enemy.take_damage(10)
                if explosions_group:
                    explosions_group.add(Explosion(self.x, self.y))
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
