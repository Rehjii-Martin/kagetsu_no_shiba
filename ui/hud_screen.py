# /core/ui/hud_screen.py
import pygame
import pytmx
import os
from entities.player import Player
from ui.panels.skills import SkillsPanel
from ui.panels.vitals import VitalsPanel
from core.camera import Camera
from entities.enemies import Enemy

class Wall(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect

class HUDScreen:
    def __init__(self, game, map_width, map_height, tmx_data):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.coord_font = pygame.font.SysFont("monospace", 16)
        self.show_exit_dialog = False
        self.exit_selected = "No"

        # --- Load TMX map & collision objects ---
        tmx_path = os.path.join("assets", "maps", "test_map.tmx")
        tmx_data = pytmx.load_pygame(tmx_path)
        self.tmx_data = tmx_data
        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight
        self.map_rect = pygame.Rect(0, 0, self.map_width, self.map_height)

        # --- Build collision rects & wall sprites ---
        self.collision_tiles = []
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name and "collision" in layer.name.lower():
                for obj in layer:
                    self.collision_tiles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        self.wall_sprites = pygame.sprite.Group()
        for rect in self.collision_tiles:
            self.wall_sprites.add(Wall(rect))

        # --- Enemies group with “safe” spawns (away from any collision) ---
        self.enemies = pygame.sprite.Group()
        safe_spawns = [
            (100, 150),
            (400, 200),
            (600, 450),
        ]
        for sx, sy in safe_spawns:
            test_rect = pygame.Rect(
                sx - Enemy.FRAME_WIDTH // 2,
                sy - Enemy.FRAME_HEIGHT // 2,
                Enemy.FRAME_WIDTH,
                Enemy.FRAME_HEIGHT
            )
            if not any(test_rect.colliderect(r) for r in self.collision_tiles):
                self.enemies.add(Enemy(sx, sy))

        # --- Player spawn point from TMX ---
        spawn_x, spawn_y = 100, 100
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "PlayerSpawn":
                if len(layer):
                    obj = layer[0]
                    spawn_x, spawn_y = int(obj.x), int(obj.y)
                break
        self.spawn_x, self.spawn_y = spawn_x, spawn_y

        # --- Player & camera ---
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(800, 600, world_width=self.map_width, world_height=self.map_height)

        # --- UI state ---
        self.projectiles       = pygame.sprite.Group()
        self.explosions        = pygame.sprite.Group()
        self.chat_messages     = []
        self.chat_input        = ""
        self.chat_input_active = False
        self.panel_visible     = True
        self.cursor_timer      = 0.0
        self.cursor_visible    = True
        self.chat_scroll       = 0
        self.active_tab        = "Skills"
        self.tab_panels        = {
            "Skills": SkillsPanel(),
            "Vitals": VitalsPanel(self.player),
        }

    def update(self, dt, events):
        keys = pygame.key.get_pressed()

        # 1) Player movement (blocked by collisions)
        if not self.chat_input_active:
            self.player.update(keys, dt, self.map_rect, self.collision_tiles)

        # 2) Projectiles → move & handle collisions
        self.projectiles.update(
            dt,
            walls_group=self.wall_sprites,
            enemies_group=self.enemies,
            explosions_group=self.explosions
        )

        # 3) Explosions animate
        self.explosions.update(dt)

        # 4) Enemies move & animate (blocked by collisions)
        for e in self.enemies:
            e.update(dt, collision_rects=self.collision_tiles, map_rect=self.map_rect)

        # 5) Player ↔ Enemy contact damage (0.5s cooldown per enemy)
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect):
                cd = getattr(e, "_hit_cooldown", 0.0)
                if cd <= 0.0:
                    self.player.health -= 10
                    print(f"[ENEMY] Player hit! health now {self.player.health}")
                    e._hit_cooldown = 0.5
                else:
                    e._hit_cooldown = cd - dt

        # 6) Player death & respawn
        if self.player.health <= 0:
            print("[PLAYER] Died! Respawning…")
            self.player.health = self.player.max_health
            self.player.rect.center = (self.spawn_x, self.spawn_y)

        # 7) Camera follow & cursor blink
        self.camera.follow(self.player.rect)
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0

        # 8) Input & UI toggles
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # chat box
                input_box = pygame.Rect(400, 390, 500, 24)
                self.chat_input_active = input_box.collidepoint(event.pos)

                # tabs
                tab_w = 500 // len(self.tab_panels)
                for i, t in enumerate(self.tab_panels):
                    if pygame.Rect(400 + i*tab_w, 0, tab_w, 30).collidepoint(event.pos):
                        self.active_tab = t

                # exit dialog
                if self.show_exit_dialog:
                    if self.yes_rect.collidepoint(event.pos): pygame.quit(); exit()
                    if self.no_rect.collidepoint(event.pos):  self.show_exit_dialog = False

                # skill‐panel clicks
                if self.active_tab == "Skills":
                    sp = self.tab_panels["Skills"]
                    if hasattr(sp, "ki_rect") and sp.ki_rect.collidepoint(event.pos):
                        proj = self.player.try_shoot(keys)
                        if proj:
                            self.projectiles.add(proj)
                            self.player.energy = max(0, self.player.energy - 5)
                    if hasattr(sp, "dash_rect") and sp.dash_rect.collidepoint(event.pos):
                        self.player.try_dash(dt, self.collision_tiles, self.map_rect)

            elif event.type == pygame.KEYDOWN:
                if self.show_exit_dialog:
                    # exit dialog nav
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                        self.exit_selected = "Yes" if self.exit_selected=="No" else "No"
                    elif event.key == pygame.K_RETURN:
                        if self.exit_selected=="Yes": pygame.quit(); exit()
                        else: self.show_exit_dialog=False

                elif self.chat_input_active:
                    # chat typing
                    if event.key == pygame.K_RETURN and self.chat_input.strip():
                        self.chat_messages.append("[Player]: " + self.chat_input.strip())
                        self.chat_input = ""; self.chat_scroll = 0
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_input = self.chat_input[:-1]
                    elif event.key == pygame.K_UP:
                        self.chat_scroll = min(self.chat_scroll+1, max(0, len(self.chat_messages)-5))
                    elif event.key == pygame.K_DOWN:
                        self.chat_scroll = max(self.chat_scroll-1, 0)
                    else:
                        self.chat_input += event.unicode

                else:
                    # general keys
                    if event.key == pygame.K_TAB:
                        self.panel_visible = not self.panel_visible
                        self.chat_input_active = False
                        self.chat_input = ""
                        self.chat_scroll = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.show_exit_dialog = True
                        self.exit_selected = "No"
                    elif event.key == pygame.K_z:
                        self.camera.zoom = max(self.camera.min_zoom, self.camera.zoom-0.1)
                    elif event.key == pygame.K_x:
                        self.camera.zoom = min(self.camera.max_zoom, self.camera.zoom+0.1)

        # 9) Fire with spacebar
        if keys[pygame.K_SPACE] and not self.chat_input_active:
            proj = self.player.try_shoot(keys)
            if proj:
                self.projectiles.add(proj)
                self.player.energy = max(0, self.player.energy - 5)

    def draw(self, surface):
        # --- draw map layers ---
        if self.tmx_data:
            for layer in self.tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    tw, th = self.tmx_data.tilewidth, self.tmx_data.tileheight
                    sx = int(self.camera.offset_x//tw)
                    sy = int(self.camera.offset_y//th)
                    ex = int((self.camera.offset_x+self.camera.viewport_width/self.camera.zoom)//tw)+1
                    ey = int((self.camera.offset_y+self.camera.viewport_height/self.camera.zoom)//th)+1
                    for x in range(max(0,sx), min(layer.width, ex)):
                        for y in range(max(0,sy), min(layer.height, ey)):
                            gid = layer.data[y][x]
                            img = self.tmx_data.get_tile_image_by_gid(gid & 0x1FFFFFFF)
                            if img:
                                dx = int((x*tw - self.camera.offset_x)*self.camera.zoom)
                                dy = int((y*th - self.camera.offset_y)*self.camera.zoom)
                                surface.blit(
                                    pygame.transform.scale(img, (int(tw*self.camera.zoom), int(th*self.camera.zoom))),
                                    (dx, dy)
                                )
        else:
            pygame.draw.rect(surface, (80,80,100), self.camera.apply(self.map_rect), 5)

        # --- draw entities ---
        self.player.draw(surface, self.camera)
        for p  in self.projectiles: p.draw(surface, self.camera.offset_x, self.camera.offset_y, self.camera.zoom)
        for ex in self.explosions:  ex.draw(surface, self.camera.offset_x, self.camera.offset_y, self.camera.zoom)
        for e  in self.enemies:     e.draw(surface, self.camera)

        # --- HUD bars & panels ---
        # energy bar (blue)
        pygame.draw.rect(surface, (0,180,180),(20,50, int(150*(self.player.energy/self.player.max_energy)),20))
        # health bar (red) – now updates!
        pygame.draw.rect(surface, (200,0,0),(20,20, int(150*(self.player.health/self.player.max_health)),20))
        # xp bar
        pygame.draw.rect(surface, (240,240,0),(20,80,150,10))

        if self.panel_visible:
            pygame.draw.rect(surface,(245,245,220),(400,0,500,600))
            self.draw_tabs(surface)
            self.tab_panels[self.active_tab].draw(surface,400,40,500,340)

            # chat box
            box = pygame.Rect(400,420,500,140)
            pygame.draw.rect(surface,(30,30,30),box)
            pygame.draw.rect(surface,(255,255,255),box,2)
            lines = 5
            start = max(0,len(self.chat_messages)-lines-self.chat_scroll)
            end   = max(0,len(self.chat_messages)-self.chat_scroll)
            for i,msg in enumerate(self.chat_messages[start:end]):
                surf = self.font.render(msg,True,(255,255,255))
                surface.blit(surf,(box.x+10,box.y+10+i*22))
            ib = pygame.Rect(box.x,box.y-30,box.width,24)
            bg = (70,70,70) if self.chat_input_active else (50,50,50)
            pygame.draw.rect(surface,bg,ib)
            pygame.draw.rect(surface,(255,255,255),ib,1)
            txt = self.font.render(self.chat_input,True,(255,255,255))
            surface.blit(txt,(ib.x+5,ib.y+2))
            if self.chat_input_active and self.cursor_visible:
                cx = ib.x+5+txt.get_width()+2; cy = ib.y+4
                pygame.draw.line(surface,(255,255,255),(cx,cy),(cx,cy+16),2)

        # debug border & coords
        pygame.draw.rect(surface,(255,0,0),pygame.Rect(0,0,self.camera.viewport_width,self.camera.viewport_height),1)
        coords = f"X: {self.player.rect.centerx} | Y: {self.player.rect.centery}"
        ct = self.coord_font.render(coords,True,(255,255,255))
        cr = ct.get_rect(center=(surface.get_width()//2,15))
        pygame.draw.rect(surface,(0,0,0,150),cr.inflate(10,4))
        surface.blit(ct,cr)

        # exit dialog
        if self.show_exit_dialog:
            self.draw_exit_dialog(surface)

    def draw_tabs(self, surface):
        w = 500//len(self.tab_panels)
        for i, t in enumerate(self.tab_panels):
            r = pygame.Rect(400+i*w,0,w,30)
            col = (255,165,0) if t==self.active_tab else (220,180,120)
            pygame.draw.rect(surface,col,r)
            lbl = self.font.render(t,True,(0,0,0))
            surface.blit(lbl,(r.x+5,r.y+5))

    def draw_exit_dialog(self, surface):
        dw,dh = 300,150
        x = self.camera.viewport_width//2 - dw//2
        y = self.camera.viewport_height//2 - dh//2
        self.yes_rect = pygame.Rect(x+40,y+80,80,30)
        self.no_rect  = pygame.Rect(x+180,y+80,80,30)
        overlay = pygame.Surface((self.camera.viewport_width,self.camera.viewport_height))
        overlay.fill((0,0,0)); surface.blit(overlay,(0,0))
        pygame.draw.rect(surface,(50,50,50),(x,y,dw,dh))
        pygame.draw.rect(surface,(255,255,255),(x,y,dw,dh),2)
        surf = self.font.render("Exit game?",True,(255,255,255))
        surface.blit(surf,(x+90,y+20))
        yc = (200,200,0) if self.exit_selected=="Yes" else (100,100,100)
        nc = (200,200,0) if self.exit_selected=="No"  else (100,100,100)
        pygame.draw.rect(surface,yc,self.yes_rect)
        pygame.draw.rect(surface,nc,self.no_rect)
        surface.blit(self.font.render("Yes",True,(0,0,0)),(x+60,y+85))
        surface.blit(self.font.render("No", True,(0,0,0)),(x+205,y+85))
