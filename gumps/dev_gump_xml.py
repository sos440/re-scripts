import xml.etree.ElementTree as ET
from typing import Any, Optional, Tuple, List, Dict, Callable, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uo_runtime.gumps import Gumps
    from uo_runtime.player import Player


################################################################################
# Library part
################################################################################


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

        self.id = hash(element) & 0xFFFF  # Unique ID for the element

    def __getitem__(self, item: str):
        return self.element.attrib.get(item, None)

    def __setitem__(self, item: str, value: Any):
        self.element.attrib[item] = str(value)

    def __repr__(self) -> str:
        return f"GumpNodeWrapper({self.element.tag}, {self.element.attrib})"

    def __iter__(self):
        return iter(self.children)

    def append(self, child: "GumpDOMNode"):
        self.children.append(child)
        child.parent = self

    def iter(self):
        yield self
        for child in self.children:
            yield from child.iter()

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

    def _parse_padmargin(self, padmargin: str):
        """Parse padding/margin string into four floats."""
        values = padmargin.split()
        if len(values) == 1:
            value = float(values[0])
            return value, value, value, value
        elif len(values) == 2:
            return float(values[0]), float(values[1]), float(values[0]), float(values[1])
        elif len(values) == 3:
            return float(values[0]), float(values[1]), float(values[2]), float(values[1])
        elif len(values) == 4:
            return float(values[0]), float(values[1]), float(values[2]), float(values[3])
        else:
            raise ValueError(f"Invalid padding/margin format: {padmargin}")

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
        self.min_width = float(self["min-width"] or 0)
        self.min_height = float(self["min-height"] or 0)
        self.max_width = float(self["max-width"] or float("inf"))
        self.max_height = float(self["max-height"] or float("inf"))

        # Sanitize padding/margin
        self.padding = self._parse_padmargin(self["padding"] or "0")
        self.margin = self._parse_padmargin(self["margin"] or "0")
        self.spacing = float(self["spacing"] or 0)

        # Apply default values for specific tags
        # ToDo: Make this more generic and less hardcoded
        # Maybe I can implement "preprocess" method in the GumpDOMNode class
        if self.element.tag == "h":
            self.width_type = "relative"
            self.width_value = 1.0
            self.height_type = "absolute"
            self.height_value = 18.0
            self["centered"] = "yes"
        elif self.element.tag == "hfill":
            self.width_type = "flex"
            self.flex = 1.0
        elif self.element.tag == "vfill":
            self.height_type = "flex"
            self.flex = 1.0
        elif self.element.tag == "hbox":
            self.width_type = "relative"
            self.width_value = 1.0
        elif self.element.tag == "vbox":
            self.height_type = "relative"
            self.height_value = 1.0
        elif self.element.tag == "label":
            self.height_type = "absolute"
            self.height_value = 18.0
        elif self.element.tag == "textentry":
            self.height_type = "absolute"
            self.height_value = 18.0
        elif self.element.tag == "button":
            if self["src"] == "40018":
                self.width_type = "absolute"
                self.width_value = 65.0
                self.height_type = "absolute"
                self.height_value = 18.0
            elif self["src"] in ("40019", "40020", "40021", "40297", "40299"):
                self.width_type = "absolute"
                self.width_value = 125.0
                self.height_type = "absolute"
                self.height_value = 18.0
        elif self.element.tag == "checkbox":
            if self["src"] == "9026":
                self.width_type = "absolute"
                self.width_value = 18.0
                self.height_type = "absolute"
                self.height_value = 18.0

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


class GumpStyleSheet:
    """
    This is a collection of styles for each element type.
    """

    def __init__(self):
        self.styles: Dict[str, GumpStyleElement] = {}

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
            if tag == e.element.tag and style.test(e):
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
            send(x: int, y: int) -> None:
                Sends the gump to the client and listens for events.
        """

        def __init__(self, gd: Gumps.GumpData, gdom: GumpDOMNode):
            self.gd = gd
            self.gdom = gdom
            self.id = gdom.id
            self.events: Dict[Optional[str], List[Callable]] = {}

        def add_event(self, button_id: Optional[str], handler: Callable) -> None:
            if button_id not in self.events:
                self.events[button_id] = []
            self.events[button_id].append(handler)

        def send_and_listen(self, x: int, y: int) -> Tuple[Optional[str], Dict[str, Any]]:
            Gumps.SendGump(self.id, Player.Serial, x, y, self.gd.gumpDefinition, self.gd.gumpStrings)
            return self._listen()

        def _listen(self):
            button_id = None
            iv_map = {}
            # Wait for the gump to be closed or a button to be clicked
            if Gumps.WaitForGump(self.id, 3600000):
                gd = Gumps.GetGumpData(self.id)
                # Parse the response and update the gump data
                text_map = {id_int: text for id_int, text in zip(gd.textID, gd.text)}
                for e in self.gdom.iter():
                    assert isinstance(e, GumpDOMNode)
                    if e.id == gd.buttonid:
                        button_id = e["id"]
                    elif e.element.tag == "textentry":
                        e["text"] = text_map.get(e.id, "")
                        iv_map[e["id"]] = e["text"]
                    elif e.element.tag == "checkbox":
                        e["checked"] = e.id in gd.switches
                        iv_map[e["id"]] = e["checked"]
            # Handles the click event
            if button_id in self.events:
                for handler in self.events[button_id]:
                    handler(iv_map)
            return button_id, iv_map

    @classmethod
    def parse(cls, root: ET.Element, gcss: GumpStyleSheet) -> "GumpDOMParser.RenderedGump":
        """
        Parses the `ElementTree` XML structure and builds a gump.

        This method performs the following steps:
        1. Wraps the parsed `ElementTree` into a tree structure of `GumpDOMNode` objects.
        2. Measures and lays out the gump structure.
        3. Renders the gump using the provided `GumpStyleSheet`.
        4. Returns a `RenderedGump` object containing the gump data and the root `GumpDOMNode`.
        """
        # Creates an empty gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        # Parse the XML and create a GumpDOMNode object
        gdom = GumpDOMNode(root)._init_parse()._measure()._layout()
        # Render the gump using the GumpStyleSheet
        for e in gdom.iter():
            assert isinstance(e, GumpDOMNode)
            gcss.apply(gd, e)
            tooltip = e["tooltip"]
            if tooltip is not None:
                Gumps.AddTooltip(gd, tooltip)
        # Return the root GumpDOMNode object
        return GumpDOMParser.RenderedGump(gd, gdom)


def parse_bool(val: Optional[str]) -> bool:
    if val is None:
        return False
    val = val.lower()
    if val in ("true", "yes", "1"):
        return True
    if val in ("false", "no", "0"):
        return False
    raise ValueError(f"Invalid value for 'checked': {val}")


################################################################################
# Application part
################################################################################


def build_gump_ss_default() -> GumpStyleSheet:
    def render_container(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        if e["bg"] is None:
            return
        x, y, w, h = int(e.x), int(e.y), int(e.measured_w), int(e.measured_h)
        bg = int(e["bg"] or "0")
        Gumps.AddBackground(gd, x, y, w, h, bg)
        if parse_bool(e["alpha"]):
            Gumps.AddAlphaRegion(gd, x, y, w, h)

    def render_label(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        x, y, w, h = int(e.x), int(e.y), int(e.measured_w), int(e.measured_h)
        color = int(e["color"] or "0")
        text = e["text"] or ""
        Gumps.AddLabelCropped(gd, x, y, w, h, color, text)

    def render_html(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        x, y, w, h = int(e.x), int(e.y), int(e.measured_w), int(e.measured_h)
        text = e.element.text or ""
        bg = parse_bool(e["bg"])
        scrollbar = parse_bool(e["scrollbar"])
        if e["color"]:
            text = f'<BASEFONT COLOR="{e["color"]}">{text}</BASEFONT>'
        if parse_bool(e["centered"]):
            text = f"<CENTER>{text}</CENTER>"
        Gumps.AddHtml(gd, x, y, w, h, text, bg, scrollbar)

    def render_itemimg(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        x, y = int(e.x), int(e.y)
        src = int(e["src"] or "0")
        color = int(e["color"] or "0")
        Gumps.AddItem(gd, x, y, src, color)

    def render_gumpimg(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        x, y = int(e.x), int(e.y)
        src = int(e["src"] or "0")
        color = int(e["color"] or "0")
        Gumps.AddImage(gd, x, y, src, color)

    def render_gumpimgtiled(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        x, y, w, h = int(e.x), int(e.y), int(e.measured_w), int(e.measured_h)
        src = int(e["src"] or "0")
        Gumps.AddImageTiled(gd, x, y, w, h, src)

    def render_textentry(gd: Gumps.GumpData, e: GumpDOMNode) -> None:
        x, y, w, h = int(e.x), int(e.y), int(e.measured_w), int(e.measured_h)
        color = int(e["color"] or "0")
        text = e["text"] or ""
        Gumps.AddBackground(gd, x, y - 2, w, h + 4, 9350)
        Gumps.AddTextEntry(gd, x + 2, y, w - 4, h, color, e.id, text)

    class render_button(GumpStyleElement):
        def test(self, e: GumpDOMNode) -> bool:
            return e["src"] in ["40018", "40019", "40020", "40021", "40297", "40299"]

        def render(self, gd: Gumps.GumpData, e: GumpDOMNode) -> None:
            x, y, w, h = int(e.x), int(e.y), int(e.measured_w), int(e.measured_h)
            src = int(e["src"] or "0")
            text = e["text"] or ""
            if src in [40018, 40019, 40020, 40021]:
                Gumps.AddButton(gd, x, y - 2, src, src + 10, e.id, 1, 0)
            elif src in [40297, 40299]:
                Gumps.AddButton(gd, x, y - 2, src, src + 1, e.id, 1, 0)
            else:
                raise ValueError(f"Unimplemented button source: {src}")
            Gumps.AddHtml(gd, x, y, w, h, f'<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>', False, False)

    class render_checkbox(GumpStyleElement):
        def test(self, e: GumpDOMNode) -> bool:
            return e["src"] == "9026"

        def render(self, gd: Gumps.GumpData, e: GumpDOMNode) -> None:
            x, y = int(e.x), int(e.y)
            checked = parse_bool(e["checked"])
            Gumps.AddCheck(gd, x, y, 9026, 9027, checked, e.id)

    gcss = GumpStyleSheet()
    for tag in ["window", "container", "hbox", "vbox", "hfill", "vfill"]:
        gcss.add_style(tag, GumpStyleElement.wrap(render_container))
    gcss.add_style("label", render_label)
    gcss.add_style("html", render_html)
    gcss.add_style("h", render_html)
    gcss.add_style("itemimg", render_itemimg)
    gcss.add_style("gumpimg", render_gumpimg)
    gcss.add_style("gumpimgtiled", render_gumpimgtiled)
    gcss.add_style("textentry", render_textentry)
    gcss.add_style("button", render_button)
    gcss.add_style("checkbox", render_checkbox)

    return gcss


gump_ss_default = build_gump_ss_default()


def open_confirm(
    msg: str,
    width: int,
    height: int,
    x: Optional[int] = 300,
    y: Optional[int] = 150,
) -> bool:
    dialog_xml = f"""
    <window width="{width}" height="{height}" bg="30546" padding="15" alpha="yes" orientation="vertical">
        <html width="100%" flex="1" margin="0 0 0 15" centered="yes" color="#FFFFFF">{msg}</html>
        <hbox>
            <hfill />
            <button id="yes" text="Yes" src="40018" />
            <button id="no" text="No" src="40018" />
            <hfill />
        </hbox>
    </window>
    """
    root = ET.fromstring(dialog_xml)
    g = GumpDOMParser.parse(root, gump_ss_default)
    g.id = hash(dialog_xml) & 0xFFFFFFFF
    res, _ = g.send_and_listen(300, 200)
    return res == "yes"


def main():
    WINDOW_EXAMPLE = """
    <window width="800" height="600" bg="9270" padding="5">
        <container width="100%" height="100%" bg="3000" spacing="-5">
            <hbox height="50" bg="3500" padding="20 16">
                <label text="Profile:" width="50" />
                <textentry id="profile_name" width="180" text="Default Profile" />
                <button id="profile_rename" text="Rename" src="40018" />
                <button id="profile_load" text="Load" src="40018" />
                <button id="profile_save" text="Save" src="40018" />
            </hbox>
            <hbox flex="1" spacing="-5">
                <vbox width="200" bg="3500" padding="20 12">
                    <h>RULES</h>
                </vbox>
                <vbox flex="1" height="100%" bg="3500" padding="20 12" spacing="10">
                    <h>RULE EDITOR</h>
                    <hbox>
                        <label text="Name:" width="50" />
                        <textentry id="rule_name" width="180" text="Current Rule" />
                        <button id="rule_rename" text="Rename" src="40018" />
                        <button id="rule_load" text="Load" src="40018" />
                        <button id="rule_save" text="Save" src="40018" />
                    </hbox>
                    <hbox spacing="5">
                        <checkbox id="rule_enabled" src="9026" checked="true" />
                        <label text="Enable" width="100" tooltip="When unchecked, the lootmaster will bypass this rule." />
                        <checkbox id="rule_highlight" src="9026" />
                        <label text="Highlight" width="100" tooltip="When checked, the lootmaster will highlight the matched items with a bright shiny color." />
                        <checkbox id="rule_notify" src="9026" />
                        <label text="Notify" width="100" tooltip="When checked, the lootmaster will inform you of the matched items." />
                    </hbox>
                    <vfill />
                    <hbox padding="0 10">
                        <hfill />
                        <button id="rule_apply_chg" text="Apply Change" src="40020" />
                        <button id="rule_discard_chg" text="Discard Change" src="40297" />
                    </hbox>
                </vbox>
            </hbox>
        </container>
    </window>
    """

    root = ET.fromstring(WINDOW_EXAMPLE)
    gump_id = hash(WINDOW_EXAMPLE) & 0xFFFFFFFF

    while True:
        g = GumpDOMParser.parse(root, gump_ss_default)
        g.id = gump_id
        res, iv_map = g.send_and_listen(300, 200)
        if res is None:
            if open_confirm("Are you sure you want to close the window?", 300, 100):
                break


if __name__ == "__main__":
    main()
