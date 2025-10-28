import pygame
from src.projectile import Projectile # Precisa do projétil para atacar

"""
Classe Weapon: Gerencia o ataque automático e a criação de projéteis.
Define o cooldown (intervalo entre ataques) e o dano.
"""
class Weapon:
    def __init__(self, player, cooldown=500, damage=10):
        self.player = player
        self.cooldown = cooldown # Tempo em milissegundos entre ataques
        self.damage = damage
        self.last_shot_time = 0 # Tempo do último ataque realizado

    def fire_attack(self, enemies):
        """
        Atira automaticamente no inimigo mais próximo.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.cooldown:
            self.last_shot_time = current_time
            # Encontra inimigo mais próximo
            nearest_enemy = None
            min_dist = float('inf')
            for enemy in enemies:
                dx = enemy.rect.centerx - self.player.rect.centerx
                dy = enemy.rect.centery - self.player.rect.centery
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_enemy = enemy
            # Se houver inimigo, calcula direção
            if nearest_enemy:
                dx = nearest_enemy.rect.centerx - self.player.rect.centerx
                dy = nearest_enemy.rect.centery - self.player.rect.centery
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist != 0:
                    direction = (dx / dist, dy / dist)
                else:
                    direction = (1, 0)
                return Projectile(self.player.rect.centerx, self.player.rect.centery, direction)
        return None

