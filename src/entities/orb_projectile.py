import pygame
import math

"""
Classe OrbProjectile: Herda de Sprite. 
Representa a pedra que gira. Sua posição é calculada em relação ao jogador (player_rect).
Usa seno e cosseno para o movimento orbital.
"""
class OrbProjectile(pygame.sprite.Sprite):
    def __init__(self, player, radius=50, speed=0.012, damage=3):
        super().__init__()
        self.player = player
        self.radius = radius  # Raio de órbita
        self.angle = 0  # Ângulo inicial (em radianos)
        self.rotation_speed = speed  # Velocidade de rotação
        self.damage = damage
        try:
            img = pygame.image.load('assets/sprites/Stone.png').convert_alpha()
            self.image = pygame.transform.scale(img, (32, 32))
        except Exception:
            self.image = pygame.Surface((32, 32))
            self.image.fill((120, 120, 120))
        self.rect = self.image.get_rect(center=self._calc_orbital_pos())
        self.mask = pygame.mask.from_surface(self.image)

    def _calc_orbital_pos(self):
        cx, cy = self.player.rect.center
        x = cx + self.radius * math.cos(self.angle)
        y = cy + self.radius * math.sin(self.angle)
        return (int(x), int(y))

    def update(self):
        self.angle += self.rotation_speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
        self.rect.center = self._calc_orbital_pos()
        # Atualiza a mask para garantir que a hitbox acompanha o sprite
        self.mask = pygame.mask.from_surface(self.image)
