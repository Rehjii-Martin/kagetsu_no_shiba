import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Kagetsu no Shiba")

    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        dt = clock.tick(60) / 1000.0  # Convert ms to seconds
        game.update(dt)
        game.draw()

if __name__ == "__main__":
    main()