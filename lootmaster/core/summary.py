import os
import sys
import re
import xml.etree.ElementTree as ET
from typing import Optional, Union, Any, Dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)


################################################################################
# Property Parser
################################################################################


RARITY_MAP = {
    "minor magic item": 0,
    "lesser magic item": 1,
    "greater magic item": 2,
    "major magic item": 3,
    "minor artifact": 4,
    "lesser artifact": 5,
    "greater artifact": 6,
    "major artifact": 7,
    "legendary artifact": 8,
}


def parse_magic_prop_db(xml_data: str) -> dict:
    """
    Parse the XML data for magic properties and return a dictionary of properties.
    """
    root = ET.fromstring(xml_data)
    properties = {}
    for prop in root.findall("property"):
        name = prop.get("name")
        prop_type = prop.get("type")
        properties[name] = {"type": prop_type}
    return properties


with open(os.path.join(PATH, "magic_prop_db.xml"), "r") as file:
    MAGIC_PROPERTY_DATA = parse_magic_prop_db(file.read())


class ItemSummary:
    """
    A class that summarizes item information.

    Attributes:
        serial (int): The serial number of the item.
        id (int): The ID of the item.
        color (int): The color of the item.
        amount (int): The amount of the item.
        name (str): The name of the item.
        weight (int): The weight of the item. Defaults to `0`.
        rarity (int): The rarity of the item. Defaults to `-1`.
        magic_props (dict): A dictionary of magic properties of the item.

        content_count (int): The number of contents in the container. Defaults to `0`.
        content_maxcount (int): The maximum number of contents allowed. Defaults to `0`.
        content_weight (int): The weight of the contents in the container. Defaults to `0`.
        content_maxweight (int): The maximum weight of the contents allowed. Defaults to `0`.

        damage_min (int): The minimum damage of the item (if it is a weapon). Defaults to `0`.
        damage_max (int): The maximum damage of the item (if it is a weapon). Defaults to `0`.
        weapon_speed (float): The speed of the weapon. Defaults to `0`.

        props (list): A list of properties of the item.

    Methods:
        __init__(item: Item):
            Initializes the ItemSummary with the given item.
    """

    def __init__(self, item):
        self.serial: int = item.Serial
        self.id: int = item.ItemID
        self.color: int = item.Color
        self.amount: int = item.Amount
        self.name: str = item.Name
        self.weight: int = item.Weight
        self.rarity: int = -1
        self.magic_props: Dict[str, Union[int, bool, str]] = {}

        self.content_count = 0
        self.content_maxcount = 0
        self.content_weight = 0
        self.content_maxweight = 0
        self.damage_min = 0
        self.damage_max = 0
        self.weapon_speed = 0

        Items.WaitForProps(item.Serial, 1000)
        self.props = Items.GetPropStringList(item.Serial)

        for prop in self.props:
            prop = prop.lower()

            # find content
            res = re.search(r"^contents: (\d+)/(\d+) items, (\d+)/(\d+) stones", prop)
            if res is not None:
                self.content_count = int(res.group(1))
                self.content_maxcount = int(res.group(2))
                self.content_weight = int(res.group(3))
                self.content_maxweight = int(res.group(3))
                continue

            # find damage min/max
            res = re.search(r"^weapon damage (\d+) - (\d+)", prop)
            if res is not None:
                self.damage_min = int(res.group(1))
                self.damage_max = int(res.group(2))
                continue

            # find weapon speed
            res = re.search(r"^weapon speed ([\d\.]+)s", prop)
            if res is not None:
                self.weapon_speed = float(res.group(1))
                continue

            # determine rarity
            if prop in RARITY_MAP:
                self.rarity = RARITY_MAP[prop]
                continue

            # determine slayer property
            res = re.match(r"^(.+) slayer$", prop)
            if res is not None:
                self.magic_props["Slayer"] = res.group(1)
                continue
            elif prop == "silver":
                self.magic_props["Slayer"] = "undead"
                continue

            # determine magic properties
            for magic_prop, prop_data in MAGIC_PROPERTY_DATA.items():
                magic_prop = magic_prop.lower()
                if not prop.startswith(magic_prop):
                    continue
                if prop_data["type"] == "percent":
                    res = re.search(r"^" + magic_prop + r"\s*:?\s*([+-]?\d+)%$", prop)
                    if res is not None:
                        self.magic_props[magic_prop] = int(res.group(1))
                        break
                elif prop_data["type"] == "int":
                    res = re.search(r"^" + magic_prop + r"\s*:?\s*([+-]?\d+)$", prop)
                    if res is not None:
                        self.magic_props[magic_prop] = int(res.group(1))
                        break
                elif prop_data["type"] == "bool":
                    self.magic_props[magic_prop] = True
                    break
