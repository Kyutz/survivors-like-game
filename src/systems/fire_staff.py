
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
        # Toca som da bola de fogo
        try:
            from src.systems.audio_manager import play as play_sound
            play_sound('fireball')
        except Exception:
            pass
        # --- Lógica de amount_multiplier (projéteis extras) ---
        amount = 1 + int(getattr(self.player, 'amount_multiplier', 0))
        spread_angle = 25
        projectiles = []
        for i in range(amount):
            if amount == 1:
                angle_offset = 0
            else:
                angle_offset = (i - (amount-1)/2) * spread_angle
            vec = pygame.math.Vector2(direction).rotate(angle_offset)
            projectiles.append(FireBall(self.player.rect.centerx, self.player.rect.centery, vec, self.damage))
        if len(projectiles) == 1:
            return projectiles[0]
        return projectiles
