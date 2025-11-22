from pygame.sprite import Sprite
import pygame

"""
Classe HealingDrop: Herda de Sprite. 
Representa um item de cura (Carne). Usa um sprite heal.png ou um quadrado azul se não encontrar.
Define o valor de cura (heal_amount).
"""
class HealingDrop(Sprite):
    def __init__(self, x, y, heal_amount=10):
        super().__init__()
        try:
            img = pygame.image.load('assets/sprites/heal.png').convert_alpha()
            self.image = pygame.transform.scale(img, (16, 16))
        except Exception:
            self.image = pygame.Surface((12, 12))
            self.image.fill((0, 0, 150)) # Azul Escuro (Item de Cura)
        self.rect = self.image.get_rect(center=(x, y))
        self.heal_amount = heal_amount
        self.magnet_radius = 48  # igual ao XP
        self.magnet_speed = 3
        self.target_player = None

    def set_player(self, player):
        self.target_player = player

    def update(self):
        # Magnetismo: se o player estiver próximo, move em direção ao player
        if self.target_player:
            player_rect = self.target_player.rect
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < self.magnet_radius and dist > 0:
                dx /= dist
                dy /= dist
                self.rect.x += int(dx * self.magnet_speed)
                self.rect.y += int(dy * self.magnet_speed)
