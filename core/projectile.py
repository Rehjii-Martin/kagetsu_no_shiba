# core/projectile.py
import os, math, pygame, json, urllib.request, urllib.error, urllib.parse
from core.explosion import Explosion
from services.damage_service import DamageService

# ───────────────────────── Debug Toggle ─────────────────────────
# Turn this on to get console logs and visual debugging overlays
DEBUG_PROJECTILES = False
# NOTE: no per-frame spam. We only log on create/impact/kill.
# Visuals are cheap (rect/line outlines) and only drawn when enabled.
# ────────────────────────────────────────────────────────────────

def _damage_from_service(projectile_type: str, distance: float, base_url: str = "http://localhost:7002") -> int:
    try:
        qs = urllib.parse.urlencode({"projectile_type": projectile_type, "distance": distance})
        with urllib.request.urlopen(f"{base_url}/damage?{qs}", timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return int(data.get("damage", 10))
    except Exception:
        return 10  # safe fallback


class Projectile(pygame.sprite.Sprite):
    def __init__(self, *groups, start_pos=None, direction=None, speed=800, max_range=800, image_path=None, projectile_type="ki", owner=None, **kwargs):
        super().__init__()
        if start_pos is None or direction is None:
            raise ValueError("start_pos and direction must be provided")
        self.x, self.y = start_pos
        self.dx, self.dy = direction
        self.speed = speed
        self.max_range = max_range
        self.travelled = 0
        self.is_circle = False
        self.type = projectile_type
        self.start_pos_tuple = start_pos

        self.from_enemy = kwargs.get("from_enemy", False)
        self.projectile_type = kwargs.get("projectile_type", "KiBlast" if not self.from_enemy else "EnemyBlast")
        self.owner_bonus = int(kwargs.get("owner_bonus", 0))
        self.owner = owner 

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

        if DEBUG_PROJECTILES:
            print(f"[PROJ+] create type={self.projectile_type} from_enemy={self.from_enemy} "
                  f"start=({self.x:.1f},{self.y:.1f}) dir=({self.dx:.3f},{self.dy:.3f}) "
                  f"speed={self.speed} range={self.max_range} owner={getattr(self.owner,'name',None)}")

    def _kill_with_reason(self, reason: str):
        if DEBUG_PROJECTILES:
            print(f"[PROJ-] kill type={self.projectile_type} reason={reason} "
                  f"pos=({self.x:.1f},{self.y:.1f}) travelled={self.travelled:.1f}/{self.max_range}")
        self.kill()

    def update(self, dt, walls_group=None, enemies_group=None, players_group=None, explosions_group=None):
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

        # range limit
        if self.travelled >= self.max_range:
            if explosions_group is not None:
                explosions_group.add(Explosion(self.x, self.y))
            self._kill_with_reason("max_range")
            return

        # wall collisions
        if walls_group:
            for wall in walls_group:
                if self.rect.colliderect(wall.rect):
                    if explosions_group is not None:
                        explosions_group.add(Explosion(self.rect.centerx, self.rect.centery, 0.08))
                    self._kill_with_reason("hit_wall")
                    return

        # enemy collisions (only for player-fired shots)
        if enemies_group and not self.from_enemy:
            hit = pygame.sprite.spritecollide(self, enemies_group, False)
            for enemy in hit:
                # call damage microservice
                import json, urllib.request, urllib.parse
                try:
                    qs = urllib.parse.urlencode({
                        "projectile_type": "KiBlast",
                        "distance": float(self.travelled)
                    })
                    with urllib.request.urlopen(f"http://localhost:7002/damage?{qs}", timeout=1.5) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        dmg = int(data.get("damage", 10))
                except Exception:
                    dmg = 10
                enemy.take_damage(dmg)
                if DEBUG_PROJECTILES:
                    print(f"[PROJ*] hit_enemy dmg={dmg} enemy={getattr(enemy,'__class__',type(enemy)).__name__} "
                          f"pos=({self.rect.centerx},{self.rect.centery})")
                if explosions_group is not None:
                    explosions_group.add(Explosion(self.rect.centerx, self.rect.centery))
                self._kill_with_reason("hit_enemy")
                return

        # player collisions (only for enemy-fired shots)
        if players_group and self.from_enemy:
            hit_players = pygame.sprite.spritecollide(self, players_group, False)
            for pl in hit_players:
                dist = math.hypot(self.x - self.start_pos_tuple[0], self.y - self.start_pos_tuple[1])
                dmg = DamageService.get_damage(self.type, distance=dist)
                pl.health -= dmg
                if DEBUG_PROJECTILES:
                    print(f"[PROJ*] hit_player dmg={dmg} player={getattr(pl,'name','Player')} "
                          f"pos=({self.rect.centerx},{self.rect.centery})")
                if explosions_group is not None:
                    explosions_group.add(Explosion(self.rect.centerx, self.rect.centery))
                self._kill_with_reason("hit_player")
                return

    def _debug_draw(self, screen, screen_x, screen_y, zoom):
        # Draw a small direction line and an outline around the sprite/circle
        try:
            # direction line (projectile forward vector)
            line_len = max(8, int(16 * zoom))
            end_x = int(screen_x + self.dx * line_len)
            end_y = int(screen_y + self.dy * line_len)
            pygame.draw.line(screen, (0, 255, 255), (screen_x, screen_y), (end_x, end_y), 2)

            # bounding outline
            if self.is_circle:
                radius = max(1, int(self.radius * zoom))
                pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), radius, 1)
            else:
                # approximate outline using current image rect
                scaled_image = pygame.transform.rotozoom(self.base_image, 0, zoom)
                rect = scaled_image.get_rect(center=(screen_x, screen_y))
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        except Exception:
            # Never crash the game because of debug visuals
            pass

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

        if DEBUG_PROJECTILES:
            self._debug_draw(screen, screen_x, screen_y, zoom)
