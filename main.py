import pygame
import sys
from src.player import Player
from src.enemy import Enemy
from src.weapon import Weapon
from src.projectile import Projectile
from src.game_over import GameOver
import random

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

        # Variáveis do Spawner
        self.enemy_spawn_timer = 0
        self.spawn_rate = 60 # Spawn a cada 60 frames (1 segundo)
        
        # Grupo de Sprites para gerenciar todos os inimigos
        self.enemies = pygame.sprite.Group()

        """
        Inicializa a instância do jogador (self.player).
        """
        self.player = Player()
        # Inicializa arma do player (dano configurável).
        # Ajuste 'damage' para controlar quantos tiros são necessários para matar inimigos.
        # Por padrão aqui definimos 1 para permitir que inimigos com Health(3) precisem de 3 tiros.
        self.weapon = Weapon(self.player, damage=1)
        # Grupo de projéteis
        self.projectiles = pygame.sprite.Group()

    def reset(self):
        """Reinicia o estado do jogo para começar novamente."""
        self.enemies.empty()
        self.projectiles.empty()
        self.player = Player()
        self.weapon = Weapon(self.player, damage=1)
        self.enemy_spawn_timer = 0
        self.running = True

    def handle_player_death(self):
        """Abre a tela de Game Over e age conforme escolha do jogador."""
        go = GameOver(self.screen)
        action = go.run()
        if action == 'restart':
            self.reset()
        else:
            self.running = False

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

        # Spawner de inimigos
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.spawn_rate:
            self.enemy_spawn_timer = 0
            # Gera posição aleatória fora da tela (borda)
            spawn_side = random.choice(['top', 'bottom', 'left', 'right'])
            if spawn_side == 'top':
                x = random.randint(0, self.screen_width - 16)
                y = -16
            elif spawn_side == 'bottom':
                x = random.randint(0, self.screen_width - 16)
                y = self.screen_height
            elif spawn_side == 'left':
                x = -16
                y = random.randint(0, self.screen_height - 16)
            else: # right
                x = self.screen_width
                y = random.randint(0, self.screen_height - 16)
            enemy = Enemy()
            enemy.rect.x = x
            enemy.rect.y = y
            self.enemies.add(enemy)

        # Atualiza todos os inimigos (eles se moverão em direção ao jogador)
        self.enemies.update(self.player.rect)

        # Checa colisões entre inimigos e o jogador. Se colidir, aplica dano e remove o inimigo.
        collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, dokill=True)
        for e in collided_enemies:
            died = self.player.health.take_damage(10)
            if died:
                # chama tela de Game Over e age conforme escolha do jogador
                self.handle_player_death()
                break

        # Ataque automático do player: Weapon faz toda a lógica de mira
        projectile = self.weapon.fire_attack(self.enemies)
        if projectile:
            self.projectiles.add(projectile)

        # Atualiza projéteis
        self.projectiles.update()

        # Checa colisões entre projéteis e inimigos: projétil some, inimigo recebe dano
        collisions = pygame.sprite.groupcollide(self.projectiles, self.enemies, True, False)
        for proj, hit_enemies in collisions.items():
            for enemy in hit_enemies:
                # aplica dano via componente Health; se morrer, remove o inimigo
                # proj pode ser um Sprite; usamos getattr para fallback
                dmg = getattr(proj, 'damage', 10)
                died = False
                # se o enemy tiver atributo health e método take_damage
                if hasattr(enemy, 'health') and hasattr(enemy.health, 'take_damage'):
                    died = enemy.health.take_damage(dmg)
                else:
                    # compatibilidade: se health for um int, subtrai normalmente
                    try:
                        enemy.health -= dmg
                        if enemy.health <= 0:
                            died = True
                    except Exception:
                        # não sabemos aplicar dano; apenas mata o inimigo por segurança
                        died = True

                if died:
                    enemy.kill()

    def draw(self):
        """
        Preenche a tela e desenha o jogador e os inimigos.
        """
        self.screen.fill((0, 0, 0)) # Fundo preto
        self.screen.blit(self.player.image, self.player.rect)
        # Desenha a barra de vida do jogador logo abaixo do sprite
        self.player.draw_health(self.screen)
        # Desenha todos os inimigos
        self.enemies.draw(self.screen)
        # Desenha projéteis
        self.projectiles.draw(self.screen)
        pygame.display.flip()

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
    # O loop termina quando self.running é False. sys.exit() é chamado no final.
    pygame.quit()
    sys.exit()