import pygame
from pytmx import load_pygame

def get_blocked_tiles(tmx_path):
    """
    Retorna uma lista de retângulos (pygame.Rect) para todos os tiles bloqueados (paredes) do mapa Tiled.
    Considera que a camada de blocos é a primeira layer visível e que todos os tiles não nulos são paredes.
    """
    tmx_data = load_pygame(tmx_path)
    blocked_rects = []
    tile_size = 32  # O jogo está usando tiles de 32x32
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'tiles'):
            width = tmx_data.width
            height = tmx_data.height
            for x, y, image in layer.tiles():
                # Paredes: duas primeiras linhas, última linha, primeira/última coluna
                if y in (0, 1, height-1) or x in (0, width-1):
                    blocked_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))
            break  # Só considera a primeira camada de blocos
    return blocked_rects
