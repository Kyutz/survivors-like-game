import pygame

"""
Classe Player: Herda de pygame.sprite.Sprite. 
Inicializa o sprite como um quadrado verde (32x32). 
Define a posição inicial (400, 300) e a velocidade de movimento (5).
Adiciona um método update_movement para lidar com o input WASD.
"""
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(400, 300))
        self.speed = 5
        self.direction_vector = (1, 0)  # Direção inicial: direita

    def update_movement(self, keys, screen_rect):
        """
        Implementa a lógica para mover o jogador com as teclas WASD. 
        Atualiza self.rect.x e self.rect.y com base na velocidade.
        Garanta que o jogador não possa se mover para fora da área da tela (screen_rect).
        Atualiza direction_vector conforme a última tecla pressionada.
        """
        if keys[pygame.K_w] and self.rect.top > screen_rect.top:
            self.rect.y -= self.speed
            self.direction_vector = (0, -1)
        if keys[pygame.K_s] and self.rect.bottom < screen_rect.bottom:
            self.rect.y += self.speed
            self.direction_vector = (0, 1)
        if keys[pygame.K_a] and self.rect.left > screen_rect.left:
            self.rect.x -= self.speed
            self.direction_vector = (-1, 0)
        if keys[pygame.K_d] and self.rect.right < screen_rect.right:
            self.rect.x += self.speed
            self.direction_vector = (1, 0)
            