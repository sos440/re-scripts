import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any, Union, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


################################################################################
# Path and Directory Setup
################################################################################


PATH_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_EXPORT_DIR = os.path.join(PATH_SCRIPT_DIR, "exports")
if not os.path.exists(PATH_EXPORT_DIR):
    os.makedirs(PATH_EXPORT_DIR)


################################################################################
# Magic Property Parsing
################################################################################


RARITY_MAP = {
    "Minor Magic Item": 0,
    "Lesser Magic Item": 1,
    "Greater Magic Item": 2,
    "Major Magic Item": 3,
    "Minor Artifact": 4,
    "Lesser Artifact": 5,
    "Greater Artifact": 6,
    "Major Artifact": 7,
    "Legendary Artifact": 8,
}


def to_proper_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


class MagicProperty:
    """
    A class representing a magic property of an item.

    Attributes:
        name (str): The name of the magic property.
        prop_type (str): The type of the magic property.
        key (Optional[str]): The key associated with the magic property, if any.
    """

    def __init__(self, name: str, prop_type: str, key: Optional[str] = None):
        self.name = name
        self.type = prop_type
        self.key = key

    @classmethod
    def parse_xml_db(cls, xml_db: str) -> List["MagicProperty"]:
        """
        Parse the XML data for magic properties and return a dictionary of properties.
        """
        root = ET.fromstring(xml_db)
        properties = []
        for prop in root.findall("property"):
            name = prop.get("name")
            prop_type = prop.get("type")
            assert name is not None, "Property name is missing"
            assert prop_type is not None, "Property type is missing"
            prop_key = prop.get("key", None)
            properties.append(MagicProperty(name, prop_type, prop_key))
        return properties


MAGIC_PROP_DB = MagicProperty.parse_xml_db(
    """<?xml version="1.0" encoding="utf-8"?>
<root>
    <!-- Stat & Resist Item Properties -->
    <property name="Strength Bonus" key="Str" type="int" />
    <property name="Dexterity Bonus" key="Dex" type="int" />
    <property name="Intelligence Bonus" key="Int" type="int" />
    <property name="Hit Point Increase" key="Hits" type="int" />
    <property name="Hit Point Regeneration" key="HitsRegen" type="int" />
    <property name="Stamina Increase" key="Stam" type="int" />
    <property name="Stamina Regeneration" key="StamRegen" type="int" />
    <property name="Mana Increase" key="Mana" type="int" />
    <property name="Mana Regeneration" key="ManaRegen" type="int" />
    <property name="Luck" key="Luck" type="int" />
    <property name="Physical Resist" key="PhysRes" type="percent" />
    <property name="Cold Resist" key="ColdRes" type="percent" />
    <property name="Fire Resist" key="FireRes" type="percent" />
    <property name="Poison Resist" key="PoisonRes" type="percent" />
    <property name="Energy Resist" key="EnergyRes" type="percent" />

    <!-- Melee Item Properties -->
    <property name="Damage Increase" key="DI" type="percent" />
    <property name="Defense Chance Increase" key="DCI" type="percent" />
    <property name="Hit Chance Increase" key="HCI" type="percent" />
    <property name="Swing Speed Increase" key="SSI" type="percent" />
    <property name="Soul Charge" type="percent" />
    <property name="Reactive Paralyze" type="bool" />
    <property name="Reflect Physical Damage" key="RPD" type="percent" />
    <property name="Battle Lust" type="bool" />
    <property name="Blood Drinker" type="bool" />
    <property name="Balanced" type="bool" />
    <property name="Searing Weapon" type="bool" />
    <property name="Use Best Weapon Skill" type="bool" />
    <property name="Fire Eater" type="percent" />
    <property name="Cold Eater" type="percent" />
    <property name="Poison Eater" type="percent" />
    <property name="Energy Eater" type="percent" />
    <property name="Kinetic Eater" type="percent" />
    <property name="Damage Eater" type="percent" />
    <property name="Physical Damage" type="percent" />
    <property name="Cold Damage" type="percent" />
    <property name="Fire Damage" type="percent" />
    <property name="Poison Damage" type="percent" />
    <property name="Energy Damage" type="percent" />
    <property name="Chaos Damage" type="percent" />

    <!-- Caster Item Properties -->
    <property name="Spell Damage Increase" key="SDI" type="percent" />
    <property name="Casting Focus" type="int" />
    <property name="Lower Mana Cost" key="LMC" type="percent" />
    <property name="Lower Reagent Cost" key="LRC" type="percent" />
    <property name="Mage Weapon" type="int" />
    <property name="Faster Cast Recovery" key="FCR" type="int" />
    <property name="Faster Casting" key="FC" type="int" />
    <property name="Spell Channeling" type="bool" />
    <property name="Mage Armor" type="bool" />

    <!-- Skills -->
    <property name="Alchemy" type="int" />
    <property name="Anatomy" type="int" />
    <property name="Animal Lore" type="int" />
    <property name="Item Identification" type="int" />
    <property name="Arms Lore" type="int" />
    <property name="Parry" type="int" />
    <property name="Begging" type="int" />
    <property name="Blacksmithing" type="int" />
    <property name="Bowcraft/Fletching" type="int" />
    <property name="Peacemaking" type="int" />
    <property name="Camping" type="int" />
    <property name="Carpentry" type="int" />
    <property name="Cartography" type="int" />
    <property name="Cooking" type="int" />
    <property name="Detect Hidden" type="int" />
    <property name="Discordance" type="int" />
    <property name="Evaluating Intelligence" type="int" />
    <property name="Healing" type="int" />
    <property name="Fishing" type="int" />
    <property name="Forensic Evaluation" type="int" />
    <property name="Herding" type="int" />
    <property name="Hiding" type="int" />
    <property name="Provocation" type="int" />
    <property name="Inscription" type="int" />
    <property name="Lockpicking" type="int" />
    <property name="Magery" type="int" />
    <property name="Magic Resist" type="int" />
    <property name="Tactics" type="int" />
    <property name="Snooping" type="int" />
    <property name="Musicianship" type="int" />
    <property name="Poisoning" type="int" />
    <property name="Archery" type="int" />
    <property name="Spirit Speak" type="int" />
    <property name="Stealing" type="int" />
    <property name="Tailoring" type="int" />
    <property name="Animal Taming" type="int" />
    <property name="Taste Identification" type="int" />
    <property name="Tinkering" type="int" />
    <property name="Tracking" type="int" />
    <property name="Veterinary" type="int" />
    <property name="Swordsmanship" type="int" />
    <property name="Mace Fighting" type="int" />
    <property name="Fencing" type="int" />
    <property name="Wrestling" type="int" />
    <property name="Lumberjacking" type="int" />
    <property name="Mining" type="int" />
    <property name="Meditation" type="int" />
    <property name="Stealth" type="int" />
    <property name="Remove Trap" type="int" />
    <property name="Necromancy" type="int" />
    <property name="Focus" type="int" />
    <property name="Chivalry" type="int" />
    <property name="Bushido" type="int" />
    <property name="Ninjitsu" type="int" />
    <property name="Spellweaving" type="int" />
    <property name="Imbuing" type="int" />
    <property name="Mysticism" type="int" />
    <property name="Throwing" type="int" />

    <!-- On Hit Spells -->
    <property name="Hit Magic Arrow" type="percent" />
    <property name="Hit Harm" type="percent" />
    <property name="Hit Fireball" type="percent" />
    <property name="Hit Lightning" type="percent" />
    <property name="Hit Cold Area" type="percent" />
    <property name="Hit Energy Area" type="percent" />
    <property name="Hit Fire Area" type="percent" />
    <property name="Hit Physical Area" type="percent" />
    <property name="Hit Poison Area" type="percent" />
    <property name="Hit Dispel" type="percent" />
    <property name="Hit Curse" type="percent" />
    <property name="Hit Lower Attack" type="percent" />
    <property name="Hit Lower Defense" type="percent" />
    <property name="Hit Life Leech" type="percent" />
    <property name="Hit Mana Leech" type="percent" />
    <property name="Hit Stamina Leech" type="percent" />
    <property name="Hit Fatigue" type="percent" />
    <property name="Hit Mana Drain" type="percent" />
    <property name="Splintering Weapon" type="percent" />
    <property name="Velocity" type="percent" />

    <!-- Special Item Properties -->
    <property name="Gargoyles Only" type="bool" />
    <property name="Elves Only" type="bool" />
    <property name="Night Sight" type="bool" />
    <property name="Self Repair" type="int" />
    <property name="Lower Requirements" type="percent" />
    <property name="Enhance Potions" type="percent" />
    <property name="Artifact Rarity" type="int" />

    <!-- Negatives -->
    <property name="Cursed" type="bool" />
    <property name="Antique" type="bool" />
    <property name="Prized" type="bool" />
    <property name="Brittle" type="bool" />

    <!-- Wands -->
    <property name="Greater Healing Charges" type="int" />
    <property name="Healing Charges" type="int" />
    <property name="Harm Charges" type="int" />
    <property name="Magic Arrow Charges" type="int" />
    <property name="Lightning Charges" type="int" />
</root>
"""
)


class ParsedItem:
    """
    A wrapper class for the Razor Enhanced Item class with additional properties.

    Attributes:
        Serial (int): The serial number of the item.
        ItemID (int): The ID of the item.
        Color (int): The color of the item.
        Amount (int): The amount of the item.
        Name (str): The name of the item.
        Weight (int): The weight of the item. Defaults to `0`.
        Rarity (int): The rarity of the item. Defaults to `-1`.
        MagicProperties (dict): A dictionary of magic properties of the item.

        ContentCount (int): The number of contents in the container. Defaults to `0`.
        ContentMaxCount (int): The maximum number of contents allowed. Defaults to `0`.
        ContentWeight (int): The weight of the contents in the container. Defaults to `0`.
        ContentMaxWeight (int): The maximum weight of the contents allowed. Defaults to `0`.

        DamageMin (int): The minimum damage of the item (if it is a weapon). Defaults to `0`.
        DamageMax (int): The maximum damage of the item (if it is a weapon). Defaults to `0`.
        WeaponSpeed (float): The speed of the weapon. Defaults to `0`.

        Properties (list): A list of properties of the item.

    Methods:
        __init__(item: Item):
            Initializes the ItemSummary with the given item.
    """

    def __init__(self, item):
        self.Serial: int = item.Serial
        self.ItemID: int = item.ItemID
        self.Color: int = item.Color
        self.Amount: int = item.Amount
        self.Name: str = item.Name
        self.Weight: int = item.Weight
        self.Rarity: int = -1
        self.MagicProperties: Dict[str, Union[int, bool, str]] = {}

        self.ContentCount = 0
        self.ContentMaxCount = 0
        self.ContentWeight = 0
        self.ContentMaxWeight = 0
        self.DamageMin = 0
        self.DamageMax = 0
        self.WeaponSpeed = 0

        Items.WaitForProps(item.Serial, 1000)
        self.Properties = Items.GetPropStringList(item.Serial)

        for prop in self.Properties:
            prop = to_proper_case(prop)

            # find content
            res = re.search(r"^Contents: (\d+)/(\d+) Items, (\d+)/(\d+) Stones", prop)
            if res is not None:
                self.ContentCount = int(res.group(1))
                self.ContentMaxCount = int(res.group(2))
                self.ContentWeight = int(res.group(3))
                self.ContentMaxWeight = int(res.group(3))
                continue

            # find damage min/max
            res = re.search(r"^Weapon Damage (\d+) - (\d+)", prop)
            if res is not None:
                self.DamageMin = int(res.group(1))
                self.DamageMax = int(res.group(2))
                continue

            # find weapon speed
            res = re.search(r"^Weapon Speed ([\d\.]+)s", prop)
            if res is not None:
                self.WeaponSpeed = float(res.group(1))
                continue

            # determine rarity
            if prop in RARITY_MAP:
                self.Rarity = RARITY_MAP[prop]
                continue

            # determine slayer property
            res = re.match(r"^(.+) Slayer$", prop)
            if res is not None:
                self.MagicProperties["Slayer"] = res.group(1)
                continue
            elif prop == "Silver":
                self.MagicProperties["Slayer"] = "Undead"
                continue

            # determine magic properties
            for prop_data in MAGIC_PROP_DB:
                prop_name = to_proper_case(prop_data.name)
                if not prop.startswith(prop_name):
                    continue
                if prop_data.type == "percent":
                    res = re.search(r"^" + prop_name + r"\s*:?\s*([+-]?\d+)%$", prop)
                    if res is not None:
                        self.MagicProperties[prop_name] = int(res.group(1))
                        break
                elif prop_data.type == "int":
                    res = re.search(r"^" + prop_name + r"\s*:?\s*([+-]?\d+)$", prop)
                    if res is not None:
                        self.MagicProperties[prop_name] = int(res.group(1))
                        break
                elif prop_data.type == "bool":
                    self.MagicProperties[prop_name] = True
                    break

    @property
    def property_html(self) -> str:
        """
        Returns the HTML representation of the item's properties.
        """
        if len(self.Properties) == 0:
            return "<i>No Properties</i>"

        return f'<basefont color="#FFFF00">{to_proper_case(self.Properties[0])}</basefont>' + "".join(
            [f"<br />{to_proper_case(line)}" for line in self.Properties[1:]]
        )


################################################################################
# Item Parsing
################################################################################


def get_target():
    serial = Target.PromptTarget("Choose the container to examime.", 0x47E)
    if serial == 0:
        return None
    return Items.FindBySerial(serial)


def scan_target(target) -> List[ParsedItem]:
    if target is None:
        return []

    if not Items.WaitForContents(target.Serial, 1000):
        return []

    Misc.Pause(100)
    scan = Items.FindAllByID(list(range(65536)), -1, target.Serial, 0, False)
    return list(map(ParsedItem, scan))


def scan_contained() -> List[ParsedItem]:
    filter = Items.Filter()
    filter.Enabled = True
    scan_all = Items.ApplyFilter(filter)

    backpack = Items.FindBySerial(Player.Backpack.Serial)
    top_containers = {Player.Backpack.Serial: backpack}
    for item in scan_all:
        if not item.OnGround:
            continue
        if not item.IsContainer:
            continue
        dx = Player.Position.X - item.Position.X
        dy = Player.Position.Y - item.Position.Y
        dist = max(abs(dx), abs(dy))
        if dist > 2:
            continue
        top_containers[item.Serial] = item

    contained = []
    for item in scan_all:
        if item.RootContainer == Player.Serial:
            contained.append(ParsedItem(item))
            continue
        if item.RootContainer in top_containers:
            contained.append(ParsedItem(item))
            continue

    return contained


################################################################################
# Display
################################################################################


GUMP_MENU = hash("MagicItemViewer") & 0xFFFFFFFF
GUMP_PROMPT = hash("MagicItemSortByPrompt") & 0xFFFFFFFF


class ViewerContext:
    def __init__(self, items: List[ParsedItem]):
        self.items = items
        self.items_per_page = 16
        self.page = 0
        self.sort_by: Optional[str] = None
        self.sort_by_type: Optional[str] = None
        self.sort_order = "dsc"  # "asc" or "dsc"
        self.filter = None

    def key(self, item: ParsedItem) -> Any:
        if self.sort_by is None:
            return item.Serial
        if self.sort_by == "Name":
            return item.Name
        if self.sort_by == "Rarity":
            return item.Rarity
        if self.sort_by == "Weight":
            return item.Weight
        if self.sort_by == "Damage":
            return (item.DamageMin, item.DamageMax)
        if self.sort_by == "Speed":
            return item.WeaponSpeed
        return int(item.MagicProperties.get(self.sort_by, 0))

    def sort_items(self) -> None:
        if self.sort_order == "asc":
            self.items.sort(key=self.key)
        elif self.sort_order == "dsc":
            self.items.sort(key=self.key, reverse=True)
        else:
            raise ValueError(f"Invalid sort order: {self.sort_order}")

    @property
    def max_page(self) -> int:
        return (len(self.items) - 1) // self.items_per_page

    def prev_page(self) -> None:
        if self.page > 0:
            self.page -= 1

    def next_page(self) -> None:
        if self.page < self.max_page:
            self.page += 1


def gump_menu(ctx: ViewerContext) -> None:
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 800, 600, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 800, 600)
    Gumps.AddHtml(
        gd, 10, 10, 780, 18, '<center><basefont color="#FFFFFF">Magic Item Viewer</basefont></center>', False, False
    )

    # Header
    Gumps.AddLabelCropped(gd, 10, 40, 40, 18, 88, "Index")
    Gumps.AddLabelCropped(gd, 50, 40, 200, 18, 88, "Name")
    if ctx.sort_by is None:
        Gumps.AddLabelCropped(gd, 260, 40, 170, 18, 88, "Sort by What?")
    else:
        Gumps.AddLabelCropped(gd, 260, 40, 170, 18, 88, f"{ctx.sort_by}")
    Gumps.AddButton(gd, 430, 38, 4005, 4007, 1101, 1, 0)
    if ctx.sort_order == "asc":
        Gumps.AddButton(gd, 460, 39, 251, 250, 1201, 1, 0)
    elif ctx.sort_order == "dsc":
        Gumps.AddButton(gd, 460, 39, 253, 252, 1201, 1, 0)
    Gumps.AddLabelCropped(gd, 490, 40, 200, 18, 88, "Actions")

    # List the items
    i_min = ctx.page * ctx.items_per_page
    i_max = min(i_min + ctx.items_per_page, len(ctx.items))
    for i in range(i_min, i_max):
        row = i % ctx.items_per_page
        y = 70 + row * 30
        item = ctx.items[i]

        Gumps.AddLabelCropped(gd, 10, y, 40, 18, 53, str(i + 1))
        Gumps.AddLabelCropped(gd, 50, y, 200, 18, 1153, to_proper_case(item.Name))
        Gumps.AddTooltip(gd, item.property_html)

        if ctx.sort_by is not None:
            color = 0x3B2 if ctx.key(item) == 0 else 1153
            if ctx.sort_by_type == "percent":
                Gumps.AddLabelCropped(gd, 260, y, 200, 18, color, f"{ctx.key(item)}%")
            elif ctx.sort_by_type == "int":
                Gumps.AddLabelCropped(gd, 260, y, 200, 18, color, f"{ctx.key(item)}")
            elif ctx.sort_by_type == "bool":
                Gumps.AddLabelCropped(gd, 260, y, 200, 18, color, "Yes" if ctx.key(item) else "No")
            else:
                Gumps.AddLabelCropped(gd, 260, y, 200, 18, color, str(ctx.key(item)))

        Gumps.AddButton(gd, 490, y - 2, 4005, 4007, 2000 + i, 1, 0)
        Gumps.AddTooltip(gd, item.property_html)
        Gumps.AddLabelCropped(gd, 525, y, 100, 18, 1153, "To Inventory")
        Gumps.AddButton(gd, 625, y - 2, 4005, 4007, 3000 + i, 1, 0)
        Gumps.AddTooltip(gd, item.property_html)
        Gumps.AddLabelCropped(gd, 660, y, 100, 18, 1153, "Equip")

    # Footer
    Gumps.AddButton(gd, 10, 568, 4014, 4016, 1001, 1, 0)
    Gumps.AddLabel(gd, 45, 570, 1153, "Previous Page")
    Gumps.AddButton(gd, 160, 568, 4005, 4007, 1002, 1, 0)
    Gumps.AddLabel(gd, 195, 570, 1153, "Next Page")
    Gumps.AddButton(gd, 310, 568, 4017, 4019, 1000, 1, 0)
    Gumps.AddLabel(gd, 345, 570, 1153, "Exit")
    Gumps.AddLabel(gd, 700, 570, 1153, f"Page {ctx.page + 1} / {ctx.max_page + 1}")

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def prompt_sort_by() -> Tuple[Optional[str], Optional[str]]:
    Gumps.CloseGump(GUMP_PROMPT)

    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 500, 400, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 500, 400)
    Gumps.AddHtml(
        gd,
        10,
        10,
        480,
        18,
        '<center><basefont color="#FFFFFF">Which properto to sort by?</basefont></center>',
        False,
        False,
    )

    rows = 15
    cols = 2
    max_page = (len(MAGIC_PROP_DB) - 1) // (rows * cols)
    for i, prop_data in enumerate(MAGIC_PROP_DB):
        cur_page = i // (rows * cols)
        cur_idx = i % (rows * cols)
        if cur_idx == 0:
            Gumps.AddPage(gd, cur_page + 1)
            Gumps.AddButton(gd, 10, 368, 4014, 4016, 0, 0, max(cur_page, 1))
            Gumps.AddLabel(gd, 45, 370, 1153, "Previous")
            Gumps.AddButton(gd, 110, 368, 4005, 4007, 0, 0, min(cur_page + 2, max_page))
            Gumps.AddLabel(gd, 145, 370, 1153, "Next")
        cur_row = cur_idx % rows
        cur_col = cur_idx // rows
        x = 10 + 240 * cur_col
        y = 50 + 20 * cur_row
        Gumps.AddButton(gd, x, y - 2, 4005, 4007, 1000 + i, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y, 205, 18, 1153, prop_data.name)

    Gumps.SendGump(GUMP_PROMPT, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
    if not Gumps.WaitForGump(GUMP_PROMPT, 3600000):
        return None, None
    gd = Gumps.GetGumpData(GUMP_PROMPT)
    if gd.buttonid >= 1000:
        i = gd.buttonid - 1000
        return MAGIC_PROP_DB[i].name, MAGIC_PROP_DB[i].type
    return None, None


def main():
    target = get_target()
    if target is None:
        Misc.SendMessage("Failed to identify the target.", 33)
        return

    parsed = scan_target(target)
    if len(parsed) == 0:
        Misc.SendMessage("No items found.", 33)
        return

    ctx = ViewerContext(parsed)
    ctx.sort_items()

    while Player.Connected:
        gump_menu(ctx)
        if not Gumps.WaitForGump(GUMP_MENU, 3600000):
            continue
        gd = Gumps.GetGumpData(GUMP_MENU)
        if gd.buttonid == 1000:
            break
        if gd.buttonid == 0:
            ctx.items = scan_target(target)
            ctx.sort_items()
            continue
        if gd.buttonid == 1001:
            ctx.prev_page()
            continue
        if gd.buttonid == 1002:
            ctx.next_page()
            continue
        if gd.buttonid == 1101:
            sort_by, sort_by_type = prompt_sort_by()
            if sort_by is None:
                continue
            ctx.sort_by = sort_by
            ctx.sort_by_type = sort_by_type
            ctx.sort_items()
            continue
        if gd.buttonid == 1201:
            if ctx.sort_order == "asc":
                ctx.sort_order = "dsc"
            else:
                ctx.sort_order = "asc"
            ctx.sort_items()
            continue
        if 2000 <= gd.buttonid < 3000:
            i = gd.buttonid - 2000
            Items.Move(ctx.items[i].Serial, Player.Backpack.Serial, -1)
            ctx.items = scan_target(target)
            ctx.sort_items()
            continue
        if 3000 <= gd.buttonid < 4000:
            i = gd.buttonid - 3000
            Player.EquipItem(ctx.items[i].Serial)
            ctx.items = scan_target(target)
            ctx.sort_items()
            continue


main()
