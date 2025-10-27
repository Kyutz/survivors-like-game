import pygame
import math
import random # Necessário para spawn aleatório

"""
Classe Enemy: Herda de pygame.sprite.Sprite. 
Inicializa com sprite de quadrado vermelho (16x16), saúde de 1 e velocidade de 2.
Define o retângulo e a posição inicial.
"""
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

        # Define uma posição inicial aleatória dentro de uma área de 800x600
        self.rect.x = random.randint(0, 800 - self.rect.width)
        self.rect.y = random.randint(0, 600 - self.rect.height)

        self.health = 1
        self.move_speed = 2

    def update(self, player_rect):
        """
        Chama o método de movimento, usando a posição do jogador como alvo.
        """
        self.move_towards_player(player_rect)

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
  

