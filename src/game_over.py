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
        self.options = ["Reiniciar", "Quit"]
        self.selected = 0

    def draw(self):
        # overlay semitransparente
        overlay = pygame.Surface((self.w, self.h), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # título
        title_surf = self.title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.w // 2, self.h // 2 - 80))
        self.screen.blit(title_surf, title_rect)

        # opções
        for i, opt in enumerate(self.options):
            color = (255, 220, 0) if i == self.selected else (200, 200, 200)
            opt_surf = self.menu_font.render(opt, True, color)
            opt_rect = opt_surf.get_rect(center=(self.w // 2, self.h // 2 - 10 + i * 48))
            self.screen.blit(opt_surf, opt_rect)

        # instrução pequena
        instr = self.menu_font.render("Use ESQ ou clique nas opções acima", True, (180, 180, 180))
        instr_rect = instr.get_rect(center=(self.w // 2, self.h // 2 + 110))
        self.screen.blit(instr, instr_rect)

        pygame.display.flip()

    def run(self):
        # loop da tela de Game Over. Retorna 'restart' ou 'quit'
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return 'restart' if self.selected == 0 else 'quit'
                    elif event.key == pygame.K_ESCAPE:
                        return 'quit'
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # detectar clique nas opções
                    for i in range(len(self.options)):
                        opt_y = self.h // 2 - 10 + i * 48
                        rect = pygame.Rect(self.w//2 - 120, opt_y - 18, 240, 36)
                        if rect.collidepoint(mx, my):
                            return 'restart' if i == 0 else 'quit'
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    for i in range(len(self.options)):
                        opt_y = self.h // 2 - 10 + i * 48
                        rect = pygame.Rect(self.w//2 - 120, opt_y - 18, 240, 36)
                        if rect.collidepoint(mx, my):
                            self.selected = i

            self.draw()
