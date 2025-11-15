"""
Gerenciador de estados do jogo (menu, jogando, game over, etc).
"""

class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    GAME_OVER = 'game_over'
    PAUSED = 'paused'

    def __init__(self):
        self.state = GameState.MENU

    def set_state(self, new_state: str):
        self.state = new_state

    def is_menu(self):
        return self.state == GameState.MENU

    def is_playing(self):
        return self.state == GameState.PLAYING

    def is_game_over(self):
        return self.state == GameState.GAME_OVER

    def is_paused(self):
        return self.state == GameState.PAUSED
