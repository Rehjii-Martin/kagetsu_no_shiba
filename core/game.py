import pygame
from entities.player import Player

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(x=100, y=100)
        self.bg_color = (10, 10, 10)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)
    
    def draw(self):
        self.screen.fill(self.bg_color)
        self.player.draw(self.screen)
        pygame.display.flip()

    
