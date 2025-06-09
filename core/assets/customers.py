"""Módulo que armazena as classes para criar os clientes do jogo."""

import pygame
import random
from core.assets.order import Order

class Customer:
    """Classe do jogo."""
    def __init__(self, id):
        self.id = id
        self.status = "waiting"  # waiting, eating, done, left
        self.order = Order(self)
        self.timer = 0
        self.satisfaction = 1.0

    def update(self, dt):
        if self.status == "waiting":
            self.timer += dt
            if self.timer >= self.patience:
                self.status = "left"
                self.satisfaction = 0.0

    def serve(self):
        self.status = "eating"
        self.timer = 0

    def finish(self):
        self.status = "done"
        self.satisfaction = max(0.4, self.patience / self.max_patience)

    def get_tip(self):
        return int(self.order.dish.price * self.satisfaction)

    def draw(self, screen, x, y, font):
        if self.status == "left":
            return  # não desenha se já saiu
        pygame.draw.rect(screen, (200, 100, 80), (x, y, 40, 40))
        label = font.render(f"C{self.id}", True, (255, 255, 255))
        screen.blit(label, (x + 5, y + 5))


class CommonCustomer(Customer):
    """Classe do jogo."""
    def __init__(self, id):
        super().__init__(id)
        self.type = "comum"
        self.patience = random.uniform(15, 20)
        self.max_patience = self.patience

    def draw(self, screen, x, y, font):
        pygame.draw.rect(screen, (80, 130, 200), (x, y, 40, 40))
        text = font.render(f"C{self.id}", True, (255, 255, 255))
        screen.blit(text, (x + 5, y + 5))

        if self.status == "waiting":
            order_text = font.render(self.order.dish.name, True, (0, 0, 0))
            screen.blit(order_text, (x + 50, y + 5))


class ImpatientCustomer(Customer):
    """Classe do jogo."""
    def __init__(self, id):
        super().__init__(id)
        self.type = "apressado"
        self.patience = random.uniform(8, 12)
        self.max_patience = self.patience

    def draw(self, screen, x, y, font):
        pygame.draw.rect(screen, (200, 80, 80), (x, y, 40, 40))
        text = font.render(f"I{self.id}", True, (255, 255, 255))
        screen.blit(text, (x + 5, y + 5))

        if self.status == "waiting":
            order_text = font.render(self.order.dish.name, True, (0, 0, 0))
            screen.blit(order_text, (x + 50, y + 5))


class BossCustomer(Customer):
    """Classe do jogo."""
    def __init__(self, id):
        super().__init__(id)
        self.type = "boss"
        self.patience = random.uniform(25, 30)
        self.max_patience = self.patience
        self.reward_multiplier = 2.0

    def get_tip(self):
        return int(self.order.dish.price * self.satisfaction * self.reward_multiplier)

    def draw(self, screen, x, y, font):
        pygame.draw.rect(screen, (120, 60, 180), (x, y, 50, 50))
        text = font.render(f"B{self.id}", True, (255, 255, 0))
        screen.blit(text, (x + 5, y + 5))

        if self.status == "waiting":
            order_text = font.render(self.order.dish.name, True, (0, 0, 0))
            screen.blit(order_text, (x + 50, y + 5))
