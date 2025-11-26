import pygame


class DamageText:
    def __init__(self, value, position, duration=500, is_crit=False):
        self.is_crit = is_crit
        # If crit, add '!' prefix
        self.value = f"!{value}" if is_crit else str(value)
        self.position = list(position)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 255
        self.font = pygame.font.SysFont('arial', 22, bold=True)
        self.finished = False

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            self.finished = True
        else:
            self.position[1] -= 0.5  # Float up
            self.alpha = max(0, 255 - int(255 * (elapsed / self.duration)))

    def draw(self, surface):
        # Render text: red for crit, white otherwise
        color = (255, 0, 0) if self.is_crit else (255, 255, 255)
        text_surf = self.font.render(self.value, True, color)
        # Render black outline
        outline = self.font.render(self.value, True, (0, 0, 0))
        outline.set_alpha(self.alpha)
        text_surf.set_alpha(self.alpha)
        x, y = int(self.position[0]), int(self.position[1])
        # Draw outline (4 directions)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            surface.blit(outline, (x+dx, y+dy))
        # Draw main text
        surface.blit(text_surf, (x, y))
