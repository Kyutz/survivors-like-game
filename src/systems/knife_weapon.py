from src.entities.weapon import Weapon
from src.entities.projectile import Projectile
import os
import pygame

"""
Classe KnifeWeapon: Herda de Weapon.
Atira sempre na direção do vetor de movimento do player, ignorando inimigos.
"""
class KnifeWeapon(Weapon):
    def __init__(self, player, cooldown=500, damage=8, icon_path=None):
        # Aumenta o cooldown para 500ms (menos ataques por segundo)
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
        # Só dispara se cooldown passou
        if current_time - self.last_shot_time > effective_cooldown:
            self.last_shot_time = current_time
            direction = self.player.direction_vector
            final_damage, critico = self.calcular_dano_efetivo()
            amount = 1 + int(getattr(self.player, 'amount_multiplier', 0))
            spread_angle = 25
            projectiles = []
            # Garante que só dispara um conjunto de projéteis por cooldown
            for i in range(amount):
                if amount == 1:
                    angle_offset = 0
                else:
                    angle_offset = (i - (amount-1)/2) * spread_angle
                vec = pygame.math.Vector2(direction).rotate(angle_offset)
                # toca som apenas uma vez por disparo
                if i == 0:
                    try:
                        from src.systems.audio_manager import play as play_sound
                        play_sound('knife')
                    except Exception:
                        pass
                proj = Projectile(
                    self.player.rect.centerx, self.player.rect.centery, vec,
                    damage=final_damage, sprite_path=self.icon_path)
                proj.is_crit = critico
                projectiles.append(proj)
            if len(projectiles) == 1:
                return projectiles[0]
            return projectiles
        return None
