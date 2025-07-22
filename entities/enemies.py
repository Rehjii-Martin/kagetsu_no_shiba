# entities/enemies.py
import os, random, pygame

class Enemy(pygame.sprite.Sprite):
    FRAME_WIDTH = 32
    FRAME_HEIGHT = 64
    FRAMES_PER_DIR = 6
    DIRECTIONS = ["right", "up", "left", "down"]

    def __init__(self, x, y, speed=50, max_health=50):
        super().__init__()
        # load your sheets
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        run_path   = os.path.join(project_root, "assets", "characters", "enemies", "run_horizontal_32x32_2.png")
        idle_path  = os.path.join(project_root, "assets", "characters", "enemies", "idle_32x32_2.png")
        self.run_sheet  = pygame.image.load(run_path).convert_alpha()
        self.idle_sheet = pygame.image.load(idle_path).convert_alpha()

        # slice into animations
        self.animations = {
            d: [
                self.run_sheet.subsurface(pygame.Rect((di*self.FRAMES_PER_DIR + i)*self.FRAME_WIDTH, 0,
                                                      self.FRAME_WIDTH, self.FRAME_HEIGHT)).copy()
                for i in range(self.FRAMES_PER_DIR)
            ]
            for di, d in enumerate(self.DIRECTIONS)
        }
        self.idles = {
            d: self.idle_sheet.subsurface(
                pygame.Rect(di*self.FRAME_WIDTH, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
            ).copy()
            for di, d in enumerate(self.DIRECTIONS)
        }

        # float position & random-walk state
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.change_dir_timer = random.uniform(1.0, 3.0)
        self.direction = random.choice(self.DIRECTIONS)
        self.dir_vectors = {"right": (1,0), "left": (-1,0), "up": (0,-1), "down": (0,1)}

        # animation state
        self.frame_index    = 0
        self.frame_timer    = 0.0
        self.frame_duration = 0.15

        # health
        self.health     = max_health
        self.max_health = max_health

        # initial image & rect
        self.image = self.idles[self.direction]
        self.rect  = self.image.get_rect(center=(x, y))

    def update(self, dt, collision_rects=None, map_rect=None):
        # 1) random‐walk direction change
        self.change_dir_timer -= dt
        if self.change_dir_timer <= 0:
            self.direction = random.choice(self.DIRECTIONS)
            self.change_dir_timer = random.uniform(1.0, 3.0)

        # 2) attempt to move
        vx, vy = self.dir_vectors[self.direction]
        dx = vx * self.speed * dt
        dy = vy * self.speed * dt

        # horizontal
        nr = self.rect.move(dx, 0)
        if not collision_rects or not any(nr.colliderect(r) for r in collision_rects):
            self.x += dx
            self.rect.x = int(self.x)
        else:
            # bounce off wall
            self.direction = random.choice(self.DIRECTIONS)
            self.change_dir_timer = random.uniform(1.0, 3.0)

        # vertical
        nr = self.rect.move(0, dy)
        if not collision_rects or not any(nr.colliderect(r) for r in collision_rects):
            self.y += dy
            self.rect.y = int(self.y)
        else:
            self.direction = random.choice(self.DIRECTIONS)
            self.change_dir_timer = random.uniform(1.0, 3.0)

        # clamp to map bounds
        if map_rect:
            self.rect.clamp_ip(map_rect)
            self.x, self.y = float(self.rect.x), float(self.rect.y)

        # 3) animation
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
            self.image = self.animations[self.direction][self.frame_index]

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw(self, surface, camera):
        # scale & position
        zoom = camera.zoom
        sr  = camera.apply(self.rect)
        w   = int(self.image.get_width() * zoom)
        h   = int(self.image.get_height() * zoom)
        img = pygame.transform.scale(self.image, (w, h))
        ir  = img.get_rect(center=sr.center)
        surface.blit(img, ir)

        # health bar
        bar_w = ir.width
        fill  = int(bar_w * (self.health/self.max_health))
        pygame.draw.rect(surface, (0,0,0),   (ir.x, ir.y-8, bar_w, 5))
        pygame.draw.rect(surface, (100,255,100),(ir.x, ir.y-8, fill, 5))
