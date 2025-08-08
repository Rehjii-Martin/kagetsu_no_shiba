# entities/enemies.py
import os, random, math, pygame
from typing import Optional
from core.projectile import Projectile
from entities.player import Player

# tunables
CHASE_RADIUS, ATTACK_RADIUS, LOSE_RADIUS = 220, 160, 280
SHOT_COOLDOWN, PROJECTILE_SPEED, PATROL_SPEED = 1.2, 300, 40

class Enemy(pygame.sprite.Sprite):
    FRAME_WIDTH, FRAME_HEIGHT, FRAMES_PER_DIR = 32, 64, 6
    DIRECTIONS = ["right", "up", "left", "down"]
    projectile_group: Optional[pygame.sprite.Group] = None

    def __init__(self, x, y, speed=80, max_health=60):
        super().__init__()
        self.projectile_group: Optional[pygame.sprite.Group] = None
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        run_path  = os.path.join(root, "assets", "characters", "enemies", "run_horizontal_32x32_2.png")
        idle_path = os.path.join(root, "assets", "characters", "enemies", "idle_32x32_2.png")

        self.run_sheet  = pygame.image.load(run_path).convert_alpha()
        self.idle_sheet = pygame.image.load(idle_path).convert_alpha()

        self.animations = {
            d: [self.run_sheet.subsurface(
                    pygame.Rect((row*self.FRAMES_PER_DIR + i)*self.FRAME_WIDTH, 0,
                                self.FRAME_WIDTH, self.FRAME_HEIGHT)).copy()
                for i in range(self.FRAMES_PER_DIR)]
            for row, d in enumerate(self.DIRECTIONS)
        }
        self.idles = {
            d: self.idle_sheet.subsurface(
                    pygame.Rect(row*self.FRAME_WIDTH, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)).copy()
            for row, d in enumerate(self.DIRECTIONS)
        }

        # state
        self.x, self.y = float(x), float(y)
        self.speed = speed
        self.direction = random.choice(self.DIRECTIONS)
        self.state = "patrol"
        self.change_dir_timer = random.uniform(1.5, 3.0)
        self.dir_vec = {"right": (1,0), "left": (-1,0), "up": (0,-1), "down": (0,1)}

        # timers
        self.shoot_timer, self.frame_timer, self.frame_index = 0.0, 0.0, 0

        # health
        self.health = self.max_health = max_health

        # sprite & rect
        self.image = self.idles[self.direction]
        self.rect  = self.image.get_rect(center=(x, y))


    # ─────────── main update ────────────
    def update(self, dt, player, collision_rects=None, map_rect=None):
        self.shoot_timer += dt
        px, py = player.rect.center
        dist   = math.hypot(px - self.rect.centerx, py - self.rect.centery)

        # FSM
        if   dist <= ATTACK_RADIUS: self.state = "attack"
        elif dist <= CHASE_RADIUS : self.state = "chase"
        elif dist >  LOSE_RADIUS  : self.state = "patrol"

        if self.state == "patrol":
            moved = self._patrol(dt, collision_rects, map_rect)
        elif self.state == "chase":
            moved = self._chase(dt, px, py, collision_rects, map_rect, self.speed)
        else:  # attack
            moved = self._chase(dt, px, py, collision_rects, map_rect, self.speed)
            self._shoot(player)  # now passes full Player object

        self._animate(dt, moved)

    # ───────────── behaviours ───────────
    def _patrol(self, dt, collision_rects, map_rect):
        self.change_dir_timer -= dt
        if self.change_dir_timer <= 0:
            self.change_dir_timer = random.uniform(1.5,3.0)
            self.direction = random.choice(self.DIRECTIONS)
        vx, vy = self.dir_vec[self.direction]
        return self._move(vx*PATROL_SPEED*dt, vy*PATROL_SPEED*dt, collision_rects, map_rect)

    def _chase(self, dt, tx, ty, collision_rects, map_rect, speed):
        dx, dy = tx - self.rect.centerx, ty - self.rect.centery
        dist   = math.hypot(dx, dy)
       

        # ───── Free 360° movement ─────
        length = max(dist, 1e-6)
        step_x = dx / length * speed * dt
        step_y = dy / length * speed * dt

        # choose facing direction based on actual motion
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        return self._move(step_x, step_y, collision_rects, map_rect)
    
    # ───────────── movement util ────────
    def _move(self, dx, dy, collision_rects, map_rect):
        old_center = self.rect.center

        # Attempt horizontal movement
        self.x += dx
        self.rect.centerx = int(self.x)
        if not self._free(self.rect, collision_rects):
            self.x -= dx  # undo
            self.rect.centerx = int(self.x)

        # Attempt vertical movement
        self.y += dy
        self.rect.centery = int(self.y)
        if not self._free(self.rect, collision_rects):
            self.y -= dy  # undo
            self.rect.centery = int(self.y)

        # Clamp to map
        if map_rect:
            self.rect.clamp_ip(map_rect)
            self.x, self.y = float(self.rect.centerx), float(self.rect.centery)

        return self.rect.center != old_center



    def _free(self, rect, tiles):  # collision helper
        return (not tiles) or all(not rect.colliderect(t) for t in tiles)

    # ───────────── shooting ─────────────
    def _shoot(self, player: "Player"):
        if self.shoot_timer < SHOT_COOLDOWN or self.projectile_group is None:
            return
        self.shoot_timer = 0.0
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        length = max(math.hypot(dx, dy), 1e-6)
        direction = (dx / length, dy / length)
        bullet = Projectile(
            start_pos=self.rect.center,
            direction=direction,
            speed=PROJECTILE_SPEED,
            from_enemy=True,
            projectile_type="enemy",
            owner=self
        )
        self.projectile_group.add(bullet)

    # ───────────── visuals ──────────────
    def _animate(self, dt, moved):
        if moved:
            self.frame_timer += dt
            if self.frame_timer >= 0.15:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
            self.image = self.animations[self.direction][self.frame_index]
        else:
            self.frame_index = 0
            self.image = self.idles[self.direction]

    def take_damage(self, dmg):  # called by ProjectileSystem
        self.health -= dmg
        if self.health <= 0:
            self.kill()

    def draw(self, surface, camera):
        zoom = camera.zoom
        rs   = camera.apply(self.rect)
        img  = pygame.transform.scale(self.image,
                                      (int(self.image.get_width()*zoom),
                                       int(self.image.get_height()*zoom)))
        ir   = img.get_rect(center=rs.center)
        surface.blit(img, ir)
        # hp bar
        fill = int(ir.width * self.health / self.max_health)
        pygame.draw.rect(surface, (0,0,0), (ir.x, ir.y-8, ir.width, 5))
        pygame.draw.rect(surface, (100,255,100), (ir.x, ir.y-8, fill,      5))
