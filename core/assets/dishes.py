# core/assets/dishes.py
"""
Catálogo de ingredientes, habilidades e pratos do jogo.

- Mantém a estrutura original (dataclasses e chaves de efeitos).
- Amplia o catálogo com 20 novos pratos (algumas variações).
- Apenas ALGUNS pratos possuem habilidades estratégicas; os demais
  não têm habilidades (campo `abilities` vazio), para balanceamento.
- Novos pratos (ainda sem arte) usam a imagem placeholder:
  `graphics/sprites/lock.png` em ícone e preview.
"""

from dataclasses import dataclass
from typing import Dict, List


# ======================================================================
# MODELOS
# ======================================================================

@dataclass
class Ingredient:
    """Ingrediente básico com ícone para exibir no cardápio."""
    key: str
    name: str
    icon_path: str


@dataclass
class Ability:
    """
    Habilidade/passiva do prato.

    effect: payload numérico usado pelos sistemas
            (ex.: {"patience_add": 1, "prep_time_mult": 0.9})
    """
    key: str
    label: str               # título curto exibido no cardápio
    description: str         # explicação textual (mostrada no painel)
    effect: Dict[str, float]


@dataclass
class Dish:
    """
    Definição de um prato do jogo.
    Inclui 'price' (inteiro) para exibição junto às estrelas.
    """
    key: str
    name: str
    icon_path: str             # ícone pequeno (grade)
    preview_path: str          # imagem maior (painel)
    description: str
    ingredient_keys: List[str]  # chaves em INGREDIENTS
    stars: int                  # 1..5
    price_tier: str             # "$".."$$$$$" (mantido para balanceamento)
    abilities: List[Ability]
    prep_time: float            # tempo BASE de preparo (s) antes de mults
    price: int                  # PREÇO INTEIRO para exibir no painel (ex.: 18)

    # ---- Helpers ----
    def effective_prep_time(self) -> float:
        """
        Retorna o tempo de preparo após aplicar multiplicadores das
        habilidades (campo effect['prep_time_mult']). Se não houver,
        retorna prep_time.
        """
        t = float(self.prep_time)
        for ab in (self.abilities or []):
            mult = ab.effect.get("prep_time_mult")
            if isinstance(mult, (int, float)) and mult > 0:
                t *= float(mult)
        # evita zero/negativo por configuração incorreta
        return max(0.1, t)


# ======================================================================
# INGREDIENTES (ícones)
# (Mantidos conforme estrutura já existente no projeto)
# ======================================================================

INGREDIENTS: Dict[str, Ingredient] = {
    "pasta": Ingredient(
        "pasta", "Massa", "graphics/sprites/ingredients/icon_pasta.png"
    ),
    "tomato_sauce": Ingredient(
        "tomato_sauce", "Molho de Tomate",
        "graphics/sprites/ingredients/icon_tomato.png",
    ),
    "cheese": Ingredient(
        "cheese", "Queijo", "graphics/sprites/ingredients/icon_carrot.png"
    ),
    "bun": Ingredient(
        "bun", "Pão", "graphics/sprites/ingredients/icon_tomato.png"
    ),
    "beef": Ingredient(
        "beef", "Carne", "graphics/sprites/ingredients/icon_potato.png"
    ),
    "lettuce": Ingredient(
        "lettuce", "Alface", "graphics/sprites/ingredients/icon_lettuce.png"
    ),
    "tomato": Ingredient(
        "tomato", "Tomate", "graphics/sprites/ingredients/icon_tomato.png"
    ),
    "broth": Ingredient(
        "broth", "Caldo", "graphics/sprites/ingredients/icon_broccoli.png"
    ),
    "veggies": Ingredient(
        "veggies", "Legumes", "graphics/sprites/ingredients/icon_icon_pasta.png"
    ),
    "herbs": Ingredient(
        "herbs", "Ervas", "graphics/sprites/ingredients/icon_lettuce.png"
    ),
    # ... adicione mais conforme necessário ...
}


# ======================================================================
# HABILIDADES (existentes)
# ======================================================================

PAT1 = Ability(
    key="patience_plus_1",
    label="+1 Paciência",
    description="Aumenta a paciência do grupo em +1 quando o prato é servido.",
    effect={"patience_add": 1},
)

FAST1 = Ability(
    key="prep_speed_10",
    label="Preparo Rápido",
    description="Reduz o tempo de preparo em 10% para este prato.",
    effect={"prep_time_mult": 0.90},
)

TIPG1 = Ability(
    key="gourmet_tip_10",
    label="Gorjeta Gourmet",
    description="Gourmets dão +10% de gorjeta quando escolhem este prato.",
    effect={"tip_bonus_pct_gourmet": 10},
)

# ======================================================================
# HABILIDADES (extras – mesmas chaves já conhecidas)
# ======================================================================

PAT2 = Ability(
    key="patience_plus_2",
    label="+2 Paciência",
    description="Aumenta a paciência do grupo em +2 quando este prato é servido.",
    effect={"patience_add": 2},
)

FAST2 = Ability(
    key="prep_speed_20",
    label="Preparo Ágil",
    description="Reduz o tempo de preparo em 20% para este prato.",
    effect={"prep_time_mult": 0.80},
)

TIPG2 = Ability(
    key="gourmet_tip_15",
    label="Gorjeta Premium",
    description="Clientes gourmets deixam +15% de gorjeta com este prato.",
    effect={"tip_bonus_pct_gourmet": 15},
)

# Novas opções para uso futuro (mantêm as mesmas chaves de efeito)
PAT3 = Ability(
    key="patience_plus_3",
    label="+3 Paciência",
    description="Aumenta a paciência do grupo em +3 quando o prato é servido.",
    effect={"patience_add": 3},
)

FAST3 = Ability(
    key="prep_speed_30",
    label="Preparo Relâmpago",
    description="Reduz o tempo de preparo em 30% para este prato.",
    effect={"prep_time_mult": 0.70},
)

TIPG3 = Ability(
    key="gourmet_tip_20",
    label="Gorjeta de Chef",
    description="Clientes gourmets deixam +20% de gorjeta com este prato.",
    effect={"tip_bonus_pct_gourmet": 20},
)


# ======================================================================
# CATÁLOGO DE PRATOS
# - Mantém os já existentes.
# - Ajusta para que apenas ALGUNS tenham habilidades.
# - Adiciona 20 novos pratos (sem arte própria → lock.png).
# ======================================================================

LOCK_IMG = "graphics/sprites/lock.png"

DISHES: List[Dish] = [
    # ------------------------------
    # EXISTENTES (ajustados)
    # ------------------------------
    Dish(
        key="spaghetti",
        name="Espaguete",
        icon_path="graphics/sprites/dishes/spaghetti_icon.png",
        preview_path="graphics/sprites/dishes/spaghetti_preview.png",
        description=(
            "Um clássico de massa com molho de tomate e queijo. "
            "Confortável e popular entre clientes comuns."
        ),
        ingredient_keys=["pasta", "tomato_sauce", "cheese"],
        stars=3,
        price_tier="$$",
        abilities=[PAT1],        # mantém como estratégico
        prep_time=12.0,
        price=18,
    ),
    Dish(
        key="hamburger",
        name="Hamburguer",
        icon_path="graphics/sprites/dishes/hamburger_icon.png",
        preview_path="graphics/sprites/dishes/hamburger_preview.png",
        description=(
            "Pão tostado com carne suculenta e vegetais. "
            "Ótimo em horários de pico."
        ),
        ingredient_keys=["bun", "beef", "lettuce", "tomato"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade (balanceamento)
        prep_time=8.0,
        price=12,
    ),
    Dish(
        key="soup",
        name="Sopa",
        icon_path="graphics/sprites/dishes/soup_icon.png",
        preview_path="graphics/sprites/dishes/soup_preview.png",
        description=(
            "Caldo leve com legumes e ervas. "
            "Acalma e aquece — bom para dias frios."
        ),
        ingredient_keys=["broth", "veggies", "herbs"],
        stars=2,
        price_tier="$",
        abilities=[PAT1],        # estratégica
        prep_time=6.0,
        price=9,
    ),
    Dish(
        key="pizza",
        name="Pizza",
        icon_path="graphics/sprites/dishes/pizza_icon.png",
        preview_path="graphics/sprites/dishes/pizza_preview.png",
        description=(
            "Massa assada com molho e queijo. "
            "A favorita de grupos e gourmets."
        ),
        ingredient_keys=["pasta", "tomato_sauce", "cheese"],
        stars=4,
        price_tier="$$$",
        abilities=[TIPG1],       # estratégica
        prep_time=15.0,
        price=22,
    ),

    # ------------------------------
    # EXISTENTES (novos adicionados antes)
    # com ajuste: apenas alguns com habilidades
    # ------------------------------
    Dish(
        key="cupcake",
        name="Cupcake",
        icon_path="graphics/sprites/dishes/cupcake_icon.png",
        preview_path="graphics/sprites/dishes/cupcake_preview.png",
        description="Bolinho individual com cobertura. Encanta crianças.",
        ingredient_keys=["bun", "cheese"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=6.0,
        price=8,
    ),
    Dish(
        key="donut",
        name="Rosquinha",
        icon_path="graphics/sprites/dishes/donut_icon.png",
        preview_path="graphics/sprites/dishes/donut_preview.png",
        description="Clássica rosquinha doce. Perfeita para um lanche rápido.",
        ingredient_keys=["bun"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=5.0,
        price=7,
    ),
    Dish(
        key="fried_fish",
        name="Peixe Frito",
        icon_path="graphics/sprites/dishes/fried_fish_icon.png",
        preview_path="graphics/sprites/dishes/fried_fish_preview.png",
        description="Filés crocantes acompanhados de ervas. Crocância e sabor.",
        ingredient_keys=["herbs", "tomato"],
        stars=3,
        price_tier="$$",
        abilities=[FAST1],       # estratégica
        prep_time=9.0,
        price=18,
    ),
    Dish(
        key="fries",
        name="Batatas Fritas",
        icon_path="graphics/sprites/dishes/fries_icon.png",
        preview_path="graphics/sprites/dishes/fries_preview.png",
        description="Porção de batatas douradas. Acompanha bem quase tudo.",
        ingredient_keys=["veggies", "herbs"],
        stars=1,
        price_tier="$",
        abilities=[FAST2],       # estratégica
        prep_time=5.0,
        price=6,
    ),
    Dish(
        key="grilled_chicken",
        name="Frango Grelhado",
        icon_path="graphics/sprites/dishes/grilled_chicken_icon.png",
        preview_path="graphics/sprites/dishes/grilled_chicken_preview.png",
        description="Peito de frango ao ponto, finalizado com ervas.",
        ingredient_keys=["beef", "herbs"],
        stars=3,
        price_tier="$$",
        abilities=[],            # sem habilidade
        prep_time=10.0,
        price=20,
    ),
    Dish(
        key="hotdog",
        name="Cachorro-quente",
        icon_path="graphics/sprites/dishes/hotdog_icon.png",
        preview_path="graphics/sprites/dishes/hotdog_preview.png",
        description="Pão, salsicha e molhos. Sai voando no pico.",
        ingredient_keys=["bun", "tomato", "beef"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=5.0,
        price=9,
    ),
    Dish(
        key="ice_cream",
        name="Sorvete",
        icon_path="graphics/sprites/dishes/ice_cream_icon.png",
        preview_path="graphics/sprites/dishes/ice_cream_preview.png",
        description="Cremoso e refrescante. Ideal para aliviar a espera.",
        ingredient_keys=["cheese"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=4.0,
        price=10,
    ),
    Dish(
        key="lasagna",
        name="Lasanha",
        icon_path="graphics/sprites/dishes/lasagna_icon.png",
        preview_path="graphics/sprites/dishes/lasagna_preview.png",
        description="Camadas de massa, molho e queijo gratinado.",
        ingredient_keys=["pasta", "tomato_sauce", "cheese"],
        stars=4,
        price_tier="$$$",
        abilities=[PAT2],        # estratégica
        prep_time=16.0,
        price=22,
    ),
    Dish(
        key="muffin",
        name="Muffin",
        icon_path="graphics/sprites/dishes/muffin_icon.png",
        preview_path="graphics/sprites/dishes/muffin_preview.png",
        description="Bolinho macio e prático. Bom para filas em movimento.",
        ingredient_keys=["bun"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=5.0,
        price=7,
    ),
    Dish(
        key="omelete",
        name="Omelete",
        icon_path="graphics/sprites/dishes/omelete_icon.png",
        preview_path="graphics/sprites/dishes/omelete_preview.png",
        description="Clássico, leve e rápido, com queijo e tomate.",
        ingredient_keys=["cheese", "tomato", "herbs"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=6.0,
        price=12,
    ),
    Dish(
        key="pancakes",
        name="Panquecas",
        icon_path="graphics/sprites/dishes/pancakes_icon.png",
        preview_path="graphics/sprites/dishes/pancakes_preview.png",
        description="Macias e quentinhas. Perfeitas para o desjejum.",
        ingredient_keys=["bun", "cheese"],
        stars=3,
        price_tier="$$",
        abilities=[],            # sem habilidade
        prep_time=9.0,
        price=14,
    ),
    Dish(
        key="ramen",
        name="Lámen",
        icon_path="graphics/sprites/dishes/ramen_icon.png",
        preview_path="graphics/sprites/dishes/ramen_preview.png",
        description="Tigela de caldo e macarrão, com legumes e ervas.",
        ingredient_keys=["broth", "veggies", "herbs"],
        stars=4,
        price_tier="$$$",
        abilities=[TIPG1],       # estratégica
        prep_time=14.0,
        price=19,
    ),
    Dish(
        key="roast_chicken",
        name="Frango Assado",
        icon_path="graphics/sprites/dishes/roast_chicken_icon.png",
        preview_path="graphics/sprites/dishes/roast_chicken_preview.png",
        description="Frango dourado por fora e suculento por dentro.",
        ingredient_keys=["beef", "herbs"],
        stars=4,
        price_tier="$$$",
        abilities=[],            # sem habilidade
        prep_time=18.0,
        price=21,
    ),
    Dish(
        key="salad",
        name="Salada",
        icon_path="graphics/sprites/dishes/salad_icon.png",
        preview_path="graphics/sprites/dishes/salad_preview.png",
        description="Fresca e colorida: folhas, tomate e ervas.",
        ingredient_keys=["lettuce", "tomato", "herbs", "veggies"],
        stars=2,
        price_tier="$",
        abilities=[],            # sem habilidade
        prep_time=5.0,
        price=11,
    ),
    Dish(
        key="steak",
        name="Bife",
        icon_path="graphics/sprites/dishes/steak_icon.png",
        preview_path="graphics/sprites/dishes/steak_preview.png",
        description="Corte alto selado ao ponto, com ervas.",
        ingredient_keys=["beef", "herbs"],
        stars=5,
        price_tier="$$$$",
        abilities=[TIPG2],       # estratégica
        prep_time=13.0,
        price=28,
    ),
    Dish(
        key="taco",
        name="Taco",
        icon_path="graphics/sprites/dishes/taco_icon.png",
        preview_path="graphics/sprites/dishes/taco_preview.png",
        description="Tortilha recheada com carne e vegetais.",
        ingredient_keys=["bun", "beef", "tomato", "lettuce"],
        stars=3,
        price_tier="$$",
        abilities=[],            # sem habilidade
        prep_time=7.0,
        price=13,
    ),

    # ------------------------------
    # NOVOS (20 itens) – usam LOCK_IMG
    # Apenas alguns com habilidades
    # ------------------------------
    Dish(
        key="sandwich",
        name="Sanduíche",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Sanduíche clássico com pão, carne e vegetais frescos.",
        ingredient_keys=["bun", "beef", "lettuce", "tomato"],
        stars=2,
        price_tier="$",
        abilities=[],
        prep_time=6.0,
        price=10,
    ),
    Dish(
        key="sushi",
        name="Sushi",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Bocados delicados que atraem paladares exigentes.",
        ingredient_keys=["veggies", "herbs"],
        stars=4,
        price_tier="$$$",
        abilities=[TIPG2],   # estratégica (gourmet)
        prep_time=12.0,
        price=26,
    ),
    Dish(
        key="risotto",
        name="Risoto",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Cremoso e aromático, preparado lentamente no caldo.",
        ingredient_keys=["broth", "veggies", "cheese"],
        stars=4,
        price_tier="$$$",
        abilities=[PAT1],    # estratégica
        prep_time=16.0,
        price=24,
    ),
    Dish(
        key="apple_pie",
        name="Torta de Maçã",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Clássica sobremesa com massa dourada e recheio de maçã.",
        ingredient_keys=["bun", "herbs"],
        stars=3,
        price_tier="$$",
        abilities=[],
        prep_time=10.0,
        price=15,
    ),
    Dish(
        key="brownie",
        name="Brownie",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Doce denso e macio, perfeito para acompanhar café.",
        ingredient_keys=["bun", "cheese"],
        stars=2,
        price_tier="$",
        abilities=[],
        prep_time=7.0,
        price=9,
    ),
    Dish(
        key="tea",
        name="Chá",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Bebida quente e reconfortante, reduz a ansiedade.",
        ingredient_keys=["herbs"],
        stars=1,
        price_tier="$",
        abilities=[PAT1],    # leve efeito de paciência
        prep_time=3.0,
        price=5,
    ),
    Dish(
        key="coffee",
        name="Café",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Dose de energia rápida para atender mais clientes.",
        ingredient_keys=["herbs"],
        stars=1,
        price_tier="$",
        abilities=[FAST1],   # preparo rápido
        prep_time=2.0,
        price=4,
    ),
    Dish(
        key="juice",
        name="Suco",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Refrescante e natural, agrada a todos.",
        ingredient_keys=["veggies"],
        stars=1,
        price_tier="$",
        abilities=[],
        prep_time=3.0,
        price=6,
    ),
    Dish(
        key="milkshake",
        name="Milk-shake",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Cremoso e gelado, favorito dos jovens.",
        ingredient_keys=["cheese"],
        stars=2,
        price_tier="$",
        abilities=[],
        prep_time=4.0,
        price=10,
    ),
    Dish(
        key="pastel",
        name="Pastel",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Massa frita crocante com recheio salgado.",
        ingredient_keys=["bun", "beef", "tomato"],
        stars=2,
        price_tier="$",
        abilities=[FAST2],   # sai rápido
        prep_time=5.0,
        price=8,
    ),
    Dish(
        key="coxinha",
        name="Coxinha",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Salgado popular, crocante por fora e macio por dentro.",
        ingredient_keys=["bun", "herbs"],
        stars=2,
        price_tier="$",
        abilities=[],
        prep_time=6.0,
        price=8,
    ),
    Dish(
        key="esfirra",
        name="Esfirra",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Massa assada com recheio temperado.",
        ingredient_keys=["bun", "beef", "tomato"],
        stars=2,
        price_tier="$",
        abilities=[],
        prep_time=8.0,
        price=9,
    ),
    Dish(
        key="kebab",
        name="Kebab",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Carne grelhada e temperada, servida com vegetais.",
        ingredient_keys=["beef", "lettuce", "tomato", "herbs"],
        stars=3,
        price_tier="$$",
        abilities=[],
        prep_time=9.0,
        price=17,
    ),
    Dish(
        key="falafel",
        name="Falafel",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Bolinho vegetariano crocante, ótimo para combos.",
        ingredient_keys=["veggies", "herbs"],
        stars=3,
        price_tier="$$",
        abilities=[],
        prep_time=8.0,
        price=15,
    ),
    Dish(
        key="burrito",
        name="Burrito",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Enrolado farto de carne e vegetais.",
        ingredient_keys=["bun", "beef", "lettuce", "tomato"],
        stars=3,
        price_tier="$$",
        abilities=[FAST1],   # montagem ágil
        prep_time=7.0,
        price=16,
    ),
    Dish(
        key="nachos",
        name="Nachos",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Chips crocantes com cobertura de queijo e tomate.",
        ingredient_keys=["cheese", "tomato", "herbs"],
        stars=2,
        price_tier="$",
        abilities=[],
        prep_time=6.0,
        price=11,
    ),
    Dish(
        key="quesadilla",
        name="Quesadilla",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Tortilha grelhada com queijo derretido.",
        ingredient_keys=["cheese", "bun", "herbs"],
        stars=3,
        price_tier="$$",
        abilities=[],
        prep_time=7.0,
        price=14,
    ),
    Dish(
        key="gnocchi",
        name="Nhoque",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Nhoque de massa ao molho de tomate e ervas.",
        ingredient_keys=["pasta", "tomato_sauce", "herbs"],
        stars=3,
        price_tier="$$",
        abilities=[PAT1],   # reconfortante
        prep_time=12.0,
        price=19,
    ),
    Dish(
        key="calzone",
        name="Calzone",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Massa fechada com recheio de queijo e molho.",
        ingredient_keys=["pasta", "cheese", "tomato_sauce"],
        stars=4,
        price_tier="$$$",
        abilities=[TIPG2],  # atrai gourmets
        prep_time=14.0,
        price=23,
    ),
    Dish(
        key="crepe",
        name="Crepe",
        icon_path=LOCK_IMG,
        preview_path=LOCK_IMG,
        description="Fino e versátil, doce ou salgado.",
        ingredient_keys=["bun", "cheese", "herbs"],
        stars=2,
        price_tier="$",
        abilities=[FAST1],  # preparo rápido na chapa
        prep_time=5.0,
        price=12,
    ),
]
