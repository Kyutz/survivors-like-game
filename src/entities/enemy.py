import pygame
import math
import random # Necessário para spawn aleatório
from src.entities.health import Health
from src.entities.experience_gem import ExperienceGem  # Importação local para evitar ciclo

"""
Classe Enemy: Herda de pygame.sprite.Sprite. 
Inicializa com sprite de quadrado vermelho (16x16), saúde de 1 e velocidade de 2.
Define o retângulo e a posição inicial.
"""
class Enemy(pygame.sprite.Sprite):
    def check_for_drops(self):
        """
        Sempre dropa XP, e 5% de chance de dropar HealingDrop junto.
        """
        from src.entities.healing_drop import HealingDrop
        drops = [self.drop_xp()]
        import random
        if random.random() < 0.05:
            drops.append(HealingDrop(self.rect.centerx, self.rect.centery, heal_amount=10))
        return drops

    def __init__(self, enemy_type='bat'):
        super().__init__()
        from src.ui.config import ENEMY_SPRITES
        self.enemy_type = enemy_type
        sprite_path = ENEMY_SPRITES.get(enemy_type, ENEMY_SPRITES['bat'])
        try:
            img = pygame.image.load(sprite_path).convert_alpha()
            self.original_image = pygame.transform.scale(img, (32, 32))
        except pygame.error as e:
            print(f"ERRO ao carregar {sprite_path}: {e}. Usando placeholder.")
            self.original_image = pygame.Surface((32, 32))
            self.original_image.fill((255, 0, 0))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Define uma posição inicial aleatória dentro de uma área de 800x600
        self.rect.x = random.randint(0, 800 - self.rect.width)
        self.rect.y = random.randint(0, 600 - self.rect.height)

        # Stats base por tipo
        if enemy_type == 'bat':
            self.health_base = 1
            self.xp_value = 1
        elif enemy_type == 'spider':
            self.health_base = 2
            self.xp_value = 2
        elif enemy_type == 'ghost':
            self.health_base = 5
            self.xp_value = 5
        elif enemy_type == 'cultist':
            self.health_base = 10
            self.xp_value = 10
        else:
            self.health_base = 1
            self.xp_value = 1
        self.health = Health(self.health_base)
        self.move_speed = 2
        self.facing_left = False

    def update(self, player_rect, all_enemies=None):
        """
        Move em direção ao player e resolve colisão com outros inimigos.
        """
        self.move_towards_player(player_rect)
        # Colisão entre inimigos (resolve empurrando para fora)
        if all_enemies is not None:
            for other in all_enemies:
                if other is not self and self.rect.colliderect(other.rect):
                    # Calcula vetor de separação
                    dx = self.rect.centerx - other.rect.centerx
                    dy = self.rect.centery - other.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist == 0:
                        dx, dy = 1, 0  # Evita divisão por zero
                        dist = 1
                    # Move cada inimigo metade da distância para fora
                    overlap = (self.rect.width // 2 + other.rect.width // 2) - dist
                    if overlap > 0:
                        move_x = (dx / dist) * (overlap / 2)
                        move_y = (dy / dist) * (overlap / 2)
                        self.rect.x += int(move_x)
                        self.rect.y += int(move_y)

    def move_towards_player(self, player_rect):
        """
        Move em direção ao player, mas não tenta atravessar se já está colidindo.
        """
        # Se já está colidindo com o player, não tenta mover para o centro dele
        if self.rect.colliderect(player_rect):
            return
        # Calcula o centro do inimigo e do jogador
        enemy_center = self.rect.center
        player_center = player_rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            return  # Evita divisão por zero
        dx /= distance
        dy /= distance
        self.rect.x += dx * self.move_speed
        self.rect.y += dy * self.move_speed
        # Flip apenas para cultist e ghost
        if self.enemy_type in ("cultist", "ghost"):
            if dx < 0:
                if not self.facing_left:
                    self.image = pygame.transform.flip(self.original_image, True, False)
                    self.facing_left = True
            elif dx > 0:
                if self.facing_left:
                    self.image = self.original_image.copy()
                    self.facing_left = False

    def drop_xp(self):
        """
        Cria e retorna uma instância de ExperienceGem na posição atual do inimigo.
        """
        return ExperienceGem(self.rect.centerx, self.rect.centery, value=self.xp_value)

    def take_damage(self, amount):
        morreu = self.health.take_damage(amount)
        if morreu or self.health.is_dead():
            self.kill()


