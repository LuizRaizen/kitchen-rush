"""Módulo que armazena as classes para criar os clientes do jogo."""

import pygame
import random
from core.assets.order import Order


class Customer:
    """Classe do jogo com suporte a paciência/temporizador."""

    def __init__(self, id, player_menu):
        self.id = id
        self.status = "waiting"  # waiting, eating, done, left
        self.order = Order(self, player_menu)
        self.timer = 0.0              # tempo esperando/consumindo
        self.satisfaction = 1.0

        # Estes dois são definidos nas subclasses:
        # self.patience        -> tempo total de paciência para "espera"
        # self.max_patience    -> usado para normalizar a satisfação

    # ---------- utilidades novas (para a mesa/medidor) ----------
    def patience_remaining(self) -> float:
        """Quanto falta (em segundos) para a paciência acabar, enquanto 'waiting'."""
        if self.status != "waiting":
            # se já comeu/saiu, consideramos 'cheio' para não influenciar o medidor
            return self.max_patience
        return max(0.0, self.patience - self.timer)

    def patience_ratio(self) -> float:
        """Percentual [0..1] da paciência restante (para o medidor)."""
        if self.max_patience <= 0:
            return 0.0
        # enquanto esperando: uso restante/max; caso contrário: 1.0 (não pressiona o medidor)
        return (self.patience_remaining() / self.max_patience) if self.status == "waiting" else 1.0

    # ------------------------------------------------------------

    def update(self, dt):
        if self.status == "waiting":
            self.timer += dt
            if self.timer >= self.patience:
                self.status = "left"
                self.satisfaction = 0.0

    def serve(self):
        self.status = "eating"
        self.timer = 0.0

    def finish(self):
        self.status = "done"
        # Usa a fração de paciência que sobrou na hora de servir para compor satisfação mínima
        frac = max(0.0, min(1.0, self.patience_remaining() / max(1e-6, self.max_patience)))
        self.satisfaction = max(0.4, frac)

    def get_tip(self):
        return int(self.order.dish.price * self.satisfaction)

    def draw(self, screen, x, y, font):
        if self.status == "left":
            return  # não desenha se já saiu
        pygame.draw.rect(screen, (200, 100, 80), (x, y, 40, 40))
        label = font.render(f"C{self.id}", True, (255, 255, 255))
        screen.blit(label, (x + 5, y + 5))


class CommonCustomer(Customer):
    """Cliente comum: paciência média."""
    def __init__(self, id, player_menu):
        super().__init__(id, player_menu)
        self.type = "comum"
        self.patience = random.uniform(70, 80)
        self.max_patience = self.patience

    def draw(self, screen, x, y, font):
        if self.status != "left":
            pygame.draw.rect(screen, (80, 130, 200), (x, y, 40, 40))
            text = font.render(f"C{self.id}", True, (255, 255, 255))
            screen.blit(text, (x + 5, y + 5))

            if self.status == "waiting":
                order_text = font.render(self.order.dish.name, True, (0, 0, 0))
                screen.blit(order_text, (x + 50, y + 5))


class ImpatientCustomer(Customer):
    """Cliente apressado: paciência menor."""
    def __init__(self, id, player_menu):
        super().__init__(id, player_menu)
        self.type = "apressado"
        self.patience = random.uniform(40, 50)
        self.max_patience = self.patience

    def draw(self, screen, x, y, font):
        if self.status != "left":
            pygame.draw.rect(screen, (200, 80, 80), (x, y, 40, 40))
            text = font.render(f"I{self.id}", True, (255, 255, 255))
            screen.blit(text, (x + 5, y + 5))

            if self.status == "waiting":
                order_text = font.render(self.order.dish.name, True, (0, 0, 0))
                screen.blit(order_text, (x + 50, y + 5))


class BossCustomer(Customer):
    """Cliente 'boss': muito paciente e dá gorjeta maior."""
    def __init__(self, id, player_menu):
        super().__init__(id, player_menu)
        self.type = "boss"
        self.patience = random.uniform(60, 90)
        self.max_patience = self.patience
        self.reward_multiplier = 2.0

    def get_tip(self):
        return int(self.order.dish.price * self.satisfaction * self.reward_multiplier)

    def draw(self, screen, x, y, font):
        if self.status != "left":
            pygame.draw.rect(screen, (120, 60, 180), (x, y, 50, 50))
            text = font.render(f"B{self.id}", True, (255, 255, 0))
            screen.blit(text, (x + 5, y + 5))

            if self.status == "waiting":
                order_text = font.render(self.order.dish.name, True, (0, 0, 0))
                screen.blit(order_text, (x + 50, y + 5))
