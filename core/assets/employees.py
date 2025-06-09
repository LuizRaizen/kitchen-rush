"""Módulo que armazena as classes para criar os funcionários do jogo."""

from core.assets.characters import Character


class Employee(Character):
    """Classe para criar um funcionário."""
    def __init__(self, name, level=1):
        super().__init__()
        # Atributos comuns á todos os funcionários
        self.level = 1
        self.experience = 0
        self.agility = 3
        self.day_off = 5
        self.salary = 800

    def upgrade(self):
        self.level += 1

    def get_info(self):
        return f"{self.name} (Nível {self.level})"

class Waiter(Employee):
    """Classe para criar um garçom."""
    def __init__(self, name, level=1):
        super().__init__(name, level)
        # Atributos comuns á todos os garçons
        self.charisma = 1.0
        self.proactivity = 4

class Cook(Employee):
    """Classe para criar um cozinheiro."""
    def __init__(self, name, level=1):
        super().__init__(name, level)
        self.precision = 1.0 + level * 0.2

class Chef(Employee):
    """Classe para criar um chef."""
    def __init__(self, name, level=1):
        super().__init__(name, level)
        self.creativity = 1.0 + level * 0.3
        self.quality_bonus = level * 0.2

class Manager(Employee):
    """Classe para criar um gerente."""
    def __init__(self, name, level=1):
        super().__init__(name, level)
        self.efficiency = 1.0 + level * 0.25
        self.max_staff = 2 + level
