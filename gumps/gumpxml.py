import xml.etree.ElementTree as ET
import re
from typing import Any, Optional, Tuple, List, Dict, Callable, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uo_runtime.gumps import Gumps
    from uo_runtime.player import Player
    from uo_runtime.misc import Misc


################################################################################
# Library part
################################################################################


def _float_with_default(val: Optional[str], default: float) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _parse_padmargin_with_default(
    padmargin: Optional[str], default: Tuple[float, float, float, float]
) -> Tuple[float, float, float, float]:
    """Parse padding/margin string into four floats."""
    if padmargin is None:
        return default
    values = padmargin.split()
    if len(values) == 1:
        value = float(values[0])
        return value, value, value, value
    if len(values) == 2:
        return float(values[0]), float(values[1]), float(values[0]), float(values[1])
    if len(values) == 3:
        return float(values[0]), float(values[1]), float(values[2]), float(values[1])
    if len(values) == 4:
        return float(values[0]), float(values[1]), float(values[2]), float(values[3])
    raise ValueError(f"Invalid padding/margin format: {padmargin}")


def _clamp(val: float, val_min: float, val_max: float) -> float:
    if val_min is not None:
        val = max(val, val_min)
    if val_max is not None:
        val = min(val, val_max)
    return val


def _resolve_self_size(tp: str, val: float, auto_content: float, avail: float):
    if tp == "auto":
        return auto_content
    if tp == "absolute":
        return val
    if tp == "relative":
        return avail * val
    return auto_content


def parse_bool(val: Optional[str]) -> bool:
    if val is None:
        return False
    val = val.lower()
    if val in ("true", "yes", "1"):
        return True
    if val in ("false", "no", "0"):
        return False
    raise ValueError(f"Invalid value for 'checked': {val}")


class GumpDOMNode:
    def __init__(self, element: ET.Element, parent: Optional["GumpDOMNode"] = None):
        self.element = element
        self.width_type = "auto"
        self.height_type = "auto"
        self.width_value = 0.0
        self.height_value = 0.0
        self.min_width = 0.0
        self.min_height = 0.0
        self.max_width = float("inf")
        self.max_height = float("inf")
        self.flex = 0.0
        self.orientation = "horizontal"
        self.padding = (0.0, 0.0, 0.0, 0.0)
        self.margin = (0.0, 0.0, 0.0, 0.0)
        self.spacing = 0.0

        self.measured_w = 0.0  # Width for the border-box model
        self.measured_h = 0.0  # Height for the border-box model
        self.x = 0.0  # X position of the element
        self.y = 0.0  # Y position of the element

        self.parent: Optional["GumpDOMNode"] = parent
        self.children: List["GumpDOMNode"] = []

        self.hash = hash(self["id"] or element) & 0xFFFF  # Unique ID for the element

    def __getitem__(self, item: str):
        return self.element.attrib.get(item, None)

    def __setitem__(self, item: str, value: Any):
        self.element.attrib[item] = str(value)

    def __repr__(self) -> str:
        return f"GumpNodeWrapper({self.tag}, {self.element.attrib})"

    def __iter__(self):
        return iter(self.children)

    def append(self, child: "GumpDOMNode"):
        self.children.append(child)
        child.parent = self

    def iter(self):
        yield self
        for child in self.children:
            yield from child.iter()

    def find_by_id(self, id: str) -> "GumpDOMNode":
        for e in self.iter():
            if e.id == id:
                return e
        raise ValueError(f"Element with id '{id}' not found.")

    @property
    def id(self) -> Optional[str]:
        """ID of the element wrapped by this GumpDOMNode object."""
        return self["id"]

    @property
    def tag(self) -> str:
        """Tag name of the element wrapped by this GumpDOMNode object."""
        return self.element.tag

    @tag.setter
    def tag(self, value: str):
        """Set the tag name of the element wrapped by this GumpDOMNode object."""
        self.element.tag = value

    @property
    def text(self) -> Optional[str]:
        """Text content of the element wrapped by this GumpDOMNode object."""
        return self.element.text

    @text.setter
    def text(self, value: str):
        """Set text content of the element wrapped by this GumpDOMNode object."""
        self.element.text = value

    @property
    def checked(self) -> bool:
        """Checked state of the element wrapped by this GumpDOMNode object."""
        return parse_bool(self["checked"])

    @property
    def content_x(self) -> float:
        """Content x position (excluding padding)"""
        return self.x + self.padding[0]

    @property
    def content_y(self) -> float:
        """Content y position (excluding padding)"""
        return self.y + self.padding[1]

    @property
    def content_w(self) -> float:
        """Content width (excluding padding)"""
        return self.measured_w - (self.padding[0] + self.padding[2])

    @content_w.setter
    def content_w(self, value: float):
        """Set content width (excluding padding)"""
        self.measured_w = value + (self.padding[0] + self.padding[2])

    @property
    def content_h(self) -> float:
        """Content height (excluding padding)"""
        return self.measured_h - (self.padding[1] + self.padding[3])

    @content_h.setter
    def content_h(self, value: float):
        """Set content height (excluding padding)"""
        self.measured_h = value + (self.padding[1] + self.padding[3])

    @property
    def outer_w(self) -> float:
        """Outer width (including margin)"""
        return self.measured_w + (self.margin[0] + self.margin[2])

    @outer_w.setter
    def outer_w(self, value: float):
        """Set outer width (including margin)"""
        self.measured_w = value - (self.margin[0] + self.margin[2])

    @property
    def outer_h(self) -> float:
        """Outer height (including margin)"""
        return self.measured_h + (self.margin[1] + self.margin[3])

    @outer_h.setter
    def outer_h(self, value: float):
        """Set outer height (including margin)"""
        self.measured_h = value - (self.margin[1] + self.margin[3])

    def _init_parse(self):
        # Sanitize orientation type
        parent_orientation = self.parent.orientation if self.parent else "vertical"
        orientation = self["orientation"]
        if orientation is None:
            if parent_orientation == "horizontal":
                orientation = "vertical"
            else:
                orientation = "horizontal"
        self.orientation = orientation

        # Sanitize width and height
        width = self["width"]
        height = self["height"]
        flex = self["flex"]
        if width is None:
            if parent_orientation == "horizontal" and flex is not None:
                self.width_type = "flex"
                self.flex = float(flex)
        elif width == "auto":
            pass
        elif width.endswith("%"):
            try:
                self.width_value = float(width[:-1]) / 100.0
                self.width_type = "relative"
            except ValueError:
                pass
        else:
            try:
                self.width_value = float(width)
                self.width_type = "absolute"
            except ValueError:
                pass

        if height is None:
            if parent_orientation == "vertical" and flex is not None:
                self.height_type = "flex"
                self.flex = float(flex)
        elif height == "auto":
            pass
        elif height.endswith("%"):
            try:
                self.height_value = float(height[:-1]) / 100.0
                self.height_type = "relative"
            except ValueError:
                pass
        else:
            try:
                self.height_value = float(height)
                self.height_type = "absolute"
            except ValueError:
                pass

        # Sanitize min/max width/height
        self.min_width = _float_with_default(self["min-width"], self.min_width)
        self.min_height = _float_with_default(self["min-height"], self.min_height)
        self.max_width = _float_with_default(self["max-width"], self.max_width)
        self.max_height = float(self["max-height"] or self.max_height or float("inf"))

        # Sanitize padding/margin
        self.padding = _parse_padmargin_with_default(self["padding"], self.padding)
        self.margin = _parse_padmargin_with_default(self["margin"], self.margin)
        self.spacing = _float_with_default(self["spacing"], self.spacing)

        # Sanitize children
        for child in self.element:
            self.append(GumpDOMNode(child, self)._init_parse())

        return self

    def _measure(self, avail_w: Optional[float] = None, avail_h: Optional[float] = None):
        if avail_w is None or avail_h is None:
            assert self.parent is None, "Parent must be None if the available dimensions are None"
            assert self.width_type == "absolute", "Width type must be absolute if the available dimensions are None"
            assert self.height_type == "absolute", "Height type must be absolute if the available dimensions are None"
            avail_w = self.width_value
            avail_h = self.height_value
        else:
            avail_w = max(0, avail_w - (self.margin[0] + self.margin[2]))
            avail_h = max(0, avail_h - (self.margin[1] + self.margin[3]))

        if self.width_type == "absolute":
            self.measured_w = self.width_value
            avail_w = self.measured_w
        elif self.width_type == "relative":
            self.measured_w = self.width_value * avail_w
            avail_w = self.measured_w
        self.measured_w = _clamp(self.measured_w, self.min_width, self.max_width)

        if self.height_type == "absolute":
            self.measured_h = self.height_value
            avail_h = self.measured_h
        elif self.height_type == "relative":
            self.measured_h = self.height_value * avail_h
            avail_h = self.measured_h
        self.measured_h = _clamp(self.measured_h, self.min_height, self.max_height)

        # If no children, measure self
        if not self.children:
            return self

        # Compute the content size using the children
        fixed_total = self.spacing * (len(self.children) - 1)
        flex_children: List[GumpDOMNode] = []
        max_cross = 0

        avail_content_w = max(0, avail_w - (self.padding[0] + self.padding[2]))
        avail_content_h = max(0, avail_h - (self.padding[1] + self.padding[3]))

        if self.orientation == "vertical":
            for child in self:
                if child.height_type == "flex":
                    flex_children.append(child)
                else:
                    child._measure(avail_content_w, avail_content_h - fixed_total)
                    fixed_total += child.outer_h
                    max_cross = max(max_cross, child.outer_w)

            if flex_children:
                remain = max(0, avail_content_h - fixed_total)
                total_weight = sum(child.flex for child in flex_children)
                for child in flex_children:
                    child.outer_h = remain * child.flex / total_weight
                    child.measured_h = _clamp(child.measured_h, child.min_height, child.max_height)
                    child._measure(avail_content_w, child.measured_h)

            self.content_w = max_cross
            self.content_h = fixed_total + sum(child.outer_h for child in flex_children)
        else:
            for child in self:
                if child.width_type == "flex":
                    flex_children.append(child)
                else:
                    child._measure(avail_content_w - fixed_total, avail_content_h)
                    fixed_total += child.outer_w
                    max_cross = max(max_cross, child.outer_h)

            if flex_children:
                remain = max(0, avail_content_w - fixed_total)
                total_weight = sum(child.flex for child in flex_children)
                for child in flex_children:
                    child.outer_w = remain * child.flex / total_weight
                    child.measured_w = _clamp(child.measured_w, child.min_width, child.max_width)
                    child._measure(child.outer_w, avail_content_h)

            self.content_w = fixed_total + sum(child.outer_w for child in flex_children)
            self.content_h = max_cross

        self.measured_w = _resolve_self_size(self.width_type, self.width_value, self.measured_w, avail_w)
        self.measured_h = _resolve_self_size(self.height_type, self.height_value, self.measured_h, avail_h)
        self.measured_w = _clamp(self.measured_w, self.min_width, self.max_width)
        self.measured_h = _clamp(self.measured_h, self.min_height, self.max_height)
        return self

    def _layout(self, x: float = 0, y: float = 0):
        self.x = x + self.margin[0]
        self.y = y + self.margin[1]
        if not self.children:
            return self

        cx = self.x + self.padding[0]
        cy = self.y + self.padding[1]
        for child in self.children:
            child._layout(cx, cy)
            if self.orientation == "vertical":
                cy += child.outer_h + self.spacing
            else:
                cx += child.outer_w + self.spacing
        return self


class GumpStyleElement:
    """
    This specifies how each element should be rendered.
    """

    def test(self, e: GumpDOMNode) -> bool:
        """
        Provides anny additional test to determine if the style should be applied.
        """
        return True

    def render(self, gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        """
        Renders the element using the `GumpData` object.
        This method should be overridden by subclasses to provide specific rendering logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def wrap(cls, renderer: Callable) -> "GumpStyleElement":
        """
        Wraps a callable function into a `GumpStyleElement` instance.

        The callable function should accept `GumpData` and `GumpDOMNode` as arguments.
        This allows for dynamic rendering based on the element's attributes and state.
        """

        class _(GumpStyleElement):
            def render(self, gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                renderer(gd, e)

        return _()


class GumpTheme:
    """
    This is a collection of styles for each element type.
    """

    def __init__(self):
        self.styles: Dict[str, GumpStyleElement] = {}

    def preprocess(self, root: ET.Element) -> ET.Element:
        """
        Preprocess the XML tree before parsing.
        This method can be overridden by subclasses to modify the XML structure.
        """
        return root

    def add_style(self, tag: str, style) -> None:
        """
        Adds a style for a specific tag.
        The style can be:
        - a subclass of `GumpStyleElement`,
        - an instance of `GumpStyleElement`, or
        - a callable function accepting `GumpData` and `GumpDOMNode` as arguments.
        """
        if isinstance(style, type) and issubclass(style, GumpStyleElement):
            style = style()
        elif callable(style):
            style = GumpStyleElement.wrap(style)
        self.styles[tag] = style

    def apply(self, gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        for tag, style in self.styles.items():
            if tag == e.tag and style.test(e):
                return style.render(gd, e)


class GumpDOMParser:
    class RenderedGump:
        """
        This class represents a rendered gump.

        It contains the gump data and the root node of the gump DOM.
        It also provides methods to send the gump and handle events.

        Attributes:
            gd (Gumps.GumpData): The gump data object.
            gdom (GumpDOMNode): The root node of the gump DOM.
            id (int): The ID of the gump.
            events (dict): A dictionary mapping button IDs to event handlers.

        Methods:
            add_event(button_id: Optional[str], handler: Callable) -> None:
                Adds an event handler for a specific button ID.
                Each hander accepts a dictionary of field IDs and their values.
            send_and_listen(x: int, y: int) -> Tuple[Optional[str], Dict[str, Any]]:
                Sends the gump to the player and waits for a button click or gump close event.
                Returns the button ID and a dictionary of field IDs and their values.
        """

        def __init__(self, gd: Gumps.GumpData, gdom: GumpDOMNode):
            self.gd = gd
            self.gdom = gdom
            self.id = gdom.hash
            self.events: Dict[Optional[str], List[Callable]] = {}

        def add_event_listener(self, button_id: Optional[str], handler: Callable[[GumpDOMNode], None]) -> None:
            """
            Adds an event handler for a specific button ID.

            Each handler accepts the GumpDOMNode object, representing clicked element, as an argument.
            In other words, the signature of `handler` should be `(GumpDOMNode) -> None`.
            """
            if button_id not in self.events:
                self.events[button_id] = []
            self.events[button_id].append(handler)

        def send_and_listen(self, x: int, y: int) -> Tuple[Optional[str], Dict[str, GumpDOMNode]]:
            """
            Sends the gump to the player and waits for a button click or gump close event.

            Returns the button ID and a dictionary of field IDs and their values.

            Arguments:
                x (int): The x-coordinate of the gump. It is used to position the gump first time it is opened.
                y (int): The y-coordinate of the gump. It is used to position the gump first time it is opened.
            """
            Gumps.SendGump(self.id, Player.Serial, x, y, self.gd.gumpDefinition, self.gd.gumpStrings)
            clicked_element = None
            ev_map = {}
            # Wait for the gump to be closed or a button to be clicked
            if Gumps.WaitForGump(self.id, 3600000):
                gd = Gumps.GetGumpData(self.id)
                # Parse the response and update the gump data
                text_map = {id_int: text for id_int, text in zip(gd.textID, gd.text)}
                for e in self.gdom.iter():
                    assert isinstance(e, GumpDOMNode)
                    if e.id is not None:
                        ev_map[e.id] = e
                    if e.hash == gd.buttonid:
                        clicked_element = e
                    elif e.tag == "textentry":
                        e.text = text_map.get(e.hash, "")
                    elif e.tag == "checkbox":
                        e["checked"] = e.hash in gd.switches
            # Returns the button ID and the field values
            if clicked_element is not None:
                for handler in self.events.get(clicked_element.id, []):
                    handler(clicked_element)
                return clicked_element.id, ev_map
            return None, ev_map

    @classmethod
    def render(cls, root: Union[str, ET.Element], gtheme: GumpTheme) -> "GumpDOMParser.RenderedGump":
        """
        Parses the `ElementTree` XML structure and builds a gump.

        This method performs the following steps:
        1. Wraps the parsed `ElementTree` into a tree structure of `GumpDOMNode` objects.
        2. Measures and lays out the gump structure.
        3. Renders the gump using the provided `GumpTheme`.
        4. Returns a `RenderedGump` object containing the gump data and the root `GumpDOMNode`.
        """
        # Creates an empty gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        # If the root is a string, parse it into an ElementTree
        if isinstance(root, str):
            root = ET.fromstring(root)
        # Preprocess the XML tree before parsing
        root = gtheme.preprocess(root)
        # Parse the XML and create a GumpDOMNode object
        gdom = GumpDOMNode(root)._init_parse()._measure()._layout()
        # Render the gump using the GumpTheme
        for e in gdom.iter():
            assert isinstance(e, GumpDOMNode)
            # Background and alpha region
            x, y, w, h = round(e.x), round(e.y), round(e.measured_w), round(e.measured_h)
            bg = e["bg"]
            if bg is not None:
                match_frame = re.match(r"frame\s*:\s*(\d+)\s*", bg)
                if match_frame:
                    bg = int(match_frame.group(1))
                    Gumps.AddBackground(gd, x, y, w, h, bg)
                else:
                    bg = int(bg)
                    Gumps.AddImageTiled(gd, x, y, w, h, bg)
            if parse_bool(e["alpha"]):
                Gumps.AddAlphaRegion(gd, x, y, w, h)
            # Element-specific rendering
            gtheme.apply(gd, e)
            tooltip = e["tooltip"]
            # Add tooltip if present
            if tooltip is not None:
                Gumps.AddTooltip(gd, tooltip)
        # Return the root GumpDOMNode object
        return GumpDOMParser.RenderedGump(gd, gdom)


################################################################################
# Presets
################################################################################


GUMP_BUTTON_PRESET = {
    # Configurations
    239: {"src-active": 240, "width": 63, "height": 23},  # yellow jewel apply
    243: {"src-active": 241, "width": 63, "height": 23},  # red jewel cancel
    246: {"src-active": 244, "width": 63, "height": 23},  # blue jewel default
    249: {"src-active": 248, "width": 63, "height": 23},  # green jewel okay
    251: {"src-active": 250, "width": 15, "height": 21},  # arrow up
    253: {"src-active": 252, "width": 15, "height": 21},  # arrow down
    # Login
    1144: {"src-active": 1145, "width": 71, "height": 37},  # oval red jewel cancel
    1147: {"src-active": 1148, "width": 71, "height": 37},  # oval green jewel okay
    # Generic
    1150: {"src-active": 1152, "width": 28, "height": 21},  # round-corner gray X
    1153: {"src-active": 1155, "width": 28, "height": 21},  # round-corner gray check
    # Small buttons
    1209: {"src-active": 1210, "width": 14, "height": 14},  # small blue jewel
    1625: {"src-active": 1626, "width": 17, "height": 24},  # small blue jewel with arrow bottom
    5837: {"src-active": 5838, "width": 24, "height": 17},  # small blue jewel with arrow right
    5839: {"src-active": 5840, "width": 24, "height": 17},  # small blue jewel with arrow left
    5841: {"src-active": 5842, "width": 17, "height": 24},  # small blue jewel with arrow top
    # Town Crier News
    1531: {"src-active": 1532, "width": 23, "height": 21},  # eye icon
    1533: {"src-active": 1534, "width": 23, "height": 21},  # write icon
    1535: {"src-active": 1536, "width": 23, "height": 21},  # X icon
    1537: {"src-active": 1538, "width": 23, "height": 21},  # check icon
    1539: {"src-active": 1540, "width": 23, "height": 21},  # duble arrow right icon
    1541: {"src-active": 1542, "width": 23, "height": 21},  # duble arrow left icon
    1543: {"src-active": 1544, "width": 15, "height": 21},  # single arrow right icon
    1545: {"src-active": 1546, "width": 15, "height": 21},  # single arrow left icon
    # Parchment Style
    1588: {"src-active": 1589, "width": 126, "height": 25},  # wide button 1
    1590: {"src-active": 1591, "width": 126, "height": 25},  # wide button 2
    1592: {"src-active": 1593, "width": 65, "height": 25},  # narrow button
    1594: {"src-active": 1595, "width": 45, "height": 25},  # narrower button
    # Paperdoll
    2006: {"src-active": 2007, "width": 64, "height": 21},  # blue jewel options
    2009: {"src-active": 2010, "width": 64, "height": 22},  # blue jewel logout
    2012: {"src-active": 2013, "width": 64, "height": 21},  # blue jewel journal
    2015: {"src-active": 2016, "width": 65, "height": 21},  # blue jewel skills
    2018: {"src-active": 2019, "width": 64, "height": 21},  # blue jewel chat
    2021: {"src-active": 2022, "width": 64, "height": 22},  # blue jewel peace
    2024: {"src-active": 2025, "width": 64, "height": 22},  # red jewel war
    2027: {"src-active": 2028, "width": 65, "height": 22},  # blue jewel status
    2031: {"src-active": 2032, "width": 64, "height": 21},  # blue jewel help
    # Classic Confirm Gump
    2071: {"src-active": 2072, "width": 56, "height": 21},  # red jewel cancel
    2074: {"src-active": 2075, "width": 46, "height": 21},  # green jewel okay
    # Skill Gump
    2103: {"src-active": 2104, "width": 11, "height": 11},  # small blue jewel
    # Obsolete Gump
    2111: {"src-active": 2112, "width": 56, "height": 22},  # orange jewel auto
    2114: {"src-active": 2115, "width": 56, "height": 22},  # purple jewel manual
    2117: {"src-active": 2118, "width": 15, "height": 15},  # small blue jewel
    2119: {"src-active": 2120, "width": 55, "height": 21},  # red jewel cancel
    2122: {"src-active": 2123, "width": 55, "height": 21},  # yellow jewel apply
    2125: {"src-active": 2126, "width": 55, "height": 21},  # blue jewel default
    2128: {"src-active": 2129, "width": 55, "height": 21},  # green jewel okay
    2141: {"src-active": 2142, "width": 46, "height": 21},  # narrow green jewel okay
    # Generic
    2151: {"src-active": 2152, "width": 29, "height": 29},  # lozenge blue jewel unchecked
    2153: {"src-active": 2154, "width": 29, "height": 29},  # lozenge blue jewel checked
    2435: {"src-active": 2436, "width": 9, "height": 11},  # small arrow up
    2437: {"src-active": 2438, "width": 9, "height": 11},  # small arrow down
    2472: {"src-active": 2473, "width": 27, "height": 27},  # lozenge red jewel
    5826: {"src-active": 5827, "width": 29, "height": 29},  # lozenge green jewel
    5843: {"src-active": 5844, "width": 29, "height": 29},  # lozenge purple jewel
    9720: {"src-active": 9722, "width": 29, "height": 29},  # lozenge gray jewel unchecked
    9723: {"src-active": 9725, "width": 29, "height": 29},  # lozenge gray jewel checked
    9726: {"src-active": 9728, "width": 29, "height": 29},  # lozenge monochrome jewel unchecked
    9729: {"src-active": 9731, "width": 29, "height": 29},  # lozenge monochrome jewel checked
    # black-gold gump (2520)
    2640: {"src-active": 2641, "width": 27, "height": 27},  # black-gold X button
    2644: {"src-active": 2645, "width": 27, "height": 27},  # black-gold - button
    2646: {"src-active": 2647, "width": 19, "height": 21},  # black arrow down
    2650: {"src-active": 2651, "width": 19, "height": 20},  # black arrow up
    2704: {"src-active": 2705, "width": 11, "height": 19},  # narrow black arrow up
    2706: {"src-active": 2707, "width": 11, "height": 19},  # narrow black arrow down
    2708: {"src-active": 2709, "width": 19, "height": 19},  # black X
    2710: {"src-active": 2711, "width": 18, "height": 19},  # black -
    2714: {"src-active": 2715, "width": 18, "height": 19},  # black check
    # Generic Party
    4002: {"src-active": 4004, "width": 30, "height": 22},  # person X
    4005: {"src-active": 4007, "width": 30, "height": 22},  # arrow right
    4008: {"src-active": 4010, "width": 30, "height": 22},  # people
    4011: {"src-active": 4013, "width": 30, "height": 22},  # memo
    4014: {"src-active": 4016, "width": 30, "height": 22},  # arrow left
    4017: {"src-active": 4019, "width": 30, "height": 22},  # X
    4020: {"src-active": 4022, "width": 30, "height": 22},  # now allowed
    4023: {"src-active": 4025, "width": 30, "height": 22},  # okay
    4026: {"src-active": 4028, "width": 30, "height": 22},  # E
    4029: {"src-active": 4031, "width": 30, "height": 22},  # send note
    # Login
    5525: {"src-active": 5527, "width": 62, "height": 23},  # round-corner gray help
    5530: {"src-active": 5532, "width": 62, "height": 23},  # round-corner gray delete
    5533: {"src-active": 5535, "width": 62, "height": 23},  # round-corner gray new
    5537: {"src-active": 5539, "width": 19, "height": 21},  # round-corner arrow left
    5540: {"src-active": 5542, "width": 19, "height": 21},  # round-corner arrow right
    9900: {"src-active": 9902, "width": 21, "height": 21},  # round-corner arrow up
    9903: {"src-active": 9905, "width": 21, "height": 21},  # round-corner arrow right
    9906: {"src-active": 9908, "width": 21, "height": 21},  # round-corner arrow down
    9909: {"src-active": 9911, "width": 21, "height": 21},  # round-corner arrow left
    # UO Store
    40016: {"src-active": 40026, "width": 32, "height": 22},  # arrow left
    40017: {"src-active": 40027, "width": 32, "height": 22},  # arrow right
    40018: {"src-active": 40028, "width": 64, "height": 22},  # narrow button
    40019: {"src-active": 40029, "width": 126, "height": 25},  # wide button
    40020: {"src-active": 40030, "width": 126, "height": 25},  # wide green button
    40021: {"src-active": 40031, "width": 125, "height": 25},  # wide blue button
    40297: {"src-active": 40298, "width": 125, "height": 25},  # wide red button
    40299: {"src-active": 40300, "width": 125, "height": 25},  # wide yellow button
}

GUMP_CHECKBOX_PRESET = {
    208: {"src-active": 209, "width": 19, "height": 20},  # round checkbox
    210: {"src-active": 211, "width": 19, "height": 20},  # square checkbox
    9790: {"src-active": 9791, "width": 21, "height": 27},  # yellow parchment checkbox
    9792: {"src-active": 9793, "width": 21, "height": 27},  # gray parchment checkbox
    40014: {"src-active": 40015, "width": 22, "height": 22},  # uo store black-gold checkbox
}


class GumpThemePresets:
    class _Light(GumpTheme):
        def __init__(self):
            super().__init__()

            def render_container(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                pass

            def render_label(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                cx, cy, cw, ch = (round(e.content_x), round(e.content_y), round(e.content_w), round(e.content_h))
                color = int(e["color"] or "0")
                text = e.text or ""
                if text:
                    Gumps.AddLabelCropped(gd, cx, cy, cw, ch, color, text)

            def render_html(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                cx, cy, cw, ch = (round(e.content_x), round(e.content_y), round(e.content_w), round(e.content_h))
                scrollbar = parse_bool(e["scrollbar"])
                text = e.text or ""
                if e["color"]:
                    text = f'<BASEFONT COLOR="{e["color"]}">{text}</BASEFONT>'
                if parse_bool(e["centered"]):
                    text = f"<CENTER>{text}</CENTER>"
                Gumps.AddHtml(gd, cx, cy, cw, ch, text, False, scrollbar)

            def render_itemimg(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                cx, cy = (round(e.content_x), round(e.content_y))
                src = int(e["src"] or "0")
                color = int(e["color"] or "0")
                Gumps.AddItem(gd, cx, cy, src, color)

            def render_gumpimg(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                cx, cy = (round(e.content_x), round(e.content_y))
                src = int(e["src"] or "0")
                color = int(e["color"] or "0")
                Gumps.AddImage(gd, cx, cy, src, color)

            def render_gumpimgtiled(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                cx, cy, cw, ch = (round(e.content_x), round(e.content_y), round(e.content_w), round(e.content_h))
                src = int(e["src"] or "0")
                Gumps.AddImageTiled(gd, cx, cy, cw, ch, src)

            def render_textentry(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                cx, cy, cw, ch = (round(e.content_x), round(e.content_y), round(e.content_w), round(e.content_h))
                color = int(e["color"] or "0")
                text = e.text or ""
                Gumps.AddTextEntry(gd, cx, cy, cw, ch, color, e.hash, text)

            def render_button(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                # Add button
                x, y = int(e.x), int(e.y)
                src_up = int(e["src"] or "0")
                src_down = int(e["src-active"] or "0")
                Gumps.AddButton(gd, x, y, src_up, src_down, e.hash, 1, 0)
                # Add text for the button if present
                render_html(gd, e)

            def render_checkbox(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
                x, y = int(e.x), int(e.y)
                checked = parse_bool(e["checked"])
                src_off = int(e["src"] or "0")
                src_on = int(e["src-active"] or "0")
                Gumps.AddCheck(gd, x, y, src_off, src_on, checked, e.hash)

            for tag in ["frame", "container", "hbox", "vbox", "hfill", "vfill"]:
                self.add_style(tag, GumpStyleElement.wrap(render_container))
            self.add_style("label", render_label)
            self.add_style("html", render_html)
            self.add_style("h", render_html)
            self.add_style("itemimg", render_itemimg)
            self.add_style("gumpimg", render_gumpimg)
            self.add_style("gumpimgtiled", render_gumpimgtiled)
            self.add_style("textentry", render_textentry)
            self.add_style("button", render_button)
            self.add_style("checkbox", render_checkbox)

        def preprocess(self, root: ET.Element) -> ET.Element:
            for e in root.iter():
                if e.tag == "h":
                    e.attrib["width"] = e.attrib.get("width", "100%")
                    e.attrib["height"] = e.attrib.get("height", "18")
                    e.attrib["centered"] = e.attrib.get("centered", "yes")
                    continue
                if e.tag == "hfill":
                    e.attrib["flex"] = e.attrib.get("flex", "1.0")
                    continue
                if e.tag == "vfill":
                    e.attrib["flex"] = e.attrib.get("flex", "1.0")
                    continue
                if e.tag == "hbox":
                    e.attrib["orientation"] = e.attrib.get("orientation", "horizontal")
                    e.attrib["width"] = e.attrib.get("width", "100%")
                    continue
                if e.tag == "vbox":
                    e.attrib["orientation"] = e.attrib.get("orientation", "vertical")
                    e.attrib["height"] = e.attrib.get("height", "100%")
                    continue
                if e.tag == "label":
                    e.attrib["height"] = e.attrib.get("height", "18")
                    continue
                if e.tag == "textentry":
                    e.attrib["min-width"] = e.attrib.get("min-width", "22")
                    e.attrib["height"] = e.attrib.get("height", "22")
                    e.attrib["margin"] = e.attrib.get("margin", "0 -2")
                    e.attrib["padding"] = e.attrib.get("padding", "2 2")
                    continue
                if e.tag == "button":
                    # Set default values for button attributes
                    e.attrib["src"] = e.attrib.get("src", "40018")
                    e.attrib["color"] = e.attrib.get("color", "#FFFFFF")
                    e.attrib["centered"] = e.attrib.get("centered", "yes")
                    e.attrib["valign"] = e.attrib.get("valign", "baseline")
                    # Set default button size
                    src = int(e.attrib["src"] or "0")
                    if src in GUMP_BUTTON_PRESET:
                        preset = GUMP_BUTTON_PRESET[src]
                        e.attrib["width"] = e.attrib.get("width", str(preset["width"]))
                        e.attrib["height"] = e.attrib.get("height", str(preset["height"]))
                        e.attrib["src-active"] = e.attrib.get("src-active", str(preset["src-active"]))
                        if e.attrib.get("valign") == "baseline":
                            m = (18 - preset["height"]) / 2
                            e.attrib["margin"] = e.attrib.get("margin", f"0 {m}")
                            e.attrib["padding"] = e.attrib.get("padding", f"0 {-m}")
                    continue
                if e.tag == "checkbox":
                    # Set default values for checkbox attributes
                    e.attrib["src"] = e.attrib.get("src", "210")
                    e.attrib["valign"] = e.attrib.get("valign", "baseline")
                    # Set default checkbox size
                    src = int(e.attrib["src"] or "0")
                    if src in GUMP_CHECKBOX_PRESET:
                        preset = GUMP_CHECKBOX_PRESET[src]
                        e.attrib["width"] = e.attrib.get("width", str(preset["width"]))
                        e.attrib["height"] = e.attrib.get("height", str(preset["height"]))
                        e.attrib["src-active"] = e.attrib.get("src-active", str(preset["src-active"]))
                        if e.attrib.get("valign") == "baseline":
                            m = (18 - preset["height"]) / 2
                            e.attrib["margin"] = e.attrib.get("margin", f"0 {m}")
                            e.attrib["padding"] = e.attrib.get("padding", f"0 {-m}")

            return root

    Light = _Light()


################################################################################
# Application part
################################################################################


class GumpPresets:
    """
    This is a collection of preset gumps for common use cases.
    """

    @classmethod
    def confirm(
        cls,
        msg: str,
        width: int,
        height: int,
        x: int = 400,
        y: int = 300,
        yes_text: str = "Yes",
        no_text: str = "No",
        gtheme: GumpTheme = GumpThemePresets.Light,
    ) -> bool:
        """
        Opens a confirmation dialog with "Yes" and "No" buttons.

        Arguments:
            msg (str): The message to display in the dialog.
            width (int): The width of the dialog.
            height (int): The height of the dialog.
            x (int): The x-coordinate of the dialog. Defaults to 300.
            y (int): The y-coordinate of the dialog. Defaults to 150.

        Returns:
            bool: True if the user clicked "Yes", False if the user clicked "No".
        """
        dialog_xml = f"""
        <frame width="{width}" height="{height}" bg="frame:30546" padding="15" alpha="yes" orientation="vertical">
            <html width="100%" flex="1" margin="0 0 0 15" centered="yes" color="#FFFFFF">{msg}</html>
            <hbox>
                <hfill />
                <button id="yes">{yes_text}</button>
                <button id="no">{no_text}</button>
                <hfill />
            </hbox>
        </frame>
        """
        root = ET.fromstring(dialog_xml)
        g = GumpDOMParser.render(root, gtheme)
        g.id = hash(dialog_xml) & 0xFFFFFFFF
        res, _ = g.send_and_listen(x, y)
        return res == "yes"

    @classmethod
    def prompt(
        cls,
        msg: str,
        width: int,
        height: int,
        value: str = "",
        x: int = 400,
        y: int = 300,
        gtheme: GumpTheme = GumpThemePresets.Light,
    ) -> Tuple[bool, str]:
        """
        Opens a prompt dialog with a text entry field.

        Arguments:
            msg (str): The message to display in the dialog.
            width (int): The width of the dialog.
            height (int): The height of the dialog.
            default_text (str): The default text to display in the text entry field. Defaults to an empty string.
            x (int): The x-coordinate of the dialog. Defaults to 300.
            y (int): The y-coordinate of the dialog. Defaults to 150.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the user submitted the dialog and the text entered by the user.
        """
        dialog_xml = f"""
        <frame width="{width}" height="{height}" bg="frame:30546" padding="15" alpha="yes" orientation="vertical">
            <html width="100%" flex="1" margin="0 0 0 15" color="#FFFFFF">{msg}</html>
            <hbox>
                <textentry id="prompt" flex="1" bg="9354">{value}</textentry>
                <button id="yes">Submit</button>
                <button id="no">Cancel</button>
            </hbox>
        </frame>
        """
        root = ET.fromstring(dialog_xml)
        g = GumpDOMParser.render(root, gtheme)
        g.id = hash(dialog_xml) & 0xFFFFFFFF
        res, ev_map = g.send_and_listen(x, y)
        if res == "yes":
            return True, ev_map["prompt"].text or ""
        else:
            return False, value


__export__ = [
    "GumpStyleElement",
    "GumpTheme",
    "GumpDOMParser",
    "GumpThemePresets",
    "GumpPresets",
    "ET",
]
