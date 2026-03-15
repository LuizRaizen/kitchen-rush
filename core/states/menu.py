"""
Módulo de Menu.

Tela para visualizar e selecionar pratos do restaurante.

Alterações desta versão:
- Removida a lógica de baseline na descrição (sem dependência de linha riscada).
- Descrição usa integralmente a ZONE_DESC (com padding).
- Estrelas e preço usam apenas ZONE_STARS_PRICE.
- Mantidas as “ZONAS” para fácil ajuste ao fundo.
- Rolagem interna apenas do texto (descrição + habilidades).

Melhorias:
- Preview do prato só muda ao clicar (não mais no hover).
- Botão de adicionar prato sem texto (só o ícone "+").
- Destaque do card selecionado usando a MESMA escala do hover (efeito rádio).
- Correção de seleção “aleatória”: ordem de update e prioridade de hit-test.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import pygame

from settings import Settings
from utils.functions import render_text_with_outline
from core.effects.animated_popup import AnimatedPopup
from core.gui.ui_button import UIButton
from core.gui.ui_scrollbar import UIScrollbar
from core.assets.dishes import INGREDIENTS


Color = Tuple[int, int, int]


class Menu(AnimatedPopup):
    """Tela de Menu de Cardápio do jogo."""

    # --------------------------------------------------------------------- #
    #                             ZONAS DO LAYOUT                           #
    # --------------------------------------------------------------------- #

    # Lista (grade) à esquerda
    GRID_SURF_W = 390
    GRID_SURF_H = 380  # altura visível da lista (topo=98 → base≈478)
    GRID_OFFSET = (142, 98)  # onde a grade é blitada

    # Painel direito (ajuste conforme o PNG do fundo)
    ZONE_PREVIEW = pygame.Rect(560, 125, 238, 120)
    ZONE_TITLE = pygame.Rect(560, 245, 238, 22)
    ZONE_ING_COLUMN = pygame.Rect(780, 120, 160, 148)

    # Descrição ocupa integralmente a área definida (sem baseline)
    ZONE_DESC = pygame.Rect(570, 330, 240, 123)

    # Estrelas (à esquerda) e preço (à direita) nesta faixa
    ZONE_STARS_PRICE = pygame.Rect(578, ZONE_DESC.bottom + 3, 210, 28)

    # --------------------------------------------------------------------- #
    #                     APARÊNCIA / TIPOGRAFIA / ESPAÇOS                  #
    # --------------------------------------------------------------------- #

    PREVIEW_IMG_SIZE = (150, 100)

    TITLE_FONT_PATH = "fonts/Baloo2-Bold.ttf"
    TITLE_FONT_SIZE = 22
    META_FONT_PATH = "fonts/Baloo2-Bold.ttf"
    META_FONT_SIZE = 16
    DESC_FONT_NAME = "arial"
    DESC_FONT_SIZE = 14

    COLOR_TEXT_MAIN: Color = (90, 60, 40)
    COLOR_TEXT_DESC: Color = (60, 40, 30)
    COLOR_LABEL: Color = (100, 70, 40)

    # Ícones de ingredientes
    COLOR_ING_OUTLINE: Color = (66, 54, 34)
    ING_OUTLINE_WIDTH = 2

    SECTION_GAP = 8
    DESC_PAD = 8
    DESC_SCROLL_GUTTER = 12
    DESC_REDUCE_H = 14
    DESC_BOTTOM_PAD = 10
    SEC_BEFORE_ABIL = 10
    ABIL_LABEL_GAP = 6
    ABIL_BLOCK_GAP = 8

    SCROLLBAR_WIDTH = 8
    SCROLLBAR_MIN_BAR = 40

    ING_ICON_SIZE = 28
    ING_ROW_H = 30
    ING_ICON_TEXT_GAP = 8
    ING_ICON_SPACING = 10

    STAR_SIZE = (24, 24)
    STAR_SPACING = 4

    GRID_COLS = 4
    GRID_CARD_GAP = 4
    GRID_MARGIN = (10, 10)

    WINDOW_TITLE_FONT = ("fonts/LuckiestGuy-Regular.ttf", 40)
    WINDOW_TITLE_COLOR = (255, 255, 255)
    WINDOW_TITLE_OUTLINE = (0, 0, 0)
    WINDOW_TITLE_TOP = 15

    DESC_TITLE_TEXT = "DESCRIÇÃO"
    DESC_TITLE_COLOR: Color = (30, 19, 7)
    DESC_TITLE_ALIGN = "left"

    DESC_BOTTOM_EXTRA = 12

    # --------------------------------------------------------------------- #
    #                              CONSTRUÇÃO                               #
    # --------------------------------------------------------------------- #

    def __init__(self, game) -> None:
        self.game = game
        self.config = Settings()

        # Fundo do menu
        self.bg_image = pygame.image.load("graphics/images/menu.png").convert_alpha()
        self.bg_rect = self.bg_image.get_rect(
            center=(
                self.config.SCREEN["width"] // 2,
                self.config.SCREEN["height"] // 2,
            )
        )

        # Superfície do popup
        self.menu_surface = pygame.Surface(
            (self.config.SCREEN["width"], self.config.SCREEN["height"]),
            pygame.SRCALPHA,
        )

        # Título da janela ("CARDÁPIO")
        title_font = pygame.font.Font(*self.WINDOW_TITLE_FONT)
        self.window_title_font = title_font
        self.title_text = render_text_with_outline(
            title_font, "CARDÁPIO", self.WINDOW_TITLE_COLOR, self.WINDOW_TITLE_OUTLINE
        )
        self.title_rect = self.title_text.get_rect(
            centerx=self.config.SCREEN["width"] // 2
        )
        self.title_rect.top = self.WINDOW_TITLE_TOP

        # Animação base
        super().__init__(
            screen_width=self.config.SCREEN["width"],
            screen_height=self.config.SCREEN["height"],
            content_surface=self.menu_surface,
            open_sound="swipe",
            close_sound="swipe",
        )

        # ------------------------------- LISTA (grade) ------------------------------ #
        self.dish_list = pygame.Surface((self.GRID_SURF_W, self.GRID_SURF_H), pygame.SRCALPHA)
        self.scroll_offset = 0
        self.margin_x, self.margin_y = self.GRID_MARGIN

        self.dishes: List["Dish"] = self.game.player_menu.owned_dishes()

        grid_card_bg = pygame.image.load("graphics/sprites/dish_card.png").convert_alpha()
        dish_font = pygame.font.Font(self.TITLE_FONT_PATH, 14)

        self.dish_cards: List[UIButton] = []
        for d in self.dishes:
            icon = pygame.image.load(d.icon_path).convert_alpha()
            self.dish_cards.append(
                UIButton(
                    0,
                    0,
                    grid_card_bg,
                    icon,
                    d.name,
                    dish_font,
                    (93, 52, 29),
                    enable_scale=True,
                    max_scale=1.1,
                    text_align="bottom",
                    text_padding=5,
                    hover_sound="hover",
                )
            )

        # Botão de "novo prato": somente ícone "+", sem texto
        plus_icon = pygame.image.load("graphics/sprites/add_icon.png").convert_alpha()
        self.add_recipe_card = UIButton(
            0,
            0,
            grid_card_bg,
            plus_icon,
            text=None,  # sem texto
            font=None,
            enable_scale=True,
            max_scale=1.1,
            hover_sound="hover",
        )
        self.dish_cards.append(self.add_recipe_card)

        # Scrollbar da grade
        card_h = self.dish_cards[0].original_size[1] if self.dish_cards else 0
        rows = math.ceil(len(self.dish_cards) / self.GRID_COLS) if card_h else 0
        content_h = rows * (card_h + self.GRID_CARD_GAP) + self.margin_y
        view_h = self.dish_list.get_height()

        self.scrollbar = UIScrollbar(
            x=self.GRID_OFFSET[0] + self.GRID_SURF_W + 8,
            y=self.GRID_OFFSET[1] + 12,
            height=view_h,
            content_height=content_h,
            view_height=view_h,
            width=self.SCROLLBAR_WIDTH,
            hover_scale=1.5,
            bar_color=(100, 70, 40),
            bg_color=(180, 130, 100),
        )

        # ---------------------------- PAINEL DIREITO ------------------------------- #
        self.selected_index: Optional[int] = 0  # prato ativo
        self.hovered_index: Optional[int] = None  # só para efeito visual

        self.title_font = pygame.font.Font(self.TITLE_FONT_PATH, self.TITLE_FONT_SIZE)
        self.meta_font = pygame.font.Font(self.META_FONT_PATH, self.META_FONT_SIZE)
        self.desc_font = pygame.font.SysFont(self.DESC_FONT_NAME, self.DESC_FONT_SIZE)

        # Estrelas
        self.star_full_img = pygame.transform.smoothscale(
            pygame.image.load("graphics/sprites/star.png").convert_alpha(), self.STAR_SIZE
        )
        self.star_blank_img = pygame.transform.smoothscale(
            pygame.image.load("graphics/sprites/star_blank.png").convert_alpha(), self.STAR_SIZE
        )

        # Scrollbar da descrição (trilho == janela visível)
        inner_h = max(0, self.ZONE_DESC.height - self.DESC_PAD * 2)
        self.desc_scroll = UIScrollbar(
            x=self.ZONE_DESC.right - self.SCROLLBAR_WIDTH - 4,
            y=self.ZONE_DESC.top + self.DESC_PAD,
            height=inner_h,
            content_height=inner_h,
            view_height=inner_h,
            width=self.SCROLLBAR_WIDTH,
            hover_scale=1.5,
            bar_color=(170, 140, 110),
            bg_color=(220, 200, 170),
        )
        self.desc_offset = 0

        # prato atual exibido no painel (key)
        self._current_panel_key: Optional[str] = None

        # Botão de retorno
        back_img = pygame.image.load("graphics/sprites/go_back.png").convert_alpha()
        self.go_back = UIButton(self.config.SCREEN["width"] - 165, 15, back_img, enable_scale=True)

        # Aplica estado ativo inicial ao primeiro card (se existir e não for o "+")
        if self.dish_cards and not self._is_plus_index(self.selected_index):
            self.dish_cards[self.selected_index].set_active(True)

    # --------------------------------------------------------------------- #
    #                                HELPERS                                #
    # --------------------------------------------------------------------- #

    def _is_plus_index(self, idx: int) -> bool:
        return idx == len(self.dish_cards) - 1

    def _dish_for_panel(self) -> Optional["Dish"]:
        """Retorna APENAS o prato selecionado (não usa hover)."""
        if self.selected_index is not None and not self._is_plus_index(self.selected_index):
            return self.dishes[self.selected_index]
        return None

    @staticmethod
    def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        words = text.split()
        lines: List[str] = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    @staticmethod
    def _recalc_scrollbar_geometry(sb: UIScrollbar, min_bar: int) -> None:
        if sb.view_height > 0 and sb.content_height > sb.view_height:
            new_h = max(min_bar, int(sb.view_height * (sb.view_height / sb.content_height)))
        else:
            new_h = sb.height
        sb.bar_height = new_h
        sb.bar_rect.height = new_h
        sb.bar_rect.y = max(sb.y, min(sb.bar_rect.y, sb.y + sb.height - new_h))

    # --------------------------------------------------------------------- #
    #                             CICLO DE VIDA                             #
    # --------------------------------------------------------------------- #

    def update(self, dt: float) -> None:
        super().update(dt)
        if not (self.animation_done and not self.closing):
            return

        # ----- Scroll da grade -----
        if self.dish_cards:
            card_h = self.dish_cards[0].original_size[1]
            rows = math.ceil(len(self.dish_cards) / self.GRID_COLS)
            content_h = rows * (card_h + self.GRID_CARD_GAP) + self.margin_y
        else:
            content_h = 0

        self.scrollbar.content_height = content_h
        self.scrollbar.view_height = self.dish_list.get_height()
        self.scrollbar.height = self.scrollbar.view_height
        self._recalc_scrollbar_geometry(self.scrollbar, self.SCROLLBAR_MIN_BAR)
        self.scrollbar.update(dt)
        self.scroll_offset = self.scrollbar.get_scroll_offset()

        # ----- Cards da grade -----
        for i, card in enumerate(self.dish_cards):
            row = i // self.GRID_COLS
            col = i % self.GRID_COLS

            # posição lógica (sem offsets)
            card.x = self.margin_x + col * (card.original_size[0] + self.GRID_CARD_GAP)
            card.y = self.margin_y + row * (card.original_size[1] + self.GRID_CARD_GAP)

            # 1) atualiza animações/hover
            card.update(dt)
            # 2) só depois aplica offsets de surface e scroll — mantém fixed_rect em coordenadas de TELA
            card.update_position(
                offset_x=self.GRID_OFFSET[0],
                offset_y=self.GRID_OFFSET[1] - self.scroll_offset,
            )

        # Hover persistente (apenas para efeito visual)
        self.hovered_index = None
        for i, card in enumerate(self.dish_cards):
            if card.hovered:
                self.hovered_index = i
                break

        # ----- Texto rolável (Descrição + Habilidades) -----
        dish = self._dish_for_panel()
        if dish:
            # reset seguro quando troca o prato exibido (clicado)
            if dish.key != self._current_panel_key:
                self._current_panel_key = dish.key
                self.desc_scroll.bar_rect.y = self.desc_scroll.y
                self.desc_offset = 0

            inner_rect = self.ZONE_DESC.inflate(-self.DESC_PAD * 2, -self.DESC_PAD * 2)
            reserved = self.desc_scroll.default_width + self.DESC_SCROLL_GUTTER
            wrap_w = max(16, inner_rect.width - reserved)

            line_h = self.desc_font.get_linesize()
            meta_h = self.meta_font.get_linesize()

            content_h = 0

            lines_desc = self._wrap_text(dish.description, self.desc_font, wrap_w)
            content_h += len(lines_desc) * line_h

            abil_blocks = [
                (ab.label, self._wrap_text(ab.description, self.desc_font, wrap_w))
                for ab in dish.abilities
            ]
            if abil_blocks:
                content_h += self.SEC_BEFORE_ABIL + meta_h
                for idx, (_, block) in enumerate(abil_blocks):
                    content_h += self.ABIL_LABEL_GAP + len(block) * line_h
                    if idx < len(abil_blocks) - 1:
                        content_h += self.ABIL_BLOCK_GAP

            # folga no rodapé: evita "grudar" a última linha
            content_h += self.DESC_BOTTOM_PAD + self.DESC_BOTTOM_EXTRA

            inner_h = max(0, self.ZONE_DESC.height - self.DESC_PAD * 2)

            # trilho lógico == janela visível
            self.desc_scroll.view_height = inner_h
            self.desc_scroll.height = inner_h
            self.desc_scroll.content_height = max(inner_h, content_h)
            self.desc_scroll.x = self.ZONE_DESC.right - self.desc_scroll.default_width - 4
            self.desc_scroll.y = self.ZONE_DESC.top + self.DESC_PAD

            self._recalc_scrollbar_geometry(self.desc_scroll, self.SCROLLBAR_MIN_BAR)
            self.desc_scroll.update(dt)

            # clamp do offset ao novo limite (caso tenha mudado de prato)
            max_off = max(0, self.desc_scroll.content_height - self.desc_scroll.view_height)
            self.desc_offset = min(self.desc_scroll.get_scroll_offset(), max_off)

        self.go_back.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        self.menu_surface.fill((0, 0, 0, 0))
        self.menu_surface.blit(self.bg_image, self.bg_rect)

        self.menu_surface.blit(self.title_text, (self.title_rect.left, self.title_rect.top))

        if self.animation_done and not self.closing:
            # -------------------- Grade -------------------- #
            self.dish_list.fill((0, 0, 0, 0))
            # desenha não-hover primeiro
            for card in self.dish_cards:
                if not card.hovered:
                    card.render_on_surface(self.dish_list, offset_y=-self.scroll_offset)
            # desenha hovered por cima
            for card in self.dish_cards:
                if card.hovered:
                    card.render_on_surface(self.dish_list, offset_y=-self.scroll_offset)

            self.menu_surface.blit(self.dish_list, self.GRID_OFFSET)
            self.scrollbar.render_at(self.menu_surface, y_offset=0)

        # -------------------- Painel direito ------------------- #
        dish = self._dish_for_panel()
        if dish:
            # Preview
            try:
                preview_img = pygame.image.load(dish.preview_path).convert_alpha()
            except Exception:
                preview_img = pygame.image.load(dish.icon_path).convert_alpha()
            preview_scaled = pygame.transform.smoothscale(preview_img, self.PREVIEW_IMG_SIZE)
            preview_pos = preview_scaled.get_rect(center=self.ZONE_PREVIEW.center)
            self.menu_surface.blit(preview_scaled, preview_pos.topleft)

            # Título
            title_surf = self.title_font.render(dish.name, True, self.COLOR_TEXT_MAIN)
            title_rect = title_surf.get_rect(center=self.ZONE_TITLE.center)
            self.menu_surface.blit(title_surf, title_rect)

            # Ingredientes (apenas ícones), alinhados verticalmente ao lado do preview
            self._render_ingredient_column(dish)

            # Título "DESCRIÇÃO"
            self._render_description_title()

            # Descrição + habilidades
            self._render_description_block(dish)

            # Estrelas e preço
            self._render_stars_and_price(dish)

        self.go_back.render_at(self.menu_surface, y_offset=0)
        super().render(screen)

    # --------------------------------------------------------------------- #
    #                         RENDER: SUBSEÇÕES DO PAINEL                   #
    # --------------------------------------------------------------------- #

    def _render_ingredient_column(self, dish: "Dish") -> None:
        """
        Renderiza SOMENTE os ícones de ingredientes, com contorno,
        alinhados verticalmente ao lado do preview, iniciando no topo.
        """
        icon_size = (self.ING_ICON_SIZE, self.ING_ICON_SIZE)

        icons: List[pygame.Surface] = []
        for key in dish.ingredient_keys:
            meta = INGREDIENTS.get(key)
            if not meta:
                continue
            try:
                icon = pygame.image.load(meta.icon_path).convert_alpha()
                icon = pygame.transform.smoothscale(icon, icon_size)
                icons.append(icon)
            except Exception:
                continue

        if not icons:
            return

        x = self.ZONE_ING_COLUMN.left
        y = self.ZONE_PREVIEW.top

        for icon in icons:
            frame_rect = pygame.Rect(x - 3, y - 2, self.ING_ICON_SIZE + 6, self.ING_ICON_SIZE + 6)
            pygame.draw.rect(
                self.menu_surface,
                self.COLOR_ING_OUTLINE,
                frame_rect,
                width=self.ING_OUTLINE_WIDTH,
                border_radius=8,
            )
            self.menu_surface.blit(icon, (x, y))
            y += self.ING_ICON_SIZE + self.ING_ICON_SPACING

    def _render_description_title(self) -> None:
        """Desenha o título 'DESCRIÇÃO' acima da ZONE_DESC."""
        title_surf = self.meta_font.render(self.DESC_TITLE_TEXT, True, self.DESC_TITLE_COLOR)
        title_w = title_surf.get_width()

        if self.DESC_TITLE_ALIGN == "center":
            x = self.ZONE_DESC.centerx - title_w // 2
        elif self.DESC_TITLE_ALIGN == "right":
            x = self.ZONE_DESC.right - title_w
        else:
            x = self.ZONE_DESC.left

        y = self.ZONE_DESC.top - title_surf.get_height() - 4
        self.menu_surface.blit(title_surf, (x, y))

    def _render_description_block(self, dish: "Dish") -> None:
        inner = self.ZONE_DESC.inflate(-self.DESC_PAD * 2, -self.DESC_PAD * 2)
        reserved = self.desc_scroll.default_width + self.DESC_SCROLL_GUTTER
        wrap_w = max(16, inner.width - reserved)
        line_h = self.desc_font.get_linesize()
        meta_h = self.meta_font.get_linesize()

        visible_clip = pygame.Rect(inner.left, inner.top, max(0, inner.width), max(0, inner.height))
        prev_clip = self.menu_surface.get_clip()
        self.menu_surface.set_clip(visible_clip)

        y_cursor = inner.top - self.desc_offset

        # Descrição
        lines_desc = self._wrap_text(dish.description, self.desc_font, wrap_w)
        for ln in lines_desc:
            surf = self.desc_font.render(ln, True, self.COLOR_TEXT_DESC)
            self.menu_surface.blit(surf, (inner.left, y_cursor))
            y_cursor += line_h

        # Habilidades
        if dish.abilities:
            y_cursor += self.SEC_BEFORE_ABIL
            label_ab = self.meta_font.render("Habilidades:", True, self.COLOR_LABEL)
            self.menu_surface.blit(label_ab, (inner.left, y_cursor))
            y_cursor += meta_h

            for idx, ab in enumerate(dish.abilities):
                label_surf = self.meta_font.render(f"• {ab.label}:", True, self.COLOR_TEXT_MAIN)
                label_w = label_surf.get_width()
                label_h = label_surf.get_height()
                self.menu_surface.blit(label_surf, (inner.left, y_cursor))

                after_label_gap = 6
                first_wrap_w = max(16, wrap_w - label_w - after_label_gap)

                words = ab.description.split()
                first_line = ""
                cut_idx = 0
                for i, w in enumerate(words):
                    test = (first_line + " " + w).strip()
                    if self.desc_font.size(test)[0] <= first_wrap_w:
                        first_line = test
                    else:
                        cut_idx = i
                        break
                else:
                    cut_idx = len(words)

                if first_line:
                    first_desc_surf = self.desc_font.render(first_line, True, self.COLOR_TEXT_MAIN)
                    first_y = y_cursor + (label_h - first_desc_surf.get_height()) // 2
                    self.menu_surface.blit(first_desc_surf, (inner.left + label_w + after_label_gap, first_y))

                y_cursor += line_h

                remaining_text = " ".join(words[cut_idx:])
                if remaining_text:
                    for ln in self._wrap_text(remaining_text, self.desc_font, wrap_w):
                        tx = self.desc_font.render(ln, True, self.COLOR_TEXT_MAIN)
                        self.menu_surface.blit(tx, (inner.left + 16, y_cursor))
                        y_cursor += line_h

                if idx < len(dish.abilities) - 1:
                    y_cursor += self.ABIL_BLOCK_GAP

        self.menu_surface.set_clip(prev_clip)
        self.desc_scroll.render(self.menu_surface)

    def _render_stars_and_price(self, dish: "Dish") -> None:
        stars_y = self.ZONE_STARS_PRICE.top
        stars_x = self.ZONE_STARS_PRICE.left
        for i in range(5):
            img = self.star_full_img if i < dish.stars else self.star_blank_img
            self.menu_surface.blit(img, (stars_x, stars_y))
            stars_x += self.STAR_SIZE[0] + self.STAR_SPACING

        price_value = getattr(dish, "price", None)
        if isinstance(price_value, int):
            price_surf = self.meta_font.render(f"$ {price_value}", True, self.COLOR_TEXT_MAIN)
            price_rect = price_surf.get_rect(top=stars_y, right=self.ZONE_STARS_PRICE.right)
            self.menu_surface.blit(price_surf, price_rect)

    # --------------------------------------------------------------------- #
    #                              EVENTOS                                  #
    # --------------------------------------------------------------------- #

    def handle_event(self, event: pygame.event.Event) -> None:
        if not (self.animation_done and not self.closing):
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = event.pos

            # Prioriza: hovered → selecionado → demais | dentro de cada grupo, do "topo" para baixo
            indices = list(range(len(self.dish_cards)))
            hovered_idxs = [i for i, c in enumerate(self.dish_cards) if c.hovered]
            selected_idxs = (
                [self.selected_index] if (self.selected_index is not None) else []
            )
            # remove duplicados preservando ordem
            def uniq(seq):
                seen = set()
                out = []
                for x in seq:
                    if x not in seen:
                        out.append(x)
                        seen.add(x)
                return out

            base = uniq(hovered_idxs + selected_idxs + indices)
            # Reverte para testar primeiro os últimos desenhados (maior chance de estarem “por cima”)
            hit_order = list(reversed(base))

            for i in hit_order:
                card = self.dish_cards[i]
                if card.fixed_rect.collidepoint(mouse):
                    if not self._is_plus_index(i):
                        self.selected_index = i
                        # Atualiza estado "ativo" (rádio): só o selecionado fica ativo
                        for j, c in enumerate(self.dish_cards):
                            c.set_active(j == self.selected_index and not self._is_plus_index(j))
                        # Reset da rolagem ao trocar o prato ativo
                        self.desc_scroll.bar_rect.y = self.desc_scroll.y
                        self.desc_offset = 0
                    else:
                        print("[Menu] Novo Prato: abrir tela de receitas (em breve).")
                    break

            if self.go_back.rect.collidepoint(mouse):
                self.start_closing()

        self.scrollbar.handle_event(event)
        self.desc_scroll.handle_event(event)

    # --------------------------------------------------------------------- #
    #                              CICLO FECHAR                             #
    # --------------------------------------------------------------------- #

    def on_close(self) -> None:
        self.game.menu = None
