import pygame

class VitalsPanel:
    def __init__(self, player):
        self.player = player
        # panel origin to help size bars if needed
        self._panel_pos = (0, 0)
        self._panel_size = (0, 0)

    def draw(self, surface, x, y, width, height):
        font = pygame.font.SysFont(None, 24)
        self._panel_pos = (x, y)
        self._panel_size = (width, height)

        # background
        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))
        surface.blit(font.render("Vitals:", True, (255, 255, 255)), (x + 10, y + 10))

        bar_w = int(width * 0.6)  # 60% of panel width for bars

        # --- Health Bar ---
        health_ratio = self.player.health / max(1, self.player.max_health)
        hp_rect = pygame.Rect(x + 20, y + 40, int(bar_w * health_ratio), 20)
        pygame.draw.rect(surface, (180, 100, 100), hp_rect)
        pygame.draw.rect(surface, (255, 255, 255), (x + 20, y + 40, bar_w, 20), 2)
        surface.blit(font.render(f"{self.player.health}/{self.player.max_health}", True, (255,255,255)),
                     (x + 20, y + 65))

        # --- Ki (Energy) Bar ---
        ki_ratio = self.player.energy / max(1, self.player.max_energy)
        ki_rect = pygame.Rect(x + 20, y + 100, int(bar_w * ki_ratio), 20)
        pygame.draw.rect(surface, (100, 180, 180), ki_rect)
        pygame.draw.rect(surface, (255, 255, 255), (x + 20, y + 100, bar_w, 20), 2)
        surface.blit(font.render(f"{self.player.energy}/{self.player.max_energy}", True, (255,255,255)),
                     (x + 20, y + 125))

        # --- XP Bar ---
        # assuming you have a .xp_to_next_level field; else omit the fill
        xp_to_next = getattr(self.player, "xp_to_next_level", 100)
        xp_ratio = (self.player.xp % xp_to_next) / xp_to_next
        xp_rect = pygame.Rect(x + 20, y + 160, int(bar_w * xp_ratio), 10)
        pygame.draw.rect(surface, (240, 240, 100), xp_rect)
        pygame.draw.rect(surface, (255, 255, 255), (x + 20, y + 160, bar_w, 10), 1)
        surface.blit(font.render(f"XP: {self.player.xp}", True, (255,255,255)),
                     (x + 20, y + 175))
