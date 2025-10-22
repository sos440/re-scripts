################################################################################
# User settings
################################################################################

# IDs for plant chests
# You need three chests to organize all the seeds
CHEST_IDS = [
    # chest for campion flowers, poppies, snowdrops, bulrushes, lilies, pampas grass
    0x408DBDC1,
    # chest for rushes, elephant ear plant, fern, ponytail palm, small palm, century plant
    0x410EDF8D,
    # chest for water plant, snake plant, prickly pear cactus, barrel cactus, tribarrel cactus
    0x52547AF3,
]


# List of colors for plant seeds
# Seeds will be sorted vertically by color in the order defined here
color_name_list = [
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

name_itemid_list = [
    ("campion flowers", 3203),
    ("poppies", 3206),
    ("snowdrops", 3208),
    ("bulrushes", 3220),
    ("lilies", 3211),
    ("pampas grass", 3237),
    ("rushes", 3239),
    ("elephant ear plant", 3223),
    ("fern", 3231),
    ("ponytail palm", 3238),
    ("small palm", 3228),
    ("century plant", 3377),
    ("water plant", 3332),
    ("snake plant", 3241),
    ("prickly pear cactus", 3372),
    ("barrel cactus", 3366),
    ("tribarrel cactus", 3367),
]

################################################################################
# Script starts here
################################################################################

from AutoComplete import *
from typing import Dict, Tuple, List
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte, Int32  # type: ignore
import os
import sys
import re

sys.path.append(os.path.dirname(__file__))
from gumpradio.templates import CraftingGumpBuilder


# A dictionary mapping chest serial to list of plant types it contains
# Key: chest serial
plant_map = {
    CHEST_IDS[0]: [
        "campion flowers",
        "poppies",
        "snowdrops",
        "bulrushes",
        "lilies",
        "pampas grass",
    ],
    CHEST_IDS[1]: [
        "rushes",
        "elephant ear plant",
        "fern",
        "ponytail palm",
        "small palm",
        "century plant",
    ],
    CHEST_IDS[2]: [
        "water plant",
        "snake plant",
        "prickly pear cactus",
        "barrel cactus",
        "tribarrel cactus",
    ],
}


# Convert the plant list to a dictionary for easy lookup
# Key: plant type, Value: container, index
plant_invmap: Dict[str, Tuple[int, int]] = {}
for cont_serial, plants in plant_map.items():
    for index, plant in enumerate(plants):
        plant_invmap[plant] = (cont_serial, index)

# Convert the name-itemid list to a dictionary for easy lookup
# Key: itemid, Value: (index, plant type)
itemid_invmap: Dict[int, Tuple[int, str]] = {itemid: (i, name) for i, (name, itemid) in enumerate(name_itemid_list)}

# Convert the color list to a dictionary for easy lookup
# Key: color code, Value: (index, color name)
color_invmap: Dict[int, Tuple[int, str]] = {color: (i, name) for i, (color, name) in enumerate(color_name_list)}


def is_valid_seed(seed: "Item") -> bool:
    if seed.RootContainer in plant_map:
        return True
    if seed.RootContainer == Player.Backpack.Serial:
        return True
    return False


def parse_cliloc(props: List["Property"]) -> int:
    if not props:
        return 0
    cliloc = props[0].Number
    args = re.split("\t", props[0].Args)
    graphics = 0
    # Multiple seeds
    if cliloc in (1113492, 1113493, 1113715, 1113716):
        if len(args) < 3:
            return 0
        graphics = int(args[2].strip("#@")) - 1020000
    # Single seed
    elif cliloc in (1061917, 1061918, 1095221, 1080533):
        if len(args) < 2:
            return 0
        graphics = int(args[1].strip("#@")) - 1020000
    if graphics == 78212:
        graphics = 19340  # vanilla's graphic need a fix
    return graphics


def show_seed_summary(my_plants: Dict[str, Dict[int, int]]):
    CELL_WIDTH = 75
    CELL_HEIGHT = 50
    gb = CraftingGumpBuilder(id="MySeedSummaryGump")
    with gb.Column(padding=10, background="frame:2620"):
        # Header row
        with gb.Row():
            gb.Spacer(spacing=100)
            for name, _ in name_itemid_list:
                gb.Html(name.title(), width=CELL_WIDTH, height=40, color="#FFFF00", centered=True)
        # Icon row
        with gb.Row():
            gb.Spacer(spacing=100)
            for _, itemid in name_itemid_list:
                gb.TileArt(itemid, width=CELL_WIDTH, height=80, centered=True)
        # Data rows
        for row_idx, (color_code, color_name) in enumerate(color_name_list):
            with gb.Row(valign="middle"):
                gb.Text(color_name.title(), width=100, hue=(color_code or 0x3B2) - 1)
                for name, itemid in name_itemid_list:
                    amount = my_plants[name].get(color_code, 0)
                    if amount > 0:
                        gb.Html(str(amount), width=CELL_WIDTH, height=22, color="#FFFFFF", centered=True)
                    else:
                        gb.Spacer(spacing=CELL_WIDTH)

    gb.launch()


def scan_seeds():
    seeds = []

    for cont_serial in plant_map:
        cont = Items.FindBySerial(cont_serial)
        if cont is None:
            continue
        if not cont.ContainerOpened or len(cont.Contains) == 0:
            Misc.SendMessage("Opening the container...", 68)
            Items.WaitForContents(cont_serial, 1000)
            Misc.Pause(1000)

    filter = Items.Filter()
    filter.Enabled = True
    filter.OnGround = False
    filter.Graphics = CList[Int32]([0x0DCF])
    seeds = [seed for seed in Items.ApplyFilter(filter) if is_valid_seed(seed)]

    n = len(seeds)
    Misc.SendMessage(f"{n} seeds found!", 0x3B2)

    my_plants = {name: dict() for (name, _) in name_itemid_list}
    for i, seed in enumerate(seeds):
        if seed.Color not in color_invmap:
            continue
        row_idx, color_name = color_invmap[seed.Color]

        itemid = parse_cliloc(seed.Properties)
        if itemid not in itemid_invmap:
            continue

        plant_idx, plant_type = itemid_invmap[itemid]
        my_plants[plant_type][seed.Color] = seed.Amount

    show_seed_summary(my_plants)


if __name__ == "__main__":
    scan_seeds()
