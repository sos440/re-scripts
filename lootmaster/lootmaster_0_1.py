import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Optional, Union, List


################################################################################
# Default Values
################################################################################


SAVE_DIR = "./Data/Lootmaster/"
PROFILE_DIR = os.path.join(SAVE_DIR, "Profiles")
RULE_DIR = os.path.join(SAVE_DIR, "Rules")


################################################################################
# Logger
################################################################################


class Logger:
    @classmethod
    def Error(cls, msg: str):
        Misc.SendMessage(msg, 33)

    @classmethod
    def Warn(cls, msg: str):
        Misc.SendMessage(msg, 43)

    @classmethod
    def Info(cls, msg: str):
        Misc.SendMessage(msg, 63)

    @classmethod
    def Debug(cls, msg: str):
        Misc.SendMessage(msg, 0x3B2)


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


MAGIC_PROPERTY_DATA = parse_magic_prop_db(
    """<root>
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

    <!-- Melee Item Properties -->
    <property name="Damage Increase" type="percent" />
    <property name="Defense Chance Increase" type="percent" />
    <property name="Hit Chance Increase" type="percent" />
    <property name="Swing Speed Increase" type="percent" />
    <property name="Soul Charge" type="percent" />
    <property name="Reactive Paralyze" type="bool" />
    <property name="Reflect Physical Damage" type="percent" />
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

    <!-- Caster Item Properties -->
    <property name="Spell Damage Increase" type="percent" />
    <property name="Casting Focus" type="int" />
    <property name="Lower Mana Cost" type="percent" />
    <property name="Lower Reagent Cost" type="percent" />
    <property name="Mage Weapon" type="int" />
    <property name="Faster Cast Recovery" type="int" />
    <property name="Faster Casting" type="int" />
    <property name="Spell Channeling" type="bool" />
    <property name="Mage Armor" type="bool" />

    <!-- Stat & Resist Item Properties -->
    <property name="Strength Bonus" type="int" />
    <property name="Dexterity Bonus" type="int" />
    <property name="Intelligence Bonus" type="int" />
    <property name="Hit Point Increase" type="int" />
    <property name="Hit Point Regeneration" type="int" />
    <property name="Stamina Increase" type="int" />
    <property name="Stamina Regeneration" type="int" />
    <property name="Mana Increase" type="int" />
    <property name="Mana Regeneration" type="int" />
    <property name="Luck" type="int" />
    <property name="Physical Resist" type="percent" />
    <property name="Cold Resist" type="percent" />
    <property name="Fire Resist" type="percent" />
    <property name="Poison Resist" type="percent" />
    <property name="Energy Resist" type="percent" />

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

    <!-- Wands -->
    <property name="Greater Healing Charges" type="int" />
    <property name="Healing Charges" type="int" />
    <property name="Harm Charges" type="int" />
    <property name="Magic Arrow Charges" type="int" />
    <property name="Lightning Charges" type="int" />
</root>"""
)


class ItemSummary:
    """
    A class that summarizes item information.

    Attributes:
        serial (int): The serial number of the item.
        id (int): The ID of the item.
        color (int): The color of the item.
        amount (int): The amount of the item.
        name (str): The name of the item.
        weight (int | None): The weight of the item. Defaults to None.
        rarity (int | None): The rarity of the item. Defaults to None.
        magic_props (dict): A dictionary of magic properties of the item.

    Methods:
        __init__(item: Item):
            Initializes the ItemSummary with the given item.
    """

    def __init__(self, item):
        self.serial = item.Serial
        self.id = item.ItemID
        self.color = item.Color
        self.amount = item.Amount
        self.name = item.Name
        self.weight = item.Weight
        self.rarity = None
        self.magic_props = {}

        Items.WaitForProps(item.Serial, 1000)
        self.props = Items.GetPropStringList(item.Serial)

        for prop in self.props:
            prop = prop.lower()

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


################################################################################
# Loot Matching
################################################################################


class LootMatch:
    """
    An abstract base class representing criteria for matching items.
    """

    name: str

    def __init__(self):
        raise NotImplementedError("The initializer must be implemented.")

    def test(self, item: ItemSummary) -> bool:
        raise NotImplementedError("The tester must be implemented.")

    def to_dict(self) -> dict:
        """
        Convert the LootMatch object to a dictionary representation.
        This method should be implemented in subclasses to provide specific serialization logic.
        """
        raise NotImplementedError("The to_dict method must be implemented.")

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatch":
        """
        Load a LootMatch object from a dictionary representation.
        This method should be implemented in subclasses to provide specific deserialization logic.
        """
        if match_dict["type"] == "LootMatchItemBase":
            return LootMatchItemBase.load(match_dict)
        elif match_dict["type"] == "LootMatchItemGroup":
            return LootMatchItemGroup.load(match_dict)
        elif match_dict["type"] == "LootMatchWeight":
            return LootMatchWeight.load(match_dict)
        elif match_dict["type"] == "LootMatchRarity":
            return LootMatchRarity.load(match_dict)
        elif match_dict["type"] == "LootMatchProperty":
            return LootMatchProperty.load(match_dict)
        elif match_dict["type"] == "LootMatchMagicProperty":
            return LootMatchMagicProperty.load(match_dict)
        else:
            raise ValueError(f"Unknown LootMatch type: {match_dict['type']}")


class LootMatchItemBase(LootMatch):
    """
    A class that defines criteria for matching items based on their ID, color, and name.

    Attributes:
        id (int): The base ID of the item to match.
        color (int): The color of the item to match. Defaults to -1, which means any color.
        name (str | None): The name of the item to match. Can be a string or None. Defaults to None.
        is_regex (bool): A flag indicating whether the name should be treated as a regular expression. Defaults to False.
    """

    def __init__(
        self,
        name: str,
        id: int,
        color: int = -1,
    ):
        self.name = name
        self.id = id
        self.color = color

    def test(self, item: ItemSummary) -> bool:
        # Check the id
        if item.id != self.id:
            return False
        # Check the color
        if self.color != -1 and item.color != self.color:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchItemBase",
            "name": self.name,
            "id": self.id,
            "color": self.color,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchItemBase":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "id" in match_dict
        assert "color" in match_dict
        assert match_dict["type"] == "LootMatchItemBase"

        return LootMatchItemBase(
            name=match_dict["name"],
            id=match_dict["id"],
            color=match_dict["color"],
        )


class LootMatchItemGroup(LootMatch):
    """
    A class that represents a group of loot items based on their item IDs.

    Attributes:
        id_list (list[int]): A list of item IDs that belong to this loot group.
    """

    def __init__(self, name: str, id_list: List[int]):
        self.name = name
        self.id_list = id_list

    def test(self, item: ItemSummary) -> bool:
        return item.id in self.id_list

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchItemGroup",
            "name": self.name,
            "id_list": self.id_list,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchItemGroup":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "id_list" in match_dict
        assert match_dict["type"] == "LootMatchItemGroup"

        return LootMatchItemGroup(
            name=match_dict["name"],
            id_list=match_dict["id_list"],
        )


class LootMatchName(LootMatch):
    """
    A class that defines criteria for matching items based on their name.

    Attributes:
        name (str): The name to match against.
        is_regex (bool): A flag indicating whether the name should be treated as a regular expression. Defaults to False.
    """

    def __init__(self, name: str, pattern: str, is_regex: bool = False):
        self.name = name
        self.pattern = pattern
        self.is_regex = is_regex

    def test(self, item: ItemSummary) -> bool:
        if self.is_regex:
            return re.search(self.pattern, item.name) is not None
        else:
            return self.pattern.lower() in item.name.lower()

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchName",
            "name": self.name,
            "pattern": self.pattern,
            "is_regex": self.is_regex,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchName":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "pattern" in match_dict
        assert "is_regex" in match_dict
        assert match_dict["type"] == "LootMatchName"

        return LootMatchName(
            name=match_dict["name"],
            pattern=match_dict["pattern"],
            is_regex=match_dict["is_regex"],
        )


class LootMatchWeight(LootMatch):
    """
    A class that defines criteria for matching items based on their weight.

    Attributes:
        weight_min (int): The minimum weight to match against.
        weight_max (int): The maximum weight to match against.
    """

    def __init__(self, name: str = "Weight Range", weight_min: int = 0, weight_max: int = 255):
        self.name = name
        self.weight_min = weight_min
        self.weight_max = weight_max

    def test(self, item: ItemSummary) -> bool:
        if item.weight is None:
            return False
        return self.weight_min <= item.weight <= self.weight_max

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchWeight",
            "name": self.name,
            "weight_min": self.weight_min,
            "weight_max": self.weight_max,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchWeight":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "weight_min" in match_dict
        assert "weight_max" in match_dict
        assert match_dict["type"] == "LootMatchWeight"

        return LootMatchWeight(
            name=match_dict["name"],
            weight_min=match_dict["weight_min"],
            weight_max=match_dict["weight_max"],
        )


class LootMatchRarity(LootMatch):
    """
    A class that defines criteria for matching items based on their rarity.

    Attributes:
        rarity (int): The rarity level to match against.
    """

    def __init__(self, name: str = "Rarity Range", rarity_min: int = 0, rarity_max: int = 8):
        self.name = name
        self.rarity_min = rarity_min
        self.rarity_max = rarity_max

    def test(self, item: ItemSummary) -> bool:
        if item.rarity is None:
            return False
        return self.rarity_min <= item.rarity <= self.rarity_max

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchRarity",
            "name": self.name,
            "rarity_min": self.rarity_min,
            "rarity_max": self.rarity_max,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchRarity":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "rarity_min" in match_dict
        assert "rarity_max" in match_dict
        assert match_dict["type"] == "LootMatchRarity"

        return LootMatchRarity(
            name=match_dict["name"],
            rarity_min=match_dict["rarity_min"],
            rarity_max=match_dict["rarity_max"],
        )


class LootMatchProperty(LootMatch):
    """
    A class that defines criteria for matching items based on their properties.

    Attributes:
        pattern (str): The pattern to match against item properties.
        is_regex (bool): A flag indicating whether the pattern should be treated as a regular expression. Defaults to False.
    """

    def __init__(
        self,
        name: str = "Property Match",
        pattern: Optional[str] = None,
        is_regex: bool = False,
    ):
        assert pattern is not None, "Pattern must be provided."
        self.name = name
        self.pattern = pattern
        self.is_regex = is_regex

    def test(self, item: ItemSummary) -> bool:
        if self.is_regex:
            return any(re.search(self.pattern, prop.lower()) for prop in item.props)
        else:
            return any(self.pattern.lower() in prop.lower() for prop in item.props)

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchProperty",
            "name": self.name,
            "pattern": self.pattern,
            "is_regex": self.is_regex,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchProperty":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "pattern" in match_dict
        assert "is_regex" in match_dict
        assert match_dict["type"] == "LootMatchProperty"

        return LootMatchProperty(
            name=match_dict["name"],
            pattern=match_dict["pattern"],
            is_regex=match_dict["is_regex"],
        )


class LootMatchMagicProperty(LootMatch):
    """
    A class that defines criteria for matching items based on their magic properties.

    Attributes:
        prop (str): The magic property to match against.
        value (int): The value of the magic property to match against.
        is_regex (bool): A flag indicating whether the value should be treated as a regular expression. Defaults to False.
    """

    def __init__(
        self,
        name: str = "Magic Property Match",
        prop: Optional[str] = None,
        min_value: int = 0,
    ):
        assert prop is not None, "Property must be provided."
        self.name = name
        self.prop = prop
        if prop == "Silver":
            self.prop = "Undead Slayer"
        self.min_value = min_value

    def test(self, item: ItemSummary) -> bool:
        if self.prop.endswith("Slayer"):
            value = item.magic_props.get("Slayer", None)
            if value is None:
                return False
            match = re.search(r"^(.+) slayer$", self.prop.lower())
            if match is None:
                return False
            return value.lower() == match.group(1)

        value = item.magic_props.get(self.prop, None)
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value >= self.min_value

        return False

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchMagicProperty",
            "name": self.name,
            "prop": self.prop,
            "min_value": self.min_value,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchMagicProperty":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "prop" in match_dict
        assert "min_value" in match_dict
        assert match_dict["type"] == "LootMatchMagicProperty"

        return LootMatchMagicProperty(
            name=match_dict["name"],
            prop=match_dict["prop"],
            min_value=match_dict["min_value"],
        )


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


################################################################################
# Loot Rules
################################################################################


class LootRules(LootMatch):
    name: str
    enabled: bool
    notify: bool
    lootbag: int
    match_base: List[LootMatch]
    match_props: List[LootMatch]
    match_except: List[LootMatch]

    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.notify = True
        self.lootbag = 0
        self.match_base = []
        self.match_props = []
        self.match_except = []

    def test(self, item: ItemSummary) -> bool:
        if not self.enabled:
            return False
        if self.match_base and not any(match.test(item) for match in self.match_base):
            return False
        if not all(match.test(item) for match in self.match_props):
            return False
        if any(match.test(item) for match in self.match_except):
            return False
        return True

    def add_match_base(self, match: LootMatch) -> LootMatch:
        self.match_base.append(match)
        return match

    def add_match_props(self, match: LootMatch) -> LootMatch:
        self.match_props.append(match)
        return match

    def add_match_except(self, match: LootMatch) -> LootMatch:
        self.match_except.append(match)
        return match

    def remove_match_base(self, match: LootMatch):
        self.match_base.remove(match)

    def remove_match_props(self, match: LootMatch):
        self.match_props.remove(match)

    def remove_match_except(self, match: LootMatch):
        self.match_except.remove(match)

    def to_dict(self) -> dict:
        return {
            "type": "LootRules",
            "name": self.name,
            "enabled": self.enabled,
            "notify": self.notify,
            "lootbag": self.lootbag,
            "match_base": [match.to_dict() for match in self.match_base],
            "match_props": [match.to_dict() for match in self.match_props],
            "match_except": [match.to_dict() for match in self.match_except],
        }

    @classmethod
    def load(cls, rule_dict: dict) -> "LootRules":
        assert "type" in rule_dict
        assert "name" in rule_dict
        assert "enabled" in rule_dict
        assert "notify" in rule_dict
        assert "lootbag" in rule_dict
        assert "match_base" in rule_dict
        assert "match_props" in rule_dict
        assert "match_except" in rule_dict
        assert rule_dict["type"] == "LootRules"

        rule = LootRules(rule_dict["name"])
        rule.enabled = rule_dict["enabled"]
        rule.notify = rule_dict["notify"]
        rule.lootbag = rule_dict["lootbag"]
        rule.match_base = [LootMatch.load(match) for match in rule_dict["match_base"]]
        rule.match_props = [LootMatch.load(match) for match in rule_dict["match_props"]]
        rule.match_except = [LootMatch.load(match) for match in rule_dict["match_except"]]
        return rule


class LootProfile(LootMatch):
    name: str
    rules: list[LootRules]

    def __init__(self, name: str):
        self.name = name
        self.rules = []

    def test(self, item: ItemSummary) -> bool:
        return any(rule.test(item) for rule in self.rules)

    def add_rule(self, rule: LootRules) -> LootRules:
        self.rules.append(rule)
        return rule

    def remove_rule(self, rule: LootRules):
        self.rules.remove(rule)

    def move_up_rule(self, rule: LootRules):
        index = self.rules.index(rule)
        if index > 0:
            self.rules[index], self.rules[index - 1] = self.rules[index - 1], self.rules[index]

    def move_down_rule(self, rule: LootRules):
        index = self.rules.index(rule)
        if index < len(self.rules) - 1:
            self.rules[index], self.rules[index + 1] = self.rules[index + 1], self.rules[index]

    def to_dict(self) -> dict:
        return {
            "type": "LootProfile",
            "name": self.name,
            "rules": [rule.to_dict() for rule in self.rules],
        }

    @classmethod
    def load(cls, profile_dict: dict) -> "LootProfile":
        assert "type" in profile_dict
        assert "name" in profile_dict
        assert "rules" in profile_dict
        assert profile_dict["type"] == "LootProfile"

        profile = LootProfile(profile_dict["name"])
        profile.rules = [LootRules.load(rule) for rule in profile_dict["rules"]]
        return profile

    @classmethod
    def create_template(cls) -> "LootProfile":
        profile = LootProfile(f"{Player.Name}")

        rule = profile.add_rule(LootRules("Gold"))
        rule.add_match_base(LootMatchPresets.Gold())

        rule = profile.add_rule(LootRules("Gems"))
        rule.add_match_base(LootMatchPresets.Gem())

        rule = profile.add_rule(LootRules("Artifacts"))
        rule.add_match_props(LootMatchWeight(name="No Heavy", weight_max=49))
        rule.add_match_props(LootMatchPresets.Artifact())

        return profile


################################################################################
# Gumps
################################################################################


class GumpWrapper:
    # ToDo: Implement GumpWrapper class to handle gump interactions.
    ...


def gump_shortcut():
    gd = Gumps.CreateGump(movable=True) 
    Gumps.AddPage(gd, 0)
    
    Gumps.AddBackground(gd, 0, 0, 450, 53, 39925) 
    Gumps.AddAlphaRegion(gd,0,0,450,53) 
    Gumps.AddButton(gd, 5, 5, 2241, 2241, 1, 1, 0)
    Gumps.AddTooltip(gd, r"Create Food")
    Gumps.AddButton(gd, 49, 5, 2254, 2254, 2, 1, 0)
    Gumps.AddTooltip(gd, r"Protection")
    Gumps.AddButton(gd, 93, 5, 2261, 2261, 3, 1, 0)
    Gumps.AddTooltip(gd, r"Teleport")
    Gumps.AddButton(gd, 137, 5, 2269, 2269, 4, 1, 0)
    Gumps.AddTooltip(gd, r"Lightning")
    Gumps.AddButton(gd, 181, 5, 2271, 2271, 5, 1, 0)
    Gumps.AddTooltip(gd, r"Recall")
    Gumps.AddButton(gd, 225, 5, 2281, 2281, 6, 1, 0)
    Gumps.AddTooltip(gd, r"Energy Bolt")
    Gumps.AddButton(gd, 269, 5, 2283, 2283, 7, 1, 0)
    Gumps.AddTooltip(gd, r"Invisibility")
    Gumps.AddButton(gd, 313, 5, 2284, 2284, 8, 1, 0)
    Gumps.AddTooltip(gd, r"Mark")
    Gumps.AddButton(gd, 357, 5, 2287, 2287, 9, 1, 0)
    Gumps.AddTooltip(gd, r"Reveal")
    Gumps.AddButton(gd, 401, 5, 2291, 2291, 10, 1, 0)
    Gumps.AddTooltip(gd, r"Gate Travel")
    
    Gumps.SendGump(987654, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)

    Gumps.WaitForGump(987654, 60000)
    Gumps.CloseGump(987654)
    gd = Gumps.GetGumpData(987654)
    if gd.buttonid == 1: 
        Spells.CastMagery('Create Food')
    elif gd.buttonid == 2:
        Spells.CastMagery('Protection')
    elif gd.buttonid == 3:
        Spells.CastMagery('Teleport') 
    elif gd.buttonid == 4:
        Spells.CastMagery('Lightning')
    elif gd.buttonid == 5:
        Spells.CastMagery('Recall')
    elif gd.buttonid == 6:
        Spells.CastMagery('Energy Bolt')
    elif gd.buttonid == 7:
        Spells.CastMagery('Invisibility')
    elif gd.buttonid == 8:
        Spells.CastMagery('Mark') 
    elif gd.buttonid == 9:
        Spells.CastMagery('Reveal') 
    elif gd.buttonid == 10:
        Spells.CastMagery('Gate Travel') 


################################################################################
# Main
################################################################################


SETTING_SCHEMA = {
    "last-profile-path": None,
    "last-profile-name": None,
    "refresh-rate": 500,
    "action-delay": 900,
    "color-corpse-after-looting": True,
    "color-corpse": 1014,
}


def load_setting() -> dict:
    SETTING_PATH = os.path.join(SAVE_DIR, "settings.json")
    setting = None
    if os.path.exists(SETTING_PATH):
        with open(SETTING_PATH, "r") as f:
            setting = json.load(f)
            # Check the validity of the setting
            for option_key in SETTING_SCHEMA:
                if option_key in setting:
                    continue
                Logger.Error(f"Invalid setting file!")
                setting = None
                break

    if setting is None:
        setting = SETTING_SCHEMA.copy()

    return setting


def save_setting(setting: dict):
    SETTING_PATH = os.path.join(SAVE_DIR, "settings.json")
    with open(SETTING_PATH, "w") as f:
        json.dump(setting, f, indent=4)


def load_profile(profile_path: str) -> LootProfile:
    profile_path = os.path.join(PROFILE_DIR, profile_path)
    with open(profile_path, "r") as f:
        profile_dict = json.load(f)
    return LootProfile.load(profile_dict)


def save_profile(profile: LootProfile, profile_path: str):
    profile_path = os.path.join(PROFILE_DIR, profile_path)
    with open(profile_path, "w") as f:
        json.dump(profile.to_dict(), f, indent=4)


def main():
    # Create a profile directory if necessary
    if not os.path.exists(PROFILE_DIR):
        os.mkdir(PROFILE_DIR)

    # Create a rule directory if necessary
    if not os.path.exists(RULE_DIR):
        os.mkdir(RULE_DIR)

    # Load the setting if exists
    setting = load_setting()
    Logger.Info("Lootmaster has been initialized.")

    # Load the last profile if exists, or create a new one
    if setting["last-profile-path"] is not None:
        if os.path.exists(os.path.join(PROFILE_DIR, setting["last-profile-path"])):
            profile = load_profile(setting["last-profile-path"])
            Logger.Info(f"Loaded profile: {profile.name}")
        else:
            Logger.Error(f"Last profile not found: {setting['last-profile-path']}")
            profile = LootProfile.create_template()
    else:
        profile = LootProfile.create_template()
        Logger.Info("No last profile found. Created a new profile.")

    # Save the profile
    filename = f"{profile.name}.json"
    save_profile(profile, filename)
    Logger.Info(f"Profile saved as: {filename}")

    # Update the setting with the last profile path and name
    setting["last-profile-path"] = filename
    setting["last-profile-name"] = profile.name
    save_setting(setting)
    Logger.Info("Setting saved.")


if __name__ == "__main__":
    main()
