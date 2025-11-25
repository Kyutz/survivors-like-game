from .projectile import Projectile
import pygame
import math

"""
Classe FireBall: Herda de Projectile.
Visual laranja/amarelo, tamanho 16x16, usa Fireball.png se disponível.
"""
class FireBall(Projectile):
    def __init__(self, start_x, start_y, direction_vector, damage):
        super().__init__(start_x, start_y, direction_vector, damage)
        self.speed = 6  # Mais lenta que a flecha (ajuste conforme necessário)
        try:
            img = pygame.image.load('assets/sprites/Fireball.png').convert_alpha()
            self.image = pygame.transform.scale(img, (24, 24))
        except Exception:
            self.image = pygame.Surface((24, 24))
            self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        # Movimento manual para usar self.speed
        self.rect.x += int(self.direction_vector[0] * self.speed)
        self.rect.y += int(self.direction_vector[1] * self.speed)
        # Gira o sprite na direção do movimento
        angle = math.degrees(math.atan2(-self.direction_vector[1], self.direction_vector[0]))
        try:
            img = pygame.image.load('assets/sprites/Fireball.png').convert_alpha()
            base_img = pygame.transform.scale(img, (24, 24))
        except Exception:
            base_img = pygame.Surface((24, 24))
            base_img.fill((255, 100, 0))
        self.image = pygame.transform.rotate(base_img, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
