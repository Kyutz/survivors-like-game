import pygame
import math
from src.entities.orb_projectile import OrbProjectile

"""
Classe StoneOrbWeapon: cria e gerencia um OrbProjectile girando ao redor do player.
Não possui cooldown, o orbe é persistente enquanto a arma existir.
"""

class StoneOrbWeapon:
    icon_path = 'assets/sprites/Stone.png'

    def _can_hit(self, orb, enemy, cooldown_ms=500):
        now = pygame.time.get_ticks()
        if not hasattr(orb, '_last_hit_times'):
            orb._last_hit_times = {}
        last = orb._last_hit_times.get(enemy, 0)
        if now - last >= cooldown_ms:
            orb._last_hit_times[enemy] = now
            return True
        return False

    def __init__(self, player, radius=50, speed=0.012, damage=3):
        self.player = player
        self.radius = radius
        self.speed = speed
        self.damage = damage
        self.orb_group = pygame.sprite.Group()
        self._last_amount = None
        self._init_orbs()

    def _init_orbs(self):
        self.orb_group.empty()
        self.orb1 = OrbProjectile(self.player, radius=self.radius, speed=self.speed, damage=self.damage)
        self.orb_group.add(self.orb1)
        amount = int(getattr(self.player, 'amount_multiplier', 0))
        if amount > 0:
            self.orb2 = OrbProjectile(self.player, radius=self.radius, speed=self.speed, damage=self.damage)
            self.orb2.angle = math.pi  # 180 graus oposto
            self.orb_group.add(self.orb2)
        self._last_amount = amount

    def update_orbs(self):
        # Chame este método sempre que amount_multiplier do player mudar
        amount = int(getattr(self.player, 'amount_multiplier', 0))
        if amount != self._last_amount:
            self._init_orbs()

    def fire_attack(self, enemies):
        # Atualiza orbs se amount_multiplier mudou
        self.update_orbs()
        # O orbe é persistente, não dispara projéteis
        self.orb_group.update()
        # Colisão: se o orbe colidir com algum inimigo, remove imediatamente
        from src.entities.damage_text import DamageText
        for orb in self.orb_group:
            collided = pygame.sprite.spritecollide(orb, enemies, False, pygame.sprite.collide_mask)
            final_damage = orb.damage
            if hasattr(self.player, 'damage_multiplier'):
                final_damage = int(final_damage * self.player.damage_multiplier)
            for enemy in collided:
                if not self._can_hit(orb, enemy):
                    continue
                # Usa o sistema de vida do inimigo
                if hasattr(enemy, 'take_damage'):
                    took_damage = enemy.take_damage(final_damage)
                    if took_damage and hasattr(self.player, 'game_manager') and self.player.game_manager:
                        # Stone Orb does not currently support crits, but for future-proofing:
                        self.player.game_manager.damage_texts.append(DamageText(final_damage, enemy.rect.center, is_crit=False))
                else:
                    enemy.kill()
        return None

    def draw(self, surface):
        self.orb_group.draw(surface)
