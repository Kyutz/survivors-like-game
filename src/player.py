import pygame
from src.health import Health

"""
Classe Player: Herda de pygame.sprite.Sprite. 
Inicializa o sprite como um quadrado verde (32x32). 
Define a posição inicial (400, 300) e a velocidade de movimento (5).
Adiciona um método update_movement para lidar com o input WASD.
"""
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Carrega o spritesheet completo com tratamento de erro
        try:
            img = pygame.image.load('assets/sprites/Soldier-Idle.png').convert_alpha()
            self.image = pygame.transform.scale(img, (192, 192))
        except pygame.error as e:
            print(f"FALHA NO CARREGAMENTO. {e}")
            self.image = pygame.Surface((192, 192))
            self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(400, 300))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 5
        self.direction_vector = (1, 0)  # Direção inicial: direita
        # Componente de vida reutilizável
        self.health = Health(100)

    def update_movement(self, keys, screen_rect):
        """
        Implementa a lógica para mover o jogador com as teclas WASD. 
        Atualiza self.rect.x e self.rect.y com base na velocidade.
        Garanta que o jogador não possa se mover para fora da área da tela (screen_rect).
        Atualiza direction_vector conforme a última tecla pressionada.
        """
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.direction_vector = (0, -1)
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.direction_vector = (0, 1)
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction_vector = (-1, 0)
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction_vector = (1, 0)
        # Corrige limites para encostar a arte visível nas bordas
        mask_bbox = self.mask.get_bounding_rects()[0] if hasattr(self.mask, 'get_bounding_rects') else self.mask.get_bounding_rect()
        # mask_bbox é relativo ao topo esquerdo do self.rect
        # Ajusta borda esquerda
        if self.rect.left + mask_bbox.left < screen_rect.left:
            self.rect.left = screen_rect.left - mask_bbox.left
        # Ajusta borda direita
        if self.rect.left + mask_bbox.right > screen_rect.right:
            self.rect.left = screen_rect.right - mask_bbox.right
        # Ajusta borda superior
        if self.rect.top + mask_bbox.top < screen_rect.top:
            self.rect.top = screen_rect.top - mask_bbox.top
        # Ajusta borda inferior
        if self.rect.top + mask_bbox.bottom > screen_rect.bottom:
            self.rect.top = screen_rect.bottom - mask_bbox.bottom

    def draw_health(self, surface: pygame.Surface):
        """Desenha apenas a barra de vida (delegada ao componente Health)."""
        bar_width = 32  # Tamanho original
        bar_height = 6  # Tamanho original
        y_offset = -75  # Mais acima do sprite
        x_offset = -2  # Move um pouco para a esquerda
        self.health.draw(surface, self.rect.move(x_offset, 0), bar_width=bar_width, bar_height=bar_height, y_offset=y_offset)
            