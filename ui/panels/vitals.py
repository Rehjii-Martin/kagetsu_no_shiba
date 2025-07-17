class VitalsPanel:
    def __init__(self, player):
        self.player = player

    def draw(self, surface, x, y, width, height):
        import pygame
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))
        surface.blit(font.render("Vitals:", True, (255, 255, 255)), (x + 10, y + 10))
        surface.blit(font.render(f"HP: {self.player.health} / {self.player.max_health}", True, (180, 100, 100)), (x + 20, y + 40))
        surface.blit(font.render(f"Ki: {self.player.energy} / {self.player.max_energy}", True, (100, 180, 180)), (x + 20, y + 70))
        surface.blit(font.render(f"XP: {self.player.xp}", True, (240, 240, 100)), (x + 20, y + 100))
