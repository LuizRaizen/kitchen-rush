"""Módulo de configurações do jogo."""

class Settings:
    """Classe do jogo."""

    def __init__(self):
        self.SCREEN = {
            'width': 960,
            'height': 540
        }
        self.MOUSE = {
            'image': 'graphics/sprites/pointer.png'
        }
        self.MONEY = {
            'image': "graphics/sprites/money_1.png",
            'amount': 100,
            'font': 'fonts/Baloo2-Bold.ttf',
            'font_size': 42,
        }
        self.CLOCK = {
            'image': 'graphics/sprites/clock_1.png',
            'font': 'fonts/Baloo2-Bold.ttf',
            'font_size': 36,
        }