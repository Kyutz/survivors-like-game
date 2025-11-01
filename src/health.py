import pygame


class Health:
    """Componente de vida reutilizável.

    - max_health: vida máxima
    - current: vida atual
    - invuln_ms: período (ms) após receber dano em que não recebe novo dano
    """
    def __init__(self, max_health: int, invuln_ms: int = 500):
        self.max_health = max(1, int(max_health))
        self.current = int(self.max_health)
        self._invuln_ms = int(invuln_ms)
        self._last_hit_time = 0

    def take_damage(self, amount: int) -> bool:
        """Aplica dano se não estiver em invulnerabilidade.

        Retorna True se a entidade morreu (vida <= 0).
        """
        now = pygame.time.get_ticks()
        if now - self._last_hit_time < self._invuln_ms:
            return False
        self._last_hit_time = now
        self.current -= int(amount)
        if self.current < 0:
            self.current = 0
        return self.current == 0

    def heal(self, amount: int):
        self.current = min(self.max_health, self.current + int(amount))

    def is_dead(self) -> bool:
        return self.current <= 0

    def draw(self, surface: pygame.Surface, owner_rect: pygame.Rect, *,
             bar_width: int = 28, bar_height: int = 6, y_offset: int = 4):
        """Desenha uma barra pequena de vida abaixo do rect do owner.

        Parâmetros pequenos por padrão para não atrapalhar visão.
        """
        x = owner_rect.centerx - bar_width // 2
        y = owner_rect.bottom + y_offset

        fill_ratio = max(0, self.current) / max(1, self.max_health)
        fill_width = int(bar_width * fill_ratio)

        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        fg_rect = pygame.Rect(x, y, fill_width, bar_height)

        pygame.draw.rect(surface, (100, 0, 0), bg_rect)
        if fill_width > 0:
            pygame.draw.rect(surface, (0, 200, 0), fg_rect)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)
