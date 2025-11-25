from src.entities.weapon import Weapon
import pygame

"""
Classe LongSwordWeapon: Herda de Weapon. Implementa um ataque de área de efeito (AOE)
que verifica colisões em uma hitbox ao redor do jogador.
"""
class LongSwordWeapon(Weapon):
    def __init__(self, player, cooldown=600, damage=10):
        super().__init__(player, cooldown, damage)
        self.attack_range = 40  # Raio de ataque da espada
        self.icon_path = 'assets/sprites/Greatsword.png'
        self.aoe_sprite_path = 'assets/sprites/Sword_Aoe.png'
        self.last_hitbox_rect = None  # Para debug/desenho opcional
        self.aoe_visible_until = 0  # Timestamp até quando o AOE deve ser desenhado

    def fire_attack(self, enemies):
        """
        Verifica o cooldown. Se pronto, cria uma hitbox (pygame.Rect) que representa o ataque
        da espada (Ex: um retângulo de 80x40) à frente do jogador, na direção do movimento.
        O AOE pisca por 100ms.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.cooldown:
            self.last_shot_time = current_time
            # --- Direção do ataque (como a faca) ---
            dx, dy = self.player.direction_vector if hasattr(self.player, 'direction_vector') else (1, 0)
            # Se o player está parado, ataque para a direita
            if dx == 0 and dy == 0:
                dx, dy = 1, 0
            import math
            # Normaliza direção
            length = math.hypot(dx, dy)
            ndx, ndy = (dx / length, dy / length) if length != 0 else (1, 0)
            # Offset para frente do player
            offset = 44  # mais distante do centro
            centerx = int(self.player.rect.centerx + ndx * offset)
            centery = int(self.player.rect.centery + ndy * offset)
            # Hitbox orientada à frente do player
            width = self.attack_range * 2
            height = self.attack_range
            # Rotaciona hitbox se ataque for vertical
            if abs(ndx) > abs(ndy):
                # Ataque horizontal (padrão)
                hitbox_rect = pygame.Rect(centerx - self.attack_range, centery - height // 2, width, height)
            else:
                # Ataque vertical
                hitbox_rect = pygame.Rect(centerx - height // 2, centery - self.attack_range, height, width)
            self.last_hitbox_rect = hitbox_rect
            self.aoe_visible_until = current_time + 60  # Pisca por 60ms
            # --- Lógica de Colisão de Área ---
            enemies_hit = [enemy for enemy in enemies if hitbox_rect.colliderect(enemy.rect)]
            for enemy in enemies_hit:
                final_damage = self.damage * getattr(self.player, 'damage_multiplier', 1.0)
                # Se Enemy tiver take_damage, use:
                # enemy.take_damage(final_damage)
                enemy.kill()
            # toca som da espada (uma vez por uso) via audio manager
            try:
                from src.systems.audio_manager import play as play_sound
                play_sound('longsword')
            except Exception:
                pass
            return True
        return False

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
