"""Módulo para representar os pedidos dos clientes."""

import random
from core.assets.menu import PlayerMenu
from core.assets.dishes import Dish


class Order:
    """Representa um pedido feito por um cliente."""

    def __init__(self, customer, player_menu: PlayerMenu):
        self.customer = customer

        # escolhe um prato aleatório entre os pratos que o jogador já desbloqueou
        owned = player_menu.owned_dishes()
        if not owned:
            raise ValueError("O jogador não possui nenhum prato desbloqueado!")

        self.dish: Dish = random.choice(owned)

        self.status = "waiting"  # waiting, preparing, ready, served
        self.progress = 0.0      # progresso de preparo (0 a 100)

    def start_preparing(self):
        """Coloca o prato em preparo."""
        if self.status == "waiting":
            self.status = "preparing"
            self.progress = 0.0

    def update(self, dt: float):
        """Atualiza o progresso do preparo do prato."""
        if self.status == "preparing":
            prep_time = self.dish.effective_prep_time()
            self.progress += dt * (100.0 / prep_time)

            if self.progress >= 100.0:
                self.progress = 100.0
                self.status = "ready"

    def serve(self):
        """Marca o prato como servido ao cliente."""
        if self.status == "ready":
            self.status = "served"

    def __str__(self):
        return f"{self.dish.name} ({self.status} - {self.progress:.0f}%)"
