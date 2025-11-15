import pygame
import os
import sys
import random
from src.player import Player
from src.enemy import Enemy
from src.weapon import Weapon
from src.projectile import Projectile
from src.game_over import GameOver
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, SPAWN_RATE, WEAPON_COOLDOWN, WEAPON_DAMAGE
from src.assets import get_tilemap_image

class GameManager:
    def __init__(self):
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Survivor-Like")
        self.tilemap_bg = get_tilemap_image()
        self.clock = pygame.time.Clock()
        self.running = True
        self.enemy_spawn_timer = 0
        self.spawn_rate = SPAWN_RATE
        self.enemies = pygame.sprite.Group()
        self.player = Player()
        self.weapon = Weapon(self.player, cooldown=WEAPON_COOLDOWN, damage=WEAPON_DAMAGE)
        self.projectiles = pygame.sprite.Group()

    def reset(self):
        self.enemies.empty()
        self.projectiles.empty()
        self.player = Player()
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
            self.update()
            self.draw()
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
        collisions = pygame.sprite.groupcollide(self.projectiles, self.enemies, True, False, collided=pygame.sprite.collide_mask)
        for proj, hit_enemies in collisions.items():
            for enemy in hit_enemies:
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
        if self.tilemap_bg:
            tile_w, tile_h = self.tilemap_bg.get_size()
            for x in range(0, self.screen_width, tile_w):
                for y in range(0, self.screen_height, tile_h):
                    self.screen.blit(self.tilemap_bg, (x, y))
        else:
            self.screen.fill((0, 0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        self.player.draw_health(self.screen)
        self.enemies.draw(self.screen)
        self.projectiles.draw(self.screen)
        pygame.display.flip()
