import json
import uuid
from datetime import datetime
from core.assets.restaurant import Restaurant


class Player:
    """
    Classe que representa um jogador no Kitchen Rush 1.
    Armazena dados de progresso, identidade, configurações e controle de restaurantes.
    """

    def __init__(self, nickname: str, restaurant_name: str):
        """
        Inicializa um novo perfil de jogador.

        :param nickname: Nome do jogador
        :param restaurant_name: Nome do primeiro restaurante criado
        """
        self.nickname = nickname
        self.player_id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()

        # Restaurante(s)
        self.restaurants = [Restaurant(restaurant_name)]
        self.active_restaurant_id = self.restaurants[0].restaurant_id

        # Configurações pessoais
        self.settings = {
            "volume": 0.8,
            "language": "pt-BR",
            "notifications": True
        }

    def get_active_restaurant(self):
        """Retorna o restaurante atualmente selecionado pelo jogador."""
        for r in self.restaurants:
            if r.restaurant_id == self.active_restaurant_id:
                return r
        return None

    def add_restaurant(self, name: str):
        """Cria e adiciona um novo restaurante ao perfil do jogador."""
        new_restaurant = Restaurant(name)
        self.restaurants.append(new_restaurant)
        self.active_restaurant_id = new_restaurant.restaurant_id

    def switch_restaurant(self, restaurant_id: str):
        """Troca o restaurante ativo para outro já existente no perfil."""
        if any(r.restaurant_id == restaurant_id for r in self.restaurants):
            self.active_restaurant_id = restaurant_id

    def to_dict(self):
        """Converte os dados do jogador para um dicionário serializável."""
        return {
            "nickname": self.nickname,
            "player_id": self.player_id,
            "created_at": self.created_at,
            "settings": self.settings,
            "active_restaurant_id": self.active_restaurant_id,
            "restaurants": [r.__dict__ for r in self.restaurants],
        }

    def save_to_file(self, filepath: str):
        """
        Salva os dados do jogador em um arquivo JSON.

        :param filepath: Caminho do arquivo de salvamento
        """
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str):
        """
        Carrega dados de um jogador a partir de um arquivo JSON.

        :param filepath: Caminho do arquivo salvo
        :return: Instância de Player carregada
        """
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        player = cls(data["nickname"], data["restaurants"][0]["name"])
        player.player_id = data["player_id"]
        player.created_at = data["created_at"]
        player.settings = data["settings"]
        player.active_restaurant_id = data["active_restaurant_id"]

        player.restaurants = []
        for r_data in data["restaurants"]:
            r = Restaurant(r_data["name"])
            r.__dict__.update(r_data)
            player.restaurants.append(r)

        return player
