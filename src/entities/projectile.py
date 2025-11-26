import pygame

"""
Classe Projectile: Herda de pygame.sprite.Sprite. 
Define um projétil simples (ex: quadrado branco 8x8) que se move em linha reta.
Inicializa com a posição inicial e uma velocidade de 7.
"""
class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, direction_vector, damage: int = 10, sprite_path=None):
        super().__init__()
        if sprite_path is None:
            sprite_path = 'assets/sprites/arrow01.png'
        try:
            proj_img = pygame.image.load(sprite_path).convert_alpha()
            # Redimensiona Knife.png para 16x16, Arrow01.png mantém tamanho original
            if 'knife' in sprite_path.lower():
                proj_img = pygame.transform.scale(proj_img, (16, 16))
            dx, dy = direction_vector
            # Ajusta rotação conforme sprite
            if 'arrow' in sprite_path.lower():
                angle = pygame.math.Vector2(dx, dy).angle_to((0, -1)) + 90
            elif 'knife' in sprite_path.lower():
                angle = pygame.math.Vector2(dx, dy).angle_to((0, -1)) + 50
            else:
                angle = pygame.math.Vector2(dx, dy).angle_to((0, -1))
            self.image = pygame.transform.rotate(proj_img, angle)
        except pygame.error as e:
            print(f"ERRO ao carregar {sprite_path}: {e}. Usando placeholder.")
            self.image = pygame.Surface((8, 8))
            self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(start_x, start_y))
        # Velocidade customizada para faca
        if 'knife' in (sprite_path or '').lower():
            self.velocity = 18  # Muito rápido para sair logo da tela
        else:
            self.velocity = 7
        # Normaliza o vetor de direção para garantir diagonais corretas
        vec = pygame.math.Vector2(direction_vector)
        if vec.length() != 0:
            vec = vec.normalize()
        self.direction_vector = (vec.x, vec.y)
        self.direction_vector = direction_vector
        self.damage = damage
        self.screen = pygame.display.get_surface()
        # Tocar som do projétil se for uma flecha (garante som mesmo se Weapon não tocar)
        try:
            if 'arrow' in (sprite_path or '').lower():
                from src.systems.audio_manager import play as play_sound
                play_sound('arrow')
        except Exception:
            pass

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

 