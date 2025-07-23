import pygame
class TabManager:
    def __init__(self, tab_panels, font):
        self.tab_panels = tab_panels
        self.font = font
        self.active = next(iter(tab_panels))
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                total_w = 500; x0 = 400
                tab_w = total_w//len(self.tab_panels)
                for i, name in enumerate(self.tab_panels):
                    if pygame.Rect(x0+i*tab_w, 0, tab_w,30).collidepoint(event.pos):
                        self.active = name
    def draw(self, surface):
        total_w = 500; x0 = 400
        tab_w = total_w//len(self.tab_panels)
        for i, name in enumerate(self.tab_panels):
            r = pygame.Rect(x0+i*tab_w,0,tab_w,30)
            col = (255,165,0) if name==self.active else (220,180,120)
            pygame.draw.rect(surface, col, r)
            lbl = self.font.render(name, True, (0,0,0))
            surface.blit(lbl, (r.x+5, r.y+5))
        # draw panel content below
        self.tab_panels[self.active].draw(surface, x0, 40, total_w, 340)
