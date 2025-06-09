"""
Módulo menu.

Contém as classes MenuButton e MainMenu, responsáveis pela exibição e animação
da tela principal do jogo Kitchen Rush, incluindo céu animado, chef animado,
botões interativos e efeito de transição com fade-in/fade-out.
"""

import pygame
import math

from settings import Settings
from core.gui.ui_button import UIButton
from core.states.restaurant_select import RestaurantSelect
from utils.audio_manager import audio_manager


class MenuButton(UIButton):
    """
    Botão animado do Menu Principal.

    Surge de baixo da tela com atraso controlado (delay) e
    possui animação reversa ao sair da tela. Ideal para menus estilizados.
    """

    def __init__(self, image_path, x, y, delay=0.0, scale=1.0):
        """
        Inicializa o botão com sua imagem, posição final e atraso inicial.

        :param image_path: Caminho para a imagem do botão.
        :param x: Posição X final do botão.
        :param y: Posição Y final do botão.
        :param delay: Tempo de atraso antes da animação iniciar.
        :param scale: Escala (não usada diretamente, pode ser futura expansão).
        """
        self.config = Settings()
        bg_image = pygame.image.load(image_path).convert_alpha()

        super().__init__(
            x=x,
            y=self.config.SCREEN['height'] + 100,  # inicia fora da tela (parte inferior)
            bg_image=bg_image,
            enable_scale=True,
            max_scale=1.15,
            scale_speed=15.0,
            hover_sound="hover",       # nome do som de hover no audio_manager
            click_sound="click"     # nome do som de clique no audio_manager
        )

        self.target_x = x
        self.target_y = y
        self.delay = delay
        self.anim_timer = 0.0
        self.appeared = False

    def update(self, dt, anim_enabled=True):
        """
        Atualiza a posição do botão com animação suave e aplica hover.

        :param dt: Delta time.
        :param anim_enabled: Indica se a animação inicial está ativa.
        """
        if anim_enabled:
            self.anim_timer += dt
            if not self.appeared and self.anim_timer >= self.delay:
                self.y += (self.target_y - self.y) * min(10 * dt, 1)
                if abs(self.y - self.target_y) < 1:
                    self.y = self.target_y
                    self.appeared = True

        self.fixed_rect.topleft = (self.x, self.y)
        super().update(dt)

    def reverse_exit(self, dt):
        """
        Move o botão de volta para fora da tela de forma suave (efeito de saída).
        """
        self.y += (self.config.SCREEN['height'] + 100 - self.y) * min(10 * dt, 1)
        self.rect = self.get_scaled_rect()


class MainMenu:
    """
    Representa a tela principal do menu do jogo Kitchen Rush.

    Inclui animações de fundo, título, personagem e botões.
    Responsável também pela transição para o próximo estado do jogo.
    """

    def __init__(self, game):
        """
        Inicializa todos os elementos visuais do menu.

        :param game: Referência ao objeto principal do jogo.
        """
        self.game = game
        self.config = Settings()

        # Imagens de fundo
        self.sky_image = pygame.image.load('graphics/backgrounds/sky_bg.png')
        self.bg_image = pygame.image.load('graphics/backgrounds/title_bg.png').convert_alpha()
        self.sky_x = 0
        self.sky_speed = 20

        # Título animado
        self.title_image = pygame.image.load('graphics/sprites/title_logo.png').convert_alpha()
        self.title_alpha = 0
        self.title_white_alpha = 255  # brilho branco inicial

        # Personagem chef
        self.chef_image = pygame.image.load('graphics/images/chef.png').convert_alpha()
        self.chef_x = self.config.SCREEN['width'] + 300
        self.chef_target_x = 420
        self.chef_y = 0
        self.chef_breath = 0  # efeito de "respiração"

        # Controle de animação
        self.anim_time = 0
        self.fade_alpha = 255
        self.delay_before_fade = 0.5
        self.fade_done = False
        self.exiting = False
        self.exit_fade = 0

        # Botões com efeito de entrada e delay
        self.buttons = {
            'play': MenuButton('graphics/sprites/button_play.png', 95, 170, delay=0.00),
            'continue': MenuButton('graphics/sprites/button_continue.png', 95, 250, delay=0.10),
            'settings': MenuButton('graphics/sprites/button_settings.png', 95, 331, delay=0.20),
            'quit': MenuButton('graphics/sprites/button_quit.png', 95, 412, delay=0.30),
        }

        # Cursor personalizado
        self.cursor_image = pygame.image.load(self.config.MOUSE['image'])
        self.cursor_image = pygame.transform.scale(self.cursor_image, (57, 40))
        pygame.mouse.set_visible(False)

    def update(self, dt):
        """
        Atualiza todos os elementos da tela do menu.

        :param dt: Delta time.
        """
        # Scroll do céu
        self.sky_x -= self.sky_speed * dt
        if self.sky_x <= -self.sky_image.get_width():
            self.sky_x = 0

        self.anim_time += dt

        # Fade-in inicial
        if self.anim_time > self.delay_before_fade:
            self.fade_alpha = max(0, self.fade_alpha - dt * 300)
            if self.fade_alpha <= 0:
                self.fade_done = True

        # Se o fade inicial terminou, anima os elementos
        if self.fade_done and not self.exiting:
            self.chef_x += (self.chef_target_x - self.chef_x) * min(5 * dt, 1)
            self.chef_breath += dt

            self.title_alpha = min(255, self.title_alpha + dt * 255)
            if self.title_alpha >= 255:
                self.title_white_alpha = max(0, self.title_white_alpha - dt * 255)

            for button in self.buttons.values():
                button.update(dt, anim_enabled=True)

        elif self.exiting:
            # Animação de saída reversa
            self.chef_x += (self.config.SCREEN['width'] + 300 - self.chef_x) * min(5 * dt, 1)
            self.title_alpha = max(0, self.title_alpha - dt * 550)
            self.exit_fade = min(255, self.exit_fade + dt * 300)
            for button in self.buttons.values():
                button.reverse_exit(dt)

    def render(self, screen):
        """
        Renderiza todos os elementos visuais na tela do menu.

        :param screen: Surface principal do jogo onde será desenhado.
        """
        # Fundo animado
        screen.blit(self.sky_image, (self.sky_x, 0))
        screen.blit(self.sky_image, (self.sky_x + self.sky_image.get_width(), 0))
        screen.blit(self.bg_image, (0, 0))

        # Chef com efeito de respiração
        breath_scale = 1 + 0.01 * math.sin(self.chef_breath * 2)
        chef_scaled = pygame.transform.scale(
            self.chef_image,
            (self.chef_image.get_width(), int(self.chef_image.get_height() * breath_scale))
        )
        screen.blit(chef_scaled, (int(self.chef_x), self.chef_y))

        # Título com fade e brilho branco
        if self.title_alpha > 0:
            title_copy = self.title_image.copy().convert_alpha()
            title_copy.set_alpha(int(self.title_alpha))
            screen.blit(title_copy, (58, 10))

        if self.title_alpha >= 255 and self.title_white_alpha > 0:
            flash = self.title_image.copy().convert_alpha()
            flash.fill((255, 255, 255, int(self.title_white_alpha)), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash, (58, 10))

        # Botões
        for button in self.buttons.values():
            button.render(screen)

        # Fade-in inicial
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.config.SCREEN['width'], self.config.SCREEN['height']))
            fade_surface.set_alpha(int(self.fade_alpha))
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))

        # Fade final (saída)
        if self.exiting and self.exit_fade > 0:
            fade_surface = pygame.Surface((self.config.SCREEN['width'], self.config.SCREEN['height']))
            fade_surface.set_alpha(int(self.exit_fade))
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
            if self.exit_fade >= 255:
                self.game.change_state(RestaurantSelect(self.game))

        # Créditos no rodapé
        credit_font = pygame.font.Font(None, 20)
        credit_text = credit_font.render("© 2025 Quantum Games · Criado por Luiz R. Dererita", True, (200, 200, 200))
        credit_rect = credit_text.get_rect(center=(self.config.SCREEN["width"] // 2, self.config.SCREEN["height"] - 15))
        screen.blit(credit_text, credit_rect)

        # Cursor do mouse customizado
        screen.blit(self.cursor_image, pygame.mouse.get_pos())

    def handle_event(self, event):
        """
        Processa eventos de entrada do jogador (mouse).

        :param event: Evento capturado pelo Pygame.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['play'].rect.collidepoint(event.pos):
                self.exiting = True

            # Toca o efeito de clique dos botões
            for button in self.buttons.values():
                button.handle_event(event)
