import pygame
import os
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
        self.tilemap_bg = None
        self.screen_width = 800
        self.screen_height = 600
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Survivor-Like")
        self.clock = pygame.time.Clock()
        self.running = True # Variável de controle do Game Loop
        tilemap_path = os.path.join('assets', 'sprites', 'Tilemap-flat.png')
        try:
            self.tilemap_bg = pygame.image.load(os.path.join('assets', 'sprites', 'Tilemap-flat.png')).convert()
        except Exception as e:
            print(f"Erro ao carregar tilemap: {e}")
            self.tilemap_bg = None

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
        # Disparo mais lento: cooldown aumentado para 2000ms (2 segundos)
        self.weapon = Weapon(self.player, cooldown=2000, damage=1)
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

        # Spawner de inimigos: sempre fora da tela
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.spawn_rate:
            self.enemy_spawn_timer = 0
            spawn_side = random.choice(['top', 'bottom', 'left', 'right'])
            enemy = Enemy()
            if spawn_side == 'top':
                enemy.rect.x = random.randint(0, self.screen_width - enemy.rect.width)
                enemy.rect.y = -enemy.rect.height
            elif spawn_side == 'bottom':
                enemy.rect.x = random.randint(0, self.screen_width - enemy.rect.width)
                enemy.rect.y = self.screen_height
            elif spawn_side == 'left':
                enemy.rect.x = -enemy.rect.width
                enemy.rect.y = random.randint(0, self.screen_height - enemy.rect.height)
            else: # right
                enemy.rect.x = self.screen_width
                enemy.rect.y = random.randint(0, self.screen_height - enemy.rect.height)
            self.enemies.add(enemy)

        # Atualiza todos os inimigos (eles se moverão em direção ao jogador)
        self.enemies.update(self.player.rect)

        # Colisão pixel-perfect entre inimigos e jogador
        collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, dokill=False, collided=pygame.sprite.collide_mask)
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

        # Colisão pixel-perfect entre projéteis e inimigos
        collisions = pygame.sprite.groupcollide(self.projectiles, self.enemies, True, False, collided=pygame.sprite.collide_mask)
        for proj, hit_enemies in collisions.items():
            for enemy in hit_enemies:
                # aplica dano via componente Health; se morrer, remove o inimigo
                dmg = getattr(proj, 'damage', 10)
                died = False
                if hasattr(enemy, 'health') and hasattr(enemy.health, 'take_damage'):
                    died = enemy.health.take_damage(dmg)
                else:
                    try:
                        enemy.health -= dmg
                        if enemy.health <= 0:
                            died = True
                    except Exception:
                        died = True
                if died:
                    enemy.kill()

    def draw(self):
        """
        Preenche a tela e desenha o fundo, jogador e inimigos.
        """
        if self.tilemap_bg:
            tile_w, tile_h = self.tilemap_bg.get_size()
            for x in range(0, self.screen_width, tile_w):
                for y in range(0, self.screen_height, tile_h):
                    self.screen.blit(self.tilemap_bg, (x, y))
        else:
            self.screen.fill((0, 0, 0)) # Fundo preto

        # ...existing code...
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