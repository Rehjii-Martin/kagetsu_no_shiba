# core/ui/screens/hud_screen.py
import os, random, math, pygame, pytmx
from typing import Optional
from typing import cast
from entities.player      import Player
from entities.enemies     import Enemy
from core.camera          import Camera
from systems.player_controller   import PlayerController
from systems.projectile_system   import ProjectileSystem
from systems.explosion_system    import ExplosionSystem
from systems.enemy_controller    import EnemyController
from ui.render.tilemap_renderer  import TilemapRenderer
from ui.components.canvas_border import CanvasBorder
from ui.components.exit_dialog   import ExitDialog
from ui.components.tab_manager   import TabManager
from ui.components.draggable_vitals_box import DraggableVitalsBox
from ui.panels.skills  import SkillsPanel
from ui.panels.vitals  import VitalsPanel
from core.explosion import Explosion


class Wall(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect):
        super().__init__()
        self.rect = rect


class HUDScreen:
    def __init__(self, game):
        self.game = game

        # ────────────────────── MAP / COLLISION ─────────────────────────────
        tmx_path   = os.path.join("assets", "maps", "test_map.tmx")
        tmx_data   = pytmx.load_pygame(tmx_path)
        self.map_width  = tmx_data.width  * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight
        self.map_rect   = pygame.Rect(0, 0, self.map_width, self.map_height)

        # collision rectangles exported from Tiled
        self.collision_tiles: list[pygame.Rect] = []
        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name and "collision" in layer.name.lower():
                for obj in layer:
                    self.collision_tiles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # sprite-based walls (helps with projectile collision)
        self.wall_sprites = pygame.sprite.Group()
        for r in self.collision_tiles:
            self.wall_sprites.add(Wall(r))

        # ────────────────────── PLAYER ──────────────────────────────────────
        spawn_x, spawn_y = 100, 100
        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "PlayerSpawn" and layer:
                spawn_x, spawn_y = int(layer[0].x), int(layer[0].y)
                break
        self.spawn_x, self.spawn_y = spawn_x, spawn_y
        self.player = Player(spawn_x, spawn_y)
        self.draggable_vitals_box = DraggableVitalsBox(self.player)

        # ────────────────────── ENEMIES & SYSTEMS ───────────────────────────
        self.enemies = pygame.sprite.Group()
        self.explosion_system = ExplosionSystem()
        self.projectile_system = ProjectileSystem(self.wall_sprites, self.enemies, self.explosion_system)
        self.projectile_group: Optional[pygame.sprite.Group] = None

        # random enemy spawns (avoid walls & player start)
        attempts, want, min_dist = 30, 5, 150
        while len(self.enemies) < want and attempts:
            attempts -= 1
            sx = random.randint(32, self.map_width  - 32)
            sy = random.randint(32, self.map_height - 32)
            test_rect = pygame.Rect(sx - 16, sy - 32, 32, 64)
            clear = (not any(test_rect.colliderect(r) for r in self.collision_tiles)
                     and math.hypot(sx - spawn_x, sy - spawn_y) >= min_dist)
            if clear:
                e = Enemy(sx, sy)
                e.projectile_group = cast(pygame.sprite.Group, self.projectile_system.projectiles)
                self.enemies.add(e)

        # controllers / helpers
        self.player_controller = PlayerController(self.player, self.collision_tiles, self.map_rect)
        self.enemy_controller  = EnemyController(self.enemies, self.collision_tiles, self.map_rect)

        # camera & renderer
        self.camera        = Camera(800, 600, world_width=self.map_width, world_height=self.map_height)
        self.map_renderer  = TilemapRenderer(tmx_data, self.camera)
        self.camera.follow(self.player.rect)

        # ────────────────────── UI / UX ─────────────────────────────────────
        self.font        = pygame.font.SysFont(None, 24)
        self.coord_font  = pygame.font.SysFont("monospace", 16)
        self.tab_panels  = {"Skills": SkillsPanel(), "Vitals": VitalsPanel(self.player)}
        self.tab_manager = TabManager(self.tab_panels, self.font)
        self.exit_dialog = ExitDialog(self.camera, self.font)
        self.border      = CanvasBorder(self.camera, self.player, self.coord_font)

        # chat
        self.chat_messages: list[str] = []
        self.chat_input       = ""
        self.chat_input_active= False
        self.panel_visible    = True
        self.chat_scroll      = 0

    # ───────────────────────── UPDATE ───────────────────────────────────────
    def update(self, dt: float, events: list[pygame.event.Event]):
        keys = pygame.key.get_pressed()
        if not self.chat_input_active:
            self.player_controller.update(dt, keys, self.projectile_system, self.chat_input_active)

        self.projectile_system.update(dt)
        
        # check enemy‐shot projectiles against the player
        for p in list(self.projectile_system.projectiles):
            if getattr(p, "from_enemy", False) and self.player.rect.colliderect(p.rect):
                # damage & explosion
                self.player.health -= 10
                self.explosion_system.explosions.add(
                    Explosion(p.x, p.y)
                )
                p.kill()

        self.explosion_system.update(dt)
        self.enemy_controller.update(dt, self.player)

        # simple respawn if player dies
        if self.player.health <= 0:
            self.player.health = self.player.max_health
            self.player.rect.center = (self.spawn_x, self.spawn_y)

        self.camera.follow(self.player.rect)

        # ─── UI & chat handling (kept compact) ─────────────────────────────
        self.tab_manager.handle_events(events)
        self.exit_dialog.handle_events(events)

        input_box = pygame.Rect(400, 390, 500, 24)
        for ev in events:
            # ESC opens exit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.exit_dialog.show = True

            # TAB always toggles sidebar
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_TAB:
                self.panel_visible = not self.panel_visible
                if not self.panel_visible:
                    # blur and clear chat when panel closes
                    self.chat_input_active = False
                    self.chat_input = ""
                    self.chat_scroll = 0

            # clicking in the chat bar gives it focus
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.chat_input_active = input_box.collidepoint(ev.pos)
            
            # only when chat is active do we consume typing keys
            if ev.type == pygame.KEYDOWN and self.chat_input_active:
                if ev.key == pygame.K_RETURN and self.chat_input.strip():
                    self.chat_messages.append(f"[Player]: {self.chat_input.strip()}")
                    self.chat_input = ""
                    self.chat_scroll = 0
                elif ev.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                elif ev.key == pygame.K_UP:
                    self.chat_scroll = min(self.chat_scroll + 1,
                                           max(0, len(self.chat_messages) - 5))
                elif ev.key == pygame.K_DOWN:
                    self.chat_scroll = max(self.chat_scroll - 1, 0)
                else:
                    self.chat_input += ev.unicode
            

    # ───────────────────────── DRAW ────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        self.map_renderer.draw(surface)
        self.player_controller.draw(surface, self.camera)
        self.projectile_system.draw(surface, self.camera)
        self.explosion_system.draw(surface, self.camera)
        self.enemy_controller.draw(surface, self.camera)
        self.draggable_vitals_box.draw(surface)

        # sidebar + chat
        if self.panel_visible:
            self.tab_manager.draw(surface)
            self._draw_chat(surface)

        self.exit_dialog.draw(surface)
        self.border.draw(surface)

    # helper
    def _draw_chat(self, surface: pygame.Surface):
        chat_rect = pygame.Rect(400, 420, 500, 140)
        pygame.draw.rect(surface, (30, 30, 30), chat_rect)
        pygame.draw.rect(surface, (255, 255, 255), chat_rect, 2)

        start = max(0, len(self.chat_messages) - 5 - self.chat_scroll)
        end   = max(0, len(self.chat_messages)     - self.chat_scroll)
        for i, msg in enumerate(self.chat_messages[start:end]):
            s = self.font.render(msg, True, (255, 255, 255))
            surface.blit(s, (chat_rect.x + 10, chat_rect.y + 10 + i * 22))

        input_box = pygame.Rect(chat_rect.x, chat_rect.y - 30, chat_rect.width, 24)
        bg = (70, 70, 70) if self.chat_input_active else (50, 50, 50)
        pygame.draw.rect(surface, bg, input_box)
        pygame.draw.rect(surface, (255, 255, 255), input_box, 1)
        txt = self.font.render(self.chat_input, True, (255, 255, 255))
        surface.blit(txt, (input_box.x + 5, input_box.y + 2))
