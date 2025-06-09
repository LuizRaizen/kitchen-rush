"""Módulo para representar os pedidos dos clientes."""

import random
from core.assets.menu import MENU

class Order:
    """Classe do jogo."""
    def __init__(self, customer):
        self.customer = customer
        self.dish = random.choice(MENU)
        self.status = "waiting"  # waiting, preparing, ready, served
        self.progress = 0  # progresso de preparo (0 a 100)

    def update(self, dt):
        if self.status == "preparing":
            self.progress += dt * (100 / self.dish.prep_time)
            if self.progress >= 100:
                self.status = "ready"

    def __str__(self):
        return f"{self.dish.name} ({self.status})"
