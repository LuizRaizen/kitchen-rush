import uuid
from datetime import datetime


class Restaurant:
    """
    Classe que representa um restaurante gerenciado pelo jogador.
    Armazena dados de progresso, equipe, cardápio e estoque.
    """

    def __init__(self, name: str):
        """
        Inicializa um novo restaurante com valores padrões.

        :param name: Nome do restaurante
        """
        self.name = name
        self.restaurant_id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()

        # Progresso do restaurante
        self.day = 1
        self.money = 0.0
        self.reputation = 3.0  # Estrelas de 0 a 5

        # Operação
        self.menu = []                     # Pratos ativos
        self.owned_ingredients = {}       # Estoque: {"Tomato": 5}
        self.employees = []               # Funcionários ativos (IDs ou objetos)
        self.events = []                  # Eventos especiais futuros

        # Estatísticas
        self.total_clients_served = 0
        self.total_money_earned = 0.0
        self.total_failed_days = 0

    def hire_employee(self, employee_id: int):
        """Adiciona um funcionário à equipe ativa."""
        if employee_id not in self.employees:
            self.employees.append(employee_id)

    def fire_employee(self, employee_id: int):
        """Remove um funcionário da equipe ativa."""
        if employee_id in self.employees:
            self.employees.remove(employee_id)

    def update_ingredient(self, name: str, quantity: int):
        """Adiciona ou consome ingredientes no estoque."""
        self.owned_ingredients[name] = self.owned_ingredients.get(name, 0) + quantity

    def add_money(self, value: float):
        """Adiciona dinheiro ao restaurante."""
        self.money += value

    def advance_day(self):
        """Avança o restaurante para o próximo dia."""
        self.day += 1
        