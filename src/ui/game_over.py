import pygame


class GameOver:
    """
    Tela de Game Over com menu simples: Reiniciar / Quit.

    Uso:
      go = GameOver(screen)
      action = go.run()  # action == 'restart' or 'quit'
    """
    def __init__(self, screen, font_name=None, title="GAME OVER"):
        self.screen = screen
        self.w, self.h = screen.get_size()
        self.font_name = font_name
        self.title = title
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.title_font = pygame.font.SysFont(font_name or None, 48, bold=True)
        self.menu_font = pygame.font.SysFont(font_name or None, 28)
        self.options = ["Reiniciar", "Menu Principal", "Quit"]
        self.selected = 0
        # Toca música de game over
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('assets/audio/gameover.mp3')
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def draw(self):
        # Fundo com Gameover.png
        try:
            bg_img = pygame.image.load('assets/sprites/Gameover.png').convert_alpha()
            bg_img = pygame.transform.smoothscale(bg_img, (self.w, self.h))
            self.screen.blit(bg_img, (0, 0))
        except Exception:
            self.screen.fill((30, 30, 30))

        # Overlay escuro para contraste
        overlay = pygame.Surface((self.w, self.h), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # Título centralizado, estilo destacado
        title_font = pygame.font.SysFont(self.font_name or None, 64, bold=True)
        title_surf = title_font.render(self.title, True, (255, 220, 0))
        title_rect = title_surf.get_rect(center=(self.w // 2, self.h // 2 - 120))
        self.screen.blit(title_surf, title_rect)

        # Caixa de opções centralizada, estilo HUD
        box_width, box_height = 320, 56
        spacing = 32
        start_y = self.h // 2 - 20
        for i, opt in enumerate(self.options):
            x = self.w // 2 - box_width // 2
            y = start_y + i * (box_height + spacing)
            # Fundo e borda
            if i == self.selected:
                pygame.draw.rect(self.screen, (60, 90, 180), (x, y, box_width, box_height), border_radius=12)
                pygame.draw.rect(self.screen, (255, 255, 120), (x, y, box_width, box_height), 4, border_radius=12)
            else:
                pygame.draw.rect(self.screen, (60, 60, 70), (x, y, box_width, box_height), border_radius=12)
                pygame.draw.rect(self.screen, (120, 120, 120), (x, y, box_width, box_height), 2, border_radius=12)
            # Texto da opção
            color = (255, 255, 0) if i == self.selected else (220, 220, 220)
            opt_surf = self.menu_font.render(opt, True, color)
            opt_rect = opt_surf.get_rect(center=(self.w // 2, y + box_height // 2))
            self.screen.blit(opt_surf, opt_rect)



        pygame.display.flip()

    def run(self):
        # loop da tela de Game Over. Retorna 'restart', 'menu' ou 'quit'
        result = None
        while result is None:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    result = 'quit'
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.selected == 0:
                            result = 'restart'
                        elif self.selected == 1:
                            result = 'menu'
                        else:
                            result = 'quit'
                    elif event.key == pygame.K_ESCAPE:
                        result = 'quit'
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # detectar clique nas opções
                    box_width, box_height = 320, 56
                    spacing = 32
                    start_y = self.h // 2 - 20
                    for i in range(len(self.options)):
                        x = self.w // 2 - box_width // 2
                        y = start_y + i * (box_height + spacing)
                        rect = pygame.Rect(x, y, box_width, box_height)
                        if rect.collidepoint(mx, my):
                            if i == 0:
                                result = 'restart'
                            elif i == 1:
                                result = 'menu'
                            else:
                                result = 'quit'
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    box_width, box_height = 320, 56
                    spacing = 32
                    start_y = self.h // 2 - 20
                    for i in range(len(self.options)):
                        x = self.w // 2 - box_width // 2
                        y = start_y + i * (box_height + spacing)
                        rect = pygame.Rect(x, y, box_width, box_height)
                        if rect.collidepoint(mx, my):
                            self.selected = i
            self.draw()
        # Para a música de game over ao sair
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        return result
