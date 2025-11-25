import pygame
from src.entities.weapon import Weapon
from src.entities.axe_projectile import AxeProjectile

"""
Classe AxeWeapon: dispara um machado em arco, perfurante.
Pode mirar no inimigo mais próximo ou atirar na direção do movimento do player.
"""
class AxeWeapon(Weapon):
    icon_path = 'assets/sprites/Axe.png'
    def __init__(self, player, cooldown=1200, damage=12):
        super().__init__(player, cooldown, damage)

    def fire_attack(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.cooldown:
            return None
        # Mira no inimigo mais próximo
        closest_enemy = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = ((enemy.rect.centerx - self.player.rect.centerx) ** 2 + (enemy.rect.centery - self.player.rect.centery) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        if closest_enemy is not None:
            dx = closest_enemy.rect.centerx - self.player.rect.centerx
            dy = closest_enemy.rect.centery - self.player.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist == 0:
                direction = (1, 0)
            else:
                direction = (dx / dist, dy / dist)
        else:
            # Se não houver inimigo, atira para a direita
            direction = (1, 0)
        self.last_shot_time = now
        # Só lança dois machados se o jogador tiver amount_multiplier > 0
        import math
        amount = 1 + int(getattr(self.player, 'amount_multiplier', 0))
        projectiles = []
        if amount == 1:
            dir1 = pygame.math.Vector2(direction)
            axe1 = AxeProjectile(self.player.rect.centerx, self.player.rect.centery, dir1, self.damage)
            projectiles.append(axe1)
        else:
            # Dois machados em direções opostas
            dir1 = pygame.math.Vector2(direction)
            dir2 = dir1.rotate(180)
            axe1 = AxeProjectile(self.player.rect.centerx, self.player.rect.centery, dir1, self.damage)
            axe2 = AxeProjectile(self.player.rect.centerx, self.player.rect.centery, dir2, self.damage)
            projectiles.extend([axe1, axe2])
        return projectiles
