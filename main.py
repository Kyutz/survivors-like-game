import pygame
import sys
from src.game_manager import GameManager

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
    pygame.quit()
    sys.exit()