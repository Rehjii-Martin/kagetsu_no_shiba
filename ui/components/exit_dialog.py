import pygame
class ExitDialog:
    def __init__(self, camera, font):
        self.camera = camera
        self.font = font
        self.show = False
        self.selected = "No"
        self.yes_rect = pygame.Rect(0, 0, 0, 0)
        self.no_rect  = pygame.Rect(0, 0, 0, 0)
    def handle_events(self, events):
        for event in events:
            if not self.show: continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.yes_rect.collidepoint(event.pos): pygame.quit(); exit()
                if self.no_rect.collidepoint(event.pos): self.show = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                    self.selected = "Yes" if self.selected=="No" else "No"
                elif event.key == pygame.K_RETURN:
                    if self.selected=="Yes": pygame.quit(); exit()
                    else: self.show = False
    def draw(self, surface):
        if not self.show: return
        dw, dh = 300, 150
        x = self.camera.viewport_width//2 - dw//2
        y = self.camera.viewport_height//2 - dh//2
        overlay = pygame.Surface((self.camera.viewport_width, self.camera.viewport_height))
        overlay.set_alpha(150); overlay.fill((0,0,0))
        surface.blit(overlay, (0,0))
        pygame.draw.rect(surface, (50,50,50), (x,y,dw,dh))
        pygame.draw.rect(surface, (255,255,255), (x,y,dw,dh),2)
        surf = self.font.render("Exit game?", True, (255,255,255))
        surface.blit(surf, (x+dw//2-surf.get_width()//2, y+20))
        self.yes_rect = pygame.Rect(x+40, y+80, 80,30)
        self.no_rect  = pygame.Rect(x+dw-40-80, y+80, 80,30)
        yc = (200,200,0) if self.selected=="Yes" else (100,100,100)
        nc = (200,200,0) if self.selected=="No" else (100,100,100)
        pygame.draw.rect(surface, yc, self.yes_rect)
        pygame.draw.rect(surface, nc, self.no_rect)
        surface.blit(self.font.render("Yes", True, (0,0,0)), (self.yes_rect.x+20, self.yes_rect.y+5))
        surface.blit(self.font.render("No", True, (0,0,0)), (self.no_rect.x+25, self.no_rect.y+5))
