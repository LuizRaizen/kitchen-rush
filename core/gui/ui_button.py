# core/gui/ui_button.py
import pygame
from utils.audio_manager import audio_manager

# +++ IMPORTANTE: importe o sistema de animação + easings
from core.effects.animations import (
    AnimatedObject,
    Tween,
    Sequence,
    lerp,
    ease_out_back,
    ease_out_sine,
    ease_in_cubic,
)


class UIButton(AnimatedObject):
    """
    Componente de interface gráfica que representa um botão visual completo e interativo.

    Recursos incluídos:
    - Animação de escala ao passar o mouse (LERP)
    - Efeito de clareamento com fade (opcional)
    - Troca de imagem ao passar o mouse (hover_image)
    - Ícone opcional
    - Texto com alinhamento e padding configuráveis
    - Sons de hover e clique

    Adições:
    - Animações de surgir/sumir (scale+alpha) usando AnimatedObject
    - Estado 'active' (efeito rádio): quando ativo, usa a MESMA escala do hover
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
        text_align="center",
        text_padding=0,
    ):
        super().__init__()  # <-- inicializa AnimatedObject

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

        # Hover scale (comportamento antigo, preservado)
        self.enable_scale = enable_scale
        self.max_scale = max_scale
        self.scale_speed = scale_speed
        self._hover_target = 1.0  # alvo só do hover/ativo
        self.current_scale = 1.0  # escala efetiva final = anim_scale * hover blend
        self.target_scale = 1.0   # (não usamos mais diretamente; mantido p/ compat)

        # Novo: escala/alpha da ANIMAÇÃO (appear/disappear)
        self.anim_scale = 1.0     # base animável que multiplica o hover
        self.anim_alpha = 1.0     # alpha global do botão
        self._visible_flag = True # estado lógico de visibilidade (alpha>0 => visível)

        # Fade (iluminar ao hover — recurso antigo, preservado)
        self.enable_fade = enable_fade
        self.fade_color = fade_color
        self.fade_speed = fade_speed
        self.fade_max_alpha = fade_max_alpha
        self.fade_alpha = 0

        # Estado de interação
        self.hovered = False
        self.was_hovering = False

        # --- NOVO: estado ativo (efeito "rádio") ---
        self.active = False

        # Áudio
        self.hover_sound = hover_sound
        self.click_sound = click_sound

        # Timelines de animação
        self._build_appear_timeline()
        self._build_disappear_timeline()

    # -------------------------------------------------
    # API de estado ativo (rádio)
    # -------------------------------------------------
    def set_active(self, value: bool) -> None:
        """Define se o botão está ativo (mantém escala de hover)."""
        self.active = bool(value)

    def is_active(self) -> bool:
        return self.active

    # -------------------------------------------------
    # ANIMAÇÕES (timelines)
    # -------------------------------------------------
    def _build_appear_timeline(self):
        # Fase A: 0.75 -> 1.08 com alpha 0 -> 1 (impacto)
        dur_a = 0.22

        def on_update_a(t):
            self.anim_scale = lerp(0.75, 1.08, t)
            self.anim_alpha = lerp(0.0, 1.0, t)

        tw_a = Tween(duration=dur_a, easing=lambda x: ease_out_back(x, 1.5), on_update=on_update_a)

        # Fase B: 1.08 -> 1.00 (assenta)
        dur_b = 0.12

        def on_update_b(t):
            self.anim_scale = lerp(1.08, 1.00, t)

        tw_b = Tween(duration=dur_b, easing=ease_out_sine, on_update=on_update_b)

        self.add_timeline("appear", Sequence([tw_a, tw_b], loop=False))

    def _build_disappear_timeline(self):
        # Fase A: 1.00 -> 1.08 (estalo) com leve queda de alpha
        dur_a = 0.10

        def on_update_a(t):
            self.anim_scale = lerp(1.00, 1.08, t)
            self.anim_alpha = lerp(1.0, 0.8, t)

        tw_a = Tween(duration=dur_a, easing=ease_out_sine, on_update=on_update_a)

        # Fase B: 1.08 -> 0.80 e alpha 0.8 -> 0
        dur_b = 0.18

        def on_update_b(t):
            self.anim_scale = lerp(1.08, 0.80, t)
            self.anim_alpha = lerp(0.8, 0.0, t)

        tw_b = Tween(duration=dur_b, easing=ease_in_cubic, on_update=on_update_b)

        seq = Sequence([tw_a, tw_b], loop=False)
        self.add_timeline("disappear", seq)

    # API pública de animação
    def appear(self):
        self._visible_flag = True
        # começa invisível/preparado
        self.anim_scale = 0.75
        self.anim_alpha = 0.0
        self.play("appear", restart=True)

    def disappear(self):
        # só dispara se estiver visível
        if self._visible_flag or self.anim_alpha > 0.01:
            self.play("disappear", restart=True)

    def is_visible(self):
        return self._visible_flag and (self.anim_alpha > 0.01)

    # -------------------------------------------------
    # LÓGICA ORIGINAL (com pequenas adaptações)
    # -------------------------------------------------
    def get_scaled_rect(self):
        """Retorna o retângulo atual com base na escala animada *e* hover/ativo."""
        eff_scale = self.anim_scale * self.current_scale
        width = int(self.original_size[0] * eff_scale)
        height = int(self.original_size[1] * eff_scale)
        draw_x = self.x + self.original_size[0] // 2 - width // 2
        draw_y = self.y + self.original_size[1] // 2 - height // 2
        return pygame.Rect(draw_x, draw_y, width, height)

    def update(self, dt):
        """Atualiza animações (appear/disappear) e efeitos de hover/scale/fade."""
        # 1) Animações (timelines) SEMPRE rodam
        self.update_animations(dt)

        # Se alguma timeline terminou e alpha ~0, marca invisível
        if not self.is_playing() and self.anim_alpha <= 0.01:
            self._visible_flag = False

        # 2) Interação
        interactive = getattr(self, "_interactive", True) and (self.anim_alpha >= 0.05)

        if interactive:
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.fixed_rect.collidepoint(mouse_pos)
            self.hovered = is_hovering

            if is_hovering and not self.was_hovering and self.hover_sound:
                audio_manager.play_sound(self.hover_sound)

            # --- alvo de escala: hover OU ativo (efeito rádio) ---
            if self.enable_scale:
                self._hover_target = self.max_scale if (is_hovering or self.active) else 1.0
            else:
                # mesmo sem hover-scale habilitado, respeita ativo
                self._hover_target = self.max_scale if self.active else 1.0

            # fade de brilho (hover)
            if self.enable_fade:
                target_alpha = self.fade_max_alpha if is_hovering else 0
                diff = target_alpha - self.fade_alpha
                self.fade_alpha += diff * min(self.fade_speed * dt, 1)
                self.fade_alpha = max(0, min(255, self.fade_alpha))

            self.was_hovering = is_hovering
        else:
            # Interação desligada: sem hover, mas mantém estado ativo
            self.hovered = False
            self._hover_target = self.max_scale if (self.active and self.enable_scale) else 1.0
            self.was_hovering = False

        # 3) Corrente de hover/ativo suavizada
        self.current_scale += (self._hover_target - self.current_scale) * min(self.scale_speed * dt, 1.0)

        # 4) Atualiza rect a partir da escala composta (anim_scale * hover/ativo)
        self.rect = self.get_scaled_rect()
        self.fixed_rect = self.rect.copy()

    def update_position(self, offset_x=0, offset_y=0):
        """
        Atualiza a posição do botão com base na escala e deslocamento da superfície pai.
        Útil em listas com rolagem e popups.
        """
        eff_scale = self.anim_scale * self.current_scale
        scaled_size = (int(self.original_size[0] * eff_scale), int(self.original_size[1] * eff_scale))
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2 + offset_x
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2 + offset_y
        self.fixed_rect = pygame.Rect(draw_x, draw_y, *scaled_size)
        self.rect = self.fixed_rect.copy()

    def _render_text(self, screen, scaled_size, draw_x, draw_y):
        """Renderiza o texto com alinhamento e padding definidos."""
        if not self.text or not self.font:
            return

        eff_scale = self.anim_scale * self.current_scale
        text_surface = self.font.render(self.text, True, self.text_color)
        original_size = text_surface.get_size()

        scaled_text = pygame.transform.smoothscale(
            text_surface,
            (int(original_size[0] * eff_scale), int(original_size[1] * eff_scale)),
        )
        text_rect = scaled_text.get_rect()

        if self.text_align == "center":
            text_rect.center = (draw_x + scaled_size[0] // 2, draw_y + scaled_size[1] // 2)
        elif self.text_align == "left":
            text_rect.midleft = (draw_x + self.text_padding, draw_y + scaled_size[1] // 2)
        elif self.text_align == "right":
            text_rect.midright = (draw_x + scaled_size[0] - self.text_padding, draw_y + scaled_size[1] // 2)
        elif self.text_align == "top":
            text_rect.midtop = (draw_x + scaled_size[0] // 2, draw_y + self.text_padding)
        elif self.text_align == "bottom":
            text_rect.midbottom = (draw_x + scaled_size[0] // 2, draw_y + scaled_size[1] - self.text_padding)

        screen.blit(scaled_text, text_rect)

    # --- render helpers ---
    def _compose_to_surface(self):
        """
        Monta o botão em uma surface temporária (do tamanho escalado),
        permitindo aplicar alpha global (anim_alpha) no fim.
        """
        eff_scale = self.anim_scale * self.current_scale
        scaled_size = (int(self.original_size[0] * eff_scale), int(self.original_size[1] * eff_scale))
        surface = pygame.Surface(scaled_size, pygame.SRCALPHA)

        base_image = self.hover_image if (self.hovered and self.hover_image) else self.bg_image
        scaled_bg = pygame.transform.smoothscale(base_image, scaled_size)
        surface.blit(scaled_bg, (0, 0))

        if self.enable_fade and self.fade_alpha > 0:
            fade_overlay = pygame.Surface(scaled_size, pygame.SRCALPHA)
            fade_overlay.fill((*self.fade_color, int(self.fade_alpha)))
            surface.blit(fade_overlay, (0, 0))

        if self.icon_image:
            scaled_icon = pygame.transform.smoothscale(self.icon_image, scaled_size)
            surface.blit(scaled_icon, (0, 0))

        # texto no topo (centralizado por padrão)
        if self.text and self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            ts = text_surface.get_size()
            scaled_text = pygame.transform.smoothscale(
                text_surface, (int(ts[0] * eff_scale), int(ts[1] * eff_scale))
            )
            text_rect = scaled_text.get_rect(center=(scaled_size[0] // 2, scaled_size[1] // 2))

            if self.text_align == "left":
                text_rect.midleft = (self.text_padding, scaled_size[1] // 2)
            elif self.text_align == "right":
                text_rect.midright = (scaled_size[0] - self.text_padding, scaled_size[1] // 2)
            elif self.text_align == "top":
                text_rect.midtop = (scaled_size[0] // 2, self.text_padding)
            elif self.text_align == "bottom":
                text_rect.midbottom = (scaled_size[0] // 2, scaled_size[1] - self.text_padding)

            surface.blit(scaled_text, text_rect)

        return surface

    def render(self, screen):
        """Renderiza o botão na posição padrão (com animação global de alpha)."""
        self._render_with_offset(screen, y_offset=0)

    def render_at(self, screen, y_offset=0):
        """Renderiza o botão com deslocamento vertical (útil para popups)."""
        self._render_with_offset(screen, y_offset)

    def _render_with_offset(self, screen, y_offset):
        """Renderiza com efeitos e deslocamento."""
        if self.anim_alpha <= 0.01:
            return  # totalmente transparente

        eff_scale = self.anim_scale * self.current_scale
        scaled_size = (int(self.original_size[0] * eff_scale), int(self.original_size[1] * eff_scale))
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2 + y_offset

        composed = self._compose_to_surface()
        if self.anim_alpha < 1.0:
            composed.set_alpha(int(255 * self.anim_alpha))

        screen.blit(composed, (draw_x, draw_y))

    def render_on_surface(self, surface, offset_x=0, offset_y=0):
        """Renderiza o botão sobre uma superfície externa, como listas ou painéis."""
        if self.anim_alpha <= 0.01:
            return

        eff_scale = self.anim_scale * self.current_scale
        scaled_size = (int(self.original_size[0] * eff_scale), int(self.original_size[1] * eff_scale))
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2 + offset_x
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2 + offset_y

        composed = self._compose_to_surface()
        if self.anim_alpha < 1.0:
            composed.set_alpha(int(255 * self.anim_alpha))

        surface.blit(composed, (draw_x, draw_y))

    def handle_event(self, event):
        """Processa eventos de clique no botão."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.click_sound:
                audio_manager.play_sound(self.click_sound)
