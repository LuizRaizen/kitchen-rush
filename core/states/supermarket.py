"""
Módulo supermarket.

Tela do supermercado:
- Lista de ingredientes (uma coluna) com ícone, nome, preço e controles [-][qty][+]
- Preview à direita (imagem grande + descrição + preço)
- Rodapé com Total (soma dinâmica) e Dinheiro (do restaurante ativo)
- Botão COMPRAR que debita do restaurante ativo e adiciona ao estoque

Refatorado para manter estética e layout compatíveis com a tela de Cardápio:
- Mesma paleta de cores e tipografia
- Zonas de layout espelhando o cardápio (lista à esquerda, preview e descrição à direita)
- Scrollbar e espaçamentos alinhados
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from settings import Settings
from core.effects.animated_popup import AnimatedPopup
from core.gui.ui_button import UIButton
from core.gui.ui_scrollbar import UIScrollbar
from utils.functions import render_text_with_outline


Color = Tuple[int, int, int]


# ---------- util: quebra de linha simples ----------
def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Quebra de linha ingênua baseada na largura do texto renderizado."""
    lines, line = [], ""
    for w in text.split():
        t = (line + " " + w).strip()
        if font.size(t)[0] <= max_width:
            line = t
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


class IngredientCard:
    """Carta de ingrediente (ícone à esquerda, infos e controles à direita)."""

    # Estética alinhada ao Cardápio
    COLOR_TEXT_MAIN: Color = (90, 60, 40)
    COLOR_TEXT_SUB: Color = (90, 60, 40)
    COLOR_BOX: Color = (230, 200, 160)
    COLOR_BOX_DARK: Color = (160, 120, 80)
    COLOR_BTN: Color = (205, 170, 130)
    COLOR_BTN_DARK: Color = (150, 115, 80)

    def __init__(
        self,
        x: int,
        y: int,
        bg_image: pygame.Surface,
        icon_image: pygame.Surface,
        name: str,
        price: float,
        name_font: pygame.font.Font,
        price_font: pygame.font.Font,
    ) -> None:
        self.x = x
        self.y = y
        self.bg_image = bg_image
        self.icon_image = icon_image
        self.name = name
        self.price = float(price)
        self.quantity = 0

        self.name_font = name_font
        self.price_font = price_font

        self.original_size = bg_image.get_size()
        self.rect = pygame.Rect(x, y, *self.original_size)

        # rects interativos (coords locais da list_surface)
        self.minus_rect = pygame.Rect(0, 0, 0, 0)
        self.plus_rect = pygame.Rect(0, 0, 0, 0)
        self.draw_rect = pygame.Rect(0, 0, *self.original_size)

        # layout interno
        self.pad = 10
        self.gap_x = 10
        self.ctrl_w = 140
        self.ctrl_h = 40

    def update_position(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    @staticmethod
    def _fmt_price(v: float) -> str:
        return f"Preço: {v:.2f}".replace(".", ",")

    def draw(self, surface: pygame.Surface, scroll_offset: int = 0) -> None:
        draw_x = self.x
        draw_y = self.y - scroll_offset

        # BG do card
        surface.blit(self.bg_image, (draw_x, draw_y))

        # Ícone centralizado no BG
        bg_w, bg_h = self.bg_image.get_size()
        icon_w, icon_h = self.icon_image.get_size()
        icon_x = draw_x + (bg_w - icon_w) // 2
        icon_y = draw_y + (bg_h - icon_h) // 2
        surface.blit(self.icon_image, (icon_x, icon_y))

        # Infos à direita do BG
        text_start_x = draw_x + self.original_size[0] + self.gap_x
        text_area_top = draw_y + self.pad

        name_surf = self.name_font.render(self.name, True, self.COLOR_TEXT_MAIN)
        surface.blit(name_surf, (text_start_x, text_area_top))

        price_surf = self.price_font.render(
            self._fmt_price(self.price), True, self.COLOR_TEXT_SUB
        )
        surface.blit(
            price_surf, (text_start_x, text_area_top + name_surf.get_height() + 6)
        )

        # Controles quantidade ([-] [qty] [+])
        ctrl_x = text_start_x + 175
        ctrl_y = draw_y + (self.original_size[1] - self.ctrl_h) // 2
        ctrl_rect = pygame.Rect(ctrl_x, ctrl_y, self.ctrl_w, self.ctrl_h)

        pygame.draw.rect(surface, self.COLOR_BOX, ctrl_rect, border_radius=10)
        pygame.draw.rect(
            surface, self.COLOR_BOX_DARK, ctrl_rect, width=2, border_radius=10
        )

        btn_w = 40
        qty_w = self.ctrl_w - (btn_w * 2)
        minus_rect = pygame.Rect(ctrl_rect.x, ctrl_rect.y, btn_w, self.ctrl_h)
        qty_rect = pygame.Rect(ctrl_rect.x + btn_w, ctrl_rect.y, qty_w, self.ctrl_h)
        plus_rect = pygame.Rect(
            ctrl_rect.x + btn_w + qty_w, ctrl_rect.y, btn_w, self.ctrl_h
        )

        pygame.draw.rect(surface, self.COLOR_BTN, minus_rect, border_radius=8)
        pygame.draw.rect(
            surface, self.COLOR_BTN_DARK, minus_rect, width=2, border_radius=8
        )
        pygame.draw.rect(surface, self.COLOR_BTN, plus_rect, border_radius=8)
        pygame.draw.rect(
            surface, self.COLOR_BTN_DARK, plus_rect, width=2, border_radius=8
        )

        minus_sign = self.name_font.render("−", True, self.COLOR_TEXT_MAIN)
        plus_sign = self.name_font.render("+", True, self.COLOR_TEXT_MAIN)
        surface.blit(minus_sign, minus_sign.get_rect(center=minus_rect.center))
        surface.blit(plus_sign, plus_sign.get_rect(center=plus_rect.center))

        qty_text = self.name_font.render(str(self.quantity), True, self.COLOR_TEXT_MAIN)
        pygame.draw.rect(surface, self.COLOR_BOX, qty_rect, border_radius=8)
        pygame.draw.rect(
            surface, self.COLOR_BOX_DARK, qty_rect, width=2, border_radius=8
        )
        surface.blit(qty_text, qty_text.get_rect(center=qty_rect.center))

        # atualiza rects interativos
        self.minus_rect = minus_rect
        self.plus_rect = plus_rect
        self.draw_rect = pygame.Rect(
            draw_x, draw_y, self.original_size[0], self.original_size[1]
        )

    def handle_click(self, local_pos: Tuple[int, int]) -> Optional[str]:
        """local_pos é relativo à list_surface."""
        if self.minus_rect.collidepoint(local_pos):
            if self.quantity > 0:
                self.quantity -= 1
            return "minus"
        if self.plus_rect.collidepoint(local_pos):
            self.quantity += 1
            return "plus"
        return None


class Supermarket(AnimatedPopup):
    """Tela de supermercado que usa o RESTAURANTE ATIVO do Player."""

    # -------------------- ESTILO / TIPOGRAFIA -------------------- #
    WINDOW_TITLE_FONT = ("fonts/LuckiestGuy-Regular.ttf", 40)
    WINDOW_TITLE_COLOR = (255, 255, 255)
    WINDOW_TITLE_OUTLINE = (0, 0, 0)
    WINDOW_TITLE_TOP = 25

    TITLE_FONT_PATH = "fonts/Baloo2-Bold.ttf"
    TITLE_FONT_SIZE = 22
    META_FONT_PATH = "fonts/Baloo2-Bold.ttf"
    META_FONT_SIZE = 16
    DESC_FONT_NAME = "arial"
    DESC_FONT_SIZE = 14

    COLOR_TEXT_MAIN: Color = (90, 60, 40)
    COLOR_TEXT_DESC: Color = (60, 40, 30)
    COLOR_LABEL: Color = (100, 70, 40)

    # Scrollbar (estética do cardápio)
    SCROLLBAR_WIDTH = 8
    SCROLLBAR_MIN_BAR = 40
    SCROLLBAR_BAR = (170, 140, 110)
    SCROLLBAR_BG = (220, 200, 170)

    # Caixa de descrição (preview)
    DESC_PAD = 8
    DESC_SCROLL_GUTTER = 12
    DESC_BOTTOM_PAD = 10
    DESC_BOTTOM_EXTRA = 12  # folga para não “grudar” no fim

    # -------------------- ZONAS DE LAYOUT (espelha o cardápio) -------------------- #
    # Lista (coluna à esquerda)
    LIST_ZONE = pygame.Rect(142, 98, 390, 380)  # mesma área visível do cardápio

    # Painel direito
    PREVIEW_IMG_ZONE = pygame.Rect(560, 125, 238, 120)
    PREVIEW_TITLE_ZONE = pygame.Rect(560, 245, 238, 22)
    PREVIEW_DESC_ZONE = pygame.Rect(570, 330, 240, 123)

    # Rodapé esquerdo (botão comprar + totais)
    FOOTER_BUY_RECT = pygame.Rect(LIST_ZONE.left, LIST_ZONE.bottom + 18, 250, 56)

    BUY_COLOR = (205, 95, 60)
    BUY_BORDER = (120, 55, 35)
    BUY_TEXT_COLOR = (255, 255, 240)

    def __init__(self, game) -> None:
        self.game = game
        self.config = Settings()

        # Inicializa dinheiro no restaurante ativo, se necessário
        r = self._active_restaurant()
        if r and float(r.money) == 0.0:
            r.money = float(self.config.MONEY["amount"])

        # Fundo da popup (mesma lógica do Cardápio)
        self.content_surface = pygame.image.load(
            "graphics/images/supermarket_bg.png"
        ).convert_alpha()
        super().__init__(
            screen_width=self.config.SCREEN["width"],
            screen_height=self.config.SCREEN["height"],
            content_surface=self.content_surface,
            open_sound="swipe",
            close_sound="swipe",
        )

        # ---------- Superfícies e fontes ----------
        # Lista rolável
        self.list_surface = pygame.Surface(
            (self.LIST_ZONE.width, self.LIST_ZONE.height), pygame.SRCALPHA
        )

        # Tipografia
        self.title_font = pygame.font.Font(self.TITLE_FONT_PATH, self.TITLE_FONT_SIZE)
        self.meta_font = pygame.font.Font(self.META_FONT_PATH, self.META_FONT_SIZE)
        self.desc_font = pygame.font.SysFont(self.DESC_FONT_NAME, self.DESC_FONT_SIZE)

        # UI (nomes/preços dos cards e rótulos)
        self.name_font = pygame.font.Font("fonts/LuckiestGuy-Regular.ttf", 28)
        self.price_font = pygame.font.Font("fonts/LuckiestGuy-Regular.ttf", 22)
        self.ui_font = pygame.font.Font("fonts/LuckiestGuy-Regular.ttf", 30)
        self.ui_small = pygame.font.Font("fonts/LuckiestGuy-Regular.ttf", 24)

        # ---------- Itens da lista ----------
        self.card_bg = pygame.image.load(
            "graphics/sprites/ingredients/icon_bg.png"
        ).convert_alpha()
        icons = [
            pygame.image.load(
                "graphics/sprites/ingredients/icon_tomato.png"
            ).convert_alpha(),
            pygame.image.load(
                "graphics/sprites/ingredients/icon_carrot.png"
            ).convert_alpha(),
            pygame.image.load(
                "graphics/sprites/ingredients/icon_lettuce.png"
            ).convert_alpha(),
            pygame.image.load(
                "graphics/sprites/ingredients/icon_potato.png"
            ).convert_alpha(),
            pygame.image.load(
                "graphics/sprites/ingredients/icon_broccoli.png"
            ).convert_alpha(),
        ]
        names_prices = [
            ("Tomate", 5),
            ("Cenoura", 5),
            ("Alface", 5),
            ("Batata", 5),
            ("Brócolis", 5),
        ]
        while len(names_prices) < len(icons):
            names_prices.append((f"Ingrediente {len(names_prices)+1}", 0.50))

        self.ingredient_cards: List[IngredientCard] = [
            IngredientCard(
                0,
                0,
                self.card_bg,
                icon,
                names_prices[i][0],
                names_prices[i][1],
                self.name_font,
                self.price_font,
            )
            for i, icon in enumerate(icons)
        ]
        self.selected_index = 0

        # ---------- Scroll da lista ----------
        _, card_h = self.card_bg.get_size()
        n = len(self.ingredient_cards)
        self.margin_x = 10
        self.margin_top = 10
        self.margin_bottom = 10
        self.item_gap = 12

        self.content_height = (
            self.margin_top
            + n * card_h
            + max(0, n - 1) * self.item_gap
            + self.margin_bottom
        )
        self.scrollbar = UIScrollbar(
            x=self.LIST_ZONE.right + 6,
            y=self.LIST_ZONE.top,
            height=self.LIST_ZONE.height,
            content_height=self.content_height,
            view_height=self.LIST_ZONE.height,
            width=self.SCROLLBAR_WIDTH,
            hover_scale=1.5,
            bar_color=self.SCROLLBAR_BAR,
            bg_color=self.SCROLLBAR_BG,
        )
        self.scroll_offset = 0

        # ---------- Scroll da descrição do preview ----------
        inner_h = max(0, self.PREVIEW_DESC_ZONE.height - self.DESC_PAD * 2)
        self.desc_scroll = UIScrollbar(
            x=self.PREVIEW_DESC_ZONE.right - self.SCROLLBAR_WIDTH - 4,
            y=self.PREVIEW_DESC_ZONE.top + self.DESC_PAD,
            height=inner_h,
            content_height=inner_h,  # ajustado no update()
            view_height=inner_h,
            width=self.SCROLLBAR_WIDTH,
            hover_scale=1.5,
            bar_color=self.SCROLLBAR_BAR,
            bg_color=self.SCROLLBAR_BG,
        )
        self.desc_offset = 0

        # ---------- Botões ----------
        button_image = pygame.image.load("graphics/sprites/go_back.png").convert_alpha()
        self.go_back = UIButton(
            self.config.SCREEN["width"] - 165, 15, button_image, enable_scale=True
        )
        self.buy_rect = self.FOOTER_BUY_RECT.copy()

        # ---------- Título ----------
        title_font = pygame.font.Font(*self.WINDOW_TITLE_FONT)
        self.title_text = render_text_with_outline(
            title_font, "SUPERMERCADO", self.WINDOW_TITLE_COLOR, self.WINDOW_TITLE_OUTLINE
        )
        self.title_rect = self.title_text.get_rect(
            centerx=self.config.SCREEN["width"] // 2
        )
        self.title_rect.top = self.WINDOW_TITLE_TOP

        self._layout_cards()

    # ---------- acesso seguro ao restaurante ativo ----------
    def _active_restaurant(self):
        player = getattr(self.game, "player", None)
        if player and hasattr(player, "get_active_restaurant"):
            return player.get_active_restaurant()
        return None

    # ---------- helpers de dinheiro/total ----------
    @staticmethod
    def _money_fmt(v: float) -> str:
        return f"{v:.2f}".replace(".", ",")

    def get_total_value(self) -> float:
        return sum(card.quantity * card.price for card in self.ingredient_cards)

    def get_remaining_money(self) -> float:
        r = self._active_restaurant()
        money = float(r.money) if r else 0.0
        return money - self.get_total_value()  # pode ficar negativo na UI; bloqueado na compra

    # ---------- layout / ciclo ----------
    def _layout_cards(self) -> None:
        if not self.ingredient_cards:
            return
        _, card_h = self.card_bg.get_size()
        x, y = self.margin_x, self.margin_top
        for card in self.ingredient_cards:
            card.update_position(x, y)
            y += card_h + self.item_gap

    def _update_desc_scroll_geometry(self, text: str) -> None:
        """Recalcula a altura de conteúdo da descrição para o scrollbar do preview."""
        inner = self.PREVIEW_DESC_ZONE.inflate(-self.DESC_PAD * 2, -self.DESC_PAD * 2)
        reserved = self.desc_scroll.default_width + self.DESC_SCROLL_GUTTER
        wrap_w = max(16, inner.width - reserved)

        lines = wrap_text(text, self.desc_font, wrap_w)
        line_h = self.desc_font.get_linesize()
        content_h = len(lines) * line_h + self.DESC_BOTTOM_PAD + self.DESC_BOTTOM_EXTRA

        inner_h = max(0, self.PREVIEW_DESC_ZONE.height - self.DESC_PAD * 2)
        self.desc_scroll.height = inner_h
        self.desc_scroll.view_height = inner_h
        self.desc_scroll.content_height = max(inner_h, content_h)
        self.desc_scroll.x = self.PREVIEW_DESC_ZONE.right - self.desc_scroll.default_width - 4
        self.desc_scroll.y = self.PREVIEW_DESC_ZONE.top + self.DESC_PAD

        # Ajusta tamanho do "thumb" (compatível com UIScrollbar do projeto)
        if self.desc_scroll.view_height > 0 and self.desc_scroll.content_height > self.desc_scroll.view_height:
            new_h = max(
                self.SCROLLBAR_MIN_BAR,
                int(self.desc_scroll.view_height * (self.desc_scroll.view_height / self.desc_scroll.content_height)),
            )
        else:
            new_h = self.desc_scroll.height
        self.desc_scroll.bar_height = new_h
        self.desc_scroll.bar_rect.height = new_h
        self.desc_scroll.bar_rect.y = max(
            self.desc_scroll.y,
            min(self.desc_scroll.bar_rect.y, self.desc_scroll.y + self.desc_scroll.height - new_h),
        )

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.animation_done and not self.closing:
            # Scroll lista
            self.scrollbar.update(dt)
            self.scroll_offset = self.scrollbar.get_scroll_offset()

            # Atualiza preview/descrição do item selecionado
            self._update_desc_scroll_geometry(self._current_desc_text())

            self.desc_scroll.update(dt)
            max_off = max(
                0, self.desc_scroll.content_height - self.desc_scroll.view_height
            )
            self.desc_offset = min(self.desc_scroll.get_scroll_offset(), max_off)

            self.go_back.update(dt)

    # ---------- preview (lado direito) ----------
    def _current_desc_text(self) -> str:
        if not self.ingredient_cards:
            return ""
        card = self.ingredient_cards[self.selected_index]
        return (
            f"{card.name} fresco, ideal para várias receitas. "
            f"{IngredientCard._fmt_price(card.price)}."
        )

    def _draw_preview(self, screen: pygame.Surface) -> None:
        if not self.ingredient_cards:
            return

        card = self.ingredient_cards[self.selected_index]

        # Ícone grande centralizado na zona de preview
        icon = card.icon_image
        # Ajusta para caber dentro do PREVIEW_IMG_ZONE
        avail_w, avail_h = self.PREVIEW_IMG_ZONE.size
        scale = min(avail_w / icon.get_width(), avail_h / icon.get_height())
        big = pygame.transform.smoothscale(
            icon, (int(icon.get_width() * scale), int(icon.get_height() * scale))
        )
        icon_rect = big.get_rect(center=self.PREVIEW_IMG_ZONE.center)
        screen.blit(big, icon_rect.topleft)

        # Título (nome do ingrediente)
        name_surf = self.title_font.render(card.name, True, self.COLOR_TEXT_MAIN)
        name_rect = name_surf.get_rect(center=self.PREVIEW_TITLE_ZONE.center)
        screen.blit(name_surf, name_rect.topleft)

        # Caixa de descrição com rolagem (estilo cardápio)
        inner = self.PREVIEW_DESC_ZONE.inflate(-self.DESC_PAD * 2, -self.DESC_PAD * 2)
        reserved = self.desc_scroll.default_width + self.DESC_SCROLL_GUTTER
        wrap_w = max(16, inner.width - reserved)

        prev_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(inner.left, inner.top, inner.width, inner.height))

        y_cursor = inner.top - self.desc_offset
        for line in wrap_text(self._current_desc_text(), self.desc_font, wrap_w):
            ts = self.desc_font.render(line, True, self.COLOR_TEXT_DESC)
            screen.blit(ts, (inner.left, y_cursor))
            y_cursor += self.desc_font.get_linesize()

        screen.set_clip(prev_clip)
        self.desc_scroll.render(screen)

    # ---------- render principal ----------
    def render(self, screen: pygame.Surface) -> None:
        super().render(screen)
        if self.animation_done and not self.closing:
            # Título
            screen.blit(self.title_text, self.title_rect)

            # Lista (lado esquerdo)
            self.list_surface.fill((0, 0, 0, 0))
            for card in self.ingredient_cards:
                card.draw(self.list_surface, self.scroll_offset)
            screen.blit(self.list_surface, self.LIST_ZONE.topleft)
            self.scrollbar.render(screen)

            # Preview (lado direito)
            self._draw_preview(screen)

            # Rodapé (botão COMPRAR + totais), alinhado ao fundo da popup
            pygame.draw.rect(screen, self.BUY_COLOR, self.buy_rect, border_radius=12)
            pygame.draw.rect(
                screen, self.BUY_BORDER, self.buy_rect, width=3, border_radius=12
            )
            txt = self.ui_font.render("COMPRAR", True, self.BUY_TEXT_COLOR)
            screen.blit(txt, txt.get_rect(center=self.buy_rect.center))

            total_val = self.get_total_value()
            money_left = self.get_remaining_money()
            total_label = self.ui_font.render(
                f"Total: {self._money_fmt(total_val)}", True, self.COLOR_TEXT_MAIN
            )
            money_label = self.ui_font.render(
                f"Dinheiro: {self._money_fmt(money_left)}", True, self.COLOR_TEXT_MAIN
            )
            totals_y = (
                self.buy_rect.y + (self.buy_rect.height - total_label.get_height()) // 2 + 2
            )
            # Coluna de totais ao lado direito do botão (em linha com estética do cardápio)
            right_x = self.PREVIEW_DESC_ZONE.right - money_label.get_width()
            screen.blit(total_label, (self.PREVIEW_DESC_ZONE.left, totals_y))
            screen.blit(money_label, (right_x, totals_y))

            # Botão Voltar
            self.go_back.render(screen)

    # ---------- eventos ----------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.animation_done and not self.closing:
            self.scrollbar.handle_event(event)
            self.desc_scroll.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # voltar
                if self.go_back.rect.collidepoint((mx, my)):
                    self.start_closing()
                    return

                # comprar
                if self.buy_rect.collidepoint((mx, my)):
                    self._confirm_purchase()
                    return

                # cliques na lista
                lx, ly = mx - self.LIST_ZONE.x, my - self.LIST_ZONE.y
                if 0 <= lx < self.list_surface.get_width() and 0 <= ly < self.list_surface.get_height():
                    clicked_control = False
                    for card in self.ingredient_cards:
                        res = card.handle_click((lx, ly))
                        if res in ("minus", "plus"):
                            clicked_control = True
                            break
                    if not clicked_control:
                        # selecionar para preview
                        for i, card in enumerate(self.ingredient_cards):
                            if card.draw_rect.collidepoint((lx, ly)):
                                self.selected_index = i
                                # Ao trocar item, reinicia rolagem da descrição
                                self.desc_scroll.bar_rect.y = self.desc_scroll.y
                                self.desc_offset = 0
                                break

    # ---------- compra ----------
    def _confirm_purchase(self) -> None:
        r = self._active_restaurant()
        if not r:
            return

        total = self.get_total_value()
        if total <= 0:
            return
        if total > float(r.money):
            # opcional: feedback de falta de dinheiro
            return

        # debita e adiciona ao estoque
        r.money -= total
        for card in self.ingredient_cards:
            if card.quantity > 0:
                if hasattr(r, "update_ingredient"):
                    r.update_ingredient(card.name, card.quantity)
                else:
                    # compatibilidade simples
                    if not hasattr(r, "owned_ingredients"):
                        r.owned_ingredients = {}
                    r.owned_ingredients[card.name] = (
                        r.owned_ingredients.get(card.name, 0) + card.quantity
                    )
                card.quantity = 0

    def on_close(self) -> None:
        """
        Chamado automaticamente quando a animação de fechamento termina.
        Remove a referência ao supermercado na instância principal do jogo.
        """
        self.game.supermarket = None
