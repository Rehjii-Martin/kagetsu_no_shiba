import pygame
import collections
from entities.player import Player

class CharacterCreateScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.races = ["Saiyan", "Namekian", "Android", "Shiba"]
        self.selected = 0
        self.char_name = ""
        self.preview = Player(400, 420, race=self.races[self.selected])

        # Preview animation state
        self.preview_direction_index = 0
        self.preview_frame_index = 0
        self.preview_anim_timer = 0
        self.preview_anim_delay = 0.12
        self.preview_directions = ["right", "up", "left", "down"]

    def update(self, dt, events):
        # Animate preview character
        self.preview_anim_timer += dt
        if self.preview_anim_timer >= self.preview_anim_delay:
            self.preview_anim_timer = 0
            self.preview_frame_index = (self.preview_frame_index + 1) % 6
            if self.preview_frame_index == 0:
                self.preview_direction_index = (self.preview_direction_index + 1) % 4

            dir_name = self.preview_directions[self.preview_direction_index]
            self.preview.direction = dir_name
            self.preview.image = self.preview.animations[dir_name][self.preview_frame_index]

        # No movement
        fake_keys = collections.defaultdict(lambda: False)
        self.preview.update(fake_keys, dt, pygame.Rect(0, 0, 800, 600), [], override_animation=True)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.races)
                    self.preview = Player(400, 420, race=self.races[self.selected])
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.races)
                    self.preview = Player(400, 420, race=self.races[self.selected])
                elif event.key == pygame.K_BACKSPACE:
                    self.char_name = self.char_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self.game.set_screen("hud")
                else:
                    self.char_name += event.unicode

    def draw(self, surface):
        surface.fill((20, 20, 20))
        surface.blit(self.font.render("Select Your Race", True, (255,255,255)), (50, 30))
        for i, race in enumerate(self.races):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            surface.blit(self.font.render(race, True, color), (60, 60 + i * 30))

        info = [
            f"Race: {self.races[self.selected]}",
            "Bonus: +10% Melee",  # placeholder
            f"Desc: {self.races[self.selected]}s are fierce..."
        ]
        for i, line in enumerate(info):
            surface.blit(self.font.render(line, True, (180,180,180)), (300, 60 + i * 25))

        surface.blit(self.font.render("Name:", True, (255,255,255)), (60, 220))
        surface.blit(self.font.render(self.char_name, True, (255,255,255)), (120, 220))

        self.preview.draw(surface, None)
