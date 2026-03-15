"""
Módulo que armazena a classe responsável por criar e administrar a tela
de criação e seleção de restaurantes, com visual alinhado ao mockup.
"""

import pygame
from math import cos, sin, pi

from settings import Settings
from core.gui.ui_button import UIButton
from core.states.tutorial import Tutorial
from core.assets.player import Player  # Player gerencia múltiplos restaurantes


# -------------------- helpers visuais --------------------

def _load_font_chain(paths, size):
    """Tenta carregar a primeira fonte disponível; se falhar, tenta as próximas."""
    for p in paths:
        try:
            return pygame.font.Font(p, size)
        except Exception:
            continue
    # fallback sistema
    return pygame.font.SysFont("arial", size, bold=True)


def _blur_surface_smooth(src: pygame.Surface, passes: int = 2, scale_step: float = 0.5) -> pygame.Surface:
    """
    Fake blur: reduz a superfície e reescala suavemente algumas vezes.
    Mais passes -> mais blur (e mais custo).
    """
    tmp = src.copy()
    for _ in range(max(1, passes)):
        w, h = tmp.get_size()
        down = pygame.transform.smoothscale(tmp, (max(1, int(w * scale_step)), max(1, int(h * scale_step))))
        tmp = pygame.transform.smoothscale(down, (w, h))
    return tmp


def _draw_star(surf: pygame.Surface, center, r, color=(255, 197, 61), border=(99, 58, 27)):
    """Desenha uma estrela 5 pontas simples."""
    cx, cy = center
    pts = []
    for i in range(10):
        ang = -pi / 2 + i * (pi / 5)
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + cos(ang) * rad, cy + sin(ang) * rad))
    pygame.draw.polygon(surf, color, pts)
    if border:
        pygame.draw.polygon(surf, border, pts, width=2)


def _render_text_outline(text: str, font: pygame.font.Font, fill=(255, 255, 255),
                         outline=(0, 0, 0), px: int = 2) -> pygame.Surface:
    """
    Renderiza texto com contorno (stroke). Desenha várias cópias deslocadas.
    px controla a espessura do contorno.
    """
    text_surf = font.render(text, True, fill)
    if px <= 0:
        return text_surf

    base = font.render(text, True, outline)
    w, h = text_surf.get_size()
    out = pygame.Surface((w + px * 2, h + px * 2), pygame.SRCALPHA)

    offsets = {(dx, dy) for dx in range(-px, px + 1) for dy in range(-px, px + 1)
               if dx * dx + dy * dy <= (px + 0.5) ** 2 and not (dx == 0 and dy == 0)}

    for dx, dy in offsets:
        out.blit(base, (dx + px, dy + px))

    out.blit(text_surf, (px, px))
    return out


# -------------------- Card específico da tela --------------------

class RestaurantCard(UIButton):
    """
    Card para os 3 slots. Herda UIButton (com as animações appear/disappear/hover)
    e desenha conteúdo no estilo do mockup usando um background de card.

    Ajustes:
    - NÃO redimensiona o asset do card (usa tamanho natural);
    - Hover sutil (max_scale baixo);
    - Título do card preenchido ("Meu Restaurante") no MESMO estilo do "Slot vazio"
      (contorno preto + fill semelhante à cor de fundo do card).
    """

    def __init__(
        self, x, y, bg_image, *,
        slot_index: int,
        fonts: dict,
        kind: str = "empty",            # "filled" ou "empty"
        data: dict | None = None,       # dados do restaurante quando "filled"
        hover_sound=None, click_sound=None,
        hover_max: float = 1.06,        # destaque menor que os cards da gameplay
        scale_speed: float = 10.0
    ):
        super().__init__(
            x, y, bg_image,
            icon_image=None,
            text=None,
            font=None,
            text_color=(255, 255, 255),
            enable_scale=True,
            max_scale=hover_max,
            scale_speed=scale_speed,
            hover_sound=hover_sound,
            click_sound=click_sound
        )
        self.slot_index = slot_index
        self.kind = kind
        self.data = data or {}
        self.fonts = fonts  # {"title": Font, "label": Font, "small": Font}
        self.design_size = self.bg_image.get_size()  # tamanho base do card (natural)
        self.appear()  # entra com impacto como os cards da gameplay

        # Cores
        self._info_color = (60, 40, 20)
        # cor do texto do slot vazio e do título preenchido, próxima ao fundo do card (tom amadeirado)
        self._wood_tone = (92, 64, 44)

    # ---------- helpers de layout ----------
    def _metrics(self, scaled_size: tuple[int, int]):
        """Calcula medidas proporcionais ao tamanho ATUAL do card."""
        w, h = scaled_size
        pad = int(min(w, h) * 0.08)  # padding proporcional
        inner = pygame.Rect(pad, pad, w - 2 * pad, h - 2 * pad)
        # escala do conteúdo (quase sempre ~1, já que não redimensionamos o asset; varia no hover)
        _, ch = self.design_size
        content_scale = max(0.85, min(1.25, h / max(1, ch)))

        star_r = int(min(inner.w, inner.h) * 0.065)    # raio das estrelas
        gap = int(inner.h * 0.04)                      # espaçamento vertical
        return inner, content_scale, star_r, gap

    def _render_text_scaled(self, text_surf: pygame.Surface, scale: float) -> pygame.Surface:
        if abs(scale - 1.0) < 0.02:
            return text_surf
        tw, th = text_surf.get_size()
        return pygame.transform.smoothscale(text_surf, (max(1, int(tw * scale)), max(1, int(th * scale))))

    def set_filled(self, data: dict):
        self.kind = "filled"
        self.data = data

    def set_empty(self):
        self.kind = "empty"
        self.data = {}

    def render(self, screen):
        """Desenha o card + conteúdo (nome, dia, dinheiro, estrelas...)."""
        if self.anim_alpha <= 0.01:
            return

        eff_scale = self.anim_scale * self.current_scale
        scaled_size = (int(self.original_size[0] * eff_scale), int(self.original_size[1] * eff_scale))
        draw_x = self.x + self.original_size[0] // 2 - scaled_size[0] // 2
        draw_y = self.y + self.original_size[1] // 2 - scaled_size[1] // 2

        # compõe em surface própria para aplicar alpha global
        composed = pygame.Surface(scaled_size, pygame.SRCALPHA)
        base_image = self.hover_image if (self.hovered and self.hover_image) else self.bg_image
        composed.blit(pygame.transform.smoothscale(base_image, scaled_size), (0, 0))

        inner, content_scale, star_r, gap = self._metrics(scaled_size)

        if self.kind == "filled":
            # TÍTULO no mesmo estilo do "Slot vazio": contorno preto + fill em tom amadeirado
            title_text = self.data.get("name", "Meu Restaurante")
            title_outlined = _render_text_outline(title_text, self.fonts["label"],
                                                  fill=self._wood_tone, outline=(0, 0, 0), px=2)
            title = self._render_text_scaled(title_outlined, content_scale)
            composed.blit(title, (inner.x, inner.y))

            # Estrelas (nível 0..5)
            level = max(0, min(5, int(self.data.get("level", 0))))
            star_y = inner.y + title.get_height() + int(gap * 0.8)
            star_x = inner.x
            for i in range(5):
                c = (255, 197, 61) if i < level else (200, 180, 150)
                _draw_star(composed, (star_x + star_r + i * int(star_r * 2.2), star_y + star_r), star_r, color=c)

            # Infos alinhadas
            line1 = self.fonts["small"].render(f"DIA: {self.data.get('day', 1)}", True, self._info_color)
            money = self.data.get('money', 0.0)
            line2 = self.fonts["small"].render(
                f"DINHEIRO: {money:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                True, self._info_color
            )
            line1 = self._render_text_scaled(line1, content_scale)
            line2 = self._render_text_scaled(line2, content_scale)

            base_y = star_y + star_r * 2 + gap
            composed.blit(line1, (inner.x, base_y))
            composed.blit(line2, (inner.x, base_y + line1.get_height() + int(gap * 0.6)))

        else:
            # Slot vazio — com contorno e cor próxima ao fundo do card
            t1 = _render_text_outline("Slot vazio", self.fonts["label"], fill=self._wood_tone, outline=(0, 0, 0), px=2)
            t2 = self.fonts["small"].render("Clique para criar", True, self._info_color)

            t1 = self._render_text_scaled(t1, content_scale)
            t2 = self._render_text_scaled(t2, content_scale)

            composed.blit(t1, t1.get_rect(center=(scaled_size[0] // 2, scaled_size[1] // 2 - int(gap * 0.4))))
            composed.blit(t2, t2.get_rect(center=(scaled_size[0] // 2, scaled_size[1] // 2 + int(gap * 0.9))))

        if self.anim_alpha < 1.0:
            composed.set_alpha(int(255 * self.anim_alpha))
        screen.blit(composed, (draw_x, draw_y))


# -------------------- Tela --------------------

class RestaurantSelect:
    """Tela de seleção/criação de restaurantes com 3 slots e formulário de criação."""

    def __init__(self, game):
        self.game = game
        self.config = Settings()
        self.mode = "select"
        self.selected_slot = None

        # --------- fontes (mockup) ----------
        self.title_font = _load_font_chain(
            ['fonts/LuckiestGuy-Regular.ttf'], 46
        )
        # textos: Baloo 2 (ou Fredoka One) → fallback para LuckiestGuy
        self.label_font = _load_font_chain(
            ['fonts/Baloo2-Bold.ttf', 'fonts/FredokaOne-Regular.ttf', 'fonts/LuckiestGuy-Regular.ttf'], 28
        )
        self.small_font = _load_font_chain(
            ['fonts/Baloo2-SemiBold.ttf', 'fonts/FredokaOne-Regular.ttf', 'fonts/LuckiestGuy-Regular.ttf'], 22
        )
        self.fonts = {"title": self.title_font, "label": self.label_font, "small": self.small_font}

        # --------- imagens/skins ----------
        self.bg_raw = pygame.image.load('graphics/backgrounds/restaurant_select_bg.png').convert()
        self.bg_image = pygame.transform.scale(self.bg_raw, (self.config.SCREEN['width'], self.config.SCREEN['height']))
        self.bg_blurred = _blur_surface_smooth(self.bg_image, passes=3, scale_step=0.45)

        self.dark_overlay = pygame.Surface((self.config.SCREEN['width'], self.config.SCREEN['height']), pygame.SRCALPHA)
        self.dark_overlay.fill((0, 0, 0, 85))  # escurece levemente

        self.title_bg = pygame.image.load('graphics/sprites/screen_title_bg.png').convert_alpha()
        self.card_bg = pygame.image.load('graphics/sprites/restaurant_select_card.png').convert_alpha()

        # back button (ícone opcional)
        try:
            self.back_icon = pygame.image.load('graphics/sprites/back_icon.png').convert_alpha()
        except Exception:
            self.back_icon = None  # desenha seta vetorial se não houver asset

        # cursor customizado
        self.cursor_image = pygame.image.load(self.config.MOUSE['image']).convert_alpha()
        pygame.mouse.set_visible(False)

        # --------- layout ----------
        W, H = self.config.SCREEN['width'], self.config.SCREEN['height']

        # título central em madeira
        self.title_rect = self.title_bg.get_rect()
        self.title_rect.midtop = (W // 2, 16)

        # ícone voltar
        self.back_rect = pygame.Rect(20, 20, 48, 48)

        # cards (3 slots) — centralizados horizontalmente (SEM redimensionar asset) e mais abaixo
        card_w, card_h = self.card_bg.get_size()
        gap = int(card_w * 0.18)
        total_w = 3 * card_w + 2 * gap
        left = (W - total_w) // 2
        top = H // 2 - card_h // 2 + 64  # desce os cards

        # cria os 3 cards (hover sutil, sem reescalar base)
        self.cards = []
        for i in range(3):
            cx, cy = left + i * (card_w + gap), top
            card = RestaurantCard(
                cx, cy, self.card_bg,
                slot_index=i,
                fonts=self.fonts,
                hover_max=1.06,
                scale_speed=10.0
            )
            self.cards.append(card)

        # --------- formulário (modo create) – mantido como está ---------
        form_w, form_h = 740, 300
        self.form_rect = pygame.Rect(
            (W - form_w) // 2, (H - form_h) // 2 + 10, form_w, form_h
        )
        self.inputs = {
            "player_name": {
                "label": "Nome do Jogador", "text": "",
                "rect": pygame.Rect(self.form_rect.x + 24, self.form_rect.y + 70, 420, 44)
            },
            "restaurant_name": {
                "label": "Nome do Restaurante", "text": "",
                "rect": pygame.Rect(self.form_rect.x + 24, self.form_rect.y + 150, 420, 44)
            },
        }
        self.active_input_key = None

        self.difficulties = ["Fácil", "Médio", "Difícil"]
        self.diff_index = 0
        diff_y = self.form_rect.y + 220
        diff_x = self.form_rect.x + 24
        self.diff_rects = [pygame.Rect(diff_x + i * (120 + 16), diff_y, 120, 42) for i in range(3)]

        btn_img_small = pygame.image.load('graphics/sprites/menu_button_1.png').convert_alpha()
        self.btn_create = UIButton(self.form_rect.centerx, self.form_rect.bottom + 46, btn_img_small,
                                   text="Criar", font=self.small_font)
        self.btn_cancel = UIButton(self.form_rect.centerx - 200, self.form_rect.bottom + 46, btn_img_small,
                                   text="Cancelar", font=self.small_font)

    # ---------- helpers de dados ----------
    def _ensure_player(self):
        if not hasattr(self.game, "player") or self.game.player is None:
            self.game.player = Player(nickname="Player", restaurant_name="Meu Restaurante")
            if self.inputs["player_name"]["text"]:
                self.game.player.nickname = self.inputs["player_name"]["text"]
            if self.inputs["restaurant_name"]["text"] and self.game.player.restaurants:
                self.game.player.restaurants[0].name = self.inputs["restaurant_name"]["text"]

    def _player(self):
        return getattr(self.game, "player", None)

    def _restaurants(self):
        p = self._player()
        return p.restaurants if p else []

    def _active_restaurant_id(self):
        p = self._player()
        return p.active_restaurant_id if p else None

    def _switch_active(self, restaurant_id):
        p = self._player()
        if p:
            p.switch_restaurant(restaurant_id)

    def _create_restaurant_from_form(self):
        nickname = self.inputs["player_name"]["text"].strip() or "Player"
        rname = self.inputs["restaurant_name"]["text"].strip() or "Meu Restaurante"
        difficulty = self.difficulties[self.diff_index]

        if not self._player():
            self.game.player = Player(nickname=nickname, restaurant_name=rname)
            new_restaurant = self.game.player.get_active_restaurant()
        else:
            self._player().nickname = nickname
            self._player().add_restaurant(rname)
            new_restaurant = self._player().get_active_restaurant()

        setattr(new_restaurant, "difficulty", difficulty)
        # opcional: inicializar nível/estrelas se não houver
        if not hasattr(new_restaurant, "level"):
            setattr(new_restaurant, "level", 1)

        self.mode = "select"
        self.selected_slot = None

    # ---------- ciclo ----------
    def update(self, dt):
        if self.mode == "select":
            for c in self.cards:
                c.update(dt)
        else:
            self.btn_create.update(dt)
            self.btn_cancel.update(dt)

    def render(self, screen):
        # fundo com blur + overlay escuro
        screen.blit(self.bg_blurred, (0, 0))
        screen.blit(self.dark_overlay, (0, 0))

        # título em madeira + texto centralizado com contorno
        screen.blit(self.title_bg, self.title_rect)
        title_text = "SELECIONAR RESTAURANTE"
        title_surf = _render_text_outline(title_text, self.title_font, fill=(255, 240, 220), outline=(0, 0, 0), px=3)
        title_rect = title_surf.get_rect(center=self.title_rect.center)  # centraliza dentro da madeira
        screen.blit(title_surf, title_rect)

        # botão/ícone de voltar
        if self.back_icon:
            screen.blit(self.back_icon, self.back_rect.topleft)
        else:
            # seta vetorial (fallback)
            pygame.draw.circle(screen, (75, 49, 31), self.back_rect.center, 24)
            p = [(self.back_rect.centerx + 6, self.back_rect.centery - 12),
                 (self.back_rect.centerx - 8, self.back_rect.centery),
                 (self.back_rect.centerx + 6, self.back_rect.centery + 12)]
            pygame.draw.polygon(screen, (255, 230, 200), p)

        if self.mode == "select":
            self._render_slots(screen)
        else:
            self._render_form(screen)

        # cursor
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.cursor_image, mouse_pos)

    def _render_slots(self, screen):
        """Preenche cada card com dados do player e renderiza."""
        restaurants = self._restaurants()

        for i, card in enumerate(self.cards):
            if i < len(restaurants):
                r = restaurants[i]
                data = {
                    "name": r.name,
                    "day": getattr(r, "day", 1),
                    "money": getattr(r, "money", 0.0),
                    "level": getattr(r, "level", getattr(r, "rating", 0))  # aceita level ou rating
                }
                card.set_filled(data)
            else:
                card.set_empty()
            card.render(screen)

    def _render_form(self, screen):
        # caixa base
        pygame.draw.rect(screen, (230, 200, 160), self.form_rect, border_radius=16)
        pygame.draw.rect(screen, (120, 85, 50), self.form_rect, width=3, border_radius=16)

        title = self.label_font.render("CRIAR NOVO RESTAURANTE", True, (60, 40, 20))
        screen.blit(title, (self.form_rect.x + 24, self.form_rect.y + 20))

        # inputs
        for key in ("player_name", "restaurant_name"):
            data = self.inputs[key]
            lbl = self.small_font.render(data["label"], True, (60, 40, 20))
            screen.blit(lbl, (data["rect"].x, data["rect"].y - 26))
            focused = (self.active_input_key == key)
            pygame.draw.rect(screen, (255, 240, 210), data["rect"], border_radius=10)
            pygame.draw.rect(screen, (120, 85, 50), data["rect"], width=3 if focused else 2, border_radius=10)
            text = self.small_font.render(data["text"], True, (60, 40, 20))
            screen.blit(text, (data["rect"].x + 10, data["rect"].y + 8))

        # dificuldade
        diff_lbl = self.small_font.render("Nível de Jogo", True, (60, 40, 20))
        screen.blit(diff_lbl, (self.form_rect.x + 24, self.form_rect.y + 190))
        for i, r in enumerate(self.diff_rects):
            selected = (i == self.diff_index)
            pygame.draw.rect(screen, (245, 225, 190), r, border_radius=10)
            pygame.draw.rect(screen, (120, 85, 50), r, width=3 if selected else 2, border_radius=10)
            t = self.small_font.render(self.difficulties[i], True, (60, 40, 20))
            screen.blit(t, t.get_rect(center=r.center))

        self.btn_cancel.render(screen)
        self.btn_create.render(screen)

    # ---------- input ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # back
            if self.back_rect.collidepoint((mx, my)) and self.mode == "select":
                # volta para a tela inicial (state do seu menu principal)
                if hasattr(self.game, "go_to_main_menu"):
                    self.game.go_to_main_menu()
                return

            if self.mode == "select":
                # detecção por rect do botão (pós-escala)
                for idx, card in enumerate(self.cards):
                    if card.rect.collidepoint((mx, my)):
                        p = self._player()
                        if p and idx < len(p.restaurants):
                            # Slot ocupado: selecionar e seguir
                            self._switch_active(p.restaurants[idx].restaurant_id)
                            self.game.change_state(Tutorial(self.game))
                        else:
                            # Slot vazio: abrir formulário
                            self.mode = "create"
                            self.selected_slot = idx
                            if not self.inputs["player_name"]["text"]:
                                self.inputs["player_name"]["text"] = "Player"
                            if not self.inputs["restaurant_name"]["text"]:
                                self.inputs["restaurant_name"]["text"] = f"Restaurante {idx + 1}"
                        # Som de clique do botão (reaproveita UIButton)
                        card.handle_event(event)
                        return

            elif self.mode == "create":
                # focos
                for key in ("player_name", "restaurant_name"):
                    if self.inputs[key]["rect"].collidepoint((mx, my)):
                        self.active_input_key = key
                        break
                else:
                    self.active_input_key = None

                # dificuldade
                for i, r in enumerate(self.diff_rects):
                    if r.collidepoint((mx, my)):
                        self.diff_index = i
                        break

                # botões
                if self.btn_cancel.rect.collidepoint((mx, my)):
                    self.mode = "select"
                    self.selected_slot = None
                    return

                if self.btn_create.rect.collidepoint((mx, my)):
                    self._ensure_player()
                    self._create_restaurant_from_form()
                    return

        # digitação do formulário
        if self.mode == "create" and event.type == pygame.KEYDOWN and self.active_input_key:
            text = self.inputs[self.active_input_key]["text"]
            if event.key == pygame.K_BACKSPACE:
                self.inputs[self.active_input_key]["text"] = text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.active_input_key == "player_name":
                    self.active_input_key = "restaurant_name"
                else:
                    self.active_input_key = None
            else:
                if len(text) < 24:
                    self.inputs[self.active_input_key]["text"] = text + event.unicode
