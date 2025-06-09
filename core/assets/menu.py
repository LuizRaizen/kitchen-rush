"""Define os pratos disponíveis no restaurante."""

import pygame


class Dish:
    """Classe do jogo."""
    def __init__(self, name, difficulty=1, price=10, prep_time=5):
        self.name = name
        self.difficulty = difficulty  # 1 a 5
        self.price = price
        self.prep_time = prep_time  # em segundos

    def __str__(self):
        return f"{self.name} - ${self.price}"
        

# Lista de pratos disponíveis
MENU = [
    Dish("Hambúrguer Simples", difficulty=1, price=10, prep_time=4),
    Dish("Sopa de Legumes", difficulty=2, price=15, prep_time=6),
    Dish("Salada Tropical", difficulty=1, price=8, prep_time=3),
    Dish("Bife Grelhado", difficulty=3, price=20, prep_time=7),
    Dish("Pizza Gourmet", difficulty=4, price=25, prep_time=10)
]
