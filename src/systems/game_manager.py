import pygame
import os
import sys
import random
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.weapon import Weapon
from src.entities.projectile import Projectile
from src.ui.game_over import GameOver
from src.ui.config import SCREEN_WIDTH, SCREEN_HEIGHT, SPAWN_RATE, WEAPON_COOLDOWN, WEAPON_DAMAGE
from src.ui.assets import get_tilemap_image

class GameManager:
    STATE_PLAYING = 0
    STATE_LEVEL_UP = 1

    def __init__(self):
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Survivor-Like")
        self.tilemap_bg = get_tilemap_image()
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = self.STATE_PLAYING
        self.enemy_spawn_timer = 0
        self.spawn_rate = SPAWN_RATE
        self.enemies = pygame.sprite.Group()
        self.player = Player()
        self.player.xp = 0
        self.player.level = 1
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.projectiles = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()

    def reset(self):
        self.enemies.empty()
        self.projectiles.empty()
        self.player = Player()
        self.player.xp = 0
        self.player.level = 1
        self.weapon = Weapon(self.player, damage=WEAPON_DAMAGE)
        self.enemy_spawn_timer = 0
        self.running = True

    def handle_player_death(self):
        go = GameOver(self.screen)
        action = go.run()
        if action == 'restart':
            self.reset()
        else:
            self.running = False

    def run(self):
        while self.running:
            self.handle_events()
            if self.state == self.STATE_PLAYING:
                self.update()
                self.draw()
            elif self.state == self.STATE_LEVEL_UP:
                self.draw()
                self.show_level_up_menu()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update_movement(keys, self.screen.get_rect())
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
            else:
                enemy.rect.x = self.screen_width
                enemy.rect.y = random.randint(0, self.screen_height - enemy.rect.height)
            self.enemies.add(enemy)
        self.enemies.update(self.player.rect)
        collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, dokill=False, collided=pygame.sprite.collide_mask)
        for e in collided_enemies:
            died = self.player.health.take_damage(10)
            if died:
                self.handle_player_death()
                break
        projectile = self.weapon.fire_attack(self.enemies)
        if projectile:
            self.projectiles.add(projectile)
        self.projectiles.update()
        self.gems.update()  # Atualiza todas as gemas para magnetismo
        # --- Colisão Projétil-Inimigo (precisão com mask) ---
        hits = pygame.sprite.groupcollide(
            self.projectiles, self.enemies, True, True,
            collided=pygame.sprite.collide_mask
        )
        for projectile, enemies_hit in hits.items():
            for enemy in enemies_hit:
                if hasattr(enemy, 'drop_xp'):
                    new_gem = enemy.drop_xp()
                    if hasattr(new_gem, 'set_player'):
                        new_gem.set_player(self.player)
                    self.gems.add(new_gem)
        # --- Colisão Jogador-Gema ---
        collected_gems = pygame.sprite.spritecollide(self.player, self.gems, dokill=True, collided=pygame.sprite.collide_mask)
        for gem in collected_gems:
            self.player.gain_xp(getattr(gem, 'xp_value', 1))
            # gem.kill() já chamado por dokill=True
        # Se o jogador pode subir de nível, pausa o jogo para menu de level-up
        if self.player.can_level_up:
            self.state = self.STATE_LEVEL_UP
    def show_level_up_menu(self):
        # Exibe um menu simples de level-up com 3 opções placeholder
        font = pygame.font.SysFont(None, 48)
        options = ["Opção 1: Placeholder", "Opção 2: Placeholder", "Opção 3: Placeholder"]
        selected = 0
        waiting = True
        # Captura o frame do jogo antes do menu
        self.draw()
        bg_frame = self.screen.copy()
        # Calcula dimensões da caixa para caber o texto
        font_height = font.get_height()
        title_text = "Level Up! Escolha uma melhoria:"
        title_width = font.size(title_text)[0]
        options_width = max(font.size(opt)[0] for opt in options)
        box_width = max(420, title_width + 40, options_width + 40)
        box_height = 40 + font_height + 30 + len(options) * (font_height + 20)
        overlay = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        overlay.fill((30, 30, 30, 220))
        overlay_x = self.screen_width//2 - box_width//2
        overlay_y = self.screen_height//2 - box_height//2
        while waiting:
            self.screen.blit(bg_frame, (0, 0))
            self.screen.blit(overlay, (overlay_x, overlay_y))
            # Título
            title = font.render(title_text, True, (255, 255, 0))
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, overlay_y + 20))
            # Opções
            for i, opt in enumerate(options):
                color = (255, 255, 255) if i == selected else (180, 180, 180)
                opt_surf = font.render(opt, True, color)
                opt_x = self.screen_width//2 - opt_surf.get_width()//2
                opt_y = overlay_y + 80 + i * (font_height + 20)
                self.screen.blit(opt_surf, (opt_x, opt_y))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        waiting = False
        # Após escolha, reseta flag e volta ao jogo
        self.player.can_level_up = False
        self.state = self.STATE_PLAYING

    def draw(self):
        if self.tilemap_bg:
            tile_w, tile_h = self.tilemap_bg.get_size()
            for x in range(0, self.screen_width, tile_w):
                for y in range(0, self.screen_height, tile_h):
                    self.screen.blit(self.tilemap_bg, (x, y))
        else:
            self.screen.fill((0, 0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        self.player.draw_health(self.screen)
        # --- Barra de XP ---
        xp = self.player.xp
        xp_max = self.player.xp_to_next_level
        bar_width = self.screen_width - 40
        bar_height = 18
        bar_x = 20
        bar_y = 20
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))  # Fundo
        fill_width = int(bar_width * (xp / xp_max)) if xp_max > 0 else 0
        pygame.draw.rect(self.screen, (255, 215, 0), (bar_x, bar_y, fill_width, bar_height))  # Progresso
        # Texto
        font = pygame.font.SysFont(None, 28)
        xp_text = font.render(f"XP: {xp} / {xp_max}", True, (0, 0, 0))
        self.screen.blit(xp_text, (bar_x + bar_width//2 - xp_text.get_width()//2, bar_y + 1))
        self.enemies.draw(self.screen)
        self.gems.draw(self.screen)  # Adiciona desenho das gemas de XP
        self.projectiles.draw(self.screen)
        pygame.display.flip()
