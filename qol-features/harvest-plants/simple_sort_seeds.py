from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import Dict, List, Optional, Any, Tuple
import re


# Positioning constants for the seed arrangement
POS_DX = 25
POS_DY = 10


# A dictionary mapping chest serial to list of plant types it contains
# Key: chest serial
plant_map = {
    0x408DBDC1: [
        "campion flowers",
        "poppies",
        "snowdrops",
        "bulrushes",
        "lilies",
        "pampas grass",
    ],
    0x410EDF8D: [
        "rushes",
        "elephant ear plant",
        "fern",
        "ponytail palm",
        "small palm",
        "century plant",
    ],
    0x52547AF3: [
        "water plant",
        "snake plant",
        "prickly pear cactus",
        "barrel cactus",
        "tribarrel cactus",
    ],
}


# A list of tuples mapping color code to color name
# The index in the list is used for sorting
color_map = [
    (0, "plain"),
    (0x0021, "bright red"),
    (0x066D, "red"),
    (0x002B, "bright orange"),
    (0x046F, "orange"),
    (0x0038, "bright yellow"),
    (0x08A5, "yellow"),
    (0x0042, "bright green"),
    (0x059B, "green"),
    (0x0005, "bright blue"),
    (0x053D, "blue"),
    (0x0010, "bright purple"),
    (0x000D, "purple"),
    (0x048E, "rare pink"),
    (0x0495, "rare aqua"),
    (0x0486, "rare magenta"),
    (0x0489, "rare fire red"),
    (0x0481, "white"),
    (0x0455, "black"),
]


# Convert the plant list to a dictionary for easy lookup
# Key: plant type, Value: container, index
plant_invmap: Dict[str, Tuple[int, int]] = {}
for cont_serial, plants in plant_map.items():
    for index, plant in enumerate(plants):
        plant_invmap[plant] = (cont_serial, index)

# Convert the color list to a dictionary for easy lookup
# Key: color code, Value: (index, color name)
color_invmap: Dict[int, Tuple[int, str]] = {entry[0]: (i, entry[1]) for i, entry in enumerate(color_map)}


def sort_seeds():
    seeds = []

    for cont_serial in plant_map:
        Items.WaitForContents(cont_serial, 1000)
        seeds.extend(Items.FindAllByID(0x0DCF, -1, cont_serial, 2))
        Misc.Pause(1000)
    seeds.extend(Items.FindAllByID(0x0DCF, -1, Player.Backpack.Serial, 2))

    n = len(seeds)
    Misc.SendMessage(f"{n} seeds found!", 0x3B2)
    
    seed_history = set()
    for i, seed in enumerate(seeds):
        name = seed.Name.lower().strip()
        if seed.Color not in color_invmap:
            Misc.SendMessage("Unknown seed color: 0x{seed.Color:04X}", 33)
            continue
        row_idx, color_name = color_invmap[seed.Color]
        match = re.search(r"^(?:\d+\s+)?" + color_name + r"\s+(.+)\s+seeds?$", name)
        if not match:
            Misc.SendMessage(f"Failed to parse the seed name: {name}", 33)
            continue
        plant_type = match.group(1)
        if plant_type not in plant_invmap:
            Misc.SendMessage(f"Unknown plant type: {plant_type}", 33)
            continue
        cont_serial, col_idx = plant_invmap[plant_type]

        Misc.SendMessage(f"Sorting ({i+1}/{n}): {color_name} {plant_type}", 68)
        seed_key = (plant_type, seed.Color)
        if seed_key not in seed_history:
            seed_history.add(seed_key)
            x = 50 + POS_DX * col_idx
            y = 59 + POS_DY * row_idx
            if seed.Container == cont_serial and seed.Position.X == x and seed.Position.Y == y:
                continue
            Items.Move(seed.Serial, cont_serial, -1, x, y)
        else:
            Items.Move(seed.Serial, cont_serial, -1)
        Misc.Pause(1000)
    
    Misc.SendMessage("Done!", 0x3B2)


if __name__ == "__main__":
    sort_seeds()