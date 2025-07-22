import os
import pygame
from core.projectile import Projectile

class Player(pygame.sprite.Sprite):
    FRAME_WIDTH = 32  
    FRAME_HEIGHT = 64
    FRAMES_PER_DIR = 6
    DIRECTIONS = ["right", "up", "left", "down"]

    def __init__(self, x, y, race="Shiba"):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        run_path = os.path.join(project_root, "assets", "characters", "players", "run_horizontal_32x32_2.png")
        idle_path = os.path.join(project_root, "assets", "characters", "players", "idle_32x32_2.png")

        self.run_sheet = pygame.image.load(run_path).convert_alpha()
        self.idle_sheet = pygame.image.load(idle_path).convert_alpha()

        self.animations = {
            dir_name: self._load_frames(row_idx)
            for row_idx, dir_name in enumerate(self.DIRECTIONS)
        }
        self.idles = {
            dir_name: self._load_idle(idx)
            for idx, dir_name in enumerate(self.DIRECTIONS)
        }

        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 0.12
        self.image = self.idles[self.direction]

        hitbox_width = 20
        hitbox_height = 28
        offset_x = (self.FRAME_WIDTH - hitbox_width) // 2
        offset_y = self.FRAME_HEIGHT - hitbox_height

        super().__init__()
        self.rect = pygame.Rect(x + offset_x, y + offset_y, hitbox_width, hitbox_height)
        self.speed = 100

        self.max_health = 100
        self.health = 100
        self.max_energy = 100
        self.energy = 100
        self.xp = 0
        self.energy_recovery_rate = 10
        self.race = race
        self.set_race_stats(race)
        self.dash_cooldown = 1.0
        self.time_since_dash = 0

        self.shot_cooldown = 0.25
        self.time_since_last_shot = 0

    def set_race_stats(self, race):
        if race == "Saiyan":
            self.max_health = 120
            self.max_energy = 90
            self.energy_recovery_rate = 8
            self.speed = 110
        elif race == "Namekian":
            self.max_health = 140
            self.max_energy = 110
            self.energy_recovery_rate = 12
            self.speed = 90
        elif race == "Android":
            self.max_health = 100
            self.max_energy = 200
            self.energy_recovery_rate = 20
            self.speed = 85
        elif race == "Shiba":
            self.max_health = 110
            self.max_energy = 100
            self.energy_recovery_rate = 10
            self.speed = 100
        else:
            self.max_health = 100
            self.max_energy = 100
            self.energy_recovery_rate = 10
            self.speed = 100

        self.health = self.max_health
        self.energy = self.max_energy

    def get_projectile_spawn_pos(self):
        center_x = self.rect.centerx
        sprite_height = self.image.get_height()
        visual_bottom = self.rect.bottom
        sprite_top = visual_bottom - sprite_height
        spawn_y = sprite_top + int(sprite_height * 0.6)
        return (center_x, spawn_y)

    def _trim_surface(self, surface):
        mask = pygame.mask.from_surface(surface)
        rect = mask.get_bounding_rects()
        if rect:
            return surface.subsurface(rect[0])
        return surface

    def _load_frames(self, direction_index):
        start = direction_index * self.FRAMES_PER_DIR
        return [
            self._trim_surface(self.run_sheet.subsurface(
                pygame.Rect((start + i) * self.FRAME_WIDTH, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
            ))
            for i in range(self.FRAMES_PER_DIR)
        ]

    def _load_idle(self, index):
        return self._trim_surface(self.idle_sheet.subsurface(
            pygame.Rect(index * self.FRAME_WIDTH, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
        ))

    def update(self, keys, dt, map_rect, collision_rects, override_animation=False):
        dx = dy = 0
        moving = False

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy, self.direction, moving = -self.speed * dt, "up", True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy, self.direction, moving = self.speed * dt, "down", True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx, self.direction, moving = -self.speed * dt, "left", True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx, self.direction, moving = self.speed * dt, "right", True

        if keys[pygame.K_q]:
            self.try_dash(dt, collision_rects, map_rect)
        else:
            self.time_since_dash += dt


        # Horizontal movement
        next_rect = self.rect.move(dx, 0)
        if not any(next_rect.colliderect(r) for r in collision_rects):
            self.rect.x += dx

        # Vertical movement
        next_rect = self.rect.move(0, dy)
        if not any(next_rect.colliderect(r) for r in collision_rects):
            self.rect.y += dy

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.top < 0: self.rect.top = 0
        self.rect.clamp_ip(map_rect)


        if override_animation:
            pass  # Skip animation logic — using manual preview
        elif moving:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_duration:
                self.frame_index = (self.frame_index + 1) % self.FRAMES_PER_DIR
                self.frame_timer = 0
            self.image = self.animations[self.direction][self.frame_index]
        else:
            self.image = self.idles[self.direction]
            self.frame_index = 0
            self.frame_timer = 0

        self.time_since_last_shot += dt
        self.energy += self.energy_recovery_rate * dt
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def try_dash(self, dt, collision_rects, map_rect):
        if self.time_since_dash < self.dash_cooldown or self.energy < 10:
            return

        dash_distance = self.speed * dt * 100  # Strong burst
        dx, dy = 0, 0

        dir_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = dir_map.get(self.direction, (0, 0))
        dx *= dash_distance
        dy *= dash_distance

        # Horizontal dash
        next_rect = self.rect.move(dx, 0)
        if not any(next_rect.colliderect(r) for r in collision_rects):
            self.rect.x += int(dx)

        # Vertical dash
        next_rect = self.rect.move(0, dy)
        if not any(next_rect.colliderect(r) for r in collision_rects):
            self.rect.y += int(dy)

        self.rect.clamp_ip(map_rect)
        self.time_since_dash = 0
        self.energy = max(0, self.energy - 10)

    
    def try_shoot(self, keys):
        if self.time_since_last_shot < self.shot_cooldown:
            return None

        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        if dx == 0 and dy == 0:
            dir_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
            dx, dy = dir_map.get(self.direction, (1, 0))

        length = max((dx**2 + dy**2) ** 0.5, 1e-5)
        dx, dy = dx / length, dy / length

        self.time_since_last_shot = 0
        return Projectile(start_pos=self.get_projectile_spawn_pos(), direction=(dx, dy))
    
    def draw(self, surface, camera):
        sprite = self.image
        screen_pos = self.rect if camera is None else camera.apply(self.rect)

        zoom = camera.zoom if camera else 1.0
        
        zoomed_sprite = pygame.transform.scale(sprite, (
            int(sprite.get_width() * zoom),
            int(sprite.get_height() * zoom)
        ))

        draw_x = int(screen_pos.centerx - zoomed_sprite.get_width() // 2)
        draw_y = int(screen_pos.bottom - zoomed_sprite.get_height())
        surface.blit(zoomed_sprite, (draw_x, draw_y))

        #Hit Box
       # if camera is not None:
       #     zoomed_rect = pygame.Rect(
       #         int(screen_pos.x),
       #         int(screen_pos.y),
       #         int(screen_pos.width * camera.zoom),
       #         int(screen_pos.height * camera.zoom)
       #     )
       #     pygame.draw.rect(surface, (0, 0, 0), screen_pos, 1)
