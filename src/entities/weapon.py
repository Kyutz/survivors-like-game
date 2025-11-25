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
        # Tenta carregar som do tiro (não falha se não existir)
        try:
            from src.ui.config import ARROW_SOUND_PATH, SOUND_VOLUME
            # inicializa mixer se necessário (pygame.init geralmente já inicializa)
            try:
                pygame.mixer.get_init()
            except Exception:
                try:
                    pygame.mixer.init()
                except Exception:
                    pass
            try:
                self.shot_sound = pygame.mixer.Sound(ARROW_SOUND_PATH)
                self.shot_sound.set_volume(SOUND_VOLUME)
            except Exception:
                self.shot_sound = None
        except Exception:
            self.shot_sound = None

    def fire_attack(self, enemies):
        """
        Atira automaticamente no inimigo mais próximo.
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
                # toca som do tiro (se carregado)
                try:
                    if getattr(self, 'shot_sound', None):
                        self.shot_sound.play()
                except Exception:
                    pass
                return Projectile(
                    self.player.rect.centerx, self.player.rect.centery, direction,
                    damage=final_damage, sprite_path='assets/sprites/arrow01.png')
        return None

