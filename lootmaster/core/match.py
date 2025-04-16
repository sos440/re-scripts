import os
import sys
import re
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

from summary import ItemSummary


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
        elif match_dict["type"] == "LootMatchSerial":
            return LootMatchSerial.load(match_dict)
        elif match_dict["type"] == "LootMatchName":
            return LootMatchName.load(match_dict)
        elif match_dict["type"] == "LootMatchWeight":
            return LootMatchWeight.load(match_dict)
        elif match_dict["type"] == "LootMatchRarity":
            return LootMatchRarity.load(match_dict)
        elif match_dict["type"] == "LootMatchProperty":
            return LootMatchProperty.load(match_dict)
        elif match_dict["type"] == "LootMatchMagicProperty":
            return LootMatchMagicProperty.load(match_dict)
        elif match_dict["type"] == "LootMatchAll":
            return LootMatchAll.load(match_dict)
        elif match_dict["type"] == "LootMatchAny":
            return LootMatchAny.load(match_dict)
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


class LootMatchSerial(LootMatch):
    """
    A class that defines criteria for matching items based on their serial number.

    Attributes:
        name (str): The name of the item to match.
        serial (int): The serial number to match against.
    """

    def __init__(self, name: str, serial: int):
        self.name = name
        self.serial = serial

    def test(self, item: ItemSummary) -> bool:
        return item.serial == self.serial

    def to_dict(self) -> dict:
        return {
            "type": "LootMatchSerial",
            "name": self.name,
            "serial": self.serial,
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchSerial":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "serial" in match_dict
        assert match_dict["type"] == "LootMatchSerial"

        return LootMatchSerial(
            name=match_dict["name"],
            serial=match_dict["serial"],
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
            assert isinstance(value, str), "Slayer value must be a string."
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


class LootMatchAll(LootMatch):
    """
    A class that matches all criteria in a list of LootMatch objects.
    This class is used to combine multiple matching criteria into a single match.
    """

    def __init__(self, name: str, match_list: List[LootMatch]):
        self.name = name
        self.match_list = match_list

    def test(self, item: ItemSummary) -> bool:
        return all(match.test(item) for match in self.match_list)

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchAll":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "match_list" in match_dict
        assert match_dict["type"] == "LootMatchAll"

        return LootMatchAll(
            name=match_dict["name"],
            match_list=[LootMatch.load(match) for match in match_dict["match_list"]],
        )


class LootMatchAny(LootMatch):
    """
    A class that matches any criteria in a list of LootMatch objects.
    This class is used to combine multiple matching criteria into a single match.
    """

    def __init__(self, name: str, match_list: List[LootMatch]):
        self.name = name
        self.match_list = match_list

    def test(self, item: ItemSummary) -> bool:
        return any(match.test(item) for match in self.match_list)

    @classmethod
    def load(cls, match_dict: dict) -> "LootMatchAny":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "match_list" in match_dict
        assert match_dict["type"] == "LootMatchAny"

        return LootMatchAny(
            name=match_dict["name"],
            match_list=[LootMatch.load(match) for match in match_dict["match_list"]],
        )


################################################################################
# Loot Rules
################################################################################


class LootRules(LootMatch):
    name: str
    enabled: bool
    highlight: bool
    highlight_color: int
    notify: bool
    lootbag: Optional[LootMatch]
    match_base: List[LootMatch]
    match_props: List[LootMatch]
    match_except: List[LootMatch]

    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.highlight = False
        self.highlight_color = 0x04EC  # Default color for highlighting
        self.notify = False
        self.lootbag = None
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
            "highlight": self.highlight,
            "highlight_color": self.highlight_color,
            "notify": self.notify,
            "lootbag": self.lootbag.to_dict() if self.lootbag else None,
            "match_base": [match.to_dict() for match in self.match_base],
            "match_props": [match.to_dict() for match in self.match_props],
            "match_except": [match.to_dict() for match in self.match_except],
        }

    @classmethod
    def load(cls, match_dict: dict) -> "LootRules":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "enabled" in match_dict
        assert "highlight" in match_dict
        # assert "highlight_color" in match_dict
        assert "notify" in match_dict
        assert "lootbag" in match_dict
        assert "match_base" in match_dict
        assert "match_props" in match_dict
        assert "match_except" in match_dict
        assert match_dict["type"] == "LootRules"

        rule = LootRules(match_dict["name"])
        rule.enabled = match_dict["enabled"]
        rule.highlight = match_dict["highlight"]
        rule.highlight_color = match_dict["highlight_color"]
        rule.notify = match_dict["notify"]
        rule.lootbag = LootMatch.load(match_dict["lootbag"]) if match_dict["lootbag"] else None
        rule.match_base = [LootMatch.load(match) for match in match_dict["match_base"]]
        rule.match_props = [LootMatch.load(match) for match in match_dict["match_props"]]
        rule.match_except = [LootMatch.load(match) for match in match_dict["match_except"]]
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
    def load(cls, match_dict: dict) -> "LootProfile":
        assert "type" in match_dict
        assert "name" in match_dict
        assert "rules" in match_dict
        assert match_dict["type"] == "LootProfile"

        profile = LootProfile(match_dict["name"])
        profile.rules = [LootRules.load(rule) for rule in match_dict["rules"]]
        return profile


__all__ = [
    "LootMatch",
    "LootMatchItemBase",
    "LootMatchItemGroup",
    "LootMatchName",
    "LootMatchWeight",
    "LootMatchRarity",
    "LootMatchProperty",
    "LootMatchMagicProperty",
    "LootMatchAll",
    "LootMatchAny",
    "LootRules",
    "LootProfile",
]
