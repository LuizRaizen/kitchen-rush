"""Módulo que armazena a classe responsável por criar e administrar a tela de criação e seleção de restaurantes."""

import pygame

from settings import Settings
from core.gui.ui_button import UIButton
from core.states.tutorial import Tutorial


class RestaurantSelect:
    """Classe para criar e administrar a tela de restaurantes."""

    def __init__(self, game):
        self.game = game
        self.config = Settings()

        # Cria um botão de teste
        font = pygame.font.SysFont(None, 20)
        button_image = pygame.image.load('graphics/sprites/menu_button_1.png')
        x = self.config.SCREEN['width'] // 2
        y = self.config.SCREEN['height'] // 2
        self.buttom = UIButton(x, y, button_image, text="Selecionar", font=font)

        # Carrega a imagem do ponteiro do mouse
        self.cursor_image = pygame.image.load(self.config.MOUSE['image'])

        # Esconde o cursor padrão do sistema
        pygame.mouse.set_visible(False)

    def update(self, dt):
        self.buttom.update(dt)

    def render(self, screen):
        screen.fill((0, 0, 0))
        self.buttom.render(screen)

        # Desenha o cursor na posição do mouse
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.cursor_image, mouse_pos)

    def handle_event(self, event):
        """Processa eventos do mouse."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttom.rect.collidepoint(event.pos):
                self.game.change_state(Tutorial(self.game))
