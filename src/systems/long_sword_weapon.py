from src.entities.weapon import Weapon
import pygame

"""
Classe LongSwordWeapon: Herda de Weapon. Implementa um ataque de área de efeito (AOE)
que verifica colisões em uma hitbox ao redor do jogador.
"""
class LongSwordWeapon(Weapon):
    def __init__(self, player, cooldown=800, damage=5):
        super().__init__(player, cooldown, damage)
        self.attack_range = 56  # Raio de ataque da espada (alcance aumentado)
        self.icon_path = 'assets/sprites/Greatsword.png'
        self.aoe_sprite_path = 'assets/sprites/Sword_Aoe.png'
        self.last_hitbox_rect = None  # Para debug/desenho opcional
        self.aoe_visible_until = 0  # Timestamp até quando o AOE deve ser desenhado
        self._last_attack_direction = (1, 0)  # Default direction

    def fire_attack(self, enemies):
        """
        Verifica o cooldown. Se pronto, cria uma hitbox (pygame.Rect) que representa o ataque
        da espada (Ex: um retângulo de 80x40) à frente do jogador, na direção do movimento.
        O AOE pisca por 60ms.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.cooldown:
            self.last_shot_time = current_time
            # --- Direção do ataque (como a faca) ---
            dx, dy = self.player.direction_vector if hasattr(self.player, 'direction_vector') else (1, 0)
            # Se o player está parado, ataque para a direita
            if dx == 0 and dy == 0:
                dx, dy = 1, 0
            self._last_attack_direction = (dx, dy)

            # Use the stored direction for hitbox calculation
            import math
            length = math.hypot(dx, dy)
            ndx, ndy = (dx / length, dy / length) if length != 0 else (1, 0)
            offset = 60  # empurra mais para frente
            centerx = int(self.player.rect.centerx + ndx * offset)
            centery = int(self.player.rect.centery + ndy * offset)
            width = self.attack_range * 2
            height = self.attack_range
            if abs(ndx) > abs(ndy):
                hitbox_rect = pygame.Rect(centerx - self.attack_range, centery - height // 2, width, height)
            else:
                hitbox_rect = pygame.Rect(centerx - height // 2, centery - self.attack_range, height, width)
            self.last_hitbox_rect = hitbox_rect
            self.aoe_visible_until = current_time + 60  # Pisca por 60ms
            # --- Lógica de Colisão de Área ---
            enemies_hit = [enemy for enemy in enemies if hitbox_rect.colliderect(enemy.rect)]
            final_damage, critico = self.calcular_dano_efetivo()
            from src.entities.damage_text import DamageText
            for enemy in enemies_hit:
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(final_damage)
                    if hasattr(self.player, 'game_manager') and self.player.game_manager:
                        self.player.game_manager.damage_texts.append(DamageText(final_damage, enemy.rect.center, is_crit=critico))
                else:
                    enemy.kill()
                try:
                    from src.systems.audio_manager import play as play_sound
                    play_sound('sword')
                except Exception:
                    pass
        return None

    def draw_aoe(self, surface):
        """
        Desenha a área de ataque da espada (Sword_Aoe.png) rotacionada conforme a direção do ataque.
        """
        import math
        now = pygame.time.get_ticks()
        if self.last_hitbox_rect and now < self.aoe_visible_until:
            try:
                aoe_img = pygame.image.load(self.aoe_sprite_path).convert_alpha()
                aoe_img = pygame.transform.scale(aoe_img, (self.last_hitbox_rect.width, self.last_hitbox_rect.height))
                # Calcula ângulo da direção do ataque
                dx, dy = self.player.direction_vector if hasattr(self.player, 'direction_vector') else (1, 0)
                angle = -math.degrees(math.atan2(dy, dx)) + 30
                aoe_img = pygame.transform.rotate(aoe_img, angle)
                # Corrige posição para centralizar o sprite rotacionado na hitbox
                aoe_rect = aoe_img.get_rect(center=self.last_hitbox_rect.center)
                surface.blit(aoe_img, aoe_rect.topleft)
            except Exception:
                pygame.draw.rect(surface, (255, 0, 0), self.last_hitbox_rect, 2)
