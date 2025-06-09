"""
Módulo phase_opening.

Contém a classe PhaseOpening, responsável por exibir uma tela inicial
antes de começar a fase de atendimento. O jogador deve confirmar a
equipe escalada antes de prosseguir para a próxima fase do jogo.
"""

import pygame
from core.states.phase_service import PhaseService


class PhaseOpening:
    """
    Tela de preparação antes da fase de atendimento.

    Permite ao jogador revisar e confirmar a equipe do dia antes de iniciar
    o turno. Após clicar em "Iniciar Atendimento", a fase de serviço é iniciada.
    """

    def __init__(self, game):
        """
        Inicializa a tela de abertura da fase.

        :param game: Referência ao objeto principal do jogo.
        """
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.SysFont("arial", 28)

        # Botão para confirmar e iniciar a fase
        self.confirm_button = pygame.Rect(700, 470, 200, 50)

    def update(self, dt):
        """
        Atualiza o estado da tela. (No momento, não há lógica dinâmica.)

        :param dt: Delta time.
        """
        pass  # Lógica futura para animações ou elementos interativos

    def draw(self):
        """
        Desenha a tela de abertura da fase, incluindo o botão de confirmação.
        """
        # Fundo da tela
        self.screen.fill((230, 210, 180))

        # Texto informativo
        text = self.font.render("Escolha os funcionários para o dia!", True, (60, 30, 10))
        self.screen.blit(text, (50, 30))

        # Botão "Iniciar Atendimento"
        pygame.draw.rect(self.screen, (60, 150, 80), self.confirm_button)
        confirm = self.font.render("Iniciar Atendimento", True, (255, 255, 255))
        self.screen.blit(confirm, (self.confirm_button.x + 10, self.confirm_button.y + 10))

    def handle_event(self, event):
        """
        Lida com eventos do pygame, como cliques do mouse.

        :param event: Evento atual capturado pelo pygame.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.confirm_button.collidepoint(event.pos):
                # Transição para a fase de atendimento
                self.game.change_state(PhaseService(self.game))
