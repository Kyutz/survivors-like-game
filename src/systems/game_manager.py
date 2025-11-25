from src.entities.passive_item import passives_list, PassiveItem
import pygame
import os
import sys
import random
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.weapon import Weapon
from src.entities.projectile import Projectile
from src.ui.game_over import GameOver
from src.ui.config import SCREEN_WIDTH, SCREEN_HEIGHT, SPAWN_RATE, WEAPON_COOLDOWN, WEAPON_DAMAGE, ASSET_PATH
from src.ui.assets import get_tilemap_image


class GameManager:
    STATE_PLAYING = 0
    STATE_LEVEL_UP = 1
    STATE_MENU = 2
    STATE_GAMEOVER = 3
    STATE_PAUSE = 4

    def __init__(self):
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Survivor-Like")
        self.tilemap_bg = get_tilemap_image()
        self.clock = pygame.time.Clock()
        self.running = True
        # --- Máquina de Estados ---
        self.state = self.STATE_MENU
        self.pause_options = ["Continuar", "Menu Principal", "Sair"]
        self.selected_pause_option = 0
        self.menu_options = ["Iniciar Jogo", "Instruções", "Sair"]
        self.selected_option = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.enemy_spawn_timer = 0
        # --- Lógica de Dificuldade Dinâmica ---
        self.available_passives = passives_list.copy()
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
        # estados de progressão / moeda
        self.player.xp = 0
        self.player.level = 1
        # gems_collected faz parte do Player (inicializado ali), mas garantimos valor
        try:
            self.player.gems_collected = int(getattr(self.player, 'gems_collected', 0))
        except Exception:
            self.player.gems_collected = 0
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.projectiles = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        # Imagem de gema para HUD
        try:
            gem_img = pygame.image.load(f"{ASSET_PATH}/sprites/Gem.png").convert_alpha()
            self.gem_img = pygame.transform.scale(gem_img, (18, 18))
        except Exception:
            self.gem_img = None
        # caminho de salvamento simples
        self.save_path = os.path.join(os.getcwd(), 'savegame.json')
        # tentar carregar jogo salvo
        self.load_game()
        # --- Lógica de Tempo ---
        self.start_time = pygame.time.get_ticks() # Tempo em ms quando o jogo começa
        self.font = pygame.font.Font(None, 36) # Fonte padrão do Pygame (tamanho 36)
        self.time_at_pause = 0
        self.game_state = "PLAYING"  # Mantém para compatibilidade, mas usa self.state para fluxo
        self.score = 0  # Inicializa a pontuação

    def reset(self):
        self.enemies.empty()
        self.projectiles.empty()
        self.gems.empty()
        self.player = Player()
        self.player.xp = 0
        self.player.level = 1
        self.player.gems_collected = 0
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

    # ---------------- Persistence (save/load) ----------------
    def save_game(self):
        data = {
            'gems': int(getattr(self.player, 'gems_collected', 0)),
            'weapon_base_damage': int(getattr(self.weapon, 'base_damage', getattr(self.weapon, 'damage', 0))),
            'weapon_cooldown': int(getattr(self.weapon, 'cooldown', 0)),
            'weapon_extra_arrows': int(getattr(self.weapon, 'extra_arrows', 0)),
            'player_xp': int(getattr(self.player, 'xp', 0)),
            'player_level': int(getattr(self.player, 'level', 1)),
            'health': {
                'current': int(getattr(self.player.health, 'current', 0)),
                'max': int(getattr(self.player.health, 'max_health', getattr(self.player.health, 'max_health', 100)))
            }
        }
        try:
            with open(self.save_path, 'w') as f:
                import json
                json.dump(data, f)
        except Exception:
            pass

    def load_game(self):
        try:
            import json
            if not os.path.exists(self.save_path):
                return
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            # aplica valores, com cuidado para tipos
            self.player.gems_collected = int(data.get('gems', getattr(self.player, 'gems_collected', 0)))
            # aplica upgrades da arma
            bd = int(data.get('weapon_base_damage', getattr(self.weapon, 'base_damage', getattr(self.weapon, 'damage', 0))))
            self.weapon.set_base_damage(bd)
            # restaura estágio de flechas extras
            try:
                self.weapon.extra_arrows = int(data.get('weapon_extra_arrows', getattr(self.weapon, 'extra_arrows', 0)))
            except Exception:
                pass
            self.weapon.cooldown = int(data.get('weapon_cooldown', self.weapon.cooldown))
            self.player.xp = int(data.get('player_xp', self.player.xp))
            self.player.level = int(data.get('player_level', self.player.level))
            health = data.get('health') or {}
            if 'max' in health:
                try:
                    self.player.health.max_health = int(health.get('max', self.player.health.max_health))
                except Exception:
                    pass
            if 'current' in health:
                try:
                    self.player.health.current = int(health.get('current', self.player.health.current))
                except Exception:
                    pass
        except Exception:
            pass

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
            if self.state == self.STATE_MENU:
                self.draw()
            elif self.state == self.STATE_PLAYING:
                self.update()
                self.draw()
            elif self.state == self.STATE_PAUSE:
                self.draw()
            elif self.state == self.STATE_LEVEL_UP:
                self.draw()
                self.show_level_up_menu()
            elif self.state == self.STATE_GAMEOVER:
                self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.state == self.STATE_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Iniciar Jogo
                            self.state = self.STATE_PLAYING
                            self.start_time = pygame.time.get_ticks()
                        elif self.selected_option == 1:  # Instruções
                            self.show_instructions()
                        elif self.selected_option == 2:  # Sair
                            self.running = False
            elif self.state == self.STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_PAUSE
                    self.selected_pause_option = 0
                    self.time_at_pause = pygame.time.get_ticks() - self.start_time
            elif self.state == self.STATE_PAUSE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_pause_option = (self.selected_pause_option - 1) % len(self.pause_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_pause_option = (self.selected_pause_option + 1) % len(self.pause_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_pause_option == 0:  # Continuar
                            self.state = self.STATE_PLAYING
                            # Ajusta o timer para descontar o tempo pausado
                            self.start_time = pygame.time.get_ticks() - self.time_at_pause
                        elif self.selected_pause_option == 1:  # Menu Principal
                            self.state = self.STATE_MENU
                        elif self.selected_pause_option == 2:  # Sair
                            self.running = False
        # Permite sair com ESC em qualquer estado
        # Permite sair com ESC em qualquer estado exceto PAUSE e MENU
        if self.state not in (self.STATE_PAUSE, self.STATE_MENU):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.running = False

    def show_instructions(self):
        # Exibe uma tela simples de instruções
        instructions = [
            "Instruções:",
            "- Mova-se com WASD",
            "- Atire automaticamente",
            "- Colete gemas para XP",
            "- Sobreviva o máximo possível!",
            "",
            "Pressione ENTER para voltar"
        ]
        waiting = True
        while waiting:
            self.screen.fill((20, 20, 20))
            y = 100
            for line in instructions:
                text = self.font_medium.render(line, True, (255, 255, 255))
                rect = text.get_rect(center=(self.screen_width // 2, y))
                self.screen.blit(text, rect)
                y += 50
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False

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
        projectiles = self.weapon.fire_attack(self.enemies)
        if projectiles:
            # pode ser um único projétil ou uma lista
            try:
                # Se for iterável (lista) adiciona cada um
                for p in projectiles:
                    self.projectiles.add(p)
            except TypeError:
                # não iterável -> único projétil
                self.projectiles.add(projectiles)
        self.projectiles.update()
        self.gems.update()  # Atualiza todas as gemas para magnetismo
        # --- Colisão Projétil-Inimigo (precisão com mask) ---
        hits = pygame.sprite.groupcollide(
            self.projectiles, self.enemies, True, True,
            collided=pygame.sprite.collide_mask
        )
        for projectile, enemies_hit in hits.items():
            for enemy in enemies_hit:
                self.score += 1  # 1 ponto por inimigo eliminado
                if hasattr(enemy, 'drop_xp'):
                    new_gem = enemy.drop_xp()
                    if hasattr(new_gem, 'set_player'):
                        new_gem.set_player(self.player)
                    self.gems.add(new_gem)
        # --- Colisão Jogador-Gema ---
        collected_gems = pygame.sprite.spritecollide(self.player, self.gems, dokill=True, collided=pygame.sprite.collide_mask)
        for gem in collected_gems:
            value = getattr(gem, 'xp_value', 1)
            # gema dá XP e também funciona como moeda
            try:
                self.player.add_gems(value)
            except Exception:
                pass
            self.player.gain_xp(value)
            # opcional: salvar de forma leve cada N gemas/coleta — aqui deixamos salvar apenas em compras
            # gem.kill() já chamado por dokill=True
        # Se o jogador pode subir de nível, pausa o jogo para menu de level-up
        if self.player.can_level_up:
            self.state = self.STATE_LEVEL_UP
    def show_level_up_menu(self):
        # Exibe um menu simples de level-up com 3 opções placeholder
        font = pygame.font.SysFont(None, 48)
        passive_options = [p for p in self.available_passives if p not in self.player.passive_items]
        if not passive_options:
            options = ["Aumenta o dano! (placeholder)", "Aumenta a velocidade! (placeholder)", "Recupera vida! (placeholder)"]
            option_types = ["dano", "velocidade", "cura"]
        else:
            options = [f"{p.name} (+{int(p.value*100)}% {p.attribute})" for p in passive_options]
            option_types = passive_options
        selected = 0
        waiting = True
        self.draw()
        bg_frame = self.screen.copy()
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
            title = font.render(title_text, True, (255, 255, 0))
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, overlay_y + 20))
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
                        if passive_options:
                            item = option_types[selected]
                            self.player.acquire_passive_item(item)
                            if item in self.available_passives:
                                self.available_passives.remove(item)
                        waiting = False
        self.player.can_level_up = False
        self.state = self.STATE_PLAYING

    def draw(self):
        if self.state == self.STATE_MENU:
            self.screen.fill((30, 30, 30))
            # Título
            title = self.font_large.render("Survivors-Like", True, (255, 255, 0))
            title_rect = title.get_rect(center=(self.screen_width // 2, 120))
            self.screen.blit(title, title_rect)
            # Opções do menu
            for i, option in enumerate(self.menu_options):
                color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                opt_text = self.font_medium.render(option, True, color)
                opt_rect = opt_text.get_rect(center=(self.screen_width // 2, 250 + i * 60))
                self.screen.blit(opt_text, opt_rect)
            pygame.display.flip()
            return
        if self.state == self.STATE_PAUSE:
            # Desenha o jogo "congelado" por baixo
            from src.ui.draw_tiled_map import draw_tiled_map
            draw_tiled_map(self.screen, 'assets/maps/main_level.tmx')
            self.screen.blit(self.player.image, self.player.rect)
            self.player.draw_health(self.screen)
            self.enemies.draw(self.screen)
            self.gems.draw(self.screen)
            self.projectiles.draw(self.screen)
            # Overlay de pausa
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            pause_title = self.font_large.render("PAUSADO", True, (255, 255, 0))
            pause_rect = pause_title.get_rect(center=(self.screen_width // 2, 160))
            self.screen.blit(pause_title, pause_rect)
            for i, option in enumerate(self.pause_options):
                color = (255, 255, 0) if i == self.selected_pause_option else (255, 255, 255)
                opt_text = self.font_medium.render(option, True, color)
                opt_rect = opt_text.get_rect(center=(self.screen_width // 2, 260 + i * 60))
                self.screen.blit(opt_text, opt_rect)
            pygame.display.flip()
            return
        # ...existing code for PLAYING, LEVEL_UP, GAMEOVER...
        from src.ui.draw_tiled_map import draw_tiled_map
        draw_tiled_map(self.screen, 'assets/maps/main_level.tmx')
        self.screen.blit(self.player.image, self.player.rect)
        self.player.draw_health(self.screen)
        # --- Exibição da Pontuação ---
        score_str = f"{self.score}"
        score_font = pygame.font.Font(None, 24)
        score_text = score_font.render(score_str, True, (255, 255, 255))
        bar_height = 14
        try:
            skull_img = pygame.image.load('assets/sprites/Skull.png').convert_alpha()
            skull_img = pygame.transform.scale(skull_img, (16, 16))
        except Exception:
            skull_img = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(skull_img, (255,255,255), (8,8), 8)
        score_x = self.screen_width - 265
        score_y = bar_height + 8
        self.screen.blit(score_text, (score_x, score_y + (skull_img.get_height() - score_text.get_height())//2))
        self.screen.blit(skull_img, (score_x + score_text.get_width() + 4, score_y))
        # --- Contador de Gemas (HUD) ---
        gems_count = int(getattr(self.player, 'gems_collected', 0))
        gem_x = score_x + score_text.get_width() + skull_img.get_width() + 16
        gem_y = score_y
        if getattr(self, 'gem_img', None):
            self.screen.blit(self.gem_img, (gem_x, gem_y))
            gem_text_x = gem_x + self.gem_img.get_width() + 6
            gem_text_y = gem_y + (self.gem_img.get_height() - score_text.get_height())//2
        else:
            # fallback: círculo
            circle_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (255, 215, 0), (9,9), 8)
            self.screen.blit(circle_surf, (gem_x, gem_y))
            gem_text_x = gem_x + 22
            gem_text_y = gem_y
        gem_text = score_font.render(str(gems_count), True, (255, 255, 255))
        self.screen.blit(gem_text, (gem_text_x, gem_text_y))
        # --- Contador de Tempo de Sobrevivência ---
        if self.game_state == "PLAYING":
            time_elapsed_ms = pygame.time.get_ticks() - self.start_time
        else:
            time_elapsed_ms = self.time_at_pause
        time_seconds = time_elapsed_ms // 1000
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        time_text = f"{minutes:02}:{seconds:02}"
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        outline_surface = self.font.render(time_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 32))
        outline_rect = outline_surface.get_rect(center=(self.screen_width // 2, 32))
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
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (xp / xp_max)) if xp_max > 0 else 0
        pygame.draw.rect(self.screen, (255, 215, 0), (bar_x, bar_y, fill_width, bar_height))
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
        from src.ui.config import ASSET_PATH
        bow_img = pygame.image.load(f"{ASSET_PATH}/sprites/Bow.png").convert_alpha()
        bow_img = pygame.transform.scale(bow_img, (SLOT_SIZE - 6, SLOT_SIZE - 6))
        hud_x = PADDING
        hud_y = XP_BAR_HEIGHT + PADDING
        # HUD de armas: da esquerda para a direita
        # Suporte para múltiplas armas no futuro, por enquanto só Bow
        weapons = []
        if hasattr(self.player, 'weapons'):
            weapons = self.player.weapons
        else:
            weapons = [self.weapon] if hasattr(self, 'weapon') else []
        for i in range(SLOTS_PER_ROW):
            x = hud_x + (i * (SLOT_SIZE + HORIZONTAL_SPACING))
            y = hud_y
            slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
            # Se o player tem uma arma nesse slot, desenha o ícone
            if i < len(weapons):
                # Por enquanto só Bow.png, mas pode ser generalizado
                try:
                    icon_img = bow_img
                    icon_rect = icon_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                    slot_surface.blit(icon_img, icon_rect)
                except Exception:
                    pass
            else:
                center = (SLOT_SIZE // 2, SLOT_SIZE // 2)
                pygame.draw.circle(slot_surface, transparent_white, center, 3)
            self.screen.blit(slot_surface, (x, y))
        # HUD de passivas: slots continuam do lado direito, mas preenchimento da esquerda para a direita
        # HUD de passivas: slots continuam do lado direito, preenchidos da direita para a esquerda
        for i in range(SLOTS_PER_ROW):
            x = self.screen_width - PADDING - SLOT_SIZE - (i * (SLOT_SIZE + HORIZONTAL_SPACING))
            y = hud_y
            slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
            # Preencher da direita para a esquerda: passiva 0 vai no slot mais à esquerda, passiva 1 no próximo à direita, etc.
            passive_idx = SLOTS_PER_ROW - 1 - i
            if passive_idx < len(self.player.passive_items):
                icon_path = getattr(self.player.passive_items[passive_idx], 'icon_path', None)
                if icon_path:
                    try:
                        icon_img = pygame.image.load(icon_path).convert_alpha()
                        icon_img = pygame.transform.scale(icon_img, (SLOT_SIZE - 6, SLOT_SIZE - 6))
                        icon_rect = icon_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                        slot_surface.blit(icon_img, icon_rect)
                    except Exception:
                        pass
            else:
                center = (SLOT_SIZE // 2, SLOT_SIZE // 2)
                pygame.draw.circle(slot_surface, transparent_white, center, 3)
            self.screen.blit(slot_surface, (x, y))
        self.enemies.draw(self.screen)
        self.gems.draw(self.screen)
        self.projectiles.draw(self.screen)
        pygame.display.flip()
