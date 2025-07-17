class SkillsPanel:
    def __init__(self):
        self.ki_rect = None
        self.dash_rect = None

    def draw(self, surface, x, y, width, height):
        import pygame
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height))
        font = pygame.font.SysFont(None, 24)
        surface.blit(font.render("Skill List:", True, (255, 255, 255)), (x + 10, y + 10))

        self.ki_rect = pygame.Rect(x + 20, y + 40, 100, 24)
        self.dash_rect = pygame.Rect(x + 20, y + 70, 100, 24)

        surface.blit(font.render("• Ki Blast", True, (200, 200, 200)), self.ki_rect.topleft)
        surface.blit(font.render("• Dash", True, (200, 200, 200)), self.dash_rect.topleft)
