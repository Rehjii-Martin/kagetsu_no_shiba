import pygame
class CanvasBorder:
    def __init__(self, camera, player, coord_font):
        self.camera = camera
        self.player = player
        self.coord_font = coord_font
    def draw(self, surface):
        pygame.draw.rect(surface, (255,0,0), pygame.Rect(0,0,self.camera.viewport_width,self.camera.viewport_height),1)
        coords = f"X: {self.player.rect.centerx} | Y: {self.player.rect.centery}"
        ct = self.coord_font.render(coords, True, (255,255,255))
        cr = ct.get_rect(center=(surface.get_width()//2,15))
        overlay = pygame.Surface((cr.width+20, cr.height+8), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        surface.blit(overlay, (cr.x-10, cr.y-4))
        surface.blit(ct, cr)