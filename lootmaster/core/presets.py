import os
import sys
from typing import List

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

from core.match import *


################################################################################
# Presets
################################################################################


def interval(a: int, b: int) -> List[int]:
    """
    Create a list of integers from a to b (inclusive).
    """
    return list(range(a, b + 1))


class LootMatchPresets:
    # ToDo: Implement `load` method for each preset class if needed.

    class Gold(LootMatchItemBase):
        def __init__(self):
            super().__init__(name="Gold Coin", id=0x0EED)

    class Arrow(LootMatchItemBase):
        def __init__(self):
            super().__init__(name="Arrow", id=0x0F3F)

    class Bolt(LootMatchItemBase):
        def __init__(self):
            super().__init__(name="Bolt", id=0x1BFB)

    class Map(LootMatchItemGroup):
        def __init__(self):
            super().__init__(name="Map", id_list=[0x14EB, 0x14EC])

    class Reagent(LootMatchItemGroup):
        def __init__(self):
            super().__init__(name="Reagent", id_list=interval(0x0F78, 0x0F91))

    class Gem(LootMatchItemGroup):
        def __init__(self):
            super().__init__(name="Gem", id_list=interval(0x0F0F, 0x0F31))

    class Scroll(LootMatchItemGroup):
        def __init__(self):
            super().__init__(
                name="Scroll",
                id_list=[0x0EF3]  # blank scroll
                + interval(0x1F2D, 0x1F72)  # Magery
                + interval(0x2260, 0x227C)  # Necromancy
                + interval(0x2D51, 0x2D60)  # Spellweaving
                + interval(0x2D9E, 0x2DAD),  # Mysticism
            )

    class Wand(LootMatchItemGroup):
        def __init__(self):
            super().__init__(name="Wand", id_list=[0x0DF2, 0x0DF3, 0x0DF4, 0x0DF5])

    class Jewelry(LootMatchItemGroup):
        def __init__(self):
            super().__init__(name="Jewelry", id_list=[0x1086, 0x108A, 0x1F06, 0x1F09, 0x4211, 0x4212])

    class Shield(LootMatchItemGroup):
        def __init__(self):
            super().__init__(
                name="Shield",
                id_list=[
                    0x1B72,
                    0x1B73,
                    0x1B74,
                    0x1B75,
                    0x1B76,
                    0x1B77,
                    0x1B78,
                    0x1B79,
                    0x1B7A,
                    0x1B7B,
                    0x1BC3,
                    0x1BC4,
                    0x1BC5,
                ],
            )

    class DailyRare(LootMatchProperty):
        def __init__(self):
            super().__init__(name="Daily Rare", pattern="[Daily Rare]")

    class MagicItem(LootMatchRarity):
        def __init__(self):
            super().__init__(name="Any Magic Item", rarity_min=0, rarity_max=8)

    class Artifact(LootMatchRarity):
        def __init__(self):
            super().__init__(name="Any Artifact", rarity_min=4, rarity_max=8)

    class LegendaryArtifact(LootMatchRarity):
        def __init__(self):
            super().__init__(name="Legendary Artifact", rarity_min=8, rarity_max=8)

    class UnwieldyMagicItem(LootMatchWeight):
        def __init__(self):
            super().__init__(name="Unwieldy Magic Item", weight_min=50, weight_max=255)

    class ArmorRefinement(LootMatchItemGroup):
        def __init__(self):
            super().__init__(
                name="Armor Refinement",
                id_list=[0x142A, 0x142B, 0x2D61, 0x4CD8, 0x4CD9, 0x4CDA],
            )