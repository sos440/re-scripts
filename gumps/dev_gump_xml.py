import xml.etree.ElementTree as ET
from typing import Any, Optional, Union, Tuple, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uo_runtime.gumps import *


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


class GumpNodeWrapper:
    def __init__(self, element: ET.Element, parent: Optional["GumpNodeWrapper"] = None):
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

        self.parent: Optional["GumpNodeWrapper"] = parent
        self.children: List["GumpNodeWrapper"] = []

        self._init_parse()

    def __getitem__(self, item: str):
        return self.element.attrib.get(item, None)

    def __setitem__(self, item: str, value: Any):
        self.element.attrib[item] = str(value)

    def __repr__(self) -> str:
        return f"GumpNodeWrapper({self.element.tag}, {self.element.attrib})"

    def __iter__(self):
        return iter(self.children)

    def append(self, child: "GumpNodeWrapper"):
        self.children.append(child)
        child.parent = self

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
        if self.element.tag == "h":
            self.width_type = "relative"
            self.width_value = 1.0
            self.height_type = "absolute"
            self.height_value = 18.0
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

        # Sanitize children
        for child in self.element:
            self.append(GumpNodeWrapper(child, self))

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
            return

        # Compute the content size using the children
        fixed_total = self.spacing * (len(self.children) - 1)
        flex_children: List[GumpNodeWrapper] = []
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

    def _layout(self, x: float = 0, y: float = 0):
        self.x = x + self.margin[0]
        self.y = y + self.margin[1]
        if not self.children:
            return

        cx = x + self.padding[0]
        cy = y + self.padding[1]
        for child in self.children:
            child._layout(cx, cy)
            if self.orientation == "vertical":
                cy += child.outer_h + self.spacing
            else:
                cx += child.outer_w + self.spacing

    def render(self, gd=None, id_list: Optional[list] = None):
        """Render the GumpNodeWrapper to a string."""
        if id_list is None:
            id_list = [None]

        if gd is None:
            gd = Gumps.CreateGump(movable=True)
            Gumps.AddPage(gd, 0)

        x, y, w, h = int(self.x), int(self.y), int(self.measured_w), int(self.measured_h)
        color = int(self["color"] or "0")
        text = self["text"] or ""
        src = int(self["src"] or "0")
        bg = int(self["bg"] or "0")

        if self.element.tag == "window" or self.element.tag == "container":
            if self["bg"] is not None:
                Gumps.AddBackground(gd, x, y, w, h, bg)
        elif self.element.tag == "label":
            Gumps.AddLabelCropped(gd, x, y, w, h, color, text)
        elif self.element.tag == "html":
            Gumps.AddHtml(gd, x, y, w, h, self.element.text or "", bool(bg), bool(int(self["scrollbar"] or "0")))
        elif self.element.tag == "h":
            Gumps.AddHtml(gd, x, y, w, h, f"<CENTER>{self.element.text}</CENTER>", False, False)
        elif self.element.tag == "itemimg":
            Gumps.AddItem(gd, x, y, src, color)
        elif self.element.tag == "gumpimg":
            Gumps.AddImage(gd, x, y, src, color)
        elif self.element.tag == "gumpimgtiled":
            Gumps.AddImageTiled(gd, x, y, w, h, src)
        elif self.element.tag == "textentry":
            assert self["id"] is not None, "Text entry must have an ID"
            Gumps.AddBackground(gd, x, y - 2, w, h + 4, 9350)
            Gumps.AddTextEntry(gd, x + 2, y, w - 4, h, color, len(id_list), text)
            id_list.append(self["id"])
        elif self.element.tag == "button":
            assert self["id"] is not None, "Text entry must have an ID"
            if src == 40018:
                Gumps.AddButton(gd, x, y - 2, 40018, 40028, len(id_list), 1, 0)
                Gumps.AddHtml(
                    gd, x, y, w, h, f'<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>', False, False
                )
            id_list.append(self["id"])

        if self["tooltip"] is not None:
            Gumps.AddTooltip(gd, self["tooltip"] or "")

        for child in self:
            child.render(gd, id_list)

        return gd, id_list


def open_gump(
    root: ET.Element,
    gump_id: Optional[int] = None,
    x: int = 200,
    y: int = 200,
) -> Tuple[ET.Element, Optional[str]]:
    gnw = GumpNodeWrapper(root)
    gnw._measure()
    gnw._layout()
    gd, id_list = gnw.render()
    gump_id = gump_id or (hash(gd) & 0xFFFFFFFF)
    Gumps.SendGump(gump_id, Player.Serial, x, y, gd.gumpDefinition, gd.gumpStrings)
    if Gumps.WaitForGump(gump_id, 3600000):
        gd = Gumps.GetGumpData(gump_id)
        id_map = {id_str: id_int for id_int, id_str in enumerate(id_list)}
        # Update the text entries
        textvalue_map = {id_int: text for id_int, text in zip(gd.textID, gd.text)}
        for entry in root.iter("textentry"):
            id = entry.attrib["id"]
            if id in id_map:
                entry.attrib["text"] = textvalue_map[id_map[id]]
    return root, id_list[gd.buttonid]


def open_confirm(
    msg: str,
    width: int,
    height: int,
    x: Optional[int] = 200,
    y: Optional[int] = 200,
) -> bool:
    dialog_xml = f"""
    <window width="{width}" height="{height}" bg="9270" padding="5">
        <container bg="3000" height="100%" padding="10">
            <h>CONFIRMATION</h>
                <container flex="1" />
            <html width="100%" height="18">&lt;center&gt;{msg}&lt;/center&gt;</html>
                <container flex="1" />
            <container width="100%">
                <container flex="1" />
                <button id="yes" text="Yes" src="40018" />
                <button id="no" text="No" src="40018" />
                <container flex="1" />
            </container>
        </container>
    </window>
    """
    root = ET.fromstring(dialog_xml)
    _, button = open_gump(root, hash(dialog_xml) & 0xFFFFFFFF)
    if button == "yes":
        return True
    elif button == "no" or button is None:
        return False
    else:
        raise ValueError(f"Unexpected button ID: {button}")


WINDOW_EXAMPLE = """
<window width="800" height="600" bg="9270" padding="5">
    <container width="100%" height="100%" bg="3000" spacing="-5">
        <container width="100%" height="50" bg="3500" padding="20 16">
            <label text="Profile:" width="50" />
            <textentry id="profile_name" width="180" text="Default Profile" />
            <button id="profile_rename" text="Rename" src="40018" />
            <button id="profile_load" text="Load" src="40018" />
            <button id="profile_save" text="Save" src="40018" />
        </container>
        <container width="100%" flex="1" spacing="-5">
            <container width="200" height="100%" bg="3500" padding="20 12">
                <h>RULES</h>
            </container>
            <container flex="1" height="100%" bg="3500" padding="20 12">
                <h>RULE EDITOR</h>
                <container width="100%" padding="0 10 0 0">
                    <label text="Name:" width="50" />
                    <textentry id="rule_name" width="180" text="Current Rule" />
                    <button id="rule_rename" text="Rename" src="40018" />
                    <button id="rule_load" text="Load" src="40018" />
                    <button id="rule_save" text="Save" src="40018" />
                </container>
                <container width="100%" padding="0 10 0 0">
                    <label text="[v]" width="20" />
                    <label text="Enable" width="100" tooltip="When unchecked, the lootmaster will bypass this rule." />
                    <label text="[v]" width="20" />
                    <label text="Notify" width="100" tooltip="When checked, the lootmaster will inform you of the matched items." />
                </container>
            </container>
        </container>
    </container>
</window>
"""


root = ET.fromstring(WINDOW_EXAMPLE)
while True:
    root, button = open_gump(root, 0x11111111)
    if button is None:
        res = open_confirm("Do you want to exit the editor?", 300, 150)
        if res:
            break
