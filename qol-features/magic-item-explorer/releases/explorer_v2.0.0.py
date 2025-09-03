################################################################################
# Imports
################################################################################

from AutoComplete import *
from typing import List, Dict, Tuple, Callable, Generator, Any, Optional, Union, TypeVar, Generic
import os
import time
import csv
import re
from datetime import datetime
from enum import Enum


################################################################################
# Library
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


class BaseProp(Generic[CT]):
    """
    This is the base class for item properties.
    """

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
        if row.has(self.id):
            return str(row[self.id])
        return None

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

    def key_none_is_inf(self, row: ItemPropRow) -> Any:
        return self._ValueWrapperNoneIsInf(row[self.id])

    def key_none_is_sup(self, row: ItemPropRow) -> Any:
        return self._ValueWrapperNoneIsSup(row[self.id])

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
            return self.sanitizer(match.group(1))
        return None


class ComparableMatchProp(MatchProp[CT], ComparableProp[CT]): ...


class BooleanProp(MatchProp[bool]):
    """
    This represents a boolean property that can be parsed from a string.
    """

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
        if row.has(self.id) and row[self.id]:
            return "Yes"
        return None


class PercentageProp(ComparableMatchProp[int]):
    """
    This represents a percentage property that can be parsed from a string.
    """

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


class IntegerProp(ComparableMatchProp[int]):
    """
    This represents an integer property that can be parsed from a string.
    """

    def __init__(self, name: str, id: str, pattern: str):
        """
        Initialize an integer property.

        :param name: The display name of the property. (Example: Strength Increase)
        :param id: The unique string identifier for the property. (Example: Str)
        :param pattern: The prefix of the integer property.
        """
        super().__init__(name, id, r"^" + pattern + r"\s*:?\s*([+-]?\d+)$", int)


class EnumProp(ComparableProp[int]):
    """
    This represents a property which can take on a limited set of string values.
    """

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
    ALL_PROPS = PropGroup(
        "All",
        "All",
        [
            PropGroup(
                "Basic",
                "Basic",
                [
                    ComparableProp("Name", "Name"),
                    ComparableProp("Serial", "Serial"),
                    ComparableProp("Type", "Type"),
                    ComparableMatchProp("Weight", "Weight", r"^Weight: (\d+)", int),
                    ComparableProp("Color", "Color"),
                    ComparableProp("Amount", "Amount"),
                    EnumProp(
                        "Rarity",
                        "Rarity",
                        {
                            "Minor Magic Item": 1,
                            "Lesser Magic Item": 2,
                            "Greater Magic Item": 3,
                            "Major Magic Item": 4,
                            "Lesser Artifact": 101,
                            "Greater Artifact": 102,
                            "Major Artifact": 103,
                            "Legendary Artifact": 104,
                        },
                        {
                            1: "Minor Magic",
                            2: "Lesser Magic",
                            3: "Greater Magic",
                            4: "Major Magic",
                            101: "Lesser Artifact",
                            102: "Greater Artifact",
                            103: "Major Artifact",
                            104: "Legendary Artifact",
                        },
                    ),
                    EnumProp(
                        "Layer",
                        "Layer",
                        {
                            "RightHand": 1,
                            "FirstValid": 2,
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
                            99: "",
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
                    IntegerProp("Hit Point Increase", "Hits", "Hit Point Increase"),
                    IntegerProp("Hit Point Regeneration", "HitsRegen", "Hit Point Regeneration"),
                    IntegerProp("Stamina Increase", "Stam", "Stamina Increase"),
                    IntegerProp("Stamina Regeneration", "StamRegen", "Stamina Regeneration"),
                    IntegerProp("Mana Increase", "Mana", "Mana Increase"),
                    IntegerProp("Mana Regeneration", "ManaRegen", "Mana Regeneration"),
                    IntegerProp("Luck", "Luck", "Luck"),
                    PercentageProp("Physical Resist", "PhysRes", "Physical Resist"),
                    PercentageProp("Cold Resist", "ColdRes", "Cold Resist"),
                    PercentageProp("Fire Resist", "FireRes", "Fire Resist"),
                    PercentageProp("Poison Resist", "PoisonRes", "Poison Resist"),
                    PercentageProp("Energy Resist", "EnergyRes", "Energy Resist"),
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
                    PercentageProp("Fire Eater", "Fire Eater", "Fire Eater"),
                    PercentageProp("Cold Eater", "Cold Eater", "Cold Eater"),
                    PercentageProp("Poison Eater", "Poison Eater", "Poison Eater"),
                    PercentageProp("Energy Eater", "Energy Eater", "Energy Eater"),
                    PercentageProp("Kinetic Eater", "Kinetic Eater", "Kinetic Eater"),
                    PercentageProp("Damage Eater", "Damage Eater", "Damage Eater"),
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
                    ComparableMatchProp("Slayer", "Slayer", r"^(Silver|.* Slayer)$", str),
                    ComparableMatchProp("Arachnid Slayer", "Arachnid Slayer", r"^(Arachnid Slayer)$", str),
                    ComparableMatchProp("Demon Slayer", "Demon Slayer", r"^(Demon Slayer)$", str),
                    ComparableMatchProp("Elemental Slayer", "Elemental Slayer", r"^(Elemental Slayer)$", str),
                    ComparableMatchProp("Fey Slayer", "Fey Slayer", r"^(Fey Slayer)$", str),
                    ComparableMatchProp("Repond Slayer", "Repond Slayer", r"^(Repond Slayer)$", str),
                    ComparableMatchProp("Reptile Slayer", "Reptile Slayer", r"^(Reptile Slayer)$", str),
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
                    ComparableMatchProp("Killer", "Killer", r"^(.+ Killer: [+-]:?\d+%)$", str),
                    ComparableMatchProp("Protection", "Protection", r"^(.+ Protection: [+-]:?\d+%)$", str),
                    ComparableMatchProp("Exceptional Bonus", "ExBonus", r"^(.+ Exceptional Bonus: [+-]:?\d+%)$", str),
                    ComparableMatchProp("Bonus", "Bonus", r"^(.+ Bonus: [+-]:?\d+%)$", str),
                    ComparableMatchProp("Crafting Failure Protection", "CraftNoFail", "Crafting Failure Protection", str),
                ],
            ),
        ],
    )

    @staticmethod
    def _apply_prop(col: BaseProp, item: "Item", lines: List[str]) -> Optional[Any]:
        try:
            if col.id == "Layer":
                return col.parse(item.Layer)
            for prop_text in lines:
                value = col.parse(prop_text)
                if value:
                    return value
        except NotImplementedError as e:
            return None

    @classmethod
    def create_row_by_serial(cls, serial: int, delay: int = 1000) -> Optional[ItemPropRow]:
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
        row["Type"] = item.ItemID
        row["Color"] = item.Color
        row["Amount"] = item.Amount

        for col in cls.ALL_PROPS.walk_prop():
            value = cls._apply_prop(col, item, lines)
            if value is not None:
                row[col.id] = value

        return row

    @classmethod
    def create_col_by_id(cls, col_id: str, metadata: Optional[Dict[str, Any]] = None) -> "Optional[SheetColumn]":
        prop = cls.ALL_PROPS[col_id]
        if prop is not None:
            col = SheetColumn(prop)
            if metadata:
                col.metadata.update(metadata)
            return col
        return None


################################################################################
# Spreadsheet
################################################################################


class SheetColumn:
    """
    This represents a column in the sheet.
    This basically acts as a wrapper around the property associated with this column.
    """

    prop: BaseProp
    """The property associated with this column."""
    sort_order: "SheetColumn.SortOrder"
    """The sort order for this column."""
    ignored_values: List[Any]
    """A list of values to ignore when filtering this column."""

    class SortOrder(Enum):
        ASCENDING = "ascending"
        DESCENDING = "descending"

    def __init__(self, prop: BaseProp):
        self.prop = prop
        self.sort_order = SheetColumn.SortOrder.ASCENDING
        self.ignored_values: List[Any] = []
        self.metadata: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self.prop.name

    @property
    def id(self) -> str:
        return self.prop.id

    def is_reverse(self) -> bool:
        return self.sort_order == SheetColumn.SortOrder.DESCENDING

    def toggle_reverse(self):
        self.sort_order = SheetColumn.SortOrder.ASCENDING if self.is_reverse() else SheetColumn.SortOrder.DESCENDING

    def filter(self, sheet: "Sheet") -> "Sheet":
        """
        Filters the given sheet based on the ignored values for this column.

        This returns a new sheet with the filtered rows.
        """
        new_sheet = Sheet(name=sheet.name)
        new_sheet.columns = sheet.columns
        for row in sheet.rows:
            if row[self.id] not in self.ignored_values:
                new_sheet.add_row(row)
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

    def filter(self) -> "Sheet":
        """
        Creates a filtered and sorted copy of the sheet based on the active column filters.
        """
        new_sheet = self
        for sheet_col in self.columns:
            new_sheet = sheet_col.filter(new_sheet)
        return new_sheet


################################################################################
# Gumps and Handlers
################################################################################


# Useful function
class GumpTools:
    CENTER_POS_CACHE: Dict[int, Tuple[int, int]] = {}

    @classmethod
    def get_centering_pos(
        cls,
        item_id: int,
        px: int = 0,
        py: int = 0,
        pw: int = 0,
        ph: int = 0,
        abs: bool = True,
    ) -> Tuple[int, int]:
        """
        Calculates the left-top position for the item to be centered at the given position or rect:
        * If only `px` and `py` are given, it centers the item at `(px, py)`.
        * If `pw` and `ph` are also given, it centers the item at the center of the rect with left-top `(px, py)` and size `(pw, ph)`.
        """
        if item_id not in cls.CENTER_POS_CACHE:
            bitmap = Items.GetImage(item_id, 0)
            w, h = bitmap.Width, bitmap.Height
            # Find the rectangle bounds
            left, top, right, bottom = w, h, 0, 0
            for y in range(h):
                for x in range(w):
                    pixel = bitmap.GetPixel(x, y)
                    if pixel.R or pixel.G or pixel.B:
                        left = min(x, left)
                        top = min(y, top)
                        right = max(x, right)
                        bottom = max(y, bottom)
            # Calculate the relative posotion of the left-top corner
            if right < left or bottom < top:
                dx, dy = 0, 0
            else:
                dx = -(left + right) // 2
                dy = -(top + bottom) // 2
            cls.CENTER_POS_CACHE[item_id] = (dx, dy)

        x, y = cls.CENTER_POS_CACHE[item_id]
        if abs:
            x, y = x + px, y + py
        x, y = x + (pw // 2), y + (ph // 2)
        return (x, y)

    @staticmethod
    def hashname(name: str) -> int:
        return hash(name) & 0xFFFFFFFF

    @staticmethod
    def tooltip_to_itemproperty(gd: Gumps.GumpData) -> str:
        """
        Converts integer-argument tooltips to item properties.
        """
        return re.sub(r"\{ tooltip (\d+) \}", r"{ itemproperty \1 }", gd.gumpDefinition)


# Gump ID
MAIN_GUMP_ID = GumpTools.hashname("ExplorerMainGump")
ACTION_GUMP_ID = GumpTools.hashname("ExplorerActionGump")
FILTER_GUMP_ID = GumpTools.hashname("ExplorerFilterGump")
SHORTCUT_GUMP_ID = GumpTools.hashname("ExplorerShortcutGump")

# Explorer gump settings
ROW_HEIGHT = 60
COL_WIDTH = 150
MENU_HEIGHT = 30
HEADER_HEIGHT = 30
BORDER_WIDTH = 10
ITEMS_PER_PAGE = 10

# Button IDs
ID_MAIN_REFRESH = 1
ID_MAIN_EXPORT = 2
ID_MAIN_TITLE = 3

IDMOD_MAIN_ACTION = 1000
IDMOD_MAIN_SORT = 2000
IDMOD_MAIN_FILTER = 3000

ID_ACTION_PICKUP = 1000
ID_ACTION_USE = 1001
ID_ACTION_EQUIP = 1002

ID_FILTER_REMOVE = 10001
IDMOD_FILTER_GROUP = 11000
IDMOD_FILTER_CHANGE = 12000

ID_SHORTCUT_INSPECT = 1

# Gump wrapping text
GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""


class ExplorerDialog:
    RARITY_COLOR_MAP = {1: 905, 2: 72, 3: 89, 4: 4, 101: 13, 102: 53, 103: 43, 104: 33}

    @staticmethod
    def show_item_actions(row: ItemPropRow):
        Gumps.CloseGump(ACTION_GUMP_ID)
        gd = Gumps.CreateGump(True)

        # Main page layout
        INNER_WIDTH = 160
        INNER_HEIGHT = 218
        WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
        HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT

        # Background
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)
        x, y = BORDER_WIDTH, BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, INNER_HEIGHT, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, INNER_HEIGHT)

        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 100, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 100)
        px, py = GumpTools.get_centering_pos(row["Type"], x, y, INNER_WIDTH, 100)
        Gumps.AddItem(gd, px, py, row["Type"], row["Color"])
        Gumps.AddTooltip(gd, row["Serial"])

        y += 105
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 113, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 113)
        x += 5
        y += 5
        Gumps.AddButton(gd, x, y, 4005, 4007, ID_ACTION_PICKUP, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "To Backpack")
        y += 27
        Gumps.AddButton(gd, x, y, 4005, 4007, ID_ACTION_USE, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Use")
        y += 27
        Gumps.AddButton(gd, x, y, 4005, 4007, ID_ACTION_EQUIP, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Equip")
        y += 27
        Gumps.AddButton(gd, x, y, 4014, 4016, 0, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Return")

        # Send gump
        gd_gumpdef = GumpTools.tooltip_to_itemproperty(gd)
        Gumps.SendGump(ACTION_GUMP_ID, Player.Serial, 100, 100, gd_gumpdef, gd.gumpStrings)

    @staticmethod
    def show_filter(col_idx: int, col: SheetColumn, group_idx: Optional[int] = None):
        Gumps.CloseGump(FILTER_GUMP_ID)
        gd = Gumps.CreateGump(True)

        all_items = list(PropMaster.ALL_PROPS.iter_group())
        cur_group = None
        cur_props = []
        if group_idx is not None and 0 <= group_idx < len(all_items):
            cur_group = all_items[group_idx]
            cur_props = list(cur_group.iter_prop())

        # Main page layout
        INNER_WIDTH = 400
        INNER_HEIGHT = 70 + 27 * max(11, len(all_items) + 2)
        WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
        HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT

        # Background
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)
        x, y = BORDER_WIDTH, BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, INNER_HEIGHT, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, INNER_HEIGHT)
        x += 5
        y += 5

        # Title
        Gumps.AddHtml(gd, x, y, INNER_WIDTH - 10, 22, GUMP_WT.format(text=f"COLUMN {col_idx+1}: {col.id}"), False, False)
        y += 30

        # Group Section
        Gumps.AddHtml(gd, x, y, 195, 22, GUMP_WT.format(text="GROUPS"), False, False)
        y_g = y + 30
        for i, group in enumerate(all_items):
            Gumps.AddButton(gd, x, y_g, 4005, 4007, IDMOD_FILTER_GROUP + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 35, y_g + 2, 180, 18, 1153, group.name)
            y_g += 27
        y_g += 27
        Gumps.AddButton(gd, x, y_g, 4017, 4019, ID_FILTER_REMOVE, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y_g + 2, 100, 18, 1153, "REMOVE")

        # Properties Section
        x = 200
        Gumps.AddHtml(gd, x, y, 195, 22, GUMP_WT.format(text="PROPERTIES"), False, False)
        PROPS_PER_PAGE = max(10, len(all_items))
        TOTAL_PAGES = (len(cur_props) + PROPS_PER_PAGE - 1) // PROPS_PER_PAGE
        for i, prop in enumerate(cur_props):
            page = i // PROPS_PER_PAGE
            i_rel = i % PROPS_PER_PAGE
            if i_rel == 0:
                y_g = y + 30
                page_1based = page + 1
                Gumps.AddPage(gd, page_1based)
                y_p = y + 30 + 27 * PROPS_PER_PAGE
                if page_1based > 1:
                    Gumps.AddButton(gd, x, y_p, 4014, 4016, 0, 0, page_1based - 1)
                    Gumps.AddLabelCropped(gd, x + 35, y_p + 2, 180, 18, 1153, "PREV")
                if page_1based < TOTAL_PAGES:
                    Gumps.AddButton(gd, x + 100, y_p, 4005, 4007, 0, 0, page_1based + 1)
                    Gumps.AddLabelCropped(gd, x + 135, y_p + 2, 180, 18, 1153, "NEXT")
            Gumps.AddButton(gd, x, y_g, 4005, 4007, IDMOD_FILTER_CHANGE + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 35, y_g + 2, 180, 18, 1153, prop.name)
            y_g += 27

        Gumps.SendGump(FILTER_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    @staticmethod
    def show_sheet(sheet: Optional[Sheet] = None) -> Optional[Sheet]:
        Gumps.CloseGump(MAIN_GUMP_ID)
        gd = Gumps.CreateGump(True)

        # Main page layout
        num_cols = len(sheet.columns) if sheet else 0
        INNER_WIDTH = 81 + max(3 * COL_WIDTH, num_cols * COL_WIDTH + 22)
        INNER_HEIGHT = MENU_HEIGHT + 5 + HEADER_HEIGHT + (ROW_HEIGHT + 1) * ITEMS_PER_PAGE
        WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
        HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT

        # Background
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)

        # If no sheet is provided, show the loading screen
        if sheet is None:
            Gumps.AddImageTiled(gd, BORDER_WIDTH, BORDER_WIDTH, INNER_WIDTH, INNER_HEIGHT, 9274)
            Gumps.AddAlphaRegion(gd, BORDER_WIDTH, BORDER_WIDTH, INNER_WIDTH, INNER_HEIGHT)
            Gumps.AddHtml(gd, BORDER_WIDTH, HEIGHT // 2 - 11, INNER_WIDTH, 22, GUMP_WT.format(text="Loading..."), False, False)
            Gumps.SendGump(MAIN_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
            return

        # Sort the columns according to the update time
        col_sorted = sorted(sheet.columns, key=lambda c: c.metadata.get("update_time", 0))
        for col in col_sorted:
            if "update_time" in col.metadata:
                sheet = col.filter(sheet)

        # Menubar
        x = BORDER_WIDTH
        y = BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, MENU_HEIGHT, 9354)
        # Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, MENU_HEIGHT)
        x += 5
        y += 4
        Gumps.AddButton(gd, x, y, 1531, 1532, ID_MAIN_REFRESH, 1, 0)
        Gumps.AddLabelCropped(gd, x + 25, y + 2, 100, 18, 0, "Refresh")
        x += 100
        Gumps.AddButton(gd, x, y, 1533, 1534, ID_MAIN_EXPORT, 1, 0)
        Gumps.AddLabelCropped(gd, x + 25, y + 2, 100, 18, 0, "Export")
        x += 100
        Gumps.AddTextEntry(gd, x, y + 2, 200, 18, 0, ID_MAIN_TITLE, sheet.name)

        # Column headers
        x = BORDER_WIDTH
        y = BORDER_WIDTH + MENU_HEIGHT + 5
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, HEADER_HEIGHT, 30550)
        # Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, HEADER_HEIGHT)
        Gumps.AddImageTiled(gd, x, y, 80, HEADER_HEIGHT, 9354)
        x += 81
        dy = (HEADER_HEIGHT - 18) // 2
        for i, col in enumerate(sheet.columns):
            Gumps.AddImageTiled(gd, x, y, COL_WIDTH - 1, HEADER_HEIGHT, 9354)
            Gumps.AddButton(gd, x + 4, y + dy + 2, 1209, 1210, IDMOD_MAIN_FILTER + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 22, y + dy, COL_WIDTH - 30, 18, 0, col.id)
            if col.is_reverse():
                Gumps.AddButton(gd, x + COL_WIDTH - 15, y + dy + 4, 2437, 2438, IDMOD_MAIN_SORT + i, 1, 0)
            else:
                Gumps.AddButton(gd, x + COL_WIDTH - 15, y + dy + 4, 2435, 2436, IDMOD_MAIN_SORT + i, 1, 0)
            x += COL_WIDTH
        Gumps.AddImageTiled(gd, x, y, 22, HEADER_HEIGHT, 9354)
        Gumps.AddButton(gd, x + 4, y + dy + 2, 1209, 1210, IDMOD_MAIN_FILTER + len(sheet.columns), 1, 0)

        # Ruled sheet
        x = BORDER_WIDTH
        y = BORDER_WIDTH + MENU_HEIGHT + 5 + HEADER_HEIGHT + 1
        for j in range(ITEMS_PER_PAGE):
            Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, ROW_HEIGHT, 30550)
            # Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, ROW_HEIGHT)
            y += ROW_HEIGHT + 1

        # Rows
        TOTAL_PAGES = (len(sheet.rows) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        for i, row in enumerate(sheet.rows):
            page = i // ITEMS_PER_PAGE
            rel_i = i % ITEMS_PER_PAGE
            x = BORDER_WIDTH
            y = BORDER_WIDTH + MENU_HEIGHT + 5
            if rel_i == 0:
                page_1based = page + 1
                Gumps.AddPage(gd, page_1based)
                # Page navigation
                Gumps.AddHtml(gd, x, y + (HEADER_HEIGHT - 18) // 2, 80, 22, f"<center>{page_1based}/{TOTAL_PAGES}</center>", False, False)
                if page_1based > 1:
                    Gumps.AddButton(gd, x, y + 6, 1545, 1546, 0, 0, page_1based - 1)
                    Gumps.AddTooltip(gd, f"Move to the previous page")
                if page_1based < TOTAL_PAGES:
                    Gumps.AddButton(gd, x + 65, y + 6, 1543, 1544, 0, 0, page_1based + 1)
                    Gumps.AddTooltip(gd, f"Move to the next page")
            y += HEADER_HEIGHT + 1 + rel_i * (ROW_HEIGHT + 1)
            px, py = GumpTools.get_centering_pos(row["Type"], x, y, 80, 60, abs=False)
            Gumps.AddImageTiledButton(gd, x, y, 2328, 2329, IDMOD_MAIN_ACTION + i, Gumps.GumpButtonType.Reply, 0, row["Type"], row["Color"], px, py)
            Gumps.AddTooltip(gd, row["Serial"])
            # Gumps.AddLabelCropped(gd, x + 3, y + 3, 50, 18, 88, str(i + 1))
            x += 81
            y += 19
            for col in sheet.columns:
                value_color = 1153
                if col.id == "Rarity":
                    rarity = row["Rarity"]
                    value_color = ExplorerDialog.RARITY_COLOR_MAP.get(rarity, 1153)
                value = col.read(row) or ""
                Gumps.AddLabelCropped(gd, x + 4, y, COL_WIDTH - 10, 18, value_color, value)
                Gumps.AddTooltip(gd, f"{col.name}: {value}")
                x += COL_WIDTH

        # Send gump
        gd_gumpdef = GumpTools.tooltip_to_itemproperty(gd)
        Gumps.SendGump(MAIN_GUMP_ID, Player.Serial, 100, 100, gd_gumpdef, gd.gumpStrings)
        return sheet

    @staticmethod
    def shortcut() -> None:
        Gumps.CloseGump(SHORTCUT_GUMP_ID)

        # Create the gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
        Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

        Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Item Explorer"), False, False)

        Gumps.AddButton(gd, 10, 30, 40021, 40031, ID_SHORTCUT_INSPECT, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text="Inspect"), False, False)

        # Send the gump and listen for the response
        Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


class ExplorerHandlers:
    @staticmethod
    def actions(row: ItemPropRow):
        ExplorerDialog.show_item_actions(row)

        if not Gumps.WaitForGump(ACTION_GUMP_ID, 1000 * 60 * 60):
            return
        gd = Gumps.GetGumpData(ACTION_GUMP_ID)
        if not gd:
            return
        if gd.buttonid == 0:
            return
        if gd.buttonid == ID_ACTION_PICKUP:
            Items.Move(row["Serial"], Player.Backpack.Serial, -1)
            Misc.Pause(500)
            return
        if gd.buttonid == ID_ACTION_USE:
            Items.UseItem(row["Serial"])
            Misc.Pause(500)
            return
        if gd.buttonid == ID_ACTION_EQUIP:
            Player.EquipItem(row["Serial"])
            Misc.Pause(500)
            return

    @staticmethod
    def filter(col_idx: int, sheet: Sheet):
        col = sheet.columns[col_idx]
        group_idx = None
        all_items = list(PropMaster.ALL_PROPS.iter_group())
        while True:
            ExplorerDialog.show_filter(col_idx, col, group_idx)
            if not Gumps.WaitForGump(FILTER_GUMP_ID, 1000 * 60 * 60):
                return
            gd = Gumps.GetGumpData(FILTER_GUMP_ID)
            if not gd:
                return

            if gd.buttonid == 0:
                return

            # Check if the user wants to remove the column
            if gd.buttonid == ID_FILTER_REMOVE:
                sheet.columns.pop(col_idx)
                return

            # Calculate current group and properties
            cur_group = None
            cur_props = []
            if group_idx is not None and 0 <= group_idx < len(all_items):
                cur_group = all_items[group_idx]
                cur_props = list(cur_group.iter_prop())

            # Check if the user wants to change the filter
            id_change = gd.buttonid - IDMOD_FILTER_CHANGE
            if 0 <= id_change < len(cur_props):
                col.prop = cur_props[id_change]
                # col.metadata["update_time"] = time.time()
                return

            # Check if the user wants to select a group
            id_group = gd.buttonid - IDMOD_FILTER_GROUP
            if 0 <= id_group < len(all_items):
                group_idx = id_group
                continue

    @staticmethod
    def export_to_csv(sheet: Sheet):
        # Escape the sheet name so it can be used as a filename
        filename = re.sub(r"[^\w\s-]", "_", sheet.name)
        os.makedirs("Data/Sheets", exist_ok=True)
        filepath = f"Data/Sheets/{filename}.csv"

        with open(filepath, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header
            csvwriter.writerow([col.name for col in sheet.columns])
            # Write rows
            for row in sheet.rows:
                csvwriter.writerow([col.read(row) for col in sheet.columns])
        Misc.SendMessage(f"The sheet has been exported to: {filepath}", 1153)

    @staticmethod
    def explorer(serial: int, old_sheet: Optional[Sheet] = None) -> Optional[Sheet]:
        cont = Items.FindBySerial(serial)
        if cont is None:
            return None
        Items.WaitForContents(serial, 1000)

        # Show the loading screen
        ExplorerDialog.show_sheet()

        # Create an "abstract" sheet that doesn't contain actual rows
        sheet = Sheet(f"Untitled_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if old_sheet is not None:
            sheet.name = old_sheet.name
            sheet.columns = old_sheet.columns
        else:
            sheet.add_column_by_id("Rarity", {"update_time": time.time()})
            sheet.add_column_by_id("Name")
            sheet.columns[0].toggle_reverse()

        # Retrieve a sorted sheet
        filtered_sheet = Sheet()
        for row in cont.Contains:
            sheet.add_row_by_serial(row.Serial)
        filtered_sheet.columns = sheet.columns
        filtered_sheet = ExplorerDialog.show_sheet(sheet)
        if filtered_sheet is None:
            return

        # Wait for the user's input
        if not Gumps.WaitForGump(MAIN_GUMP_ID, 1000 * 60 * 60):
            return

        # Parse the user's input
        gd = Gumps.GetGumpData(MAIN_GUMP_ID)
        if not gd:
            return

        sheet.name = gd.text[0]
        if gd.buttonid == 0:
            return

        if gd.buttonid == ID_MAIN_REFRESH:
            return sheet

        if gd.buttonid == ID_MAIN_EXPORT:
            ExplorerHandlers.export_to_csv(filtered_sheet)
            return sheet

        id_action = gd.buttonid - IDMOD_MAIN_ACTION
        is_action = 0 <= id_action < len(filtered_sheet.rows)
        if is_action:
            row = filtered_sheet.rows[id_action]
            ExplorerHandlers.actions(row)
            return sheet

        id_sort = gd.buttonid - IDMOD_MAIN_SORT
        if 0 <= id_sort < len(sheet.columns):
            col = sheet.columns[id_sort]
            col_sorted = sorted(sheet.columns, key=lambda c: c.metadata.get("update_time", 0))
            col_last = col_sorted[-1] if col_sorted else None
            # Toggle the sort order only when it is updated most recently
            if col_last == col:
                col.toggle_reverse()
            col.metadata["update_time"] = time.time()
            return sheet

        id_filter = gd.buttonid - IDMOD_MAIN_FILTER
        if 0 <= id_filter < len(sheet.columns):
            ExplorerHandlers.filter(id_filter, sheet)
            return sheet
        if id_filter == len(sheet.columns):
            # The added column is initially of the least priority in the sort orders
            sheet.add_column_by_id("Name")
            return sheet


################################################################################
# Top-Level Logic
################################################################################


if Player.Connected:
    open_next = True
    old_sheet = None
    while Player.Connected:
        if open_next:
            ExplorerDialog.shortcut()
            open_next = False
        if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, 100):
            continue

        open_next = True
        gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
        if not gd or gd.buttonid != ID_SHORTCUT_INSPECT:
            continue

        serial = Target.PromptTarget("Select the container to inspect.", 1153)
        if serial == 0:
            continue

        while True:
            old_sheet = ExplorerHandlers.explorer(serial, old_sheet)
            if old_sheet is None:
                break
