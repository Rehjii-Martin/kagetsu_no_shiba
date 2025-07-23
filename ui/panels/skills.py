import pygame

class SkillsPanel:
    def __init__(self):
        # define the size of each button once
        self.button_size = (100, 24)
        # placeholders; real positions get set every draw
        self.ki_rect = pygame.Rect(0, 0, *self.button_size)
        self.dash_rect = pygame.Rect(0, 0, *self.button_size)
        # store last panel coords so we can recalc in handle_click()
        self._panel_pos = (0, 0)

    def handle_click(self, pos, player, projectile_system, dt, collision_rects, map_rect):
        x, y = self._panel_pos

        # recompute button positions
        self.ki_rect.topleft   = (x + 20, y + 40)
        self.dash_rect.topleft = (x + 20, y + 70)

        # now safe to collidepoint
        if self.dash_rect.collidepoint(pos):
            player.try_dash(dt, collision_rects, map_rect) 
        elif self.ki_rect.collidepoint(pos):
            proj = player.try_shoot(pygame.key.get_pressed())
            if proj:
                projectile_system.add(proj)

    def draw(self, surface, x, y, width, height):
        import pygame  # ensure pygame is in scope
        font = pygame.font.SysFont(None, 24)

        # remember panel origin for clicks
        self._panel_pos = (x, y)

        # panel background
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height))
        surface.blit(font.render("Skill List:", True, (255, 255, 255)), (x + 10, y + 10))

        # compute & draw buttons
        self.ki_rect.topleft   = (x + 20, y + 40)
        self.dash_rect.topleft = (x + 20, y + 70)

        surface.blit(font.render("• Ki Blast", True, (200, 200, 200)), self.ki_rect.topleft)
        surface.blit(font.render("• Dash",     True, (200, 200, 200)), self.dash_rect.topleft)
