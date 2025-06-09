"""Módulo que armazena os elementos da HUD do jogo."""

import pygame
import math

from settings import Settings
from utils.audio_manager import audio_manager


class Money:
    """Classe que representa o lucro do restaurante."""
    def __init__(self, x, y, image, font):
        self.x = x
        self.y = y
        self.config = Settings()
        self.image = image  # sprite de fundo (money_1.png)
        self.font = font
        self.amount = self.config.MONEY['amount']

    def add(self, value):
        self.amount += value

    def spend(self, value):
        if self.amount >= value:
            self.amount -= value
            return True
        return False

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))
        text = self.font.render(f"$ {self.amount}", True, (65, 40, 20))
        text_rect = text.get_rect(center=(self.x + self.image.get_width() // 2, self.y + 38))
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
        