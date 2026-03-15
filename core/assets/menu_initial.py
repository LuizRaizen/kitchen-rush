# core/assets/menu.py
from typing import List
from core.assets.dishes import DISHES, Dish

class PlayerMenu:
    """
    Armazena os pratos desbloqueados do jogador.
    Você pode persistir/ carregar isso em savegames depois.
    """
    def __init__(self):
        # chaves desbloqueadas inicialmente
        self.owned_keys: List[str] = ["spaghetti", "soup", "hamburger"]  # iniciais

    def owned_dishes(self) -> List[Dish]:
        catalog = {d.key: d for d in DISHES}
        return [catalog[k] for k in self.owned_keys if k in catalog]

    def unlock(self, dish_key: str):
        if dish_key not in self.owned_keys:
            self.owned_keys.append(dish_key)

    def is_owned(self, dish_key: str) -> bool:
        return dish_key in self.owned_keys
