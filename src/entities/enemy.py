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
    def __init__(self, enemy_type='bat'):
        super().__init__()
        from src.ui.config import ENEMY_SPRITES
        sprite_path = ENEMY_SPRITES.get(enemy_type, ENEMY_SPRITES['bat'])
        try:
            img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.scale(img, (32, 32))
        except pygame.error as e:
            print(f"ERRO ao carregar {sprite_path}: {e}. Usando placeholder.")
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Define uma posição inicial aleatória dentro de uma área de 800x600
        self.rect.x = random.randint(0, 800 - self.rect.width)
        self.rect.y = random.randint(0, 600 - self.rect.height)

        # componente de vida reutilizável (inimigos pequenos com 1 de vida)
        self.health = Health(1)
        self.move_speed = 2

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
        Calcula o vetor (dx, dy) e o ângulo para mover o inimigo em direção ao centro do player.
        Usa trigonometria (math.sin, math.cos) para garantir movimento constante na direção do jogador.
        Atualiza self.rect.x e self.rect.y com base na self.move_speed.
        """
        # Calcula o centro do inimigo e do jogador
        enemy_center = self.rect.center
        player_center = player_rect.center

        # Calcula a diferença nas coordenadas
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]

        # Calcula a distância entre inimigo e jogador
        distance = math.hypot(dx, dy)
        if distance == 0:
            return  # Evita divisão por zero

        # Normaliza o vetor (dx, dy) e multiplica pela velocidade de movimento
        dx /= distance
        dy /= distance

        # Atualiza a posição do inimigo
        self.rect.x += dx * self.move_speed
        self.rect.y += dy * self.move_speed

    def drop_xp(self):
        """
        Cria e retorna uma instância de ExperienceGem na posição atual do inimigo.
        """
        return ExperienceGem(self.rect.centerx, self.rect.centery, value=1)


