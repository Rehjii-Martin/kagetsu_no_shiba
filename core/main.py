import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Kagetsu no Shiba")

    clock = pygame.time.Clock()
    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(60) / 100 # Delta time in secs

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        game.update(dt)
        game.draw()
    
    pygame.quit()

if __name__ == "__main__":
    main()