import pygame
from src.ui.config import PLAYER_SPRITE_PATH, ENEMY_SPRITE_PATH, ARROW_SPRITE_PATH, TILEMAP_PATH

def load_image(path, size=None):
    try:
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        # Só chama convert_alpha se display estiver inicializado
        if pygame.display.get_init():
            img = img.convert_alpha()
        return img
    except pygame.error as e:
        print(f"Erro ao carregar {path}: {e}")
        surf = pygame.Surface((size or (32, 32)))
        if pygame.display.get_init():
            surf = surf.convert_alpha()
        return surf

def get_player_image():
    return load_image(PLAYER_SPRITE_PATH, (192, 192))

def get_enemy_image():
    return load_image(ENEMY_SPRITE_PATH, (192, 192))

def get_arrow_image():
    return load_image(ARROW_SPRITE_PATH, (8, 8))

def get_tilemap_image():
    return load_image(TILEMAP_PATH)
