# core/projectile.py

import os, math, pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, *groups, start_pos=None, direction=None, speed=50, max_range=800, image_path=None, **kwargs):
        """
        start_pos   = (x, y) center where the blast spawns
        direction   = (dx, dy) should be normalized (length 1)
        speed       = pixels per second
        max_range   = how many pixels it can travel before disappearing
        image_path  = optional path to a sprite; if None, draws a circle
        """
        super().__init__(*groups, **kwargs)
        if start_pos is None or direction is None:
            raise ValueError("start_pos and direction must be provided")
        self.x, self.y = start_pos
        self.dx, self.dy = direction
        self.speed = speed
        self.max_range = max_range
        self.travelled = 0

         # Fallback to default image if not provided
        if image_path is None:
            image_path = os.path.join("assets", "projectiles", "default_blast.png")

        # load image or default circle
        if os.path.exists(image_path):
            raw_image = pygame.image.load(image_path).convert_alpha()
            raw_image = pygame.transform.smoothscale(raw_image, (40, 32))
            angle = math.degrees(math.atan2(-self.dy, self.dx))
            rotated_image = pygame.transform.rotate(raw_image, angle)
            self.image = rotated_image
            tip_offset = 12  # how much to shift the image backward
            shift_x = -self.dx * tip_offset
            shift_y = -self.dy * tip_offset
            self.rect = self.image.get_rect(center=(self.x + shift_x, self.y + shift_y))
        else:
            self.radius = 8
            self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255,220,50), (self.radius, self.radius), self.radius)
            self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt, walls_group=None, enemies_group=None):
        """
        dt in seconds; optionally pass in groups for collision
        """
        # move
        dx_pixels = self.dx * self.speed * dt
        dy_pixels = self.dy * self.speed * dt
        self.x += dx_pixels
        self.y += dy_pixels
        self.travelled += math.hypot(dx_pixels, dy_pixels)

        self.rect.center = (int(self.x), int(self.y))

        # out of range?
        if self.travelled >= self.max_range:
            self.kill()
            return

        # collision with walls?
        if walls_group and pygame.sprite.spritecollideany(self, walls_group):
            self.kill()
            return

        # collision with enemies?
        if enemies_group:
            hit = pygame.sprite.spritecollide(self, enemies_group, False)
            for enemy in hit:
                enemy.take_damage(10)    # or whatever
                self.kill()
                return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
