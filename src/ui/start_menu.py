import pygame
from src.ui.config import ASSET_PATH


class StartMenu:
    """Menu inicial polido com instruções.

    Uso:
      menu = StartMenu(screen)
      action = menu.run()  # 'play' ou 'quit'
    """

    def __init__(self, screen, font_path=None):
        self.screen = screen
        self.w, self.h = screen.get_size()
        pygame.font.init()
        # tenta carregar fonte do assets, se existir
        self.title_font = None
        self.menu_font = None
        if font_path:
            try:
                self.title_font = pygame.font.Font(font_path, 56)
                self.menu_font = pygame.font.Font(font_path, 22)
            except Exception:
                self.title_font = pygame.font.SysFont(None, 56, bold=True)
                self.menu_font = pygame.font.SysFont(None, 22)
        else:
            # tenta fonte em assets
            try:
                candidate = f"{ASSET_PATH}/fonts/PressStart2P-Regular.ttf"
                self.title_font = pygame.font.Font(candidate, 36)
                self.menu_font = pygame.font.Font(candidate, 18)
            except Exception:
                self.title_font = pygame.font.SysFont(None, 56, bold=True)
                self.menu_font = pygame.font.SysFont(None, 22)

        self.clock = pygame.time.Clock()
        self.options = ["Jogar", "Como Jogar", "Sair"]
        self.selected = 0

    def _draw_background(self):
        # fundo escuro com leve noise/gradient (simples)
        bg = pygame.Surface((self.w, self.h))
        bg.fill((12, 12, 18))
        # ligeiro gradiente radial
        for i in range(0, 120, 12):
            w = self.w - i * 8
            h = self.h - i * 6
            # evita criar Surface com dimensão inválida
            if w <= 0 or h <= 0:
                break
            try:
                s = pygame.Surface((w, h), flags=pygame.SRCALPHA)
            except Exception:
                # fallback: pula esta iteração se não for possível criar
                continue
            alpha = max(0, 120 - i)
            s.fill((20, 20, 30, alpha))
            self.screen.blit(s, (i * 4, i * 3))

    def draw(self, show_instructions=False):
        self._draw_background()

        # título
        title_surf = self.title_font.render("SURVIVOR-LIKE", True, (255, 200, 40))
        title_rect = title_surf.get_rect(center=(self.w // 2, int(self.h * 0.22)))
        self.screen.blit(title_surf, title_rect)

        # menu
        for i, opt in enumerate(self.options):
            is_selected = (i == self.selected)
            color = (255, 220, 100) if is_selected else (200, 200, 200)
            size = 26 if is_selected else 20
            # cria fonte localmente com tamanho desejado (fallback simples)
            try:
                text_font = pygame.font.SysFont(None, size)
            except Exception:
                text_font = self.menu_font
            text = text_font.render(opt, True, color)
            rect = text.get_rect(center=(self.w // 2, int(self.h * 0.42) + i * 56))
            # desenhar retângulo de destaque
            if is_selected:
                highlight = pygame.Surface((rect.width + 24, rect.height + 12), flags=pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 12))
                self.screen.blit(highlight, (rect.x - 12, rect.y - 6))
            self.screen.blit(text, rect)

        # instruções rápidas
        instr = [
            "Movimento: W A S D",
            "Ataque: automático (arma atira sozinha)",
            "Colete gemas para ganhar XP e subir de nível",
            "ESC para sair"
        ]
        for i, line in enumerate(instr):
            s = self.menu_font.render(line, True, (170, 170, 170))
            r = s.get_rect(center=(self.w // 2, int(self.h * 0.78) + i * 20))
            self.screen.blit(s, r)

        # painel de instruções completo (modal)
        if show_instructions:
            box_w = int(self.w * 0.72)
            box_h = int(self.h * 0.56)
            box = pygame.Surface((box_w, box_h), flags=pygame.SRCALPHA)
            box.fill((18, 18, 22, 230))
            bx = self.w // 2 - box_w // 2
            by = self.h // 2 - box_h // 2
            pygame.draw.rect(box, (255, 215, 0), (8, 8, box_w - 16, 2))
            # title
            t = self.menu_font.render("Como Jogar", True, (255, 215, 0))
            box.blit(t, (20, 20))
            lines = [
                "- Use W A S D para movimentar o jogador.",
                "- Sua arma dispara automaticamente no inimigo mais próximo.",
                "- Coletar gemas de XP permite subir de nível e escolher melhorias.",
                "- Evite contato com inimigos; você perde vida ao colidir.",
                "- Pausar/Fechar: tecla ESC.", 
            ]
            for i, ln in enumerate(lines):
                lsurf = self.menu_font.render(ln, True, (220, 220, 220))
                box.blit(lsurf, (20, 60 + i * 26))
            # instrução de fechar
            close = self.menu_font.render("Pressione ESC para fechar", True, (170, 170, 170))
            box.blit(close, (20, box_h - 40))
            self.screen.blit(box, (bx, by))

        pygame.display.flip()

    def run(self):
        show_instructions = False
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        choice = self.options[self.selected]
                        if choice == 'Jogar':
                            return 'play'
                        elif choice == 'Como Jogar':
                            show_instructions = True
                        else:
                            return 'quit'
                    elif event.key == pygame.K_ESCAPE:
                        if show_instructions:
                            show_instructions = False
                        else:
                            return 'quit'
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    for i in range(len(self.options)):
                        opt_y = int(self.h * 0.42) + i * 56
                        rect = pygame.Rect(self.w//2 - 200, opt_y - 24, 400, 48)
                        if rect.collidepoint(mx, my):
                            self.selected = i
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for i in range(len(self.options)):
                        opt_y = int(self.h * 0.42) + i * 56
                        rect = pygame.Rect(self.w//2 - 200, opt_y - 24, 400, 48)
                        if rect.collidepoint(mx, my):
                            choice = self.options[i]
                            if choice == 'Jogar':
                                return 'play'
                            elif choice == 'Como Jogar':
                                show_instructions = True
                            else:
                                return 'quit'

            self.draw(show_instructions=show_instructions)
