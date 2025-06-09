"""
Módulo supermarket.

Contém a interface do supermercado onde o jogador pode visualizar e comprar ingredientes.
Inclui rolagem com barra vertical, animação de entrada/saída e botões de interação.
"""

import pygame
import math

from settings import Settings
from core.effects.animated_popup import AnimatedPopup
from core.gui.ui_button import UIButton
from core.gui.ui_scrollbar import UIScrollbar
from utils.functions import render_text_with_outline


class IngredientCard:
    """
    Representa uma carta de ingrediente no supermercado.
    Cada carta exibe a imagem, ícone, nome, preço e pode ser renderizada com offset de rolagem.
    """

    def __init__(self, x, y, bg_image, icon_image, name, price):
        """
        Inicializa os atributos da carta de ingrediente.

        :param x: Posição X inicial.
        :param y: Posição Y inicial.
        :param bg_image: Imagem de fundo da carta.
        :param icon_image: Ícone do ingrediente.
        :param name: Nome do ingrediente.
        :param price: Preço do ingrediente.
        """
        self.x = x
        self.y = y
        self.bg_image = bg_image
        self.icon_image = icon_image
        self.name = name
        self.price = price
        self.quantity = 0
        self.original_size = bg_image.get_size()
        self.rect = pygame.Rect(x, y, *self.original_size)

    def update_position(self, x, y):
        """
        Atualiza a posição da carta.

        :param x: Nova coordenada X.
        :param y: Nova coordenada Y.
        """
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def draw(self, surface, scroll_offset=0):
        """
        Desenha a carta na superfície fornecida, ajustando pela rolagem.

        :param surface: Surface onde a carta será desenhada.
        :param scroll_offset: Offset vertical de rolagem.
        """
        draw_x = self.x
        draw_y = self.y - scroll_offset
        surface.blit(self.bg_image, (draw_x, draw_y))
        surface.blit(self.icon_image, (draw_x, draw_y))


class Supermarket(AnimatedPopup):
    """
    Tela de supermercado onde o jogador pode comprar ingredientes.
    Herda comportamento animado de entrada/saída da classe AnimatedPopup.
    """

    def __init__(self, game):
        """
        Inicializa a tela do supermercado com layout, botões e cartas de ingredientes.

        :param game: Referência à instância principal do jogo.
        """
        self.game = game
        self.config = Settings()

        # Fundo da tela
        self.content_surface = pygame.image.load('graphics/images/supermarket_bg.png')
        super().__init__(
            screen_width=self.config.SCREEN['width'],
            screen_height=self.config.SCREEN['height'],
            content_surface=self.content_surface,
            open_sound="swipe",
            close_sound="swipe"
        )

        # Superfície onde os cards serão desenhados
        self.list_surface = pygame.Surface((400, 346), pygame.SRCALPHA)

        self.scroll_offset = 0
        self.scroll_speed = 20
        self.margin_x = 10
        self.margin_y = 10

        # Carrega imagens padrão dos ingredientes
        bg = pygame.image.load('graphics/sprites/dish_card.png')
        icon = pygame.image.load('graphics/sprites/lock.png')

        # Cria a lista de cartas de ingredientes
        self.ingredient_cards = [
            IngredientCard(0, 0, bg, icon, f"Ingrediente {i}", price=5 + i) for i in range(20)
        ]

        # Barra de rolagem vertical
        self.scrollbar = UIScrollbar(
            x=550,
            y=100,
            height=346,
            content_height=math.ceil(len(self.ingredient_cards) / 2) * (bg.get_height() + 10),
            view_height=346
        )

        # Botão de voltar
        button_image = pygame.image.load('graphics/sprites/go_back.png')
        self.go_back = UIButton(self.config.SCREEN['width'] - 165, 15, button_image, enable_scale=True,)

        # Título da tela
        title_font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 40)
        self.title_text = render_text_with_outline(title_font, "SUPERMERCADO", (255, 255, 255), (0, 0, 0))
        self.title_rect = self.title_text.get_rect(centerx=self.config.SCREEN['width'] // 2)
        self.title_rect.top = 25

    def update(self, dt):
        """
        Atualiza a animação da popup, rolagem e posição dos cards.

        :param dt: Delta time.
        """
        super().update(dt)

        if self.animation_done and not self.closing:
            self.scroll_offset = self.scrollbar.get_scroll_offset()

            # Atualiza posição dos cards
            for i, card in enumerate(self.ingredient_cards):
                row = i // 2
                col = i % 2
                x = self.margin_x + col * (card.original_size[0] + 10)
                y = self.margin_y + row * (card.original_size[1] + 10)
                card.update_position(x, y)

            self.scrollbar.update(dt)
            self.go_back.update(dt)

    def render(self, screen):
        """
        Desenha todos os elementos da tela do supermercado.

        :param screen: Surface principal do jogo.
        """
        super().render(screen)

        if self.animation_done and not self.closing:
            self.list_surface.fill((0, 0, 0, 0))

            # Desenha os cards dos ingredientes
            for card in self.ingredient_cards:
                card.draw(self.list_surface, self.scroll_offset)

            screen.blit(self.list_surface, (142, 88))
            screen.blit(self.title_text, self.title_rect)
            self.scrollbar.render(screen)
            self.go_back.render(screen)

    def handle_event(self, event):
        """
        Lida com eventos de clique nos botões e rolagem.

        :param event: Evento do pygame.
        """
        if self.animation_done and not self.closing:
            self.scrollbar.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.go_back.rect.collidepoint(event.pos):
                    self.start_closing()

    def on_close(self):
        """
        Chamado automaticamente ao encerrar a animação de saída.
        Remove a referência à tela de supermercado.
        """
        self.game.supermarket = None
