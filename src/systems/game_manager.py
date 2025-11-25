from src.entities.passive_item import passives_list, PassiveItem
import pygame
from src.systems.audio_manager import pre_init as audio_pre_init, init as audio_init
import os
import sys
import random
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.weapon import Weapon
from src.systems.knife_weapon import KnifeWeapon
from src.entities.projectile import Projectile
from src.ui.game_over import GameOver
from src.ui.config import SCREEN_WIDTH, SCREEN_HEIGHT, SPAWN_RATE, WEAPON_COOLDOWN, WEAPON_DAMAGE
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
        # Pre-initialize audio mixer to reduce latency; safe no-op if pygame unavailable
        try:
            audio_pre_init()
        except Exception:
            pass
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Dungeon Survivors")
        # Define ícone customizado para a janela
        try:
            icon_img = pygame.image.load('assets/sprites/Gem.png').convert_alpha()
            pygame.display.set_icon(icon_img)
        except Exception:
            pass
        self.tilemap_bg = get_tilemap_image()
        # Fundo do menu principal
        try:
            bg_img = pygame.image.load('assets/sprites/background.png').convert_alpha()
            img_w, img_h = bg_img.get_size()
            if img_w == self.screen_width and img_h == self.screen_height:
                self.menu_background = bg_img
            else:
                self.menu_background = pygame.transform.smoothscale(bg_img, (self.screen_width, self.screen_height))
        except Exception:
            self.menu_background = None
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
        self.player.xp = 0
        self.player.level = 1
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.weapons = [self.weapon]  # Apenas o arco como arma inicial
        self.longsword_weapon = None
        self.projectiles = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        # --- Lógica de Tempo ---
        self.start_time = pygame.time.get_ticks() # Tempo em ms quando o jogo começa
        self.font = pygame.font.Font(None, 36) # Fonte padrão do Pygame (tamanho 36)
        self.time_at_pause = 0
        self.game_state = "PLAYING"  # Mantém para compatibilidade, mas usa self.state para fluxo
        self.score = 0  # Inicializa a pontuação
        # Inicializa o AudioManager (carrega sons configurados)
        try:
            audio_init()
            # Debug: reporte do estado do audio_manager (mostra quais sons foram carregados)
            try:
                from src.systems.audio_manager import status as audio_status
                st = audio_status()
                # status available for debugging but do not print in normal run
                _ = st
            except Exception:
                pass
        except Exception:
            pass

    def reset(self):
        self.enemies.empty()
        self.projectiles.empty()
        self.gems.empty()
        self.player = Player()
        self.player.xp = 0
        self.player.level = 1
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.weapons = [self.weapon]
        self.longsword_weapon = None
        self.knife_weapon = None  # Remove knife reference
        self.available_passives = passives_list.copy()  # Reset passives
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
                    if event.key in (pygame.K_UP, pygame.K_LEFT):
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
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
        # Dispara todas as armas adquiridas
        for weapon in self.weapons:
            result = weapon.fire_attack(self.enemies)
            if result and hasattr(weapon, 'draw_aoe'):
                weapon.draw_aoe(self.screen)
            if result and not hasattr(weapon, 'draw_aoe'):
                self.projectiles.add(result)
        # FireBall mata inimigos ao colidir
        for projectile in list(self.projectiles):
            from src.entities.fire_ball import FireBall
            if isinstance(projectile, FireBall):
                hit = pygame.sprite.spritecollideany(projectile, self.enemies, collided=pygame.sprite.collide_mask)
                if hit:
                    self.score += 1
                    if hasattr(hit, 'drop_xp'):
                        new_gem = hit.drop_xp()
                        if hasattr(new_gem, 'set_player'):
                            new_gem.set_player(self.player)
                        self.gems.add(new_gem)
                    hit.kill()
                    projectile.kill()
        keys = pygame.key.get_pressed()
        # Importa utilitário de colisão
        from src.systems.map_collision import get_blocked_tiles
        blocked_rects = get_blocked_tiles('assets/maps/main_level.tmx')
        self.player.update_movement(keys, self.screen.get_rect(), blocked_rects, self.enemies)

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
        # Atualiza inimigos com referência ao grupo para colisão entre eles
        for enemy in self.enemies:
            enemy.update(self.player.rect, self.enemies)
        # Agora o dano é causado por colisão de bounding box (rect), não mais por mask
        collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, dokill=False)
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
        # Flecha só mata o primeiro inimigo atingido
        for projectile in list(self.projectiles):
            hit = pygame.sprite.spritecollideany(projectile, self.enemies, collided=pygame.sprite.collide_mask)
            if hit:
                self.score += 1
                if hasattr(hit, 'drop_xp'):
                    new_gem = hit.drop_xp()
                    if hasattr(new_gem, 'set_player'):
                        new_gem.set_player(self.player)
                    self.gems.add(new_gem)
                hit.kill()
                # Só remove o projétil se não for perfurante
                if not getattr(projectile, 'piercing', False):
                    projectile.kill()
        # --- Colisão Jogador-Gema ---
        collected_gems = pygame.sprite.spritecollide(self.player, self.gems, dokill=True, collided=pygame.sprite.collide_mask)
        for gem in collected_gems:
            self.player.gain_xp(getattr(gem, 'xp_value', 1))
            # gem.kill() já chamado por dokill=True
        # Se o jogador pode subir de nível, pausa o jogo para menu de level-up
        if self.player.can_level_up:
            self.state = self.STATE_LEVEL_UP
    def show_level_up_menu(self):
        from src.systems.fire_staff import FireStaff
        from src.systems.stone_orb_weapon import StoneOrbWeapon
        from src.systems.knife_weapon import KnifeWeapon
        from src.systems.long_sword_weapon import LongSwordWeapon
        from src.systems.axe_weapon import AxeWeapon
        import random
        font = pygame.font.SysFont(None, 48)

        weapon_options = []
        # Knife
        if not any(isinstance(w, KnifeWeapon) for w in self.weapons):
            weapon_options.append({
                'name': 'Faca (Knife)',
                'desc': 'Ataca na direção do movimento',
                'class': KnifeWeapon
            })
        # Long Sword
        if not any(isinstance(w, LongSwordWeapon) for w in self.weapons):
            weapon_options.append({
                'name': 'Espada Longa (Greatsword)',
                'desc': 'Ataque de área à frente do jogador',
                'class': LongSwordWeapon
            })
        # Fire Staff
        if not any(isinstance(w, FireStaff) for w in self.weapons):
            weapon_options.append({
                'name': 'Cajado de Fogo',
                'desc': 'Dispara uma bola de fogo teleguiada',
                'class': FireStaff
            })
        # Stone Orb
        if not any(isinstance(w, StoneOrbWeapon) for w in self.weapons):
            weapon_options.append({
                'name': 'Orbe de Pedra',
                'desc': 'Gira ao redor do jogador e destrói inimigos',
                'class': StoneOrbWeapon
            })
        # Axe Weapon
        if not any(w.__class__.__name__ == 'AxeWeapon' for w in self.weapons):
            weapon_options.append({
                'name': 'Machado (Axe)',
                'desc': 'Dispara um machado em arco que perfura inimigos',
                'class': AxeWeapon
            })

        passive_options = [p for p in self.available_passives if p not in self.player.passive_items]
        all_options = passive_options + weapon_options
        random.shuffle(all_options)
        # Seleciona até 3 opções aleatórias
        if len(all_options) > 3:
            chosen = random.sample(all_options, 3)
        else:
            chosen = all_options
        options = []
        option_types = []
        for item in chosen:
            if hasattr(item, 'name') and hasattr(item, 'attribute'):
                options.append(f"{item.name} (+{int(item.value*100)}% {item.attribute})")
                option_types.append(item)
            elif isinstance(item, dict):
                options.append(f"{item['name']} - {item['desc']}")
                option_types.append(item)
        if not options:
            options = ["Aumenta o dano! (placeholder)", "Aumenta a velocidade! (placeholder)", "Recupera vida! (placeholder)"]
            option_types = ["dano", "velocidade", "cura"]
            option_types = ["dano", "velocidade", "cura"]
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
        # --- Novo layout estilo Vampire Survivors ---
        BOX_WIDTH = 380
        BOX_HEIGHT = 70
        BOX_SPACING = 18
        ICON_SIZE = 38
        ICON_PADDING = 18
        # Cores
        COLOR_BG = (30, 30, 30, 220)
        COLOR_BOX = (60, 60, 70)
        COLOR_BOX_SELECTED = (255, 230, 120)
        COLOR_BOX_SELECTED_BG = (60, 90, 180)
        COLOR_BOX_BORDER = (200, 200, 120)
        COLOR_TEXT = (255, 255, 255)
        COLOR_TEXT_SELECTED = (0, 0, 0)
        COLOR_TITLE = (180, 180, 180)
        # --- Calcula tamanho da janela principal ---
        total_height = len(options) * BOX_HEIGHT + (len(options)-1) * BOX_SPACING + 60
        window_width = BOX_WIDTH + 48
        window_height = total_height + 32
        window_x = self.screen_width//2 - window_width//2
        window_y = self.screen_height//2 - window_height//2
        # --- Loop de desenho ---
        while waiting:
            self.screen.blit(bg_frame, (0, 0))
            # Janela principal
            pygame.draw.rect(self.screen, (50, 50, 60), (window_x, window_y, window_width, window_height), border_radius=16)
            pygame.draw.rect(self.screen, COLOR_BOX_BORDER, (window_x, window_y, window_width, window_height), 4, border_radius=16)
            # Título centralizado, apenas 'Level Up!'
            title = font.render('Level Up!', True, COLOR_TITLE)
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, window_y + 18))
            # Centraliza as caixas verticalmente dentro da janela
            start_y = window_y + 60
            for i, opt in enumerate(options):
                box_x = window_x + (window_width - BOX_WIDTH)//2
                box_y = start_y + i * (BOX_HEIGHT + BOX_SPACING)
                # Fundo e borda
                if i == selected:
                    pygame.draw.rect(self.screen, COLOR_BOX_SELECTED_BG, (box_x, box_y, BOX_WIDTH, BOX_HEIGHT), border_radius=10)
                    pygame.draw.rect(self.screen, COLOR_BOX_BORDER, (box_x, box_y, BOX_WIDTH, BOX_HEIGHT), 3, border_radius=10)
                else:
                    pygame.draw.rect(self.screen, COLOR_BOX, (box_x, box_y, BOX_WIDTH, BOX_HEIGHT), border_radius=10)
                    pygame.draw.rect(self.screen, (120,120,120), (box_x, box_y, BOX_WIDTH, BOX_HEIGHT), 2, border_radius=10)
                # Ícone
                icon_path = None
                item = option_types[i]
                if hasattr(item, 'icon_path') and item.icon_path:
                    icon_path = item.icon_path
                elif isinstance(item, dict) and 'class' in item:
                    weapon_cls = item['class']
                    if hasattr(weapon_cls, 'icon_path'):
                        icon_path = weapon_cls.icon_path
                    elif weapon_cls.__name__ == 'KnifeWeapon':
                        icon_path = 'assets/sprites/Knife.png'
                    elif weapon_cls.__name__ == 'LongSwordWeapon':
                        icon_path = 'assets/sprites/Greatsword.png'
                    elif weapon_cls.__name__ == 'AxeWeapon':
                        icon_path = 'assets/sprites/weapons/axe.png'
                if icon_path:
                    try:
                        icon_img = pygame.image.load(icon_path).convert_alpha()
                        icon_img = pygame.transform.scale(icon_img, (ICON_SIZE, ICON_SIZE))
                        icon_rect = icon_img.get_rect()
                        icon_rect.left = box_x + ICON_PADDING
                        icon_rect.centery = box_y + BOX_HEIGHT//2
                        self.screen.blit(icon_img, icon_rect)
                    except Exception:
                        pass
                # Nome
                name_font = pygame.font.SysFont(None, 28, bold=True)
                name = opt.split('(')[0].strip() if '(' in opt else opt.split('-')[0].strip()
                name_surf = name_font.render(name, True, COLOR_TEXT_SELECTED if i == selected else COLOR_TEXT)
                name_x = box_x + ICON_PADDING + ICON_SIZE + 16
                name_y = box_y + 12
                self.screen.blit(name_surf, (name_x, name_y))
                # Descrição/efeito
                desc_font = pygame.font.SysFont(None, 22)
                desc = ''
                # Para passivas, mostra o atributo e valor
                if hasattr(item, 'attribute') and hasattr(item, 'value'):
                    attr = item.attribute
                    val = item.value
                    if attr == 'armor':
                        desc = f"Reduz dano recebido em {int(val*100)}%"
                    elif attr == 'damage_multiplier':
                        desc = f"Aumenta dano em {int(val*100)}%"
                    elif attr == 'cooldown_multiplier':
                        desc = f"Reduz cooldown em {abs(int(val*100))}%"
                    else:
                        desc = f"Bônus: {attr} +{val}"
                # Para armas, mostra a descrição
                elif isinstance(item, dict) and 'desc' in item:
                    desc = item['desc']
                desc_surf = desc_font.render(desc, True, COLOR_TEXT)
                desc_x = name_x
                desc_y = name_y + 28
                self.screen.blit(desc_surf, (desc_x, desc_y))
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
                        item = option_types[selected]
                        # Se for passiva
                        from src.systems.knife_weapon import KnifeWeapon
                        if isinstance(item, PassiveItem):
                            self.player.acquire_passive_item(item)
                            if item in self.available_passives:
                                self.available_passives.remove(item)
                        # Se for arma (Knife)
                        elif isinstance(item, dict) and item.get('class') == KnifeWeapon:
                            if not any(isinstance(w, KnifeWeapon) for w in self.weapons):
                                self.knife_weapon = KnifeWeapon(self.player)
                                self.weapons.append(self.knife_weapon)
                        elif isinstance(item, dict) and item.get('class').__name__ == 'LongSwordWeapon':
                            from src.systems.long_sword_weapon import LongSwordWeapon
                            if not any(isinstance(w, LongSwordWeapon) for w in self.weapons):
                                self.longsword_weapon = LongSwordWeapon(self.player)
                                self.weapons.append(self.longsword_weapon)
                        elif isinstance(item, dict) and item.get('class').__name__ == 'StoneOrbWeapon':
                            if not any(w.__class__.__name__ == 'StoneOrbWeapon' for w in self.weapons):
                                self.stone_orb_weapon = item['class'](self.player, radius=60, speed=0.012, damage=9999)
                                self.weapons.append(self.stone_orb_weapon)
                        elif isinstance(item, dict) and item.get('class').__name__ == 'FireStaff':
                            if not any(w.__class__.__name__ == 'FireStaff' for w in self.weapons):
                                self.fire_staff = item['class'](self.player, cooldown=1400, damage=15)
                                self.weapons.append(self.fire_staff)
                        elif isinstance(item, dict) and item.get('class').__name__ == 'AxeWeapon':
                            if not any(w.__class__.__name__ == 'AxeWeapon' for w in self.weapons):
                                self.axe_weapon = item['class'](self.player)
                                self.weapons.append(self.axe_weapon)
                        waiting = False
        self.player.can_level_up = False
        self.state = self.STATE_PLAYING

    def draw(self):
        if self.state == self.STATE_PLAYING:
            # Desenhar mapa
            from src.ui.draw_tiled_map import draw_tiled_map
            draw_tiled_map(self.screen, 'assets/maps/main_level.tmx')
            # Desenhar player
            self.screen.blit(self.player.image, self.player.rect)
            # Desenhar armas orbitais (StoneOrbWeapon) por cima do player
            for weapon in self.weapons:
                if hasattr(weapon, 'draw'):
                    weapon.draw(self.screen)
            # Desenhar área de ataque da LongSwordWeapon, se existir
            if getattr(self, 'longsword_weapon', None) is not None and self.longsword_weapon.last_hitbox_rect:
                self.longsword_weapon.draw_aoe(self.screen)
            self.player.draw_health(self.screen)
            # HUD, inimigos, gems, projectiles, etc.
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
            bow_img = pygame.transform.scale(bow_img, (SLOT_SIZE, SLOT_SIZE))
            hud_x = PADDING
            hud_y = XP_BAR_HEIGHT + PADDING
            for i in range(SLOTS_PER_ROW):
                x = hud_x + (i * (SLOT_SIZE + HORIZONTAL_SPACING))
                y = hud_y
                slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
                if i == 0:
                    try:
                        icon_img = bow_img
                        icon_rect = icon_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                        slot_surface.blit(icon_img, icon_rect)
                    except Exception:
                        pass
                elif i == 1 and len(self.weapons) > 1 and hasattr(self.weapons[1], 'icon_path'):
                    # Cajado de fogo
                    try:
                        staff_img = pygame.image.load(self.weapons[1].icon_path).convert_alpha()
                        staff_img = pygame.transform.scale(staff_img, (SLOT_SIZE, SLOT_SIZE))
                        staff_rect = staff_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                        slot_surface.blit(staff_img, staff_rect)
                    except Exception:
                        pass
                elif i-1 < len(self.weapons)-1:
                    icon_path = getattr(self.weapons[i], 'icon_path', None)
                    if icon_path:
                        try:
                            icon_img = pygame.image.load(icon_path).convert_alpha()
                            if 'Greatsword' in icon_path or 'greatsword' in icon_path:
                                icon_img = pygame.transform.scale(icon_img, (SLOT_SIZE - 2, SLOT_SIZE - 2))
                            else:
                                icon_img = pygame.transform.scale(icon_img, (SLOT_SIZE - 6, SLOT_SIZE - 6))
                            icon_rect = icon_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                            slot_surface.blit(icon_img, icon_rect)
                        except Exception:
                            pass
                self.screen.blit(slot_surface, (x, y))
            for i in range(SLOTS_PER_ROW):
                x = self.screen_width - PADDING - SLOT_SIZE - (i * (SLOT_SIZE + HORIZONTAL_SPACING))
                y = hud_y
                slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
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
            return
        # Mantém o restante dos estados (MENU, PAUSE, etc) igual
        if self.state == self.STATE_MENU:
            # Fundo do menu
            if getattr(self, 'menu_background', None) is not None:
                self.screen.blit(self.menu_background, (0, 0))
            else:
                self.screen.fill((30, 30, 30))
            # Opções do menu na parte inferior, alinhadas da esquerda para a direita
            num_options = len(self.menu_options)
            box_width, box_height = 220, 48
            spacing = 32
            total_width = num_options * box_width + (num_options - 1) * spacing
            start_x = (self.screen_width - total_width) // 2
            y = self.screen_height - box_height - 48
            for i, option in enumerate(self.menu_options):
                x = start_x + i * (box_width + spacing)
                color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                opt_text = self.font_medium.render(option, True, color)
                # Caixa de fundo
                pygame.draw.rect(self.screen, (40, 40, 60), (x, y, box_width, box_height), border_radius=10)
                # Borda destacada se selecionado
                if i == self.selected_option:
                    pygame.draw.rect(self.screen, (255, 255, 120), (x, y, box_width, box_height), 3, border_radius=10)
                else:
                    pygame.draw.rect(self.screen, (120, 120, 120), (x, y, box_width, box_height), 2, border_radius=10)
                # Texto centralizado na caixa
                opt_rect = opt_text.get_rect(center=(x + box_width // 2, y + box_height // 2))
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
            # Caixa centralizada para o menu de pausa (mais alta)
            box_width, box_height = 420, 340
            box_x = (self.screen_width - box_width) // 2
            box_y = (self.screen_height - box_height) // 2
            pygame.draw.rect(self.screen, (40, 40, 60), (box_x, box_y, box_width, box_height), border_radius=18)
            pygame.draw.rect(self.screen, (255, 255, 120), (box_x, box_y, box_width, box_height), 4, border_radius=18)
            # Título em branco
            pause_title = self.font_large.render("PAUSADO", True, (255, 255, 255))
            pause_rect = pause_title.get_rect(center=(self.screen_width // 2, box_y + 54))
            self.screen.blit(pause_title, pause_rect)
            # Opções centralizadas na caixa
            num_options = len(self.pause_options)
            opt_box_w, opt_box_h = 260, 48
            spacing = 24
            total_height = num_options * opt_box_h + (num_options - 1) * spacing
            start_y = box_y + 90 + (box_height - 90 - total_height) // 2
            for i, option in enumerate(self.pause_options):
                x = self.screen_width // 2 - opt_box_w // 2
                y = start_y + i * (opt_box_h + spacing)
                # Caixa de fundo
                pygame.draw.rect(self.screen, (60, 60, 90), (x, y, opt_box_w, opt_box_h), border_radius=10)
                # Borda destacada se selecionado
                if i == self.selected_pause_option:
                    pygame.draw.rect(self.screen, (255, 255, 120), (x, y, opt_box_w, opt_box_h), 3, border_radius=10)
                else:
                    pygame.draw.rect(self.screen, (120, 120, 120), (x, y, opt_box_w, opt_box_h), 2, border_radius=10)
                # Texto centralizado
                color = (255, 255, 0) if i == self.selected_pause_option else (255, 255, 255)
                opt_text = self.font_medium.render(option, True, color)
                opt_rect = opt_text.get_rect(center=(x + opt_box_w // 2, y + opt_box_h // 2))
                self.screen.blit(opt_text, opt_rect)
            pygame.display.flip()
            return

        # ...instruções removidas, volta ao show_instructions() fullscreen...
        # ...existing code for PLAYING, LEVEL_UP, GAMEOVER...
        from src.ui.draw_tiled_map import draw_tiled_map
        draw_tiled_map(self.screen, 'assets/maps/main_level.tmx')
        self.screen.blit(self.player.image, self.player.rect)
        # Desenha área de ataque da LongSwordWeapon, se existir
        if getattr(self, 'longsword_weapon', None) is not None and self.longsword_weapon.last_hitbox_rect:
            self.longsword_weapon.draw_aoe(self.screen)
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
        # HUD de armas: da esquerda para a direita
        # HUD de armas: sempre 6 slots, Bow.png sempre no primeiro slot
        for i in range(SLOTS_PER_ROW):
            x = hud_x + (i * (SLOT_SIZE + HORIZONTAL_SPACING))
            y = hud_y
            slot_surface = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(slot_surface, transparent_white, (0, 0, SLOT_SIZE, SLOT_SIZE), 1)
            if i == 0:
                # Sempre Bow.png no primeiro slot
                try:
                    icon_img = bow_img
                    icon_rect = icon_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                    slot_surface.blit(icon_img, icon_rect)
                except Exception:
                    pass
            elif i-1 < len(self.weapons)-1:
                # Armas adquiridas aparecem nos próximos slots
                icon_path = getattr(self.weapons[i], 'icon_path', None)
                if icon_path:
                    try:
                        icon_img = pygame.image.load(icon_path).convert_alpha()
                        # Se for a Greatsword, aumenta mais o tamanho
                        if 'Greatsword' in icon_path or 'greatsword' in icon_path:
                            icon_img = pygame.transform.scale(icon_img, (SLOT_SIZE - 2, SLOT_SIZE - 2))
                        else:
                            icon_img = pygame.transform.scale(icon_img, (SLOT_SIZE - 6, SLOT_SIZE - 6))
                        icon_rect = icon_img.get_rect(center=(SLOT_SIZE // 2, SLOT_SIZE // 2))
                        slot_surface.blit(icon_img, icon_rect)
                    except Exception:
                        pass
            # slots vazios: só o quadrado
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
