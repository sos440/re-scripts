from AutoComplete import *
from typing import List, Dict, Callable, Generator, Any, Optional, Union, TypeVar, Generic
import re


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
        return self.sanitizer(match.group(1)) if match else None


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
        self.items = items
        self._map = {prop.id: prop for prop in items}

    def __getitem__(self, key: str) -> Optional[BaseProp[Any]]:
        for group in self.iter_group():
            if key in group._map:
                return group._map[key]  # type: ignore

    def iter(self) -> Generator[BaseProp[Any], None, None]:
        for prop in self.items:
            if isinstance(prop, PropGroup):
                yield from prop.iter()
            else:
                yield prop

    def iter_group(self) -> "Generator[PropGroup, None, None]":
        yield self
        for group in self.items:
            if isinstance(group, PropGroup):
                yield from group.iter_group()


################################################################################
# Property Structures
################################################################################


all_props = PropGroup(
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
                        "Minor Magic Item": 0,
                        "Lesser Magic Item": 1,
                        "Greater Magic Item": 2,
                        "Major Magic Item": 3,
                        "Minor Artifact": 4,
                        "Lesser Artifact": 5,
                        "Greater Artifact": 6,
                        "Major Artifact": 7,
                        "Legendary Artifact": 8,
                    },
                    {
                        0: "Minor Magic",
                        1: "Lesser Magic",
                        2: "Greater Magic",
                        3: "Major Magic",
                        4: "Minor Artifact",
                        5: "Lesser Artifact",
                        6: "Greater Artifact",
                        7: "Major Artifact",
                        8: "Legendary Artifact",
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
                PercentageProp("Soul Charge", "Soul Charge", "Soul Charge"),
                BooleanProp("Reactive Paralyze", "Reactive Paralyze", "Reactive Paralyze"),
                PercentageProp("Reflect Physical Damage", "RPD", "Reflect Physical Damage"),
                BooleanProp("Battle Lust", "Battle Lust", "Battle Lust"),
                BooleanProp("Blood Drinker", "Blood Drinker", "Blood Drinker"),
                BooleanProp("Balanced", "Balanced", "Balanced"),
                BooleanProp("Searing Weapon", "Searing Weapon", "Searing Weapon"),
                BooleanProp("Use Best Weapon Skill", "BestWeapon", "Use Best Weapon Skill"),
                PercentageProp("Fire Eater", "Fire Eater", "Fire Eater"),
                PercentageProp("Cold Eater", "Cold Eater", "Cold Eater"),
                PercentageProp("Poison Eater", "Poison Eater", "Poison Eater"),
                PercentageProp("Energy Eater", "Energy Eater", "Energy Eater"),
                PercentageProp("Kinetic Eater", "Kinetic Eater", "Kinetic Eater"),
                PercentageProp("Damage Eater", "Damage Eater", "Damage Eater"),
                PercentageProp("Physical Damage", "PhysDmg", "Physical Damage"),
                PercentageProp("Cold Damage", "ColdDmg", "Cold Damage"),
                PercentageProp("Fire Damage", "FireDmg", "Fire Damage"),
                PercentageProp("Poison Damage", "PoisonDmg", "Poison Damage"),
                PercentageProp("Energy Damage", "EnergyDmg", "Energy Damage"),
                PercentageProp("Chaos Damage", "ChaosDmg", "Chaos Damage"),
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
                IntegerProp("Mage Weapon", "Mage Weapon", "Mage Weapon"),
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

if __name__ == "__main__":
    values: ItemPropSheet = []
    cont = Items.FindBySerial(0x6AB17E80)
    if not Items.WaitForContents(cont, 1000):
        quit()

    for item in cont.Contains:
        serial = item.Serial
        row = ItemPropRow()
        values.append(row)

        row["Name"] = item.Name
        row["Serial"] = item.Serial
        row["Type"] = item.ItemID
        row["Color"] = item.Color

        Items.WaitForProps(serial, 1000)
        for prop_col in all_props.iter():
            for prop_text in Items.GetPropStringList(serial):
                try:
                    a = prop_col.parse(prop_text)
                    if a is not None:
                        row[prop_col.id] = a
                        break
                except NotImplementedError as e:
                    break

    cur_prop = all_props["Rarity"]
    assert cur_prop is not None
    values_inc = cur_prop.sort(values, reverse=False)
    values_dec = cur_prop.sort(values, reverse=True)

    print(list(row["Rarity"] for row in values_inc))
    print(list(row["Rarity"] for row in values_dec))
