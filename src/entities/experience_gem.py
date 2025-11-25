import pygame

"""
Classe ExperienceGem: Herda de pygame.sprite.Sprite.
Representa o XP dropado por inimigos. Usa um pequeno quadrado amarelo para o sprite.
Define um valor de XP (xp_value) e gerencia a coleta.
"""
class ExperienceGem(pygame.sprite.Sprite):
    def __init__(self, x, y, value=1):
        super().__init__()
        try:
            img = pygame.image.load('assets/sprites/Gem.png').convert_alpha()
            self.image = pygame.transform.scale(img, (16, 16))
        except pygame.error as e:
            print(f"Erro ao carregar Gem.png: {e}")
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 255, 0)) # fallback amarelo
        self.rect = self.image.get_rect(center=(x, y))
        self.xp_value = value
        self.magnet_radius = 48  # distância para ativar magnetismo (reduzido)
        self.magnet_speed = 3    # velocidade normal
        self.magnetized_speed = 12  # velocidade quando magnetizado
        self.target_player = None
        self.magnetized = False  # Se já foi ativada a atração
    
    def set_player(self, player):
        """Define o player alvo para magnetismo."""
        self.target_player = player
    
    def update(self):
        # Magnetismo: só ativa se o player estiver no raio, depois segue sempre
        if self.target_player:
            player_rect = self.target_player.rect
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if not self.magnetized and dist < self.magnet_radius:
                self.magnetized = True
            speed = self.magnetized_speed if self.magnetized else self.magnet_speed
            if (self.magnetized or dist < self.magnet_radius) and dist > 0:
                dx /= dist
                dy /= dist
                self.rect.x += int(dx * speed)
                self.rect.y += int(dy * speed)
        # A gema só desaparece ao colidir com o sprite do jogador (handled by groupcollide in GameManager)