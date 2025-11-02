import pygame

"""
Classe Projectile: Herda de pygame.sprite.Sprite. 
Define um projétil simples (ex: quadrado branco 8x8) que se move em linha reta.
Inicializa com a posição inicial e uma velocidade de 7.
"""
class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, direction_vector, damage: int = 10):
        super().__init__()
        try:
            arrow_img = pygame.image.load('assets/sprites/arrow01.png').convert_alpha()
            # Calcula o ângulo em graus para rotacionar a flecha
            dx, dy = direction_vector
            # Se a flecha original aponta para cima, ajuste +90 graus
            angle = pygame.math.Vector2(dx, dy).angle_to((0, -1)) + 90
            self.image = pygame.transform.rotate(arrow_img, angle)
        except pygame.error as e:
            print(f"ERRO ao carregar arrow01.png: {e}. Usando placeholder.")
            self.image = pygame.Surface((8, 8))
            self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.velocity = 7
        self.direction_vector = direction_vector
        self.damage = damage
        self.screen = pygame.display.get_surface()

    def update(self):
        """
        Atualiza a posição do projétil (self.rect) com base no direction_vector e self.velocity.
        Remove o projétil do jogo se ele sair da área de 800x600.
        """
        self.rect.x += self.direction_vector[0] * self.velocity
        self.rect.y += self.direction_vector[1] * self.velocity

        # Remove o projétil se sair da tela
        if not self.screen.get_rect().colliderect(self.rect):
            self.kill()

 