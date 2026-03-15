# assets/patience_meter.py
import math
import pygame
from typing import Tuple
from core.effects.animations import AnimatedObject, Tween, Sequence, lerp, ease_out_back, ease_out_sine, ease_in_cubic


class PatienceMeter(AnimatedObject):
    """
    Barra semicircular de paciência com contorno grosso uniforme e animações de surgimento/saída.
    Todo o desenho (cores/geom/AA) é interno a esta classe.
    """

    def __init__(
        self,
        center: Tuple[int, int],
        radius: float = 44,
        thickness: float = 10,
        aperture_deg: float = 100,
        outline_width_px: int = 2,
        upscale: int = 2
    ):
        super().__init__()
        # Config base
        self.center = center
        self.base_radius = float(radius)
        self.base_thickness = float(thickness)
        self.aperture_deg = float(aperture_deg)
        self.outline_width_px = int(outline_width_px)
        self.upscale = int(upscale)

        # Estado dinâmico
        self.ratio = 0.0
        self.scale = 0.01
        self.alpha = 0.0
        self.visible = False

        # Cores
        self._track_color = (210, 210, 210, 255)
        self._outline_color = (0, 0, 0, 255)

        # Animações prontas
        self._build_appear_timeline()
        self._build_disappear_timeline()

    # ----------------------
    # API pública
    # ----------------------
    def set_ratio(self, r: float):
        self.ratio = max(0.0, min(1.0, float(r)))

    def appear(self):
        self.visible = True
        self.play("appear", restart=True)

    def disappear(self):
        self.play("disappear", restart=True)

    def is_visible(self) -> bool:
        return self.visible and (self.alpha > 0.01)

    def update(self, dt: float):
        self.update_animations(dt)
        if not self.is_playing() and self.alpha <= 0.01:
            self.visible = False

    def draw(self, screen: pygame.Surface):
        if not self.is_visible():
            return
        self._draw_semicircle_meter(
            screen,
            center=self.center,
            radius=self.base_radius,
            thickness=self.base_thickness,
            ratio=self.ratio,
            aperture_deg=self.aperture_deg,
            outline_width_px=self.outline_width_px,
            upscale=self.upscale,
            scale=self.scale,
            alpha=self.alpha
        )

    # ----------------------
    # Timelines (animações)
    # ----------------------
    def _build_appear_timeline(self):
        # Fase A: 0.75 → 1.08 (impacto) e alpha 0 → 1
        dur_a = 0.22
        def on_update_a(t):
            self.scale = lerp(0.75, 1.08, t)
            self.alpha = lerp(0.0, 1.0, t)
        tw_a = Tween(duration=dur_a, easing=lambda x: ease_out_back(x, 1.5), on_update=on_update_a)

        # Fase B: 1.08 → 1.00 (assentar)
        dur_b = 0.12
        def on_update_b(t):
            self.scale = lerp(1.08, 1.00, t)
        tw_b = Tween(duration=dur_b, easing=ease_out_sine, on_update=on_update_b)

        self.add_timeline("appear", Sequence([tw_a, tw_b], loop=False))

    def _build_disappear_timeline(self):
        # Fase A: 1.00 → 1.08 com leve queda de alpha
        dur_a = 0.10
        def on_update_a(t):
            self.scale = lerp(1.00, 1.08, t)
            self.alpha = lerp(1.0, 0.8, t)
        tw_a = Tween(duration=dur_a, easing=ease_out_sine, on_update=on_update_a)

        # Fase B: 1.08 → 0.80 e alpha 0.8 → 0.0
        dur_b = 0.18
        def on_update_b(t):
            self.scale = lerp(1.08, 0.80, t)
            self.alpha = lerp(0.8, 0.0, t)
        tw_b = Tween(duration=dur_b, easing=ease_in_cubic, on_update=on_update_b)

        self.add_timeline("disappear", Sequence([tw_a, tw_b], loop=False))

    # ----------------------
    # Desenho interno
    # ----------------------
    @staticmethod
    def _lerp_color(a, b, t):
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    def _multi_lerp_color(self, ratio: float):
        """
        Gradiente multi-parada:
          1.0 → verde, 0.6 → amarelo, 0.3 → laranja, 0.1 → vermelho.
        """
        stops = [
            (1.0, ( 60, 185,  70)),  # verde
            (0.6, (230, 210,  70)),  # amarelo
            (0.3, (230, 140,  60)),  # laranja
            (0.1, (200,  60,  50)),  # vermelho
        ]
        r = max(0.0, min(1.0, float(ratio)))
        for i in range(len(stops) - 1):
            a_t, a_c = stops[i]
            b_t, b_c = stops[i + 1]
            if b_t <= r <= a_t:
                t = 0.0 if a_t == b_t else (a_t - r) / (a_t - b_t)
                return self._lerp_color(a_c, b_c, t)
        return stops[-1][1]

    @staticmethod
    def _arc_points(rect: pygame.Rect, start: float, stop: float, r: float, samples: int = 64):
        cx = rect.centerx
        cy = rect.centery
        for i in range(samples + 1):
            t = i / samples
            a = start + (stop - start) * t
            yield (cx + math.cos(a) * r, cy - math.sin(a) * r)

    def _draw_ring_sector(
        self,
        surf: pygame.Surface,
        rect: pygame.Rect,
        start: float,
        stop: float,
        outer_r: float,
        thickness: float,
        color
    ):
        inner_r = max(1, outer_r - thickness)
        outer_pts = list(self._arc_points(rect, start, stop, outer_r, samples=84))
        inner_pts = list(self._arc_points(rect, stop, start, inner_r, samples=84))  # volta fechando
        pts = outer_pts + inner_pts
        pygame.draw.polygon(surf, color, pts)

    def _aa_arc(self, surf, rect, start, stop, r, color, samples=120):
        pts = list(self._arc_points(rect, start, stop, r, samples=samples))
        if len(pts) >= 2:
            pygame.draw.aalines(surf, color, False, pts)

    def _draw_semicircle_meter(
        self,
        surface: pygame.Surface,
        center: Tuple[int, int],
        radius: float,
        thickness: float,
        ratio: float,
        aperture_deg: float,
        outline_width_px: int,
        upscale: int,
        scale: float,
        alpha: float
    ):
        # Sanitização
        radius = max(1e-3, float(radius))
        thickness = max(1e-3, float(thickness))
        ratio = max(0.0, min(1.0, float(ratio)))
        aperture_deg = max(1e-3, float(aperture_deg))
        scale = max(0.01, float(scale))
        alpha = max(0.0, min(1.0, float(alpha)))
        outline_width_px = max(0, int(outline_width_px))
        upscale = max(1, int(upscale))

        cx, cy = center

        # Parâmetros em alta resolução COM scale
        base_r = radius * scale
        base_th = thickness * scale

        up_r   = int(base_r   * upscale)
        up_th  = int(base_th  * upscale)
        out_px = max(1, int(outline_width_px * upscale))

        # Raio total considerando contorno
        outer_total_r = up_r + out_px

        # Margem de segurança
        pad = max(8, out_px + 4)
        size = outer_total_r * 2 + pad

        tmp  = pygame.Surface((size, size), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, size, size).inflate(-pad // 2, -pad // 2)

        # Ângulos — arco superior central (∩)
        span  = math.radians(aperture_deg)
        mid   = math.pi * 0.5
        start = mid - span * 0.5
        stop  = mid + span * 0.5

        # 1) Contorno uniforme (anel maior)
        self._draw_ring_sector(
            tmp, rect, start, stop,
            outer_r=outer_total_r,
            thickness=up_th + 2*out_px,
            color=self._outline_color
        )

        # 1.1) Caps laterais para reforçar espessura nas extremidades
        cap_ang = max(out_px / max(1.0, float(up_r)), math.radians(1.0))
        self._draw_ring_sector(
            tmp, rect, start - cap_ang, start + cap_ang,
            outer_r=outer_total_r,
            thickness=up_th + 2*out_px,
            color=self._outline_color
        )
        self._draw_ring_sector(
            tmp, rect, stop - cap_ang, stop + cap_ang,
            outer_r=outer_total_r,
            thickness=up_th + 2*out_px,
            color=self._outline_color
        )

        # 2) Trilho (fundo)
        self._draw_ring_sector(tmp, rect, start, stop, up_r, up_th, self._track_color)

        # 3) Barra preenchida
        if ratio > 0.0:
            cur = start + (stop - start) * ratio
            col = self._multi_lerp_color(ratio)
            self._draw_ring_sector(tmp, rect, start, cur, up_r, up_th, col)

        # 4) Definição sutil nas bordas do trilho
        self._aa_arc(tmp, rect, start, stop, up_r,         (0, 0, 0, 50))
        self._aa_arc(tmp, rect, start, stop, up_r - up_th, (0, 0, 0, 50))

        # 5) Reduz e aplica alpha
        scaled_w = int(rect.width  / upscale) + (pad // upscale)
        scaled_h = int(rect.height / upscale) + (pad // upscale)
        final    = pygame.transform.smoothscale(tmp, (scaled_w, scaled_h))

        if alpha < 1.0:
            final.set_alpha(int(255 * alpha))

        surface.blit(final, (cx - (final.get_width() // 2), cy - (final.get_height() // 2)))
