import pygame
from pytmx import load_pygame

def draw_tiled_map(screen, tmx_path):
    tmx_data = load_pygame(tmx_path)
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'tiles'):
            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (32, 32))
                screen.blit(image, (x * 32, y * 32))
