from .projectile import Projectile
import pygame

"""
Classe AxeProjectile: Herda de Projectile.
O projétil se move em um arco balístico (efeito de gravidade ou curva).
Também deve ter a flag 'piercing' para perfurar inimigos.
"""
class AxeProjectile(Projectile):
    def __init__(self, start_x, start_y, direction_vector, damage):
        super().__init__(start_x, start_y, direction_vector, damage)
        self._last_hit_times = {}  # Para cooldown por inimigo
        try:
            self.original_image = pygame.image.load('assets/sprites/Axe.png').convert_alpha()
        except Exception:
            self.original_image = pygame.Surface((32, 32))
            self.original_image.fill((120, 120, 120))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.angle = 0
        self.piercing = True  # Flag para perfuração
        self.vertical_speed = -5  # Velocidade vertical inicial (para simular ser jogado para cima)
        self.gravity = 0.2  # Simulação de arco
        self.horizontal_speed = self.direction_vector[0] * 7  # Velocidade horizontal baseada na direção

    def can_hit(self, enemy, cooldown_ms=500):
        now = pygame.time.get_ticks()
        last = self._last_hit_times.get(enemy, 0)
        if now - last >= cooldown_ms:
            self._last_hit_times[enemy] = now
            return True
        return False
    def __init__(self, start_x, start_y, direction_vector, damage):
        super().__init__(start_x, start_y, direction_vector, damage)
        try:
            self.original_image = pygame.image.load('assets/sprites/Axe.png').convert_alpha()
        except Exception:
            self.original_image = pygame.Surface((32, 32))
            self.original_image.fill((120, 120, 120))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.angle = 0
        self.piercing = True  # Flag para perfuração
        self.vertical_speed = -5  # Velocidade vertical inicial (para simular ser jogado para cima)
        self.gravity = 0.2  # Simulação de arco
        self.horizontal_speed = self.direction_vector[0] * 7  # Velocidade horizontal baseada na direção

    def update(self):
        # Movimento balístico: acelera verticalmente e move horizontalmente
        self.vertical_speed += self.gravity
        self.rect.y += int(self.vertical_speed)
        self.rect.x += int(self.horizontal_speed)
        # Faz o machado girar
        self.angle = (self.angle + 18) % 360  # 20 graus por frame, ajuste se quiser mais rápido/lento
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        # Corrige o centro após rotação
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        # Remove o projétil se sair da tela
        screen = pygame.display.get_surface()
        if not screen.get_rect().colliderect(self.rect):
            self.kill()
