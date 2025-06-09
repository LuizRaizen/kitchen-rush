"""
Módulo para armazenar a classe que anima os popups do jogo.

A classe AnimatedPopup fornece uma base reutilizável para janelas popup com
animações suaves de entrada (fade e deslocamento) e saída.
"""

import pygame
from utils.audio_manager import audio_manager


class AnimatedPopup:
    """
    Classe base para popups animados com entrada e saída suaves.

    Essa classe implementa animações LERP verticais (movimento) e 
    transição de opacidade no fundo (fade) para destacar o conteúdo.
    """

    def __init__(
        self,
        screen_width,
        screen_height,
        content_surface,
        y_offset=230,
        fade_speed=300,
        move_speed=12.0,
        bg_alpha=180,
        open_sound=None,
        close_sound=None
    ):
        """
        Inicializa a popup com configurações de animação.

        :param screen_width: Largura da tela.
        :param screen_height: Altura da tela.
        :param content_surface: Superfície que representa o conteúdo do popup.
        :param y_offset: Distância inicial (fora da tela) para o movimento vertical.
        :param fade_speed: Velocidade de fade do fundo escurecido.
        :param move_speed: Velocidade da animação de movimento (LERP).
        :param bg_alpha: Alpha máximo do fundo escurecido.
        :param sound_on_open: Se True, reproduz som ao abrir.
        :param sound_on_close: Se True, reproduz som ao fechar.
        :param open_sound_name: Nome do efeito sonoro de abertura.
        :param close_sound_name: Nome do efeito sonoro de fechamento.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Superfície do conteúdo
        self.content = content_surface
        self.content_rect = self.content.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # Retângulo usado para o movimento vertical animado
        self.rect = self.content.get_rect(center=(screen_width // 2, screen_height + y_offset))
        self.start_y = float(screen_height + y_offset)
        self.final_y = float(screen_height // 2)
        self.current_y = self.start_y
        self.target_y = self.final_y

        self.move_speed = move_speed
        self.animation_done = False
        self.closing = False

        # Superfície do fundo escurecido
        self.bg_surface = pygame.Surface((screen_width, screen_height))
        self.bg_alpha = 0
        self.max_alpha = bg_alpha
        self.fade_speed = fade_speed
        self.bg_surface.set_alpha(self.bg_alpha)

        # Efeitos sonoros opcionais
        self.open_sound = open_sound
        self.close_sound = close_sound

        if self.open_sound:
            audio_manager.play_sound(self.open_sound)

    def start_closing(self):
        """
        Inicia a animação de saída (fechamento) da popup.
        """
        self.closing = True
        self.animation_done = False
        self.target_y = self.start_y

        if self.close_sound:
            audio_manager.play_sound(self.close_sound)

    def set_content_surface(self, new_surface):
        """
        Atualiza a superfície de conteúdo da popup, mantendo a posição central.

        :param new_surface: Nova surface pygame a ser exibida na popup.
        """
        self.content = new_surface
        self.content_rect = self.content.get_rect(center=(self.rect.centerx, int(self.current_y)))

    def update(self, dt):
        """
        Atualiza a animação da popup, incluindo posição vertical e opacidade do fundo.

        :param dt: Delta time (tempo desde o último frame), usado para suavizar animações.
        """
        # Animação de posição vertical (LERP)
        self.current_y += (self.target_y - self.current_y) * min(self.move_speed * dt, 1)

        # Verifica se a animação terminou
        if abs(self.current_y - self.target_y) < 0.5:
            self.current_y = self.target_y
            if self.closing:
                self.on_close()
            else:
                self.animation_done = True

        self.rect.centery = int(self.current_y)

        # Animação de opacidade do fundo (fade-in / fade-out)
        if self.closing:
            self.bg_alpha -= self.fade_speed * dt
        else:
            self.bg_alpha += self.fade_speed * dt

        self.bg_alpha = max(0, min(self.max_alpha, self.bg_alpha))
        self.bg_surface.set_alpha(int(self.bg_alpha))

    def render(self, screen):
        """
        Renderiza o fundo escurecido e o conteúdo da popup animado verticalmente.

        :param screen: Surface principal onde tudo será desenhado.
        """
        screen.blit(self.bg_surface, (0, 0))

        # Garante que o conteúdo esteja posicionado corretamente
        content_draw_rect = self.content.get_rect(center=(self.screen_width // 2, int(self.current_y)))
        screen.blit(self.content, content_draw_rect)

    def handle_event(self, event):
        """
        Manipula eventos do pygame.

        Esse método deve ser sobrescrito pelas subclasses que usam a popup.

        :param event: Evento pygame (ex: clique do mouse).
        """
        pass

    def on_close(self):
        """
        Método abstrato chamado quando a animação de saída termina.

        Deve ser implementado pela subclasse para definir o comportamento
        após o fechamento da popup.
        """
        raise NotImplementedError("Subclasse deve definir o que fazer ao fechar.")
