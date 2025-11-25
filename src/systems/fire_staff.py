
import pygame
import math
from src.entities.weapon import Weapon
from ..entities.fire_ball import FireBall

class FireStaff(Weapon):
    icon_path = 'assets/sprites/Staff.png'
    def __init__(self, player, cooldown=1200, damage=15):
        super().__init__(player, cooldown, damage)
    def fire_attack(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.cooldown:
            return None
        # Mira no inimigo mais próximo
        closest_enemy = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.hypot(enemy.rect.centerx - self.player.rect.centerx, enemy.rect.centery - self.player.rect.centery)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        if closest_enemy is None:
            return None
        dx = closest_enemy.rect.centerx - self.player.rect.centerx
        dy = closest_enemy.rect.centery - self.player.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return None
        direction = (dx / dist, dy / dist)
        self.last_shot_time = now
        return FireBall(self.player.rect.centerx, self.player.rect.centery, direction, self.damage)
