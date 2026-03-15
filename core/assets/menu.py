# core/assets/menu.py
from typing import List

from core.assets.dishes import DISHES, Dish


class PlayerMenu:
    """
    Armazena os pratos desbloqueados do jogador.
    Você pode persistir/carregar isso em savegames depois.

    OBS (teste): iniciamos com TODOS os pratos do catálogo desbloqueados,
    apenas para fins de teste/validação do cardápio.
    """

    def __init__(self) -> None:
        # TESTE: desbloquear todos os pratos disponíveis no catálogo
        self.owned_keys: List[str] = [d.key for d in DISHES]

    def owned_dishes(self) -> List[Dish]:
        catalog = {d.key: d for d in DISHES}
        return [catalog[k] for k in self.owned_keys if k in catalog]

    def unlock(self, dish_key: str) -> None:
        if dish_key not in self.owned_keys:
            self.owned_keys.append(dish_key)

    def is_owned(self, dish_key: str) -> bool:
        return dish_key in self.owned_keys
