import pygame

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
        title = self.font.render("Select or Create Your Character", True, (255, 255, 255))
        surface.blit(title, (w//2 - title.get_width()//2, 80))

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(option, True, color)
            surface.blit(text, (w//2 - text.get_width()//2, 150 + i * 40))

