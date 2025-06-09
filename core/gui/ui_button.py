"""Módulo que armazena uma classe para criar botões."""

import pygame
from utils.audio_manager import audio_manager


class UIButton:
    """
    Componente de interface gráfica que representa um botão visual completo e interativo.

    Recursos incluídos:
    - Animação de escala ao passar o mouse (LERP)
    - Efeito de clareamento com fade (opcional)
    - Troca de imagem ao passar o mouse (hover_image)
    - Ícone opcional
    - Texto com alinhamento e padding configuráveis
    - Sons de hover e clique
    """

    def __init__(
        self,
        x,
        y,
        bg_image,
        icon_image=None,
        text=None,
        font=None,
        text_color=(255, 255, 255),
        enable_scale=False,
        max_scale=1.2,
        scale_speed=15.0,
        enable_fade=False,
        fade_color=(255, 255, 255),
        fade_speed=10.0,
        fade_max_alpha=100,
        hover_image=None,
        hover_sound=None,
        click_sound=None,
        text_align='center',
        text_padding=0
    ):
        self.x = x
        self.y = y
        self.bg_image = bg_image
        self.hover_image = hover_image
        self.icon_image = icon_image
        self.text = text
        self.font = font
        self.text_color = text_color
        self.text_align = text_align
        self.text_padding = text_padding

        self.original_size = bg_image.get_size()
        self.fixed_rect = pygame.Rect(x, y, *self.original_size)
        self.rect = self.fixed_rect.copy()

        # Efeito de escala
        self.enable_scale = enable_scale
        self.max_scale = max_scale
        self.scale_speed = scale_speed
        self.current_scale = 1.0
        self.target_scale = 1.0

        # Efeito de fade
        self.enable_fade = enable_fade
        self.fade_color = fade_color
        self.fade_speed = fade_speed
        self.fade_max_alpha = fade_max_alpha
        self.fade_alpha = 0

        # Estado de interação
        self.hovered = False
        self.was_hovering = False

        # Áudio
        self.hover_sound = hover_sound
        self.click_sound = click_sound

    def get_scaled_rect(self):
        """Retorna o retângulo atual com base na escala animada."""
        width = int(self.original_size[0] * self.current_scale)
        height = int(self.original_size[1] * self.current_scale)
        draw_x = self.x + self.original_size[0] // 2 - width // 2
        draw_y = self.y + self.original_size[1] // 2 - height // 2
        return pygame.Rect(draw_x, draw_y, width, height)

    def update(self, dt):
        """Atualiza os efeitos de hover, escala e fade."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.fixed_rect.collidepoint(mouse_pos)
        self.hovered = is_hovering

        if is_hovering and not self.was_hovering and self.hover_sound:
            audio_manager.play_sound(self.hover_sound)

        if self.enable_scale:
            self.target_scale = self.max_scale if is_hovering else 1.0
            self.current_scale += (self.target_scale - self.current_scale) * min(self.scale_speed * dt, 1)
            self.rect = self.get_scaled_rect()

        if self.enable_fade:
            target_alpha = self.fade_max_alpha if is_hovering else 0
            diff = target_alpha - self.fade_alpha
            self.fade_alpha += diff * min(self.fade_speed * dt, 1)
            self.fade_alpha = max(0, min(255, self.fade_alpha))

        self.was_hovering = is_hovering

    def update_position(self, offset_x=0, offset_y=0):
        """
        Atualiza a posição do botão com base na escala e deslocamento da superfície pai.
        Útil em listas com rolagem e popups.

        :param offset_x: Deslocamento horizontal.
        :param offset_y: Deslocamento vertical.
        """
        scaled_size = (
            int(self.original_size[0] * self.current_scale),
            int(self.original_size[1] * self.current_scale)
        )
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2 + offset_x
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2 + offset_y
        self.fixed_rect = pygame.Rect(draw_x, draw_y, *scaled_size)
        self.rect = self.fixed_rect.copy()

    def _render_text(self, screen, scaled_size, draw_x, draw_y):
        """Renderiza o texto com alinhamento e padding definidos."""
        if not self.text or not self.font:
            return

        text_surface = self.font.render(self.text, True, self.text_color)
        original_size = text_surface.get_size()

        scaled_text = pygame.transform.smoothscale(
            text_surface,
            (int(original_size[0] * self.current_scale), int(original_size[1] * self.current_scale))
        )
        text_rect = scaled_text.get_rect()

        # Alinhamento
        if self.text_align == 'center':
            text_rect.center = (draw_x + scaled_size[0] // 2, draw_y + scaled_size[1] // 2)
        elif self.text_align == 'left':
            text_rect.midleft = (draw_x + self.text_padding, draw_y + scaled_size[1] // 2)
        elif self.text_align == 'right':
            text_rect.midright = (draw_x + scaled_size[0] - self.text_padding, draw_y + scaled_size[1] // 2)
        elif self.text_align == 'top':
            text_rect.midtop = (draw_x + scaled_size[0] // 2, draw_y + self.text_padding)
        elif self.text_align == 'bottom':
            text_rect.midbottom = (draw_x + scaled_size[0] // 2, draw_y + scaled_size[1] - self.text_padding)

        screen.blit(scaled_text, text_rect)

    def render(self, screen):
        """Renderiza o botão na posição padrão."""
        self._render_with_offset(screen, y_offset=0)

    def render_at(self, screen, y_offset=0):
        """Renderiza o botão com deslocamento vertical (útil para popups)."""
        self._render_with_offset(screen, y_offset)

    def _render_with_offset(self, screen, y_offset):
        """Renderiza o botão completo com efeitos visuais e deslocamento opcional."""
        scaled_size = (
            int(self.original_size[0] * self.current_scale),
            int(self.original_size[1] * self.current_scale)
        )
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2 + y_offset

        base_image = self.hover_image if (self.hovered and self.hover_image) else self.bg_image
        scaled_bg = pygame.transform.smoothscale(base_image, scaled_size)
        screen.blit(scaled_bg, (draw_x, draw_y))

        # Fade (independe de canal alpha agora)
        if self.enable_fade:
            fade_overlay = pygame.Surface(scaled_size, pygame.SRCALPHA)
            fade_overlay.fill((*self.fade_color, int(self.fade_alpha)))
            screen.blit(fade_overlay, (draw_x, draw_y))

        # Ícone
        if self.icon_image:
            scaled_icon = pygame.transform.smoothscale(self.icon_image, scaled_size)
            screen.blit(scaled_icon, (draw_x, draw_y))

        # Texto
        self._render_text(screen, scaled_size, draw_x, draw_y)

    def render_on_surface(self, surface, offset_x=0, offset_y=0):
        """Renderiza o botão sobre uma superfície externa, como listas ou painéis."""
        scaled_size = (
            int(self.original_size[0] * self.current_scale),
            int(self.original_size[1] * self.current_scale)
        )
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2 + offset_x
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2 + offset_y

        base_image = self.hover_image if (self.hovered and self.hover_image) else self.bg_image
        scaled_bg = pygame.transform.smoothscale(base_image, scaled_size)
        surface.blit(scaled_bg, (draw_x, draw_y))

        if self.enable_fade:
            fade_overlay = pygame.Surface(scaled_size, pygame.SRCALPHA)
            fade_overlay.fill((*self.fade_color, int(self.fade_alpha)))
            surface.blit(fade_overlay, (draw_x, draw_y))

        if self.icon_image:
            scaled_icon = pygame.transform.smoothscale(self.icon_image, scaled_size)
            surface.blit(scaled_icon, (draw_x, draw_y))

        self._render_text(surface, scaled_size, draw_x, draw_y)

    def handle_event(self, event):
        """Processa eventos de clique no botão."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.click_sound:
                audio_manager.play_sound(self.click_sound)
