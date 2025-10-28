from AutoComplete import *
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Dict, Tuple, Optional, Union, Generator, Callable
import xml.etree.ElementTree as ET
import re
import os


################################################################################
# Utilities


def validate_interval(value: str) -> bool:
    """
    Validate if a string is a valid interval format.
    """
    pattern = r"^\s*(\d+|0x[0-9A-Fa-f]+)(\s*\.\.\.\s*(\d+|0x[0-9A-Fa-f]+))?(\s*,\s*(\d+|0x[0-9A-Fa-f]+)(\s*\.\.\.\s*(\d+|0x[0-9A-Fa-f]+))?)*\s*$"
    return re.match(pattern, value) is not None


def interval(value: str) -> List[int]:
    """
    Create a list of integers from a string interval.

    1. If the string is a single integer, return a list with that integer.
    2. If the string is a range in the format "start...end", return a list of integers from start to end (inclusive).
    3. If the string is a comma-separated list of integers and/or ranges, return a list of all integers.
    """
    if not validate_interval(value):
        raise ValueError(f"Invalid interval format: '{value}'")
    result = []
    for entry in re.split(r"\s*,\s*", value.strip()):
        if not entry:
            continue
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


class SingleSerialMatch(BaseMatch):
    """
    A match class for a single item serial number.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "serial": int,
        "itemid": int,
        "color": int,
    }
    serial: int
    """The serial number to match."""

    def __init__(
        self,
        serial: int,
        itemid: int,
        color: int,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.serial = serial
        self.itemid = itemid
        self.color = color

    def test(self, item: "Item"):
        return item.Serial == self.serial

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        e = super().to_xml(e)
        e.set("serial", f"0x{self.serial:08X}")
        e.set("itemid", f"0x{self.itemid:04X}")
        e.set("color", f"0x{self.color:04X}")
        return e


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
        e.set("serial", to_interval(self.serial))
        return e


class SingleTypeMatch(BaseMatch):
    """
    A match class for a single item type and color.
    """

    _XML_ATTRIBUTES: dict[str, Callable] = {
        "name": str,
        "desc": str,
        "itemid": int,
        "color": int,
    }
    itemid: int
    """The item type ID to match."""
    color: Optional[int]
    """The item color to match. If `None`, any color matches."""

    def __init__(
        self,
        itemid: int,
        color: Optional[int] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        super().__init__(name=name, desc=desc)
        self.itemid = itemid
        self.color = color

    def test(self, item: "Item"):
        if item.ItemID != self.itemid:
            return False
        if self.color is not None and item.Color != self.color:
            return False
        return True

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        e = super().to_xml(e)
        e.set("itemid", f"0x{self.itemid:04X}")
        if self.color is not None:
            e.set("color", f"0x{self.color:04X}")
        elif "color" in e.attrib:
            del e.attrib["color"]
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
        elif "color" in e.attrib:
            del e.attrib["color"]
        return e


class NameMatch(PatternMatch):
    """
    A match class for item names.
    """

    def test(self, item: "Item"):
        return bool(self.pattern.search(item.Name))


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


_load_preset()
