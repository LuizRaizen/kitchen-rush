"""Módulo que armazena os elementos da HUD do jogo."""

import pygame
import math

from settings import Settings
from utils.audio_manager import audio_manager


# assets/hud.py (ou onde sua classe Money vive)
import pygame
from settings import Settings  # só se você usar para carregar imagem/fonte fora daqui

class Money:
    """HUD que exibe/atualiza o dinheiro do RESTAURANTE ATIVO do jogador."""
    def __init__(self, x, y, image, font, game):
        self.x = x
        self.y = y
        self.image = image     # sprite de fundo (money_1.png)
        self.font = font
        self.game = game       # precisamos do game para chegar no player -> restaurante ativo

    # --- util ---
    @staticmethod
    def _fmt(v: int) -> str:
        # 2 casas, separador pt-BR visual (se quiser manter $ com ponto, troque por f"${v:.2f}")
        return f"$ {v}"

    def _active_restaurant(self):
        player = getattr(self.game, "player", None)
        if player and hasattr(player, "get_active_restaurant"):
            return player.get_active_restaurant()
        return None

    # --- API pública (atalhos que atuam no restaurante ativo) ---
    def get_amount(self) -> int:
        r = self._active_restaurant()
        return r.money if r else 0

    def set_amount(self, value: int):
        r = self._active_restaurant()
        if r is not None:
            r.money = value

    def add(self, value: int):
        r = self._active_restaurant()
        if r is not None:
            r.money = r.money + value

    def spend(self, value: int) -> bool:
        r = self._active_restaurant()
        if r is None:
            return False
        value = value
        if r.money >= value:
            r.money -= value
            return True
        return False

    # --- desenho ---
    def render(self, screen: pygame.Surface):
        # fundo
        screen.blit(self.image, (self.x, self.y))

        # texto centralizado no badge
        amount = self.get_amount()
        text = self.font.render(self._fmt(amount), True, (65, 40, 20))
        cx = self.x + self.image.get_width() // 2
        cy = self.y + 38  # ajusta conforme seu sprite
        text_rect = text.get_rect(center=(cx, cy))
        screen.blit(text, text_rect)


class Clock:
    """Classe que representa o relógio de parede do jogo."""
    def __init__(self, x, y, clock_image, font):
        self.x = x
        self.y = y
        self.image = clock_image
        self.font = font
        self.elapsed_time = 0
        self.total_duration = 12 * 60  # 12 minutos em segundos

    def update(self, dt):
        self.elapsed_time += dt
        if self.elapsed_time > self.total_duration:
            self.elapsed_time = self.total_duration

    def render(self, screen):
        # Desenha o relógio base
        screen.blit(self.image, (self.x, self.y))

        # Tempo atual
        time_ratio = self.elapsed_time / self.total_duration
        game_minutes = int(time_ratio * 720)  # 12 horas = 720 minutos

        hours = 12 + (game_minutes // 60)
        minutes = game_minutes % 60

        # Quando ultrapassa 23h, vira 00h
        if hours >= 24:
            hours -= 24

        # Exibição final
        time_str = f"{hours:02}:{minutes:02}"

        # Desenhar ponteiro
        center = (self.x + 40, self.y + 48)
        angle = -90 + time_ratio * 360  # começa apontando para cima
        length = 15
        end_x = center[0] + math.cos(math.radians(angle)) * length
        end_y = center[1] + math.sin(math.radians(angle)) * length
        pygame.draw.line(screen, (60, 40, 20), center, (end_x, end_y), 4)

        # Desenhar hora
        text = self.font.render(time_str, True, (255, 255, 220))
        screen.blit(text, (self.x + 90, self.y + 20))
        