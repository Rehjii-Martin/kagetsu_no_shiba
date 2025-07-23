import pygame

class LoginScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont("segoeui", 22)
        self.label_font = pygame.font.SysFont("segoeui", 18)
        self.username = ""
        self.password = ""
        self.active_field = None
        self.cursor_timer = 0
        self.cursor_visible = True

    def update(self, dt, events):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                uname_box = pygame.Rect(280, 240, 240, 28)
                pass_box = pygame.Rect(280, 290, 240, 28)
                sign_in_button = pygame.Rect(280, 340, 240, 30)

                if uname_box.collidepoint(event.pos):
                    self.active_field = "username"
                elif pass_box.collidepoint(event.pos):
                    self.active_field = "password"
                elif sign_in_button.collidepoint(event.pos):
                    if self.username and self.password:
                        self.game.set_screen("char_select")
                else:
                    self.active_field = None

            if event.type == pygame.KEYDOWN and self.active_field:
                if event.key == pygame.K_RETURN:
                    if self.username and self.password:
                        self.game.set_screen("char_select")
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_field == "username":
                        self.username = self.username[:-1]
                    else:
                        self.password = self.password[:-1]
                else:
                    if self.active_field == "username":
                        self.username += event.unicode
                    else:
                        self.password += event.unicode

    def draw(self, surface):
        surface.fill((0, 0, 128))  # XP blue background

        # XP login box
        box = pygame.Rect(190, 180, 400, 290)
        pygame.draw.rect(surface, (192, 192, 192), box)  # outer frame
        pygame.draw.rect(surface, (255, 255, 255), box.inflate(-4, -4))  # white inner area

        # XP-style title bar
        title_bar = pygame.Rect(box.x, box.y, box.width, 30)
        pygame.draw.rect(surface, (10, 36, 106), title_bar)
        title = self.font.render("Kagetsu No Shiba Login", True, (255, 255, 255))
        surface.blit(title, (title_bar.x + 10, title_bar.y + 5))

        # Username
        surface.blit(self.label_font.render("Username:", True, (0, 0, 0)), (200, 245))
        uname_box = pygame.Rect(280, 240, 240, 28)
        pygame.draw.rect(surface, (255, 255, 255), uname_box)
        pygame.draw.rect(surface, (0, 0, 0), uname_box, 1)
        uname_text = self.font.render(self.username, True, (0, 0, 0))
        surface.blit(uname_text, (uname_box.x + 6, uname_box.y + 3))

        # Password
        surface.blit(self.label_font.render("Password:", True, (0, 0, 0)), (200, 295))
        pass_box = pygame.Rect(280, 290, 240, 28)
        pygame.draw.rect(surface, (255, 255, 255), pass_box)
        pygame.draw.rect(surface, (0, 0, 0), pass_box, 1)
        pass_hidden = "*" * len(self.password)
        pass_text = self.font.render(pass_hidden, True, (0, 0, 0))
        surface.blit(pass_text, (pass_box.x + 6, pass_box.y + 3))

        # Cursor
        if self.active_field == "username" and self.cursor_visible:
            cursor_x = uname_box.x + 6 + uname_text.get_width()
            pygame.draw.line(surface, (0, 0, 0), (cursor_x, uname_box.y + 4), (cursor_x, uname_box.y + 24), 2)
        elif self.active_field == "password" and self.cursor_visible:
            cursor_x = pass_box.x + 6 + pass_text.get_width()
            pygame.draw.line(surface, (0, 0, 0), (cursor_x, pass_box.y + 4), (cursor_x, pass_box.y + 24), 2)

        # XP-style button
        sign_in_button = pygame.Rect(280, 340, 240, 30)
        pygame.draw.rect(surface, (192, 192, 192), sign_in_button)
        pygame.draw.rect(surface, (0, 0, 0), sign_in_button, 1)
        btn_label = self.font.render("Sign In", True, (0, 0, 0))
        surface.blit(btn_label, (sign_in_button.centerx - btn_label.get_width() // 2,
                                sign_in_button.centery - btn_label.get_height() // 2))

        # Info
        info = self.font.render("[ENTER] or click Sign In", True, (10, 10, 10))
        surface.blit(info, (box.centerx - info.get_width() // 2, box.y + box.height - 40))