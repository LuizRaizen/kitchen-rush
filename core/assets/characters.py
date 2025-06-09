"""Módulo que armazena a classe responsável por gerar o molde para 
    todos os personagens do jogo.
"""

import pygame


class Character:
    """Classe para criar personagens."""

    def __init__(self):
        self.name = None
        self.available = None