import pygame
from src.entities.orb_projectile import OrbProjectile

"""
Classe StoneOrbWeapon: cria e gerencia um OrbProjectile girando ao redor do player.
Não possui cooldown, o orbe é persistente enquanto a arma existir.
"""
class StoneOrbWeapon:
    icon_path = 'assets/sprites/Stone.png'
    def __init__(self, player, radius=50, speed=0.012, damage=9999):
        self.player = player
        self.orb_group = pygame.sprite.Group()
        self.orb = OrbProjectile(player, radius=radius, speed=speed, damage=damage)
        self.orb_group.add(self.orb)

    def fire_attack(self, enemies):
        # O orbe é persistente, não dispara projéteis
        self.orb_group.update()
        # Colisão: se o orbe colidir com algum inimigo, remove imediatamente
        for orb in self.orb_group:
            collided = pygame.sprite.spritecollide(orb, enemies, False, pygame.sprite.collide_mask)
            for enemy in collided:
                enemy.kill()
        return None

    def draw(self, surface):
        self.orb_group.draw(surface)
