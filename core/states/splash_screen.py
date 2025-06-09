"""
Módulo splash_screen.

Exibe uma tela inicial com animação de fade-in e fade-out contendo o logo do estúdio
antes da transição para o menu principal do jogo.
"""

import pygame
from core.states.main_menu import MainMenu


class SplashScreen:
    """
    Tela de splash screen que mostra o logo do estúdio com animações suaves.

    Estágios:
        - fade_in_screen: tela branca aparece gradualmente.
        - fade_in_logo: o logo do estúdio surge com fade-in.
        - wait: mantém logo visível por 2 segundos.
        - fade_out: fade-out da tela e logo, depois transita para o menu principal.
    """

    def __init__(self, game):
        """
        Inicializa a splash screen.

        :param game: Referência à instância principal do jogo.
        """
        self.game = game
        self.config = game.config

        # Superfície branca usada no fundo da splash
        self.white_surface = pygame.Surface((self.config.SCREEN["width"], self.config.SCREEN["height"]))
        self.white_surface.fill((255, 255, 255))
        self.white_alpha = 0

        # Carregamento do logo e posicionamento central
        self.logo = pygame.image.load("graphics/images/splash_logo.png").convert_alpha()
        self.logo_alpha = 0
        self.logo.set_alpha(0)
        self.logo_rect = self.logo.get_rect(center=(
            self.config.SCREEN["width"] // 2,
            self.config.SCREEN["height"] // 2
        ))

        # Controle de tempo e estágio da animação
        self.timer = 0
        self.stage = "fade_in_screen"

    def update(self, dt):
        """
        Atualiza a animação da splash screen de acordo com o estágio atual.

        :param dt: Delta time.
        """
        if self.stage == "fade_in_screen":
            self.white_alpha += dt * 200
            if self.white_alpha >= 255:
                self.white_alpha = 255
                self.stage = "fade_in_logo"

        elif self.stage == "fade_in_logo":
            self.logo_alpha += dt * 200
            if self.logo_alpha >= 255:
                self.logo_alpha = 255
                self.stage = "wait"
                self.timer = 0

        elif self.stage == "wait":
            self.timer += dt
            if self.timer >= 2.0:
                self.stage = "fade_out"

        elif self.stage == "fade_out":
            self.white_alpha -= dt * 200
            self.logo_alpha -= dt * 200
            if self.white_alpha <= 0 and self.logo_alpha <= 0:
                self.white_alpha = 0
                self.logo_alpha = 0
                self.game.change_state(MainMenu(self.game))

        # Aplica os valores de alpha às surfaces
        self.white_surface.set_alpha(int(self.white_alpha))
        self.logo.set_alpha(int(self.logo_alpha))

    def render(self, screen):
        """
        Desenha os elementos visuais da splash screen na tela.

        :param screen: Surface principal do jogo.
        """
        screen.fill((0, 0, 0))  # Fundo preto
        screen.blit(self.white_surface, (0, 0))

        if self.logo_alpha > 0:
            screen.blit(self.logo, self.logo_rect.topleft)

    def handle_event(self, event):
        """
        Lida com eventos de entrada do jogador. (Atualmente não utilizado.)

        :param event: Evento capturado pelo pygame.
        """
        pass
