import json
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)


# Load the data
data = {}
with open(os.path.join(PATH, "data.json"), "r") as file:
    data = json.load(file)
    Misc.SendMessage(f"{len(data)} entries loaded.")


GUMP_PD = hash("PaperdollGump") & 0xFFFFFFFF
RE_LAYERS_NAME = [
    "RightHand",
    "LeftHand",
    "Shoes",
    "Pants",
    "Shirt",
    "Head",
    "Gloves",
    "Ring",
    "Neck",
    "Waist",
    "InnerTorso",
    "Bracelet",
    "MiddleTorso",
    "Earrings",
    "Arms",
    "Cloak",
    "OuterTorso",
    "OuterLegs",
    "InnerLegs",
    "Talisman",
]


def proper_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def iter_layers():
    for layer in RE_LAYERS_NAME:
        item = Player.GetItemOnLayer(layer)
        if item is None:
            continue
        Items.WaitForProps(item.Serial, 1000)
        yield item, layer


def get_layer(itemid: int) -> int:
    key = str(itemid)
    if key in data:
        return data[key][0]
    return -1


def get_graphic(itemid: int) -> int:
    key = str(itemid)
    if key in data:
        return data[key][1]
    return -1


def test() -> None:
    Gumps.CloseGump(GUMP_PD)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 300, 300, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 300, 300)

    worn_items = [item for item, _ in iter_layers()]
    worn_items.sort(key=lambda item: get_layer(item.ItemID))
    for item in worn_items:
        grp = get_graphic(item.ItemID)
        if grp != -1:
            if item.Color == 0:
                Gumps.AddImage(gd, 0, 0, grp + 50000)
            else:
                Gumps.AddImage(gd, 0, 0, grp + 50000, item.Color - 1)

    Gumps.SendGump(GUMP_PD, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


test()
