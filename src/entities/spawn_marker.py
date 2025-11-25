from pygame.sprite import Sprite
import pygame

"""
Classe SpawnMarker: Herda de Sprite. 
Representa o aviso visual 'X' antes que um inimigo apareça.
Pisca por um tempo e depois aciona o spawn do inimigo.
"""
class SpawnMarker(Sprite):
    def __init__(self, x, y, duration_ms=1000):
        super().__init__()
        try:
            img = pygame.image.load('assets/sprites/Spawn.png').convert_alpha()
            self.image = pygame.transform.scale(img, (32, 32))
        except Exception:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, 150)) # Placeholder
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.duration_ms = duration_ms
        self.should_spawn_enemy = False
        self.visible = True
        self.blink_interval = 150  # ms
        self.last_blink = self.spawn_time

    def update(self):
        now = pygame.time.get_ticks()
        # Pisca o X
        if now - self.last_blink > self.blink_interval:
            self.visible = not self.visible
            self.last_blink = now
        self.image.set_alpha(255 if self.visible else 0)
        # Checa se é hora de spawnar o inimigo
        if now - self.spawn_time > self.duration_ms:
            self.should_spawn_enemy = True
            self.kill()
