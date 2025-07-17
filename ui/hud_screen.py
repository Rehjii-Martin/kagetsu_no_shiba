# /core/ui/hud_screen.py
import pygame
import pytmx
import os
from math import floor
from entities.player import Player
from ui.panels.skills import SkillsPanel
from ui.panels.vitals import VitalsPanel
from core.camera import Camera

class HUDScreen:
    def __init__(self, game, map_width, map_height, tmx_data):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.coord_font = pygame.font.SysFont("monospace", 16)
        self.show_exit_dialog = False
        self.exit_selected = "No"
        
        tmx_path = os.path.join("assets", "maps", "test_map.tmx")
        tmx_data = pytmx.load_pygame(tmx_path)
        self.tmx_data = tmx_data
        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight
        print("TMX Dimensions:", tmx_data.width, "x", tmx_data.height)
        print("Pixel Dimensions:", self.map_width, "x", self.map_height)
        self.map_rect = pygame.Rect(0, 0, self.map_width, self.map_height)
        
        spawn_x, spawn_y = 100, 100
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "PlayerSpawn":
                print(f"[TMX] Found PlayerSpawn layer")
                if len(layer) > 0:
                    obj = layer[0]
                    spawn_x = int(obj.x)
                    spawn_y = int(obj.y)
                    print(f"[SPAWN] Using PlayerSpawn from layer at ({spawn_x}, {spawn_y})")
                break

        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(800, 600, world_width=self.map_width, world_height=self.map_height)
        self.projectiles = []
        self.chat_messages = []
        self.chat_input = ""
        self.chat_input_active = False
        self.panel_visible = True
        self.cursor_timer = 0
        self.cursor_visible = True
        self.chat_scroll = 0
        self.active_tab = "Skills"
        self.tab_panels = {
            "Skills": SkillsPanel(),
            "Vitals": VitalsPanel(self.player),
        }
        self.explosions = pygame.sprite.Group()

        self.collision_rects = []
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Collision Layer":
                for obj in layer:
                    self.collision_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    def update(self, dt, events):
        keys = pygame.key.get_pressed()

        if not self.chat_input_active:
            self.player.update(keys, dt, self.map_rect, self.collision_rects)

        self.explosions.update(dt)
        self.camera.follow(self.player.rect)
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_box = pygame.Rect(400, 390, 500, 24)
                if input_box.collidepoint(event.pos):
                    self.chat_input_active = True
                else:
                    self.chat_input_active = False

                tab_area_x = 400
                tab_area_width = 500
                tab_width = tab_area_width // len(self.tab_panels)

                for idx, tab in enumerate(self.tab_panels):
                    tab_rect = pygame.Rect(tab_area_x + idx * tab_width, 0, tab_width, 30)
                    if tab_rect.collidepoint(event.pos):
                        self.active_tab = tab

                if self.show_exit_dialog:
                    if self.yes_rect.collidepoint(event.pos):
                        pygame.quit()
                        exit()
                    elif self.no_rect.collidepoint(event.pos):
                        self.show_exit_dialog = False

                if self.active_tab == "Skills":
                    skills_panel = self.tab_panels["Skills"]
                    if hasattr(skills_panel, "ki_rect") and skills_panel.ki_rect.collidepoint(event.pos):
                        proj = self.player.try_shoot(keys)
                        if proj:
                            self.projectiles.append(proj)
                            self.player.energy = max(0, self.player.energy - 5)
                    if hasattr(skills_panel, "dash_rect") and skills_panel.dash_rect.collidepoint(event.pos):
                        self.player.try_dash(dt, self.collision_rects, self.map_rect)

            if event.type == pygame.KEYDOWN:
                if self.show_exit_dialog:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                        self.exit_selected = "Yes" if self.exit_selected == "No" else "No"
                    elif event.key == pygame.K_RETURN:
                        if self.exit_selected == "Yes":
                            pygame.quit()
                            exit()
                        else:
                            self.show_exit_dialog = False
                elif self.chat_input_active:
                    if event.key == pygame.K_RETURN:
                        if self.chat_input.strip():
                            self.chat_messages.append("[Player]: " + self.chat_input.strip())
                            self.chat_input = ""
                            self.chat_scroll = 0
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_input = self.chat_input[:-1]
                    elif event.key == pygame.K_UP:
                        self.chat_scroll = min(self.chat_scroll + 1, max(0, len(self.chat_messages) - 5))
                    elif event.key == pygame.K_DOWN:
                        self.chat_scroll = max(self.chat_scroll - 1, 0)
                    else:
                        self.chat_input += event.unicode
                else:
                    if event.key == pygame.K_TAB:
                        self.panel_visible = not self.panel_visible
                        self.chat_input_active = False
                        self.chat_input = ""
                        self.chat_scroll = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.show_exit_dialog = True
                        self.exit_selected = "No"
                    elif event.key == pygame.K_z:
                        self.camera.zoom = max(self.camera.min_zoom, self.camera.zoom - 0.1)
                        print(f"[ZOOM OUT] Zoom set to {self.camera.zoom:.2f}")
                    elif event.key == pygame.K_x:
                        self.camera.zoom = min(self.camera.max_zoom, self.camera.zoom + 0.1)
                        print(f"[ZOOM IN] Zoom set to {self.camera.zoom:.2f}")

        if keys[pygame.K_SPACE] and not self.chat_input_active:
            proj = self.player.try_shoot(keys)
            if proj:
                self.projectiles.append(proj)
                self.player.energy = max(0, self.player.energy - 5)

        for proj in self.projectiles:
            proj.update(dt, walls_group=self.collision_rects, explosions_group=self.explosions)

    def draw(self, surface):
        if self.tmx_data:
            for layer in self.tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x in range(layer.width):
                        for y in range(layer.height):
                            gid = layer.data[y][x]
                            tile = self.tmx_data.get_tile_image_by_gid(gid & 0x1FFFFFFF)
                            if tile:
                                draw_x = int((x * self.tmx_data.tilewidth - self.camera.offset_x) * self.camera.zoom)
                                draw_y = int((y * self.tmx_data.tileheight - self.camera.offset_y) * self.camera.zoom)

                                tile_width = int(self.tmx_data.tilewidth * self.camera.zoom)
                                tile_height = int(self.tmx_data.tileheight * self.camera.zoom)
                                scaled_tile = pygame.transform.scale(tile, (tile_width, tile_height))

                                surface.blit(scaled_tile, (draw_x, draw_y))
        else:
            map_border_on_screen = self.camera.apply(self.map_rect)
            pygame.draw.rect(surface, (80, 80, 100), map_border_on_screen, 5)

        self.player.draw(surface, self.camera)
        for proj in self.projectiles:
            proj.draw(surface, self.camera.offset_x, self.camera.offset_y, self.camera.zoom)

        for explosion in self.explosions:
            explosion.draw(surface, self.camera.offset_x, self.camera.offset_y, self.camera.zoom)


        pygame.draw.rect(surface, (200, 0, 0), (20, 20, 150, 20))
        energy_bar_width = int(150 * (self.player.energy / self.player.max_energy))
        pygame.draw.rect(surface, (0, 180, 180), (20, 50, energy_bar_width, 20))
        pygame.draw.rect(surface, (240, 240, 0), (20, 80, 150, 10))

        if self.panel_visible:
            pygame.draw.rect(surface, (245, 245, 220), (400, 0, 500, 600))
            self.draw_tabs(surface)
            self.tab_panels[self.active_tab].draw(surface, 400, 40, 500, 340)

            chat_box = pygame.Rect(400, 420, 500, 140)
            pygame.draw.rect(surface, (30, 30, 30), chat_box)
            pygame.draw.rect(surface, (255, 255, 255), chat_box, 2)

            visible_lines = 5
            start = max(0, len(self.chat_messages) - visible_lines - self.chat_scroll)
            end = max(0, len(self.chat_messages) - self.chat_scroll)
            for i, msg in enumerate(self.chat_messages[start:end]):
                rendered = self.font.render(msg, True, (255, 255, 255))
                surface.blit(rendered, (chat_box.x + 10, chat_box.y + 10 + i * 22))

            input_box = pygame.Rect(chat_box.x, chat_box.y - 30, chat_box.width, 24)
            bg_color = (70, 70, 70) if self.chat_input_active else (50, 50, 50)
            pygame.draw.rect(surface, bg_color, input_box)
            pygame.draw.rect(surface, (255, 255, 255), input_box, 1)
            chat_text = self.font.render(self.chat_input, True, (255, 255, 255))
            surface.blit(chat_text, (input_box.x + 5, input_box.y + 2))
            if self.chat_input_active and self.cursor_visible:
                cursor_x = input_box.x + 5 + chat_text.get_width() + 2
                cursor_y = input_box.y + 4
                pygame.draw.line(surface, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + 16), 2)

        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(0, 0, self.camera.viewport_width, self.camera.viewport_height), 1)

        player_coords = f"X: {int(self.player.rect.centerx)} | Y: {int(self.player.rect.centery)}"
        coord_text = self.coord_font.render(player_coords, True, (255, 255, 255))
        coord_rect = coord_text.get_rect(center=(surface.get_width() // 2, 15))
        pygame.draw.rect(surface, (0, 0, 0, 150), coord_rect.inflate(10, 4))
        surface.blit(coord_text, coord_rect)

        # Draw debug collision boxes if NOT paused
       # if not self.show_exit_dialog:
       #     for rect in self.collision_rects:
       #         screen_pos = self.camera.apply(rect)
       #         pygame.draw.rect(surface, (255, 0, 0), screen_pos, 2)

        # Draw pause dialog LAST so it overlays everything else
        if self.show_exit_dialog:
            self.draw_exit_dialog(surface)


    def draw_tabs(self, surface):
        tab_area_x = 400
        tab_area_width = 500
        tab_width = tab_area_width // len(self.tab_panels)
        for idx, tab in enumerate(self.tab_panels):
            tab_rect = pygame.Rect(tab_area_x + idx * tab_width, 0, tab_width, 30)
            color = (255, 165, 0) if tab == self.active_tab else (220, 180, 120)
            pygame.draw.rect(surface, color, tab_rect)
            label = self.font.render(tab, True, (0, 0, 0))
            surface.blit(label, (tab_rect.x + 5, tab_rect.y + 5))

    def draw_exit_dialog(self, surface):
        dialog_width, dialog_height = 300, 150
        x = self.camera.viewport_width // 2 - dialog_width // 2
        y = self.camera.viewport_height // 2 - dialog_height // 2

        self.yes_rect = pygame.Rect(x + 40, y + 80, 80, 30)
        self.no_rect = pygame.Rect(x + 180, y + 80, 80, 30)

        overlay = pygame.Surface((self.camera.viewport_width, self.camera.viewport_height))
        overlay.fill((0, 0, 0))  # fully opaque
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (50, 50, 50), (x, y, dialog_width, dialog_height))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, dialog_width, dialog_height), 2)

        title = self.font.render("Exit game?", True, (255, 255, 255))
        surface.blit(title, (x + 90, y + 20))

        yes_color = (200, 200, 0) if self.exit_selected == "Yes" else (100, 100, 100)
        no_color = (200, 200, 0) if self.exit_selected == "No" else (100, 100, 100)

        pygame.draw.rect(surface, yes_color, self.yes_rect)
        pygame.draw.rect(surface, no_color, self.no_rect)


        surface.blit(self.font.render("Yes", True, (0, 0, 0)), (x + 60, y + 85))
        surface.blit(self.font.render("No", True, (0, 0, 0)), (x + 205, y + 85))
