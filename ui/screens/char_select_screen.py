import pygame, math

class CharacterSelectScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 28)
        self.options = ["Goku (Saiyan)", "Begeta (Human)", "Majik (Android)", "Create New Character"]
        self.selected_index = 0

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.selected_index] == "Create New Character":
                        self.game.set_screen("char_create")
                    else:
                        self.game.set_screen("hud")

    def draw(self, surface):
        w, h = surface.get_size()
        surface.fill((15, 15, 30))  # Dark background

        # Title
        title = self.font.render("Select or Create Your Character", True, (255, 255, 255))
        surface.blit(title, (w // 2 - title.get_width() // 2, 60))

        # Pulsing alpha using time
        ticks = pygame.time.get_ticks() / 1000.0  # seconds
        pulse = int(60 + 50 * (1 + math.sin(ticks * 2)))  # range: 60–160 (soft sine wave)

        for i, option in enumerate(self.options):
            is_selected = i == self.selected_index
            color = (255, 255, 0) if is_selected else (180, 180, 180)
            text = self.font.render(option, True, color)
            tx = w // 2 - text.get_width() // 2
            ty = 140 + i * 40

            if is_selected:
                glow_rect = pygame.Rect(tx - 12, ty - 6, text.get_width() + 24, text.get_height() + 12)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_surface.fill((255, 255, 100, pulse))  # animated alpha
                surface.blit(glow_surface, (glow_rect.x, glow_rect.y))

                pygame.draw.rect(surface, (255, 255, 255), glow_rect, 2, border_radius=6)

            surface.blit(text, (tx, ty))

        # Keyboard hint
        hint1 = self.font.render("Use Arrow Keys to select", True, (120, 120, 120))
        hint2 = self.font.render("Press Enter to confirm", True, (120, 120, 120))

        surface.blit(hint1, (w // 2 - hint1.get_width() // 2, h - 70))
        surface.blit(hint2, (w // 2 - hint2.get_width() // 2, h - 50))


