import pygame
from src.entities.projectile import Projectile # Precisa do projétil para atacar

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
        Atira automaticamente no inimigo mais próximo. Se o player tiver amount_multiplier, dispara projéteis extras.
        """
        current_time = pygame.time.get_ticks()
        # Cooldown efetivo pode ser reduzido por passiva
        effective_cooldown = self.cooldown
        if hasattr(self.player, 'cooldown_multiplier'):
            effective_cooldown *= (1.0 + self.player.cooldown_multiplier) if self.player.cooldown_multiplier < 0 else self.player.cooldown_multiplier
        if current_time - self.last_shot_time > effective_cooldown:
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
                # Multiplica o dano pelo damage_multiplier do player
                final_damage = self.damage * getattr(self.player, 'damage_multiplier', 1.0)
                # --- Lógica de Chance Crítica ---
                import random
                if hasattr(self.player, 'crit_chance') and random.random() < self.player.crit_chance:
                    final_damage *= 2  # Dano Crítico
                # --- Lógica de amount_multiplier (projéteis extras) ---
                amount = 1 + int(getattr(self.player, 'amount_multiplier', 0))
                projectiles = []
                spread_angle = 25  # graus entre projéteis
                for i in range(amount):
                    if amount == 1:
                        angle_offset = 0
                    else:
                        angle_offset = (i - (amount-1)/2) * spread_angle
                    # Rotaciona o vetor direction pelo offset
                    vec = pygame.math.Vector2(direction)
                    vec = vec.rotate(angle_offset)
                    projectiles.append(Projectile(
                        self.player.rect.centerx, self.player.rect.centery, vec,
                        damage=final_damage, sprite_path='assets/sprites/arrow01.png'))
                if len(projectiles) == 1:
                    return projectiles[0]
                return projectiles
        return None

