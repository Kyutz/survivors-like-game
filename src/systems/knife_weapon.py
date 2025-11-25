from src.entities.weapon import Weapon
from src.entities.projectile import Projectile
import os
import pygame

"""
Classe KnifeWeapon: Herda de Weapon.
Atira sempre na direção do vetor de movimento do player, ignorando inimigos.
"""
class KnifeWeapon(Weapon):
    def __init__(self, player, cooldown=900, damage=5, icon_path=None):
        if icon_path is None:
            icon_path = os.path.join('assets', 'sprites', 'Knife.png')
        super().__init__(player, cooldown, damage)
        self.icon_path = icon_path

    def fire_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        # Cooldown efetivo pode ser reduzido por passiva
        effective_cooldown = self.cooldown
        if hasattr(self.player, 'cooldown_multiplier'):
            effective_cooldown *= (1.0 + self.player.cooldown_multiplier) if self.player.cooldown_multiplier < 0 else self.player.cooldown_multiplier
        if current_time - self.last_shot_time > effective_cooldown:
            self.last_shot_time = current_time
            direction = self.player.direction_vector
            final_damage = self.damage * getattr(self.player, 'damage_multiplier', 1.0)
            # toca som via audio manager (safe no-op se não carregado)
            try:
                from src.systems.audio_manager import play as play_sound
                play_sound('knife')
            except Exception:
                pass
            return Projectile(
                self.player.rect.centerx, self.player.rect.centery, direction,
                damage=final_damage, sprite_path=self.icon_path)
        return None
