import pygame
import sys
from src.player import Player 

"""
Classe GameManager: Implementa o Game Loop principal, a tela e gerencia os objetos do jogo (Player, Inimigos).
"""
class GameManager:
    def __init__(self):
        """
        Configurações iniciais da tela, inicialização do Pygame e criação do jogador.
        """
        self.screen_width = 800
        self.screen_height = 600
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Survivor-Like")
        self.clock = pygame.time.Clock()
        self.running = True # Variável de controle do Game Loop

        """
        Inicializa a instância do jogador (self.player).
        """
        self.player = Player()

    def run(self):
        """
        Implementa o Game Loop principal.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        """
        Processa a fila de eventos do pygame (QUIT e ESC).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False # Encerra o loop (forma limpa)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def update(self):
        """
        Chama a lógica de atualização de todos os objetos do jogo.
        """
        keys = pygame.key.get_pressed()
        # Chama o movimento do Player, passando o retângulo da tela para checagem de limites.
        self.player.update_movement(keys, self.screen.get_rect())

    def draw(self):
        """
        Preenche a tela e desenha o jogador.
        """
        self.screen.fill((0, 0, 0)) # Fundo preto
        
        # Desenha o jogador (usa self.screen.blit com o rect e image do Player)
        self.screen.blit(self.player.image, self.player.rect)
        
        pygame.display.flip()

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
    # O loop termina quando self.running é False. sys.exit() é chamado no final.
    pygame.quit()
    sys.exit()