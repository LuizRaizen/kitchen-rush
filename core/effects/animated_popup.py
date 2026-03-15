"""
Módulo para armazenar a classe que anima os popups do jogo.

A classe AnimatedPopup fornece uma base reutilizável para janelas popup com
animações suaves de entrada (fade e deslocamento) e saída.
"""

from __future__ import annotations

from typing import Optional

import pygame
from utils.audio_manager import audio_manager


class AnimatedPopup:
    """
    Classe base para popups animados com entrada e saída suaves.

    Implementa:
    - Animações verticais estilo "LERP exponencial" (movimento).
    - Transição de opacidade no fundo (fade-in / fade-out).
    - Garantia de que a janela fica 100% fora de tela antes de fechar.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        content_surface: pygame.Surface,
        y_offset: int = 230,
        fade_speed: float = 300.0,
        move_speed: float = 12.0,
        bg_alpha: int = 180,
        open_sound: Optional[str] = None,
        close_sound: Optional[str] = None,
    ) -> None:
        """
        Inicializa a popup com configurações de animação.

        Parameters
        ----------
        screen_width : int
            Largura da tela.
        screen_height : int
            Altura da tela.
        content_surface : pygame.Surface
            Superfície que representa o conteúdo do popup.
        y_offset : int, optional
            Margem adicional fora da tela usada como "folga". Mantido por
            compatibilidade (default=230).
        fade_speed : float, optional
            Velocidade do fade do fundo escurecido (px/seg equivalente).
        move_speed : float, optional
            Velocidade do easing exponencial do movimento (fator por segundo).
        bg_alpha : int, optional
            Alpha máximo do fundo escurecido.
        open_sound : str | None, optional
            Nome do efeito sonoro ao abrir.
        close_sound : str | None, optional
            Nome do efeito sonoro ao fechar.
        """
        self.screen_width = int(screen_width)
        self.screen_height = int(screen_height)

        # Superfície do conteúdo
        self.content = content_surface
        self.content_rect = self.content.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )

        # Geometria de animação (vertical)
        self.move_speed = float(move_speed)
        self._y_margin = abs(int(y_offset))  # folga adicional

        # Posição "centro" (em y) e posições offscreen calculadas
        self.final_y = float(self.screen_height // 2)
        self._recompute_offscreen_targets()

        # Estado atual do movimento
        self.current_y = self.start_y
        self.target_y = self.final_y

        self.animation_done = False
        self.closing = False

        # Fundo escurecido (fade)
        self.bg_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.max_alpha = int(bg_alpha)
        self.fade_speed = float(fade_speed)
        self.bg_alpha = 0.0
        self.bg_surface.set_alpha(int(self.bg_alpha))

        # Efeitos sonoros opcionais
        self.open_sound = open_sound
        self.close_sound = close_sound

        if self.open_sound:
            audio_manager.play_sound(self.open_sound)

        # Retângulo lógico (atualizado no update/render)
        self.rect = self.content.get_rect(
            center=(self.screen_width // 2, int(self.current_y))
        )

    # ------------------------------------------------------------------ #
    # Helpers internos
    # ------------------------------------------------------------------ #
    def _recompute_offscreen_targets(self) -> None:
        """
        Recalcula as posições iniciais/finais fora da tela com base no
        tamanho do conteúdo. Garante que o popup fique 100% fora da tela.

        start_y: centro do conteúdo suficientemente abaixo da tela.
        """
        half_h = self.content.get_height() / 2.0
        # abaixo da tela: topo do conteúdo > screen_height
        self.start_y = float(self.screen_height) + half_h + self._y_margin

    def _is_fully_offscreen(self) -> bool:
        """
        Verifica se TODO o conteúdo está fora da tela (parte de baixo).
        Útil para garantir fechamento sem "resto" visível.
        """
        half_h = self.content.get_height() / 2.0
        top = self.current_y - half_h
        return top >= (self.screen_height + 1)

    def _at_target(self) -> bool:
        """Indica se a posição atual está suficientemente próxima do alvo."""
        return abs(self.current_y - self.target_y) < 0.5

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #
    def start_closing(self) -> None:
        """
        Inicia a animação de saída (fechamento) da popup.

        - Define o alvo como a posição totalmente fora de tela.
        - Dispara som de fechamento (se houver).
        """
        self.closing = True
        self.animation_done = False
        self.target_y = self.start_y

        if self.close_sound:
            audio_manager.play_sound(self.close_sound)

    def set_content_surface(self, new_surface: pygame.Surface) -> None:
        """
        Atualiza a Surface de conteúdo mantendo a posição central e
        recalcula as posições offscreen para garantir fechamento completo.

        Parameters
        ----------
        new_surface : pygame.Surface
            Nova surface a ser exibida na popup.
        """
        self.content = new_surface
        # mantém o mesmo X; o Y é animado por current_y
        self.content_rect = self.content.get_rect(
            center=(self.rect.centerx, int(self.current_y))
        )
        self._recompute_offscreen_targets()
        # Se estiver fechando, mantém alvo fora de tela com a nova altura
        if self.closing:
            self.target_y = self.start_y

    # ------------------------------------------------------------------ #
    # Ciclo de vida
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        """
        Atualiza a animação da popup, incluindo posição vertical e
        opacidade do fundo.

        Parameters
        ----------
        dt : float
            Delta time desde o último frame (em segundos).
        """
        # Movimento vertical (easing exponencial)
        self.current_y += (self.target_y - self.current_y) * min(self.move_speed * dt, 1.0)
        self.rect.centery = int(self.current_y)

        # Fade do fundo
        if self.closing:
            self.bg_alpha -= self.fade_speed * dt
        else:
            self.bg_alpha += self.fade_speed * dt

        self.bg_alpha = max(0.0, min(float(self.max_alpha), self.bg_alpha))
        self.bg_surface.set_alpha(int(self.bg_alpha))

        # Conclusão das animações
        if self.closing:
            # Fecha somente quando:
            # 1) atingiu o alvo (suficientemente),
            # 2) o fundo já está totalmente apagado
            # 3) e TODO o conteúdo está fora da tela
            if self._at_target() and self.bg_alpha <= 1.0 and self._is_fully_offscreen():
                self.on_close()
        else:
            # Quando abre e atinge o centro, marca como concluída
            if self._at_target():
                self.current_y = self.target_y
                self.animation_done = True

    def render(self, screen: pygame.Surface) -> None:
        """
        Renderiza o fundo escurecido e o conteúdo da popup animado verticalmente.

        Parameters
        ----------
        screen : pygame.Surface
            Surface principal onde tudo será desenhado.
        """
        screen.blit(self.bg_surface, (0, 0))

        # Posiciona o conteúdo no X central e Y animado
        content_draw_rect = self.content.get_rect(
            center=(self.screen_width // 2, int(self.current_y))
        )
        screen.blit(self.content, content_draw_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Manipula eventos do pygame.

        Subclasses devem sobrescrever quando necessário.

        Parameters
        ----------
        event : pygame.event.Event
            Evento do pygame (ex.: clique do mouse).
        """
        # Padrão: não consome eventos
        return

    def on_close(self) -> None:
        """
        Chamado quando a animação de saída termina.

        Subclasses DEVEM implementar para definir o comportamento após o
        fechamento do popup (ex.: desmontar a tela, limpar estados etc.).
        """
        raise NotImplementedError("Subclasse deve definir o que fazer ao fechar.")
