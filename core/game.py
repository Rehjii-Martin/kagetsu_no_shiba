# game.py
import pygame
from entities.player import Player
from core.projectile import Projectile
from ui.login_screen import LoginScreen
from ui.char_select_screen import CharacterSelectScreen
from ui.char_create_screen import CharacterCreateScreen
from ui.hud_screen import HUDScreen

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = (25, 25, 40) # A darker color for the background

        # ADD map/world dimensions
        self.map_width = 1600
        self.map_height = 1600

        # Screens / States
        self.screens = {
            "login": LoginScreen(self),
            "char_select": CharacterSelectScreen(self),
            "char_create": CharacterCreateScreen(self),
            # UPDATED to pass map dimensions and tmx_data to the HUD
            "hud": HUDScreen(self, self.map_width, self.map_height, tmx_data=None),
        }
        self.current_screen_name = "login"

    def set_screen(self, name):
        if name in self.screens:
            self.current_screen_name = name

    def update(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        current_screen = self.screens[self.current_screen_name]
        current_screen.update(dt, events)

    def draw(self):
        self.screen.fill(self.bg_color)
        self.screens[self.current_screen_name].draw(self.screen)
        pygame.display.flip()