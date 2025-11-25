import pygame

class HealingDrop(pygame.sprite.Sprite):
    def __init__(self, x, y, heal_amount=10):
        super().__init__()
        try:
            img = pygame.image.load('assets/sprites/Heal.png').convert_alpha()
            self.image = pygame.transform.scale(img, (16, 16))
        except pygame.error as e:
            print(f"Erro ao carregar Heal.png: {e}")
            self.image = pygame.Surface((12, 12))
            self.image.fill((100, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.heal_amount = heal_amount
        self.magnet_radius = 48
        self.magnet_speed = 3
        self.magnetized_speed = 12
        self.target_player = None
        self.magnetized = False

    def set_player(self, player):
        self.target_player = player

    def update(self):
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
