# game.py
import pygame
from entities.player import Player
from core.projectile import Projectile
from ui.screens.login_screen import LoginScreen
from ui.screens.char_select_screen import CharacterSelectScreen
from ui.screens.char_create_screen import CharacterCreateScreen
from ui.screens.hud_screen import HUDScreen

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = (25, 25, 40)  # A darker color for the background

        # ADD map/world dimensions
        self.map_width = 1600
        self.map_height = 1600

        # Store CLASSES here, not instances, so we can pass kwargs on demand
        self.screens = {
            "login": LoginScreen,
            "char_select": CharacterSelectScreen,
            "char_create": CharacterCreateScreen,
            "hud": HUDScreen,
        }

        # track name + active instance
        self.current_screen_name = "login"
        self.current_screen = self.screens[self.current_screen_name](self)

    def set_screen(self, name, **kwargs):
        if name not in self.screens:
            return
        self.current_screen_name = name
        screen_cls = self.screens[name]
        # (Re)create the screen instance each time so kwargs (e.g., player=...) can be used
        self.current_screen = screen_cls(self, **kwargs)

    def update(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        # Always update the active instance
        self.current_screen.update(dt, events)

    def draw(self):
        self.screen.fill(self.bg_color)
        # Always draw the active instance
        self.current_screen.draw(self.screen)
        pygame.display.flip()
