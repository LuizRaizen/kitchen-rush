"""
Módulo de Menu.

Contém a tela de visualização e seleção dos pratos disponíveis no restaurante.
Inclui rolagem, animações com efeito de hover e interação com botões.
"""

import pygame
import math

from settings import Settings
from core.effects.animated_popup import AnimatedPopup
from core.gui.ui_button import UIButton
from core.gui.ui_scrollbar import UIScrollbar
from utils.functions import render_text_with_outline


class Menu(AnimatedPopup):
    """
    Tela de Menu de Cardápio do jogo.

    Possui scroll, cards interativos e botões de adicionar/remover pratos.
    Herda a animação suave de entrada/saída da classe AnimatedPopup.
    """

    def __init__(self, game):
        """
        Inicializa a interface do menu com seus elementos gráficos e lógicos.

        :param game: Referência à instância principal do jogo.
        """
        self.game = game
        self.config = Settings()

        # Fundo do menu
        self.bg_image = pygame.image.load('graphics/images/menu.png').convert_alpha()
        self.bg_rect = self.bg_image.get_rect(center=(
            self.config.SCREEN['width'] // 2, self.config.SCREEN['height'] // 2
        ))

        # Superfície onde o conteúdo do menu será desenhado
        self.menu_surface = pygame.Surface(
            (self.config.SCREEN['width'], self.config.SCREEN['height']), pygame.SRCALPHA
        )
        
        super().__init__(
            screen_width=self.config.SCREEN['width'],
            screen_height=self.config.SCREEN['height'],
            content_surface=self.menu_surface,
            open_sound="swipe",
            close_sound="swipe"
        )

        # Lista visual dos pratos
        self.dish_list = pygame.Surface((390, 346), pygame.SRCALPHA)
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.max_scroll = 0
        self.margin_x = 10
        self.margin_y = 10

        # Carrega as imagens dos pratos
        dishes_images = {
            'spaghetti': pygame.image.load('graphics/sprites/dishes/spaghetti_icon.png'),
            'hamburger': pygame.image.load('graphics/sprites/dishes/hamburger_icon.png'),
            'soup': pygame.image.load('graphics/sprites/dishes/soup_icon.png'),
            'pizza': pygame.image.load('graphics/sprites/dishes/pizza_icon.png'),
            'salad': pygame.image.load('graphics/sprites/dishes/salad_icon.png'),
            'grilled_chicken': pygame.image.load('graphics/sprites/dishes/grilled_chicken_icon.png'),
            'hotdog': pygame.image.load('graphics/sprites/dishes/hotdog_icon.png'),
            'lasagna': pygame.image.load('graphics/sprites/dishes/lasagna_icon.png'),
            'muffin': pygame.image.load('graphics/sprites/dishes/muffin_icon.png'),
            'cupcake': pygame.image.load('graphics/sprites/dishes/cupcake_icon.png'),
            'taco': pygame.image.load('graphics/sprites/dishes/taco_icon.png'),
            'steak': pygame.image.load('graphics/sprites/dishes/steak_icon.png'),
            'roast_chicken': pygame.image.load('graphics/sprites/dishes/roast_chicken_icon.png'),
            'donut': pygame.image.load('graphics/sprites/dishes/donut_icon.png'),
            'fried_fish': pygame.image.load('graphics/sprites/dishes/fried_fish_icon.png'),
            'fries': pygame.image.load('graphics/sprites/dishes/fries_icon.png'),
            'omelete': pygame.image.load('graphics/sprites/dishes/omelete_icon.png'),
            'pancakes': pygame.image.load('graphics/sprites/dishes/pancakes_icon.png'),
            'ice_cream': pygame.image.load('graphics/sprites/dishes/ice_cream_icon.png'),
            'add': pygame.image.load('graphics/sprites/add_icon.png'),
        }

        # Carrega a imagem do fundo do card que mostra os pratos
        bg_image = pygame.image.load('graphics/sprites/dish_card.png')
        dish_font = pygame.font.Font("fonts/Baloo2-Bold.ttf", 14)

        # Cria os cards que mostram os pratos
        self.dish_cards = [
            UIButton(
                0, 0,
                bg_image,
                dishes_images['spaghetti'],
                "Espaguete",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['soup'],
                "Sopa",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['hamburger'],
                "Hamburguer",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['pizza'],
                "Pizza",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['salad'],
                "Salada",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['grilled_chicken'],
                "Frango G.",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['hotdog'],
                "Hotdog",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['lasagna'],
                "Lasanha",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['muffin'],
                "Bolinho",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['taco'],
                "Taco",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['cupcake'],
                "Cupcake",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['steak'],
                "Bife",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['roast_chicken'],
                "Frango A.",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['donut'],
                "Donut",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['fried_fish'],
                "Peixe Frito",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['fries'],
                "Fritas",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['omelete'],
                "Omelete",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['pancakes'],
                "Panquecas",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['ice_cream'],
                "Sorvete",
                dish_font,
                (93, 52, 29),
                enable_scale=True,
                max_scale=1.1,
                text_align='bottom',
                text_padding=5,
                hover_sound="hover",
            ),
            UIButton(
                0, 0,
                bg_image,
                dishes_images['add'],
                enable_scale=True,
                max_scale=1.1,
                hover_sound="hover",
            )
        ]

        card_h = self.dish_cards[0].original_size[1]
        rows = math.ceil(len(self.dish_cards) / 4)
        self.max_scroll = max(0, rows * (card_h + 10) + self.margin_y - self.dish_list.get_height())

        # Scrollbar da lista
        self.scrollbar = UIScrollbar(538, 105, 335, self.max_scroll + 346, 346)

        # Botão de retorno
        back_img = pygame.image.load('graphics/sprites/go_back.png')
        self.go_back = UIButton(self.config.SCREEN['width'] - 165, 15, back_img, enable_scale=True,)

        # Título
        title_font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 40)
        self.title_text = render_text_with_outline(title_font, "CARDÁPIO", (255, 255, 255), (0, 0, 0))
        self.title_rect = self.title_text.get_rect(centerx=self.config.SCREEN['width'] // 2)
        self.title_rect.top = 15

        # Botões de adicionar/remover
        btn_img = pygame.image.load('graphics/sprites/menu_button_1.png')
        font = pygame.font.SysFont('arial', 20)
        self.add_button = UIButton(360, 460, btn_img, text="Adicionar", font=font, enable_scale=True)
        self.exclude_button = UIButton(500, 460, btn_img, text="Remover", font=font, enable_scale=True,)

    def update(self, dt):
        """
        Atualiza a interface e a animação dos elementos do menu.

        :param dt: Delta time.
        """
        super().update(dt)

        if self.animation_done and not self.closing:
            self.scrollbar.update(dt)
            self.scroll_offset = self.scrollbar.get_scroll_offset()

            # Posição do mouse relativa à lista com rolagem
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_rel = (mouse_x - 142, mouse_y - 88 + self.scroll_offset)

            for i, card in enumerate(self.dish_cards):
                row = i // 4
                col = i % 4
                card.x = self.margin_x + col * (card.original_size[0] + 4)
                card.y = self.margin_y + row * (card.original_size[1] + 4)
                card.update_position(offset_x=142, offset_y=98 - self.scroll_offset)
                card.update(dt)

            self.add_button.update(dt)
            self.exclude_button.update(dt)
            self.go_back.update(dt)

    def render(self, screen):
        """
        Renderiza a interface do menu sobre a surface do jogo.

        :param screen: Surface principal onde o menu será desenhado.
        """
        self.menu_surface.fill((0, 0, 0, 0))
        self.menu_surface.blit(self.bg_image, self.bg_rect)

        if self.animation_done and not self.closing:
            y_offset = 0
            self.dish_list.fill((0, 0, 0, 0))

            # Renderiza os cards (não hovered → hovered)
            for card in self.dish_cards:
                if not card.hovered:
                    card.render_on_surface(self.dish_list, offset_y=-self.scroll_offset)

                for card in self.dish_cards:
                    if card.hovered:
                        card.render_on_surface(self.dish_list, offset_y=-self.scroll_offset)

            self.menu_surface.blit(self.dish_list, (142, 98 + y_offset))
            self.menu_surface.blit(self.title_text, (self.title_rect.left, self.title_rect.top + y_offset))
            self.add_button.render_at(self.menu_surface, y_offset=y_offset)
            self.exclude_button.render_at(self.menu_surface, y_offset=y_offset)
            self.scrollbar.render_at(self.menu_surface, y_offset=y_offset)
            self.go_back.render_at(self.menu_surface, y_offset=y_offset)

        # Chama o render da animação base (fade-in/fade-out e movimento)
        super().render(screen)

    def handle_event(self, event):
        """
        Processa eventos como clique no botão de voltar e rolagem.

        :param event: Evento do pygame.
        """
        if self.animation_done and not self.closing:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.go_back.rect.collidepoint(event.pos):
                    self.start_closing()
            self.scrollbar.handle_event(event)

    def on_close(self):
        """
        Chamado automaticamente quando a animação de fechamento termina.
        Remove a referência ao menu na instância principal do jogo.
        """
        self.game.menu = None
