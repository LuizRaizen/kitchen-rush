"""
Módulo game.

Define a classe principal do jogo, responsável por gerenciar o estado atual (tela ativa)
e delegar atualizações, renderizações e eventos para o estado correspondente.
"""

from core.states.splash_screen import SplashScreen
from settings import Settings


class Game:
    """
    Classe principal do jogo.

    Gerencia o estado atual (como menus, gameplay, splash screen),
    e delega a atualização, renderização e eventos para a tela ativa.
    """

    def __init__(self):
        """
        Inicializa o jogo com as configurações e define o primeiro estado (SplashScreen).
        """
        self.config = Settings()
        self.state = SplashScreen(self)

    def change_state(self, new_state):
        """
        Troca o estado atual do jogo para um novo estado.

        :param new_state: Instância da nova tela/estado (ex: MainMenu, PhaseService).
        """
        self.state = new_state

    def update(self, dt):
        """
        Atualiza o estado atual do jogo.

        :param dt: Delta time (tempo entre frames).
        """
        self.state.update(dt)

    def render(self, screen):
        """
        Renderiza o estado atual na tela.

        :param screen: Surface principal do jogo onde tudo será desenhado.
        """
        self.state.render(screen)

    def handle_event(self, event):
        """
        Encaminha eventos de entrada (ex: mouse, teclado) para o estado atual.

        :param event: Evento do pygame.
        """
        self.state.handle_event(event)
