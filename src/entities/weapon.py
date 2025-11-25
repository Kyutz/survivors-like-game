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
        # base_damage é a referência que pode ser aumentada por upgrades
        self.base_damage = damage
        self.damage = damage
        self.last_shot_time = 0 # Tempo do último ataque realizado
        # quantas flechas extras foram compradas (0..3)
        # estágio 1: flecha oposta
        # estágio 2: oposta + acima
        # estágio 3: oposta + acima + abaixo
        self.extra_arrows = 0

    # --- Métodos de upgrade ---
    def change_base_damage(self, delta: int):
        """Aumenta/reduz o dano base permanentemente e atualiza damage atual."""
        try:
            self.base_damage += int(delta)
        except Exception:
            return
        if self.base_damage < 0:
            self.base_damage = 0
        self.damage = self.base_damage

    def set_base_damage(self, value: int):
        try:
            self.base_damage = int(value)
        except Exception:
            return
        if self.base_damage < 0:
            self.base_damage = 0
        self.damage = self.base_damage

    def reduce_cooldown(self, delta_ms: int):
        """Reduz o cooldown da arma (min cap para evitar zero/negativo)."""
        try:
            self.cooldown = max(50, self.cooldown - int(delta_ms))
        except Exception:
            pass

    def add_extra_arrow(self):
        """Adiciona uma flecha extra até o máximo de 3 estágios.

        Retorna True se adicionou, False se já estava no máximo.
        """
        try:
            if self.extra_arrows < 3:
                self.extra_arrows += 1
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def _rotate_vector(vec, angle_deg):
        """Roda um vetor 2D (x,y) por angle_deg graus e retorna novo vetor normalizado."""
        import math
        x, y = vec
        rad = math.radians(angle_deg)
        cos = math.cos(rad)
        sin = math.sin(rad)
        rx = x * cos - y * sin
        ry = x * sin + y * cos
        # normaliza
        mag = (rx * rx + ry * ry) ** 0.5
        if mag == 0:
            return (1, 0)
        return (rx / mag, ry / mag)

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
                # Cria projétil principal
                projectiles = []
                projectiles.append(Projectile(self.player.rect.centerx, self.player.rect.centery, direction, damage=self.damage))
                # Adiciona flechas extras conforme estágio
                # estágio 1: oposto (180)
                # estágio 2: oposto + acima (+90)
                # estágio 3: oposto + acima + abaixo (-90)
                if self.extra_arrows >= 1:
                    opp = self._rotate_vector(direction, 180)
                    projectiles.append(Projectile(self.player.rect.centerx, self.player.rect.centery, opp, damage=self.damage))
                if self.extra_arrows >= 2:
                    up = self._rotate_vector(direction, 90)
                    projectiles.append(Projectile(self.player.rect.centerx, self.player.rect.centery, up, damage=self.damage))
                if self.extra_arrows >= 3:
                    down = self._rotate_vector(direction, -90)
                    projectiles.append(Projectile(self.player.rect.centerx, self.player.rect.centery, down, damage=self.damage))
                return projectiles
        return None

