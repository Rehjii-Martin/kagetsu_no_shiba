import pygame

class DraggableVitalsBox:
    def __init__(self, player, x=20, y=20, width=200, height=100):
        self.player = player
        self.rect = pygame.Rect(x, y, width, height)
        self.dragging = False
        self.drag_offset = (0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mx, my = event.pos
                self.drag_offset = (self.rect.x - mx, self.rect.y - my)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            self.rect.x = mx + self.drag_offset[0]
            self.rect.y = my + self.drag_offset[1]

    def draw(self, surface):
        # background
        pygame.draw.rect(surface, (40, 40, 60), self.rect)
        pygame.draw.rect(surface, (255,255,255), self.rect, 2)

        # compute bar widths
        bar_w = self.rect.width - 20
        # Health
        h_ratio = self.player.health / max(1, self.player.max_health)
        hp = pygame.Rect(self.rect.x+10, self.rect.y+10, int(bar_w*h_ratio), 15)
        pygame.draw.rect(surface, (180, 100, 100), hp)
        pygame.draw.rect(surface, (255,255,255), (self.rect.x+10, self.rect.y+10, bar_w, 15), 2)
        # Ki
        k_ratio = self.player.energy / max(1, self.player.max_energy)
        kp = pygame.Rect(self.rect.x+10, self.rect.y+35, int(bar_w*k_ratio), 15)
        pygame.draw.rect(surface, (100, 180, 180), kp)
        pygame.draw.rect(surface, (255,255,255), (self.rect.x+10, self.rect.y+35, bar_w, 15), 2)
        # XP
        xp_to_next = getattr(self.player, "xp_to_next_level", 100)
        xp_ratio = (self.player.xp % xp_to_next) / xp_to_next
        xp = pygame.Rect(self.rect.x+10, self.rect.y+60, int(bar_w*xp_ratio), 10)
        pygame.draw.rect(surface, (240,240,100), xp)
        pygame.draw.rect(surface, (255,255,255), (self.rect.x+10, self.rect.y+60, bar_w, 10), 1)
