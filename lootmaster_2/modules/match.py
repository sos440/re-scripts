from AutoComplete import *
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Dict, Tuple, Optional, TypeVar, Generic, Union, Generator, Callable
import xml.etree.ElementTree as ET
import re
import os


################################################################################
# Utilities


def interval(value: str) -> List[int]:
    """
    Create a list of integers from a string interval.

    1. If the string is a single integer, return a list with that integer.
    2. If the string is a range in the format "start...end", return a list of integers from start to end (inclusive).
    3. If the string is a comma-separated list of integers and/or ranges, return a list of all integers.
    """
    result = []
    for entry in re.split(r"\s*,\s*", value.strip()):
        if "..." in entry:
            start, end = entry.split("...")
            result.extend(range(int(start, 0), int(end, 0) + 1))
        else:
            result.append(int(entry, 0))
    return result


def to_interval(values: Iterable[int]) -> str:
    """
    Convert a list of integers to a string interval.

    1. If the list contains consecutive integers, represent them as a range "start...end".
    2. If the list contains non-consecutive integers, represent them as a comma-separated list.
    """
    sorted_values: List[Optional[int]] = []
    sorted_values.extend(sorted(set(values)))
    sorted_values.append(None)  # Sentinel value to handle the last range

    ranges = []
    start = prev = sorted_values[0]
    for value in sorted_values[1:]:
        if value is not None and value == prev + 1:
            prev = value
        else:
            assert start is not None
            if start == prev:
                ranges.append(f"{start}")
            elif start + 1 == prev:
                ranges.append(f"{start},{prev}")
            else:
                ranges.append(f"{start}...{prev}")
            start = prev = value

    return ",".join(ranges)


################################################################################
# Match Classes


PRESETS: dict[str, "BaseMatch"] = {}
"""A registry of all loaded presets."""

PARSER_REGISTRY: Dict[str, "XmlParsable"] = {}
"""A registry of all match parsers."""


def _load_preset():
    """
    Load presets from the presets.xml file.
    """
    PRESETS.clear()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    presets_path = os.path.join(script_dir, "presets.xml")
    if not os.path.isfile(presets_path):
        return

    tree = ET.parse(presets_path)
    root = tree.getroot()
    for e in root:
        name = e.get("name")
        if name is None:
            continue
        PRESETS[name] = parse_element(e)


def parse_element(element: ET.Element) -> "BaseMatch":
    """
    Parse an XML element into a match object.
    """
    tagname = element.tag
    parser_class = PARSER_REGISTRY.get(tagname)
    if parser_class is None:
        raise ValueError(f"No parser registered for tag <{tagname}>")
    return parser_class.from_xml(element)


class XmlParsable(type(ABC)):
    """
    This metaclass automatically registers any class that uses it into the PARSER_REGISTRY.
    """

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        tagname = new_class.__name__
        if tagname in PARSER_REGISTRY:
            raise TypeError(f"Duplicate tag name '{tagname}' registry.")
        PARSER_REGISTRY[tagname] = new_class
        return new_class

    def from_xml(cls, e: ET.Element):
        raise NotImplementedError("Subclasses must implement the from_xml method.")


class BaseMatch(ABC, metaclass=XmlParsable):
    """
    A base class for all match types.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
    }
    """A mapping of XML attribute names to their conversion functions."""

    name: Optional[str]
    """A brief description of the match, to be displayed in gumps."""
    desc: Optional[str]
    """A more detailed description of the match."""

    def __init__(
        self,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        self.name = name
        self.desc = desc

    @abstractmethod
    def test(self, item: "Item") -> bool:
        pass

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        """
        Convert the match to an XML element.
        """
        if e is None:
            e = ET.Element(self.__class__.__name__)
        for attr in self._XML_ATTRIBUTES.keys():
            value = getattr(self, attr)
            if value is None:
                continue
            if attr == "pattern":
                value = value.pattern
            e.set(attr, str(value))
        return e

    @classmethod
    def _parse_xml_kwargs(cls, e: ET.Element) -> Generator[Tuple[str, Any], None, None]:
        """
        Convert an XML element to a key-value pair.
        """
        for attr, func in cls._XML_ATTRIBUTES.items():
            value = e.get(attr)
            if value is not None:
                if func == int:
                    yield attr, int(value, 0)
                else:
                    yield attr, func(value)

    @classmethod
    def from_xml(cls, e: ET.Element):
        """
        Create an instance of the class from an XML element.
        """
        data = dict(cls._parse_xml_kwargs(e))
        return cls(**data)


class GroupMatch(BaseMatch):
    """
    A base class for group-based matches.
    """

    def __init__(
        self,
        entries: Optional[List[BaseMatch]] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.entries = entries or []

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        e = super().to_xml(e)
        for entry in self.entries:
            e.append(entry.to_xml())
        return e

    @classmethod
    def from_xml(cls, e: ET.Element):
        data = dict(cls._parse_xml_kwargs(e))
        data["entries"] = list(map(parse_element, e))
        return cls(**data)


class PatternMatch(BaseMatch):
    """
    A base class for pattern-based matches.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "pattern": str,
    }
    pattern: re.Pattern

    def __init__(
        self,
        pattern: str,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.pattern = re.compile(pattern, re.IGNORECASE)


class RangeMatch(BaseMatch):
    """
    A base class for range-based integer matches.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "min_value": int,
        "max_value": int,
    }
    min_value: Optional[int]
    """The minimum value of the range."""
    max_value: Optional[int]
    """The maximum value of the range."""

    def __init__(
        self,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.min_value = min_value
        self.max_value = max_value

    @abstractmethod
    def get_number(self, item: "Item") -> Optional[int]:
        """
        Get the number to be tested from the item.
        This method should be overridden by subclasses.
        """
        pass

    def test(self, item: "Item") -> bool:
        value = self.get_number(item)
        if value is None:
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True


class DerivedMatch(GroupMatch, RangeMatch):
    """
    A base class for testing derived properties of items.
    """

    def __init__(
        self,
        entries: Optional[List[BaseMatch]] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        GroupMatch.__init__(self, entries=entries, name=name, desc=desc)
        RangeMatch.__init__(self, min_value=min_value, max_value=max_value, name=name, desc=desc)


class SumMatch(DerivedMatch):
    """
    A match class that sums the results of its entries.
    """

    def get_number(self, item: "Item") -> Optional[int]:
        total = None
        for entry in self.entries:
            if not isinstance(entry, RangeMatch):
                continue
            value = entry.get_number(item)
            if value is None:
                continue
            if total is None:
                total = 0
            total += value
        return total


class MaxMatch(DerivedMatch):
    """
    A match class that takes the maximum result of its entries.
    """

    def get_number(self, item: "Item") -> Optional[int]:
        maximum = None
        for entry in self.entries:
            if not isinstance(entry, RangeMatch):
                continue
            value = entry.get_number(item)
            if value is None:
                continue
            if maximum is None or value > maximum:
                maximum = value
        return maximum


class MinMatch(DerivedMatch):
    """
    A match class that takes the minimum result of its entries.
    """

    def get_number(self, item: "Item") -> Optional[int]:
        minimum = None
        for entry in self.entries:
            if not isinstance(entry, RangeMatch):
                continue
            value = entry.get_number(item)
            if value is None:
                continue
            if minimum is None or value < minimum:
                minimum = value
        return minimum


class SerialMatch(BaseMatch):
    """
    A match class for item serial numbers.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "serial": interval,
    }
    serial: Set[int]
    """The serial numbers to match."""

    def __init__(
        self,
        serial: Union[int, Iterable[int]],
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        # Ensure serial is a list
        if isinstance(serial, int):
            self.serial = {serial}
        else:
            self.serial = set(serial)

    def test(self, item: "Item"):
        return item.Serial in self.serial

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        e = super().to_xml(e)
        e.set("serial", ",".join(f"0x{ser:08X}" for ser in sorted(self.serial)))
        return e


class TypeMatch(BaseMatch):
    """
    A match class for item type and color.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "itemid": interval,
        "color": interval,
    }
    itemid: Set[int]
    """The item type ID to match."""
    color: Set[int]
    """The item color to match. If `None`, any color matches."""

    def __init__(
        self,
        itemid: Union[int, Iterable[int]],
        color: Union[int, Iterable[int], None] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        # Ensure itemid is a list
        if isinstance(itemid, int):
            self.itemid = {itemid}
        else:
            self.itemid = set(itemid)
        # Ensure color is a list
        if color is None:
            self.color = set()
        elif isinstance(color, int):
            self.color = {color}
        else:
            self.color = set(color)

    def test(self, item: "Item"):
        if item.ItemID not in self.itemid:
            return False
        if self.color and (item.Color not in self.color):
            return False
        return True

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        e = super().to_xml(e)
        e.set("itemid", to_interval(self.itemid))
        if len(self.color) > 0:
            e.set("color", to_interval(self.color))
        else:
            del e.attrib["color"]
        return e


class NameMatch(PatternMatch):
    """
    A match class for item names.
    """

    def test(self, item: "Item"):
        return bool(self.pattern.search(item.Name))


class WeightMatch(RangeMatch):
    """
    A match class for item weight.
    """

    def get_number(self, item: "Item"):
        return item.Weight


class RarityMatch(RangeMatch):
    """
    A match class for item rarity.
    """

    RARITY_MAP = {
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

    def get_number(self, item: "Item"):
        for prop in Items.GetPropStringList(item):
            if prop in self.RARITY_MAP:
                rarity = self.RARITY_MAP[prop]
                return rarity
        return 0


class PresetMatch(BaseMatch):
    """
    A match class that uses a predefined preset.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "preset": str,
    }
    preset: str
    """The name of the preset to use."""

    def __init__(
        self,
        preset: str,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.preset = preset

    def test(self, item: "Item"):
        preset = PRESETS.get(self.preset)
        if preset is None:
            raise ValueError(f"Preset '{self.preset}' not found.")
        return preset.test(item)


class ClilocMatch(BaseMatch):
    """
    A match class for item properties in cliloc format.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "cliloc": int,
    }
    cliloc: int
    """The cliloc number to match."""

    def __init__(
        self,
        cliloc: int,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.cliloc = cliloc

    def test(self, item: "Item"):
        return any(prop.Number == self.cliloc for prop in item.Properties)


class ClilocRangeMatch(RangeMatch):
    """
    A match class for item properties with integer values in cliloc format.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "cliloc": int,
        "index": int,
        "min_value": int,
        "max_value": int,
    }
    index: int
    """The index of the cliloc argument to be parsed."""

    def __init__(
        self,
        cliloc: int,
        index: int = 0,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        RangeMatch.__init__(self, min_value=min_value, max_value=max_value, name=name, desc=desc)
        self.cliloc = cliloc
        self.index = index

    def get_number(self, item: "Item"):
        for prop in item.Properties:
            if prop.Number != self.cliloc:
                continue
            args = prop.Args.split("\t")
            if self.index >= len(args):
                raise IndexError(f"Index {self.index} out of range for cliloc {self.cliloc} with args: {args}")
            return int(args[self.index])


class ClilocSkillMatch(RangeMatch):
    """
    A match class for item properties with skill values in cliloc format.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "skill_name": str,
        "min_value": int,
        "max_value": int,
    }
    SKILLNAME_CLILOC_MAP = {
        "Alchemy": 1044060,
        "Anatomy": 1044061,
        "Animal Lore": 1044062,
        "Item Identification": 1044063,
        "Arms Lore": 1044064,
        "Parrying": 1044065,
        "Begging": 1044066,
        "Blacksmithing": 1044067,
        "Fletching": 1044068,
        "Peacemaking": 1044069,
        "Camping": 1044070,
        "Carpentry": 1044071,
        "Cartography": 1044072,
        "Cooking": 1044073,
        "Detecting Hidden": 1044074,
        "Discordance": 1044075,
        "Eval Intelligence": 1044076,
        "Healing": 1044077,
        "Fishing": 1044078,
        "Forensics": 1044079,
        "Herding": 1044080,
        "Hiding": 1044081,
        "Provocation": 1044082,
        "Inscription": 1044083,
        "Lock Picking": 1044084,
        "Magery": 1044085,
        "Resisting Spells": 1044086,
        "Tactics": 1044087,
        "Snooping": 1044088,
        "Musicianship": 1044089,
        "Poisoning": 1044090,
        "Archery": 1044091,
        "Spirit Speak": 1044092,
        "Stealing": 1044093,
        "Tailoring": 1044094,
        "Animal Taming": 1044095,
        "Taste Identification": 1044096,
        "Tinkering": 1044097,
        "Tracking": 1044098,
        "Veterinary": 1044099,
        "Swordsmanship": 1044100,
        "Mace Fighting": 1044101,
        "Fencing": 1044102,
        "Wrestling": 1044103,
        "Lumberjacking": 1044104,
        "Mining": 1044105,
        "Meditation": 1044106,
        "Stealth": 1044107,
        "Remove Trap": 1044108,
        "Necromancy": 1044109,
        "Focus": 1044110,
        "Chivalry": 1044111,
        "Bushido": 1044112,
        "Ninjitsu": 1044113,
        "Spellweaving": 1044114,
        "Mysticism": 1044115,
        "Imbuing": 1044116,
        "Throwing": 1044117,
    }
    skill_name: str
    """The name of the skill to be matched."""

    def __init__(
        self,
        skill_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        if skill_name not in self.SKILLNAME_CLILOC_MAP:
            raise ValueError(f"Invalid skill name '{skill_name}'.")
        RangeMatch.__init__(self, min_value=min_value, max_value=max_value, name=name, desc=desc)
        self.skill_name = skill_name

    def get_number(self, item: "Item"):
        for prop in item.Properties:
            if prop.Number not in (1060451, 1060452, 1060453, 1060454, 1060455):
                continue
            args = prop.Args.split("\t")
            if len(args) < 2:
                continue
            if self.SKILLNAME_CLILOC_MAP[self.skill_name] == int(args[0].strip("#@")):
                return int(args[1])
        return None


class PropMatch(PatternMatch):
    """
    A match class for item properties in compiled string format.
    """

    def test(self, item: "Item"):
        for prop in Items.GetPropStringList(item):
            if self.pattern.search(prop):
                return True
        return False


class PropRangeMatch(RangeMatch, PatternMatch):
    """
    A match class for item properties with integer values in compiled string format.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "pattern": str,
        "min_value": int,
        "max_value": int,
    }

    def __init__(
        self,
        pattern: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        RangeMatch.__init__(self, min_value=min_value, max_value=max_value, name=name, desc=desc)
        PatternMatch.__init__(self, pattern=pattern, name=name, desc=desc)

    def get_number(self, item: "Item"):
        for prop in Items.GetPropStringList(item):
            match = self.pattern.search(prop)
            if match is None:
                continue
            return int(match.group(1))


class AllMatch(GroupMatch):
    """
    A match class that requires all entries to match.
    """

    def test(self, item: "Item"):
        return all(entry.test(item) for entry in self.entries)


class AnyMatch(GroupMatch):
    """
    A match class that requires any entry to match.
    """

    def test(self, item: "Item"):
        return any(entry.test(item) for entry in self.entries)


class ExceptMatch(GroupMatch):
    """
    A match class that requires no entries to match.
    """

    def test(self, item: "Item"):
        return not any(entry.test(item) for entry in self.entries)


_load_preset()

__export__ = [
    "parse_element",
    "BaseMatch",
    "GroupMatch",
    "PatternMatch",
    "RangeMatch",
    "SumMatch",
    "MaxMatch",
    "MinMatch",
    "SerialMatch",
    "TypeMatch",
    "NameMatch",
    "WeightMatch",
    "PresetMatch",
    "ClilocMatch",
    "ClilocRangeMatch",
    "ClilocSkillMatch",
    "PropMatch",
    "PropRangeMatch",
    "AllMatch",
    "AnyMatch",
    "ExceptMatch",
]
