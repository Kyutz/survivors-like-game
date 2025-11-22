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
        # --- Lógica de Dificuldade Dinâmica ---
        self.base_spawn_rate = 60 # Valor inicial (1 inimigo por segundo)
        self.spawn_rate = self.base_spawn_rate
        self.difficulty_level = 1
        self.difficulty_increase_interval = 60000 # 60 segundos
        self.last_difficulty_increase_time = pygame.time.get_ticks()
        # --- Lógica de Tempo e Carência ---
        self.game_start_time = pygame.time.get_ticks()
        self.grace_period_ms = 0  # Sem carência, inimigos spawnam desde o início
        self.enemies = pygame.sprite.Group()
        self.player = Player()
        self.player.xp = 0
        self.player.level = 1
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.projectiles = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        from src.entities.healing_drop import HealingDrop
        self.healing_drops = pygame.sprite.Group()
        # --- Lógica de Tempo ---
        self.start_time = pygame.time.get_ticks() # Tempo em ms quando o jogo começa
        self.font = pygame.font.Font(None, 36) # Fonte padrão do Pygame (tamanho 36)
        self.time_at_pause = 0
        self.game_state = "PLAYING"
        self.score = 0  # Inicializa a pontuação

    def reset(self):
        self.enemies.empty()
        self.projectiles.empty()
        self.gems.empty()
        self.healing_drops.empty()
        self.player = Player()
        self.player.xp = 0
        self.player.level = 1
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.enemy_spawn_timer = 0
        self.base_spawn_rate = 60
        self.spawn_rate = self.base_spawn_rate
        self.difficulty_level = 1
        self.difficulty_increase_interval = 60000
        self.last_difficulty_increase_time = pygame.time.get_ticks()
        self.game_start_time = pygame.time.get_ticks()
        self.grace_period_ms = 0
        self.start_time = pygame.time.get_ticks()
        self.state = self.STATE_PLAYING
        self.time_at_pause = 0
        self.game_state = "PLAYING"
        self.score = 0

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
        # ...existing code...
        keys = pygame.key.get_pressed()
        # Importa utilitário de colisão
        from src.systems.map_collision import get_blocked_tiles
        blocked_rects = get_blocked_tiles('assets/maps/main_level.tmx')
        self.player.update_movement(keys, self.screen.get_rect(), blocked_rects)

        current_time = pygame.time.get_ticks()
        # ...existing code...
        # --- Checagem de Dificuldade Dinâmica ---
        if current_time - self.last_difficulty_increase_time > self.difficulty_increase_interval:
            # ...existing code...
            self.last_difficulty_increase_time = current_time
            self.difficulty_level += 1
            if self.spawn_rate > 15:
                self.spawn_rate *= 0.95
            # ...existing code...

        # --- Spawner de Inimigos com Grace Period ---
        if current_time >= self.game_start_time + self.grace_period_ms:
            # ...existing code...
            self.enemy_spawn_timer += 1
            # ...existing code...
            if self.enemy_spawn_timer >= self.spawn_rate:
                # ...existing code...
                self.enemy_spawn_timer = 0
                spawn_side = random.choice(['top', 'bottom', 'left', 'right'])
                # Escolhe tipo de inimigo conforme tempo/dificuldade
                enemy_type = 'bat'
                if self.difficulty_level >= 2:
                    enemy_type = random.choice(['spider', 'bat'])
                if self.difficulty_level >= 3:
                    enemy_type = random.choice(['spider', 'bat', 'ghost'])
                if self.difficulty_level >= 4:
                    enemy_type = random.choice(['spider', 'bat', 'ghost', 'cultist'])
                enemy = Enemy(enemy_type)
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
        # Atualiza projéteis, destruindo se colidir com parede
        for projectile in self.projectiles:
            projectile.update(blocked_rects)
            self.gems.update()  # Atualiza todas as gemas para magnetismo
            self.healing_drops.update()  # Atualiza drops de cura para magnetismo
        # --- Colisão Projétil-Inimigo (precisão com mask) ---
        # Só permite dano se o inimigo não estiver colidindo com parede
        valid_enemies = [enemy for enemy in self.enemies if not any(enemy.rect.colliderect(wall) for wall in blocked_rects)]
        from pygame.sprite import Group
        valid_enemies_group = Group(valid_enemies)
        hits = pygame.sprite.groupcollide(
            self.projectiles, valid_enemies_group, True, True,
            collided=pygame.sprite.collide_mask
        )
        for projectile, enemies_hit in hits.items():
            for enemy in enemies_hit:
                self.score += 1  # 1 ponto por inimigo eliminado
                # Drops: XP e cura
                if hasattr(enemy, 'check_for_drops'):
                    for drop in enemy.check_for_drops():
                        from src.entities.healing_drop import HealingDrop
                        if isinstance(drop, HealingDrop):
                            drop.set_player(self.player)  # Set player for HealingDrop
                            self.healing_drops.add(drop)
                        else:
                            if hasattr(drop, 'set_player'):
                                drop.set_player(self.player)
                            self.gems.add(drop)
        # --- Colisão Jogador-Gema ---
        collected_gems = pygame.sprite.spritecollide(self.player, self.gems, dokill=True, collided=pygame.sprite.collide_mask)
        for gem in collected_gems:
            self.player.gain_xp(getattr(gem, 'xp_value', 1))
            # gem.kill() já chamado por dokill=True
        # --- Colisão Jogador-HealingDrop ---
        collected_heals = pygame.sprite.spritecollide(self.player, self.healing_drops, dokill=True, collided=pygame.sprite.collide_mask)
        for heal in collected_heals:
            self.player.health.heal(heal.heal_amount)
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
        from src.ui.draw_tiled_map import draw_tiled_map
        draw_tiled_map(self.screen, 'assets/maps/main_level.tmx')
        self.screen.blit(self.player.image, self.player.rect)
        self.player.draw_health(self.screen)
        # --- Desenhar drops de cura ---
        self.healing_drops.draw(self.screen)
        # --- Exibição da Pontuação ---
        # Exibe o score como número + sprite Skull.png
        score_str = f"{self.score}"
        # Fonte menor para o score
        score_font = pygame.font.Font(None, 24)
        score_text = score_font.render(score_str, True, (255, 255, 255))
        bar_height = 14
        # Caveira menor
        try:
            skull_img = pygame.image.load('assets/sprites/Skull.png').convert_alpha()
            skull_img = pygame.transform.scale(skull_img, (16, 16))
        except Exception:
            skull_img = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(skull_img, (255,255,255), (8,8), 8)
        # Posição: mais à esquerda, fora dos slots de passiva
        score_x = self.screen_width - 265  # Ajuste fino mais à esquerda
        score_y = bar_height + 8
        self.screen.blit(score_text, (score_x, score_y + (skull_img.get_height() - score_text.get_height())//2))
        self.screen.blit(skull_img, (score_x + score_text.get_width() + 4, score_y))
        # --- Contador de Tempo de Sobrevivência ---
        if self.game_state == "PLAYING":
            time_elapsed_ms = pygame.time.get_ticks() - self.start_time
        else:
            time_elapsed_ms = self.time_at_pause
        time_seconds = time_elapsed_ms // 1000
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        time_text = f"{minutes:02}:{seconds:02}"
        # Renderiza timer com contorno preto para melhor visibilidade
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        outline_surface = self.font.render(time_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 32))
        outline_rect = outline_surface.get_rect(center=(self.screen_width // 2, 32))
        # Desenha contorno (preto) levemente deslocado em 4 direções
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            self.screen.blit(outline_surface, outline_rect.move(dx, dy))
        self.screen.blit(text_surface, text_rect)
        # --- Barra de XP ---
        xp = self.player.xp
        xp_max = self.player.xp_to_next_level
        bar_width = self.screen_width
        bar_height = 14
        bar_x = 0
        bar_y = 0
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))  # Fundo
        fill_width = int(bar_width * (xp / xp_max)) if xp_max > 0 else 0
        pygame.draw.rect(self.screen, (255, 215, 0), (bar_x, bar_y, fill_width, bar_height))  # Progresso
        # Texto
        font = pygame.font.SysFont(None, 20)
        xp_text = font.render(f"XP: {xp} / {xp_max}", True, (0, 0, 0))
        self.screen.blit(xp_text, (bar_x + bar_width//2 - xp_text.get_width()//2, bar_y + 1))
        # --- HUD de Slots de Itens e Armas ---
        SLOT_SIZE = 24
        PADDING = 8
        SLOTS_PER_ROW = 6
        XP_BAR_HEIGHT = 14
        HORIZONTAL_SPACING = 1
        transparent_white = (255, 255, 255, 80)
        # Linha superior (armas)
        from src.ui.config import ASSET_PATH
        bow_img = pygame.image.load(f"{ASSET_PATH}/sprites/Bow.png").convert_alpha()
        bow_img = pygame.transform.scale(bow_img, (SLOT_SIZE - 6, SLOT_SIZE - 6))
        # HUD horizontal no topo superior esquerdo, próxima do XP
        hud_x = PADDING
        hud_y = XP_BAR_HEIGHT + PADDING
        # Linha de armas (superior)
        for i in range(SLOTS_PER_ROW):
            x = hud_x + (i * (SLOT_SIZE + HORIZONTAL_SPACING))
            y = hud_y
            slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
            if i == 0:
                bow_rect = bow_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                slot_surface.blit(bow_img, bow_rect)
            self.screen.blit(slot_surface, (x, y))
        # Linha de passivas (mesma altura dos slots de armas, alinhados à direita)
        for i in range(SLOTS_PER_ROW):
            x = self.screen_width - PADDING - SLOT_SIZE - (i * (SLOT_SIZE + HORIZONTAL_SPACING))
            y = hud_y
            slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
            center = (SLOT_SIZE // 2, SLOT_SIZE // 2)
            pygame.draw.circle(slot_surface, transparent_white, center, 3)
            self.screen.blit(slot_surface, (x, y))
        self.enemies.draw(self.screen)
        self.gems.draw(self.screen)  # Adiciona desenho das gemas de XP
        self.projectiles.draw(self.screen)
        pygame.display.flip()
