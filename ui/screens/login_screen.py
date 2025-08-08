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
        surface.fill((15, 15, 30))  # darker background

        box = pygame.Rect(220, 180, 360, 260)
        pygame.draw.rect(surface, (35, 35, 60), box, border_radius=12)
        pygame.draw.rect(surface, (70, 70, 100), box, 2, border_radius=12)

        title = self.font.render("Sign In to Kagetsu", True, (255, 255, 255))
        surface.blit(title, (box.centerx - title.get_width() // 2, box.y + 15))

        # Username
        uname_label = self.label_font.render("Username", True, (200, 200, 200))
        uname_box = pygame.Rect(250, 230, 300, 30)
        pygame.draw.rect(surface, (255, 255, 255), uname_box, border_radius=6)
        pygame.draw.rect(surface, (50, 50, 80), uname_box.inflate(-4, -4), border_radius=6)
        surface.blit(uname_label, (uname_box.x, uname_box.y - 20))
        uname_text = self.font.render(self.username, True, (255, 255, 255))
        surface.blit(uname_text, (uname_box.x + 8, uname_box.y + 4))

        # Cursor
        if self.active_field == "username" and self.cursor_visible:
            cursor_x = uname_box.x + 8 + uname_text.get_width()
            cursor_y = uname_box.y + (uname_box.height - uname_text.get_height()) // 2
            pygame.draw.line(surface, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + uname_text.get_height()), 2)

        # Password
        pass_label = self.label_font.render("Password", True, (200, 200, 200))
        pass_box = pygame.Rect(250, 280, 300, 30)
        pygame.draw.rect(surface, (255, 255, 255), pass_box, border_radius=6)
        pygame.draw.rect(surface, (50, 50, 80), pass_box.inflate(-4, -4), border_radius=6)
        surface.blit(pass_label, (pass_box.x, pass_box.y - 20))
        pass_hidden = "*" * len(self.password)
        pass_text = self.font.render(pass_hidden, True, (255, 255, 255))
        surface.blit(pass_text, (pass_box.x + 8, pass_box.y + 4))

        if self.active_field == "password" and self.cursor_visible:
            cursor_x = pass_box.x + 8 + pass_text.get_width()
            cursor_y = pass_box.y + (pass_box.height - pass_text.get_height()) // 2
            pygame.draw.line(surface, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + pass_text.get_height()), 2)

        # Button
        sign_in_button = pygame.Rect(250, 340, 300, 36)
        pygame.draw.rect(surface, (80, 140, 240), sign_in_button, border_radius=6)
        btn_label = self.font.render("Sign In", True, (255, 255, 255))
        surface.blit(btn_label, (sign_in_button.centerx - btn_label.get_width() // 2,
                                sign_in_button.centery - btn_label.get_height() // 2))
