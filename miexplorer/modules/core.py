from AutoComplete import *
from typing import Iterable, List, Dict, Set, Tuple, Callable, Generator, Any, Optional, Union, TypeVar, Generic
import re
from enum import Enum


VERSION_CORE = "1.0.0"
"""The version of the magic item explorer core module."""


################################################################################
# Core Structures
################################################################################


CT = TypeVar("CT")
"""Type variable for property values."""


class ItemPropRow:
    """
    This represents a single row of item properties, corresponding to a specific item.
    """

    def __init__(self):
        self.properties: Dict[str, Any] = {}
        self.raw_props: List[str] = []

    def __getitem__(self, key: str) -> Any:
        return self.properties.get(key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        self.properties[key] = value

    def __str__(self) -> str:
        props = [f'"{key}" = {value}' for key, value in self.properties.items()]
        return f"<Item with properties: {', '.join(props)}>"

    def __repr__(self) -> str:
        return self.__str__()

    def has(self, key: str) -> bool:
        return key in self.properties


ItemPropSheet = List[ItemPropRow]
"""This represents a sheet of item properties, containing multiple rows of properties for different items."""


class SortOrder(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"
    UNSORTED = "unsorted"


class PropTypes:
    class Boolean: ...

    class Numeric: ...

    class String: ...

    class Enum: ...


class BaseProp(Generic[CT]):
    """
    This is the base class for item properties.
    """

    default_order: SortOrder = SortOrder.UNSORTED

    def __init__(self, name: str, id: str):
        self.name = name
        self.id = id

    def parse(self, prop: str) -> Optional[CT]:
        """
        Parses the property value from a string.

        :param prop: The string representation of the property.
        :return: The parsed property value.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def stringify(self, row: ItemPropRow) -> Optional[str]:
        """
        Reads the property value from the item property row.

        :param row: The item property row to read from.
        :return: The property value.
        """
        value = self.key(row)
        if value is not None:
            return str(value)

    def key(self, row: ItemPropRow) -> Any:
        """
        This provides the key extraction for the comparison.

        Can be overridden in subclasses to provide custom key extraction logic.

        The return type should be a comparable value, implementing `SupportsRichComparison` protocol.
        """
        return row[self.id]

    def sort(self, sheet: ItemPropSheet, reverse: bool = False) -> ItemPropSheet:
        """
        Sorts the item property sheet based on the filter criteria.

        :param sheet: The item property sheet to sort.
        :param reverse: Whether to sort in reverse order.
        :return: The sorted item property sheet.
        """
        return sorted(sheet, key=self.key, reverse=reverse)

    def set_order(self, order: SortOrder) -> "BaseProp":
        """
        Sets the default sort order of the property and return self.
        """
        self.default_order = order
        return self


class DerivedProp(BaseProp[CT]):
    """
    This represents a derived property, computed using the basic properties.
    """

    def parse(self, prop: str) -> None:
        """
        Derived properties cannot be parsed from strings, and has no intrinsic value.
        """
        return

    def stringify(self, row: ItemPropRow) -> Optional[str]:
        value = self.key(row)
        return str(value) if value is not None else None

    def key(self, row: ItemPropRow) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")


class ComparableProp(BaseProp[CT]):
    """
    This represents a property with values of comparable types.

    The generic type `CT` must be bound to a comparable type, implementing `SupportsDunderLT` protocol.
    """

    class _ValueWrapperNoneIsInf:
        """
        A wrapper for comparable values.

        This ensures that `None` is comparable and treated as the lowest value.
        """

        def __init__(self, value: Optional[CT] = None):
            self.value = value

        def __str__(self) -> str:
            return str(self.value)

        def __eq__(self, other: Any) -> bool:
            if not isinstance(other, self.__class__):
                return NotImplemented
            return self.value == other.value

        def __lt__(self, other: Any) -> bool:
            if not isinstance(other, self.__class__):
                return NotImplemented
            a, b = self.value, other.value
            if a is None and b is None:
                return False
            elif a is None:
                return True
            elif b is None:
                return False
            else:
                return a.__lt__(b)  # type: ignore

        def __gt__(self, other: Any) -> bool:
            if not isinstance(other, self.__class__):
                return NotImplemented
            a, b = self.value, other.value
            if a is None and b is None:
                return False
            elif a is None:
                return False
            elif b is None:
                return True
            else:
                return b.__lt__(a)  # type: ignore

    class _ValueWrapperNoneIsSup:
        """
        A wrapper for comparable values.

        This ensures that `None` is comparable and treated as the highest value.
        """

        def __init__(self, value: Optional[CT] = None):
            self.value = value

        def __str__(self) -> str:
            return str(self.value)

        def __eq__(self, other: Any) -> bool:
            if not isinstance(other, self.__class__):
                return NotImplemented
            return self.value == other.value

        def __lt__(self, other: Any) -> bool:
            if not isinstance(other, self.__class__):
                return NotImplemented
            a, b = self.value, other.value
            if a is None and b is None:
                return False
            elif a is None:
                return False
            elif b is None:
                return True
            else:
                return a.__lt__(b)  # type: ignore

        def __gt__(self, other: Any) -> bool:
            if not isinstance(other, self.__class__):
                return NotImplemented
            a, b = self.value, other.value
            if a is None and b is None:
                return False
            elif a is None:
                return True
            elif b is None:
                return False
            else:
                return b.__lt__(a)  # type: ignore

    def __init__(self, name: str, id: str):
        super().__init__(name, id)
        self.default_order = SortOrder.DESCENDING

    def key_none_is_inf(self, row: ItemPropRow) -> Any:
        return self._ValueWrapperNoneIsInf(self.key(row))

    def key_none_is_sup(self, row: ItemPropRow) -> Any:
        return self._ValueWrapperNoneIsSup(self.key(row))

    def sort(self, sheet: ItemPropSheet, reverse: bool = False) -> ItemPropSheet:
        if reverse:
            return sorted(sheet, key=self.key_none_is_inf, reverse=True)
        else:
            return sorted(sheet, key=self.key_none_is_sup)


class MatchProp(BaseProp[CT]):
    """
    This represents a property that can be matched using a regular expression.
    """

    def __init__(
        self,
        name: str,
        id: str,
        pattern: Union[str, re.Pattern],
        sanitizer: Callable[[str], CT],
    ):
        """
        Initialize a property that can be parsed using regular expressions.

        :param name: The display name of the property. (Example: Strength Increase)
        :param id: The unique string identifier for the property. (Example: Str)
        :param pattern: The regular expression pattern to match the property value.
        :param sanitizer: A function to sanitize the extracted value.
        """
        super().__init__(name, id)
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.sanitizer = sanitizer

    def parse(self, prop: str) -> Union[CT, None]:
        match = self.pattern.match(prop)
        if not match:
            return None
        elif len(match.groups()) >= 1:
            return self.sanitizer(", ".join(g for g in match.groups() if g))
        return None


class ComparableMatchProp(MatchProp[CT], ComparableProp[CT]): ...


class ComparableDerivedProp(DerivedProp[CT], ComparableProp[CT]): ...


class BooleanProp(MatchProp[bool], PropTypes.Boolean):
    """
    This represents a boolean property that can be parsed from a string.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, pattern: Union[str, re.Pattern]):
        """
        Initialize a boolean property.

        :param name: The display name of the property. (Example: Gargoyles Only)
        :param id: The unique string identifier for the property. (Example: GargOnly)
        :param pattern: The regular expression pattern to match the property value.
        """
        super().__init__(name, id, pattern, bool)

    def parse(self, prop: str) -> bool:
        match = self.pattern.match(prop)
        if match is not None:
            return True
        return False

    def key(self, row: ItemPropRow) -> bool:
        return bool(row[self.id])

    def stringify(self, row: ItemPropRow) -> Optional[str]:
        if self.key(row):
            return "Yes"
        return None


class PercentageProp(ComparableMatchProp[int], PropTypes.Numeric):
    """
    This represents a percentage property that can be parsed from a string.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, pattern: str):
        """
        Initialize a percentage property.

        :param name: The display name of the property. (Example: Hit Chance Increase)
        :param id: The unique string identifier for the property. (Example: HCI)
        :param pattern: The prefix of the percentage property.
        """
        super().__init__(name, id, r"^" + pattern + r"\s*:?\s*([+-]?\d+)%$", int)

    def stringify(self, row: ItemPropRow) -> Optional[str]:
        value = super().stringify(row)
        if value is not None:
            return f"{value}%"
        return None


class IntegerProp(ComparableMatchProp[int], PropTypes.Numeric):
    """
    This represents an integer property that can be parsed from a string.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, pattern: str):
        """
        Initialize an integer property.

        :param name: The display name of the property. (Example: Strength Increase)
        :param id: The unique string identifier for the property. (Example: Str)
        :param pattern: The prefix of the integer property.
        """
        super().__init__(name, id, r"^" + pattern + r"\s*:?\s*([+-]?\d+)$", int)


class EnumProp(ComparableProp[int], PropTypes.Enum):
    """
    This represents a property which can take on a limited set of string values.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, pattern_to_value: Dict[str, int], value_to_str: Dict[int, str]):
        """
        Initialize an enum property.

        :param name: The display name of the property.
        :param id: The unique string identifier for the property.
        :param pattern_to_value: A mapping from regex patterns to their corresponding integer values.
        :param value_to_str: A mapping from integer values to their corresponding string representations.
        """
        super().__init__(name, id)
        self.pattern_to_value = pattern_to_value
        self.value_to_str = value_to_str

    def parse(self, prop: str) -> Union[int, None]:
        for pattern, value in self.pattern_to_value.items():
            if re.match(pattern, prop):
                return value
        return None

    def stringify(self, row: ItemPropRow) -> Optional[str]:
        if row.has(self.id):
            return self.value_to_str.get(row[self.id], None)
        return None


class AnyProp(DerivedProp[bool]):
    """
    This property matches any of the specified boolean property IDs.

    This does not check if the provided keys actually exist in the row
    or they are actually boolean values.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, prop_ids: List[str]):
        super().__init__(name, id)
        self.prop_ids = prop_ids

    def key(self, row: ItemPropRow) -> bool:
        return any(row[prop_id] for prop_id in self.prop_ids)


class AllProp(DerivedProp[bool]):
    """
    This property matches all of the specified boolean property IDs.

    This does not check if the provided keys actually exist in the row
    or they are actually boolean values.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, prop_ids: List[str]):
        super().__init__(name, id)
        self.prop_ids = prop_ids

    def key(self, row: ItemPropRow) -> bool:
        return all(row[prop_id] for prop_id in self.prop_ids)


class IntegerSumProp(DerivedProp[int], ComparableProp[int], PropTypes.Numeric):
    """
    This property calculates the sum of the specified integer property IDs.

    This does not check if the provided keys actually exist in the row
    or they are actually integer values.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, prop_ids: List[str]):
        super().__init__(name, id)
        self.prop_ids = prop_ids

    def key(self, row: ItemPropRow) -> Optional[int]:
        values = [row[prop_id] for prop_id in self.prop_ids if row[prop_id] is not None]
        if len(values) == 0:
            return None
        return sum(values)


class IntegerMaxProp(DerivedProp[int], ComparableProp[int], PropTypes.Numeric):
    """
    This property calculates the maximum of the specified integer property IDs.

    This does not check if the provided keys actually exist in the row
    or they are actually integer values.
    """

    default_order: SortOrder = SortOrder.DESCENDING

    def __init__(self, name: str, id: str, prop_ids: List[str]):
        super().__init__(name, id)
        self.prop_ids = prop_ids

    def key(self, row: ItemPropRow) -> Optional[int]:
        values = [row[prop_id] for prop_id in self.prop_ids if row[prop_id] is not None]
        if len(values) == 0:
            return None
        return max(values)


class IntegerMinProp(DerivedProp[int], ComparableProp[int], PropTypes.Numeric):
    """
    This property calculates the minimum of the specified integer property IDs.

    This does not check if the provided keys actually exist in the row
    or they are actually integer values.
    """

    default_order: SortOrder = SortOrder.ASCENDING

    def __init__(self, name: str, id: str, prop_ids: List[str]):
        super().__init__(name, id)
        self.prop_ids = prop_ids

    def key(self, row: ItemPropRow) -> Optional[int]:
        values = [row[prop_id] for prop_id in self.prop_ids if row[prop_id] is not None]
        if len(values) == 0:
            return None
        return min(values)


class PropGroup:
    """
    This represents a group of related properties.
    """

    def __init__(self, name: str, id: str, items: "List[Union[BaseProp[Any], PropGroup]]"):
        """
        Initialize a property group.

        :param name: The display name of the property group.
        :param id: The unique string identifier for the property group.
        :param properties: The list of properties that belong to this group.
        """
        self.name = name
        self.id = id
        self.children = items
        self._map = {prop.id: prop for prop in items}

    def __getitem__(self, key: str) -> Optional[BaseProp[Any]]:
        for group in self.walk_group():
            if key in group._map:
                return group._map[key]  # type: ignore

    def iter_prop(self) -> Generator[BaseProp[Any], None, None]:
        """
        Iterates through all properties in the group, excluding sub-groups.
        """
        for prop in self.children:
            if isinstance(prop, PropGroup):
                continue
            yield prop

    def iter_group(self) -> Generator["PropGroup", None, None]:
        """
        Iterates through all groups in the group, excluding sub-groups.
        """
        for group in self.children:
            if isinstance(group, PropGroup):
                yield group

    def walk_prop(self) -> Generator[BaseProp[Any], None, None]:
        """
        Walks through all properties in the group and its sub-groups.
        """
        for prop in self.children:
            if isinstance(prop, PropGroup):
                yield from prop.walk_prop()
            else:
                yield prop

    def walk_group(self) -> "Generator[PropGroup, None, None]":
        """
        Walks through all groups in the group and its sub-groups.
        """
        yield self
        for group in self.children:
            if isinstance(group, PropGroup):
                yield from group.walk_group()


################################################################################
# Property Structures
################################################################################


def to_proper_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


class PropMaster:
    RARITY_VALUES = {
        "Minor Magic Item": 1,
        "Lesser Magic Item": 2,
        "Greater Magic Item": 3,
        "Major Magic Item": 4,
        "Minor Artifact": 5,
        "Lesser Artifact": 6,
        "Greater Artifact": 7,
        "Major Artifact": 8,
        "Legendary Artifact": 9,
    }

    SKILL_NAMES = [
        "Arms Lore",
        "Begging",
        "Camping",
        "Cartography",
        "Forensic",
        "ItemID",
        "TasteID",
        "Anatomy",
        "Archery",
        "Fencing",
        "Focus",
        "Healing",
        "MaceFighting",
        "Parrying",
        "Swordsmanship",
        "Tactics",
        "Throwing",
        "Wrestling",
        "Alchemy",
        "Smithy",
        "Fletching",
        "Carpentry",
        "Cooking",
        "Inscription",
        "Lumberjacking",
        "Mining",
        "Tailoring",
        "Tinkering",
        "Bushido",
        "Chivalry",
        "EvalInt",
        "Imbuing",
        "Magery",
        "Meditation",
        "Mysticism",
        "Necromancy",
        "Ninjitsu",
        "ResistSpell",
        "Spellweaving",
        "SpiritSpeak",
        "Animal Lore",
        "Animal Taming",
        "Fishing",
        "Herding",
        "Tracking",
        "Veterinary",
        "Detect Hidden",
        "Hiding",
        "Lockpicking",
        "Poisoning",
        "Remove Trap",
        "Snooping",
        "Stealing",
        "Stealth",
        "Discordance",
        "Musicianship",
        "Peacemaking",
        "Provocation",
    ]

    ALL_PROPS = PropGroup(
        "All",
        "All",
        [
            PropGroup(
                "Basic",
                "Basic",
                [
                    BaseProp("Name", "Name"),
                    BaseProp("Serial", "Serial"),
                    BaseProp("Type", "Type").set_order(SortOrder.ASCENDING),
                    BaseProp("Weight", "Weight").set_order(SortOrder.DESCENDING),
                    BaseProp("Color", "Color").set_order(SortOrder.ASCENDING),
                    BaseProp("Amount", "Amount").set_order(SortOrder.DESCENDING),
                    EnumProp(
                        "Rarity",
                        "Rarity",
                        RARITY_VALUES,
                        {v: k for k, v in RARITY_VALUES.items()},
                    ),
                    EnumProp(
                        "Layer",
                        "Layer",
                        {
                            "FirstValid": 1,
                            "LeftHand": 2,
                            "Shoes": 3,
                            "Pants": 4,
                            "Shirt": 5,
                            "Head": 6,
                            "Gloves": 7,
                            "Ring": 8,
                            "Neck": 9,
                            "Waist": 10,
                            "InnerTorso": 11,
                            "Bracelet": 12,
                            "MiddleTorso": 13,
                            "Earrings": 14,
                            "Arms": 15,
                            "Cloak": 16,
                            "OuterTorso": 17,
                            "OuterLegs": 18,
                            "InnerLegs": 19,
                            "Talisman": 20,
                        },
                        {
                            1: "Right Hand",
                            2: "Left Hand",
                            3: "Shoes",
                            4: "Pants",
                            5: "Shirt",
                            6: "Head",
                            7: "Gloves",
                            8: "Ring",
                            9: "Neck",
                            10: "Waist",
                            11: "Inner Torso",
                            12: "Bracelet",
                            13: "Middle Torso",
                            14: "Earrings",
                            15: "Arms",
                            16: "Cloak",
                            17: "Outer Torso",
                            18: "Outer Legs",
                            19: "Inner Legs",
                            20: "Talisman",
                        },
                    ),
                    ComparableMatchProp("Contents", "Contents", r"^Contents: (\d+)", int),
                ],
            ),
            PropGroup(
                "Stats & Resists",
                "StatsResist",
                [
                    IntegerProp("Strength Bonus", "Str", "Strength Bonus"),
                    IntegerProp("Dexterity Bonus", "Dex", "Dexterity Bonus"),
                    IntegerProp("Intelligence Bonus", "Int", "Intelligence Bonus"),
                    IntegerSumProp("Total Stats Bonus", "SumStat", ["Str", "Dex", "Int"]),
                    IntegerMaxProp("Max Stats Bonus", "MaxStat", ["Str", "Dex", "Int"]),
                    IntegerProp("Hit Point Increase", "Hits", "Hit Point Increase"),
                    IntegerProp("Hit Point Regeneration", "HitsRegen", "Hit Point Regeneration"),
                    IntegerProp("Stamina Increase", "Stam", "Stamina Increase"),
                    IntegerProp("Stamina Regeneration", "StamRegen", "Stamina Regeneration"),
                    IntegerProp("Mana Increase", "Mana", "Mana Increase"),
                    IntegerProp("Mana Regeneration", "ManaRegen", "Mana Regeneration"),
                    IntegerSumProp("Total Increase", "SumInc", ["Hits", "Stam", "Mana"]),
                    IntegerMaxProp("Max Increase", "MaxInc", ["Hits", "Stam", "Mana"]),
                    IntegerSumProp("Total Regen", "SumRegen", ["HitsRegen", "StamRegen", "ManaRegen"]),
                    IntegerMaxProp("Max Regen", "MaxRegen", ["HitsRegen", "StamRegen", "ManaRegen"]),
                    IntegerProp("Luck", "Luck", "Luck"),
                    PercentageProp("Physical Resist", "PhysRes", "Physical Resist"),
                    PercentageProp("Cold Resist", "ColdRes", "Cold Resist"),
                    PercentageProp("Fire Resist", "FireRes", "Fire Resist"),
                    PercentageProp("Poison Resist", "PoisonRes", "Poison Resist"),
                    PercentageProp("Energy Resist", "EnergyRes", "Energy Resist"),
                    IntegerSumProp("Total Resist", "SumRes", ["PhysRes", "ColdRes", "FireRes", "PoisonRes", "EnergyRes"]),
                    IntegerMaxProp("Max Resist", "MaxRes", ["PhysRes", "ColdRes", "FireRes", "PoisonRes", "EnergyRes"]),
                ],
            ),
            PropGroup(
                "Melee",
                "Melee",
                [
                    PercentageProp("Damage Increase", "DI", "Damage Increase"),
                    PercentageProp("Defense Chance Increase", "DCI", "Defense Chance Increase"),
                    PercentageProp("Hit Chance Increase", "HCI", "Hit Chance Increase"),
                    PercentageProp("Swing Speed Increase", "SSI", "Swing Speed Increase"),
                    PercentageProp("Physical Damage", "PhysDmg", "Physical Damage"),
                    PercentageProp("Cold Damage", "ColdDmg", "Cold Damage"),
                    PercentageProp("Fire Damage", "FireDmg", "Fire Damage"),
                    PercentageProp("Poison Damage", "PoisonDmg", "Poison Damage"),
                    PercentageProp("Energy Damage", "EnergyDmg", "Energy Damage"),
                    PercentageProp("Chaos Damage", "ChaosDmg", "Chaos Damage"),
                    IntegerSumProp("Any Nonphysical Damage", "NonPhysDmg", ["ColdDmg", "FireDmg", "PoisonDmg", "EnergyDmg", "ChaosDmg"]),
                    PercentageProp("Fire Eater", "Fire Eater", "Fire Eater"),
                    PercentageProp("Cold Eater", "Cold Eater", "Cold Eater"),
                    PercentageProp("Poison Eater", "Poison Eater", "Poison Eater"),
                    PercentageProp("Energy Eater", "Energy Eater", "Energy Eater"),
                    PercentageProp("Kinetic Eater", "Kinetic Eater", "Kinetic Eater"),
                    PercentageProp("Damage Eater", "Damage Eater", "Damage Eater"),
                    IntegerSumProp("Any Eater", "Any Eater", ["Fire Eater", "Cold Eater", "Poison Eater", "Energy Eater", "Kinetic Eater", "Damage Eater"]),
                    PercentageProp("Soul Charge", "Soul Charge", "Soul Charge"),
                    BooleanProp("Reactive Paralyze", "Reactive Paralyze", "Reactive Paralyze"),
                    PercentageProp("Reflect Physical Damage", "RPD", "Reflect Physical Damage"),
                    BooleanProp("Battle Lust", "Battle Lust", "Battle Lust"),
                    BooleanProp("Blood Drinker", "Blood Drinker", "Blood Drinker"),
                    BooleanProp("Balanced", "Balanced", "Balanced"),
                    BooleanProp("Searing Weapon", "Searing Weapon", "Searing Weapon"),
                    BooleanProp("Use Best Weapon Skill", "BestWeapon", "Use Best Weapon Skill"),
                ],
            ),
            PropGroup(
                "Caster",
                "Caster",
                [
                    PercentageProp("Spell Damage Increase", "SDI", "Spell Damage Increase"),
                    IntegerProp("Casting Focus", "CF", "Casting Focus"),
                    PercentageProp("Lower Mana Cost", "LMC", "Lower Mana Cost"),
                    PercentageProp("Lower Reagent Cost", "LRC", "Lower Reagent Cost"),
                    ComparableMatchProp("Mage Weapon", "Mage Weapon", r"Mage Weapon ([+-]?\d+) Skill", int),
                    IntegerProp("Faster Cast Recovery", "FCR", "Faster Cast Recovery"),
                    IntegerProp("Faster Casting", "FC", "Faster Casting"),
                    BooleanProp("Spell Channeling", "Spell Channeling", "Spell Channeling"),
                    BooleanProp("Mage Armor", "Mage Armor", "Mage Armor"),
                ],
            ),
            PropGroup(
                "Skill: Misc",
                "SkillMisc",
                [
                    IntegerProp("Arms Lore", "Arms Lore", "Arms Lore"),
                    IntegerProp("Begging", "Begging", "Begging"),
                    IntegerProp("Camping", "Camping", "Camping"),
                    IntegerProp("Cartography", "Cartography", "Cartography"),
                    IntegerProp("Forensic Evaluation", "Forensic", "Forensic Evaluation"),
                    IntegerProp("Item Identification", "ItemID", "Item Identification"),
                    IntegerProp("Taste Identification", "TasteID", "Taste Identification"),
                    IntegerSumProp("Total Skills", "SumSkill", SKILL_NAMES),
                    IntegerMaxProp("Max Skill", "MaxSkill", SKILL_NAMES),
                ],
            ),
            PropGroup(
                "Skill: Combat",
                "SkillCombat",
                [
                    IntegerProp("Anatomy", "Anatomy", "Anatomy"),
                    IntegerProp("Archery", "Archery", "Archery"),
                    IntegerProp("Fencing", "Fencing", "Fencing"),
                    IntegerProp("Focus", "Focus", "Focus"),
                    IntegerProp("Healing", "Healing", "Healing"),
                    IntegerProp("Mace Fighting", "MaceFighting", "Mace Fighting"),
                    IntegerProp("Parrying", "Parrying", "Parrying"),
                    IntegerProp("Swordsmanship", "Swordsmanship", "Swordsmanship"),
                    IntegerProp("Tactics", "Tactics", "Tactics"),
                    IntegerProp("Throwing", "Throwing", "Throwing"),
                    IntegerProp("Wrestling", "Wrestling", "Wrestling"),
                ],
            ),
            PropGroup(
                "Skill: Trade",
                "SkillTrade",
                [
                    IntegerProp("Alchemy", "Alchemy", "Alchemy"),
                    IntegerProp("Blacksmithing", "Smithy", "Blacksmithing"),
                    IntegerProp("Fletching", "Fletching", "Fletching"),
                    IntegerProp("Carpentry", "Carpentry", "Carpentry"),
                    IntegerProp("Cooking", "Cooking", "Cooking"),
                    IntegerProp("Inscription", "Inscription", "Inscription"),
                    IntegerProp("Lumberjacking", "Lumberjacking", "Lumberjacking"),
                    IntegerProp("Mining", "Mining", "Mining"),
                    IntegerProp("Tailoring", "Tailoring", "Tailoring"),
                    IntegerProp("Tinkering", "Tinkering", "Tinkering"),
                ],
            ),
            PropGroup(
                "Skill: Magic",
                "SkillMagic",
                [
                    IntegerProp("Bushido", "Bushido", "Bushido"),
                    IntegerProp("Chivalry", "Chivalry", "Chivalry"),
                    IntegerProp("Evaluate Intelligence", "EvalInt", "Evaluate Intelligence"),
                    IntegerProp("Imbuing", "Imbuing", "Imbuing"),
                    IntegerProp("Magery", "Magery", "Magery"),
                    IntegerProp("Meditation", "Meditation", "Meditation"),
                    IntegerProp("Mysticism", "Mysticism", "Mysticism"),
                    IntegerProp("Necromancy", "Necromancy", "Necromancy"),
                    IntegerProp("Ninjitsu", "Ninjitsu", "Ninjitsu"),
                    IntegerProp("Resisting Spells", "ResistSpell", "Resisting Spells"),
                    IntegerProp("Spellweaving", "Spellweaving", "Spellweaving"),
                    IntegerProp("Spirit Speak", "SpiritSpeak", "Spirit Speak"),
                ],
            ),
            PropGroup(
                "Skill: Wilderness",
                "SkillWilderness",
                [
                    IntegerProp("Animal Lore", "Animal Lore", "Animal Lore"),
                    IntegerProp("Animal Taming", "Animal Taming", "Animal Taming"),
                    IntegerProp("Fishing", "Fishing", "Fishing"),
                    IntegerProp("Herding", "Herding", "Herding"),
                    IntegerProp("Tracking", "Tracking", "Tracking"),
                    IntegerProp("Veterinary", "Veterinary", "Veterinary"),
                ],
            ),
            PropGroup(
                "Skill: Thievery",
                "SkillThievery",
                [
                    IntegerProp("Detect Hidden", "Detect Hidden", "Detect Hidden"),
                    IntegerProp("Hiding", "Hiding", "Hiding"),
                    IntegerProp("Lockpicking", "Lockpicking", "Lockpicking"),
                    IntegerProp("Poisoning", "Poisoning", "Poisoning"),
                    IntegerProp("Remove Trap", "Remove Trap", "Remove Trap"),
                    IntegerProp("Snooping", "Snooping", "Snooping"),
                    IntegerProp("Stealing", "Stealing", "Stealing"),
                    IntegerProp("Stealth", "Stealth", "Stealth"),
                ],
            ),
            PropGroup(
                "Skill: Bard",
                "SkillBard",
                [
                    IntegerProp("Discordance", "Discordance", "Discordance"),
                    IntegerProp("Musicianship", "Musicianship", "Musicianship"),
                    IntegerProp("Peacemaking", "Peacemaking", "Peacemaking"),
                    IntegerProp("Provocation", "Provocation", "Provocation"),
                ],
            ),
            PropGroup(
                "On Hit Spells",
                "OnHitSpells",
                [
                    PercentageProp("Hit Magic Arrow", "Hit Magic Arrow", "Hit Magic Arrow"),
                    PercentageProp("Hit Harm", "Hit Harm", "Hit Harm"),
                    PercentageProp("Hit Fireball", "Hit Fireball", "Hit Fireball"),
                    PercentageProp("Hit Lightning", "Hit Lightning", "Hit Lightning"),
                    PercentageProp("Hit Cold Area", "Hit Cold Area", "Hit Cold Area"),
                    PercentageProp("Hit Energy Area", "Hit Energy Area", "Hit Energy Area"),
                    PercentageProp("Hit Fire Area", "Hit Fire Area", "Hit Fire Area"),
                    PercentageProp("Hit Physical Area", "Hit Physical Area", "Hit Physical Area"),
                    PercentageProp("Hit Poison Area", "Hit Poison Area", "Hit Poison Area"),
                    PercentageProp("Hit Dispel", "Hit Dispel", "Hit Dispel"),
                    PercentageProp("Hit Curse", "Hit Curse", "Hit Curse"),
                    PercentageProp("Hit Lower Attack", "Hit Lower Attack", "Hit Lower Attack"),
                    PercentageProp("Hit Lower Defense", "Hit Lower Defense", "Hit Lower Defense"),
                    PercentageProp("Hit Life Leech", "Hit Life Leech", "Hit Life Leech"),
                    PercentageProp("Hit Mana Leech", "Hit Mana Leech", "Hit Mana Leech"),
                    PercentageProp("Hit Stamina Leech", "Hit Stamina Leech", "Hit Stamina Leech"),
                    PercentageProp("Hit Fatigue", "Hit Fatigue", "Hit Fatigue"),
                    PercentageProp("Hit Mana Drain", "Hit Mana Drain", "Hit Mana Drain"),
                    PercentageProp("Splintering Weapon", "Splintering Weapon", "Splintering Weapon"),
                    PercentageProp("Velocity", "Velocity", "Velocity"),
                ],
            ),
            PropGroup(
                "Special",
                "Special",
                [
                    BooleanProp("Gargoyles Only", "Gargoyles Only", "Gargoyles Only"),
                    BooleanProp("Elves Only", "Elves Only", "Elves Only"),
                    BooleanProp("Night Sight", "Night Sight", "Night Sight"),
                    IntegerProp("Self Repair", "Self Repair", "Self Repair"),
                    PercentageProp("Lower Requirements", "LowerReq", "Lower Requirements"),
                    PercentageProp("Enhance Potions", "Enhance Potions", "Enhance Potions"),
                    IntegerProp("Artifact Rarity", "Artifact Rarity", "Artifact Rarity"),
                ],
            ),
            PropGroup(
                "Slayers",
                "Slayers",
                [
                    ComparableMatchProp("Slayer", "Slayer", r"^(?:(Silver)|(.+) Slayer)$", str),
                    ComparableMatchProp("Super Slayer", "SupSlayer", r"^(?:(Silver)|Arachnid Slayer|Demon Slayer|Elemental Slayer|Fey Slayer|Repond Slayer|Reptile Slayer)$", str),
                    ComparableMatchProp("Arachnid Slayer", "Arachnid Slayer", r"^(Arachnid) Slayer$", str),
                    ComparableMatchProp("Demon Slayer", "Demon Slayer", r"^(Demon) Slayer$", str),
                    ComparableMatchProp("Elemental Slayer", "Elemental Slayer", r"^(Elemental) Slayer$", str),
                    ComparableMatchProp("Fey Slayer", "Fey Slayer", r"^(Fey) Slayer$", str),
                    ComparableMatchProp("Repond Slayer", "Repond Slayer", r"^(Repond) Slayer$", str),
                    ComparableMatchProp("Reptile Slayer", "Reptile Slayer", r"^(Reptile) Slayer$", str),
                    ComparableMatchProp("Silver", "Silver", r"^(Silver)$", str),
                ],
            ),
            PropGroup(
                "Negatives",
                "Negatives",
                [
                    BooleanProp("Cursed", "Cursed", "Cursed"),
                    BooleanProp("Antique", "Antique", "Antique"),
                    BooleanProp("Prized", "Prized", "Prized"),
                    BooleanProp("Brittle", "Brittle", "Brittle"),
                ],
            ),
            PropGroup(
                "Wands",
                "Wands",
                [
                    IntegerProp("Greater Healing Charges", "GreaterHealChg", "Greater Healing Charges"),
                    IntegerProp("Healing Charges", "HealChg", "Healing Charges"),
                    IntegerProp("Harm Charges", "HarmChg", "Harm Charges"),
                    IntegerProp("Magic Arrow Charges", "MagicArrowChg", "Magic Arrow Charges"),
                    IntegerProp("Lightning Charges", "LightningChg", "Lightning Charges"),
                ],
            ),
            PropGroup(
                "Talismans",
                "Talismans",
                [
                    ComparableMatchProp("Killer", "Killer", r"^(.+) Killer: ([+-]?\d+%)$", str),
                    ComparableMatchProp("Protection", "Protection", r"^(.+) Protection: ([+-]?\d+%)$", str),
                    ComparableMatchProp("Exceptional Bonus", "ExBonus", r"^(.+) Exceptional Bonus: ([+-]?\d+%)$", str),
                    ComparableMatchProp("Bonus", "Bonus", r"^(.+)(?<! Exceptional) Bonus: ([+-]?\d+%)$", str),
                    ComparableMatchProp("Crafting Failure Protection", "CraftNoFail", "Crafting Failure Protection", str),
                ],
            ),
        ],
    )
    """A master tree of all properties."""

    @staticmethod
    def _apply_prop(col: BaseProp, item: "Item", lines: List[str]) -> Generator[Any, None, None]:
        """
        Applies the given property to the item and yields all the parsed values.
        """
        try:
            if col.id == "Layer":
                yield col.parse(item.Layer)
            for prop_text in lines:
                value = col.parse(prop_text)
                if value:
                    yield value
        except NotImplementedError as e:
            return

    @classmethod
    def create_row_by_serial(cls, serial: int, delay: int = 1000) -> Optional[ItemPropRow]:
        """
        Scans the item property with the given serial number and creates a row for it.
        """
        item = Items.FindBySerial(serial)
        if item is None:
            return None

        lines = [to_proper_case(str(line)) for line in Items.GetProperties(serial, delay)]
        if not lines:
            return None

        row = ItemPropRow()
        row.raw_props = lines
        row["Name"] = to_proper_case(item.Name)
        row["Serial"] = item.Serial
        row["Weight"] = item.Weight
        row["Type"] = item.ItemID
        row["Color"] = item.Color
        row["Amount"] = item.Amount

        for col in cls.ALL_PROPS.walk_prop():
            values = list(cls._apply_prop(col, item, lines))
            if values:
                if all(isinstance(value, str) for value in values):
                    # If multiple string values are found, concatenate them separated by a slash
                    # This is to handle properties like "Slayer" which can appear multiple times
                    # Later, consider introducing a ListProp type to handle such cases more elegantly
                    row[col.id] = "/".join(values)
                else:
                    # For non-string properties, just take the first matched value
                    # This is because such properties should only appear once
                    row[col.id] = values[0]
        return row

    @classmethod
    def create_col_by_id(cls, col_id: str, metadata: Optional[Dict[str, Any]] = None) -> "Optional[SheetColumn]":
        """
        Creates a new column for the sheet based on the given column ID.
        """
        prop = cls.ALL_PROPS[col_id]
        if prop is not None:
            col = SheetColumn(prop)
            col.sort_order = prop.default_order
            if metadata:
                col.metadata.update(metadata)
            return col
        return None


################################################################################
# Spreadsheet
################################################################################


class SheetColumnFilters:
    class Base:
        """
        This represents a filter for a sheet column.
        """

        def __call__(self, value: Any) -> bool:
            return True

        def to_dict(self) -> Dict[str, Any]:
            return {}

    class Boolean(Base):
        """
        This represents a boolean filter for a sheet column.
        """

        expected_value: Optional[bool]
        """The expected boolean value for the filter."""

        def __init__(self, expected_value: Optional[bool] = None):
            self.expected_value = expected_value

        def __call__(self, value: Any) -> bool:
            if not isinstance(value, bool):
                return False
            if self.expected_value is not None and value != self.expected_value:
                return False
            return True

        def to_dict(self) -> Dict[str, Any]:
            return {
                "type": "boolean",
                "expected_value": self.expected_value,
            }

    class Numeric(Base):
        """
        This represents a numeric filter for a sheet column.
        """

        min_value: Optional[int]
        """The minimum value for the filter."""
        max_value: Optional[int]
        """The maximum value for the filter."""

        def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None):
            self.min_value = min_value
            self.max_value = max_value

        def __call__(self, value: Any) -> bool:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True

        def to_dict(self) -> Dict[str, Any]:
            return {
                "type": "numeric",
                "min_value": self.min_value,
                "max_value": self.max_value,
            }

    class Enum(Base):
        """
        This represents an enum filter for a sheet column.
        """

        kvmap: Dict[str, int]
        """The mapping of enum keys to their values."""
        allowed_values: Set[int]
        """The list of allowed enum values for the filter."""

        def __init__(self, kvmap: Dict[str, int], allowed_values: Optional[Iterable[int]] = None):
            self.kvmap = kvmap
            if allowed_values is None:
                allowed_values = kvmap.values()
            self.allowed_values = set(allowed_values)

        def __call__(self, value: int) -> bool:
            if not isinstance(value, int):
                return False
            if value is None or value not in self.allowed_values:
                return False
            return True

        def to_dict(self) -> Dict[str, Any]:
            return {
                "type": "enum",
                "allowed_values": list(self.allowed_values),
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SheetColumnFilters.Base":
        filter_type = data.get("type")
        if filter_type == "boolean":
            return SheetColumnFilters.Boolean(expected_value=data.get("expected_value"))
        elif filter_type == "numeric":
            return SheetColumnFilters.Numeric(min_value=data.get("min_value"), max_value=data.get("max_value"))
        elif filter_type == "enum":
            return SheetColumnFilters.Enum(kvmap={}, allowed_values=set(data.get("allowed_values", [])))
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")


class SheetColumn:
    """
    This represents a column in the sheet.
    This basically acts as a wrapper around the property associated with this column.
    """

    prop: BaseProp
    """The property associated with this column."""
    sort_order: SortOrder
    """The sort order for this column."""
    filter: Optional[SheetColumnFilters.Base]
    """A filter to apply when filtering this column."""

    def __init__(self, prop: BaseProp):
        self.prop = prop
        self.sort_order = SortOrder.ASCENDING
        self.filter = None
        self.metadata: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self.prop.name

    @property
    def id(self) -> str:
        return self.prop.id

    def is_unsorted(self) -> bool:
        return self.sort_order == SortOrder.UNSORTED

    def is_reverse(self) -> bool:
        return self.sort_order == SortOrder.DESCENDING

    def toggle_reverse(self):
        if self.sort_order == SortOrder.ASCENDING:
            self.sort_order = SortOrder.DESCENDING
        elif self.sort_order == SortOrder.DESCENDING:
            self.sort_order = SortOrder.ASCENDING

    def apply_filter(self, sheet: "Sheet") -> "Sheet":
        """
        Filters the given sheet based on the ignored values for this column.

        This returns a new sheet with the filtered rows.
        """
        new_sheet = Sheet(name=sheet.name)
        new_sheet.columns = sheet.columns
        for row in sheet.rows:
            if not self.filter or self.filter(self.prop.key(row)):
                new_sheet.add_row(row)
        if not self.is_unsorted():
            new_sheet.rows = self.prop.sort(new_sheet.rows, reverse=self.is_reverse())

        return new_sheet

    def read(self, row: ItemPropRow) -> Optional[str]:
        return self.prop.stringify(row)


class Sheet:
    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.rows: ItemPropSheet = []
        self.columns: List[SheetColumn] = []

    def has_column(self, id: str) -> bool:
        """
        Checks if the sheet has a column with the given ID.
        """
        return any(col.id == id for col in self.columns)

    def add_column(self, col: SheetColumn):
        """
        Adds a new column to the sheet.

        This does not guarantee whether the column for the property already exists.
        """
        self.columns.append(col)

    def add_column_by_id(self, id: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[SheetColumn]:
        """
        Adds a new column to the sheet based on the property ID.
        Returns the created column or `None` if it could not be created.
        """
        col = PropMaster.create_col_by_id(id, metadata)
        if col is not None:
            self.add_column(col)
        return col

    def get_column(self, id: str) -> Optional[SheetColumn]:
        """
        Gets the column with the given ID.
        Returns the column or `None` if it could not be found.
        """
        for col in self.columns:
            if col.id == id:
                return col
        return None

    def add_row(self, row: ItemPropRow):
        """
        Adds a new row to the sheet.
        """
        self.rows.append(row)

    def add_row_by_serial(self, serial: int):
        """
        Adds a new row to the sheet based on the item with the given serial number.
        """
        row = PropMaster.create_row_by_serial(serial)
        if not row:
            return
        self.rows.append(row)


__exported__ = [
    "VERSION_CORE",
    # Core Structures
    "ItemPropRow",
    "ItemPropSheet",
    "SortOrder",
    "PropTypes",
    "BaseProp",
    "DerivedProp",
    "ComparableProp",
    "MatchProp",
    "ComparableMatchProp",
    "ComparableDerivedProp",
    "BooleanProp",
    "PercentageProp",
    "IntegerProp",
    "EnumProp",
    "AnyProp",
    "AllProp",
    "IntegerSumProp",
    "IntegerMaxProp",
    "IntegerMinProp",
    "PropGroup",
    # Property Master
    "PropMaster",
    # Spreadsheet
    "SheetColumnFilters",
    "SheetColumn",
    "Sheet",
]
