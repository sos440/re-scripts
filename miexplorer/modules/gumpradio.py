"""
Gumpradio v0.1.0 by sos440

A library for building complex gumps with automatic layout and event handling.
"""

from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from enum import Enum
from typing import List, Optional, Tuple, Dict, Union, Callable, Any


VERSION = "0.1.0"


################################################################################
# Core Classes
################################################################################


class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class HorizontalAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class _Serializable:
    _id: int = -1
    """The unique ID of the block in the gump."""


class _HasText:
    _text: str
    """The text content of the block."""
    _text_index: int = -1
    """The index of the text in the gump's text list."""

    def __init__(self, text: str = ""):
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value


class _Clickable:
    def __init__(self) -> None:
        self.click_handler: Any = None
        self.click_args: "Optional[List[_Block]]" = None

    def on_click(self, handler: Any, args: "Optional[Any]" = None):
        """
        Set the click event handler for the button.

        If `handler` is a callable, it will be called with the provided args when the button is clicked.
        Otherwise, the handler value will be returned as the gump result when clicked.
        """
        self.click_handler = handler
        self.click_args = args
        return self


class _Block:
    parent: Optional["_Container"]
    """The parent container of this block, if any."""
    has_children: bool
    """Whether this block can contain children."""
    dx: int = 0
    """Horizontal offset relative to the computed position."""
    dy: int = 0
    """Vertical offset relative to the computed position."""
    width: Optional[int]
    """The specified width of this block, if fixed."""
    height: Optional[int]
    """The specified height of this block, if fixed."""
    _calc_width: int
    """The calculated width of this block."""
    _calc_height: int
    """The calculated height of this block."""
    _calc_left: int
    """The calculated left position of this block."""
    _calc_top: int
    """The calculated top position of this block."""
    metadata: Dict[str, Any]
    """A dictionary for storing arbitrary metadata associated with the block."""

    def __init__(self, width: Optional[int] = None, height: Optional[int] = None):
        self.parent = None
        self.has_children = False
        self.width = width
        self.height = height
        self._calc_width = self.width or 0
        self._calc_height = self.height or 0
        self._calc_left = 0
        self._calc_top = 0
        self.metadata = {}

    def walk(self):
        """Generator to traverse the block tree."""
        yield self

    def compute_size(self) -> Tuple[int, int]:
        """Compute the size of the block."""
        # For an atomic block, use specified size or default to 0
        self._calc_width = self.width or 0
        self._calc_height = self.height or 0
        return (self._calc_width, self._calc_height)

    def compute_position(self, left: int = 0, top: int = 0):
        """Compute the position of the block. Call this after `compute_size()`."""
        # Nudge the block by (dx, dy)
        self._calc_left = left + self.dx
        self._calc_top = top + self.dy

    def compile(self) -> List[str]:
        """Compile the block into gump commands. Call this after size, position, IDs, and text indices are computed."""
        # Atomic blocks have no default rendering
        return []


class _Spacer(_Block):
    spacing: int
    orientation: Orientation

    def __init__(self, spacing: int = 0, orientation: Orientation = Orientation.HORIZONTAL):
        super().__init__()
        self.spacing = spacing
        self.orientation = orientation

    def compute_size(self) -> Tuple[int, int]:
        # For a spacer, size is determined by spacing and orientation
        if self.orientation == Orientation.HORIZONTAL:
            self._calc_width = self.spacing
            self._calc_height = 0
        else:
            self._calc_width = 0
            self._calc_height = self.spacing
        return (self._calc_width, self._calc_height)


class _Container(_Block):

    children: List[_Block]
    """The child blocks contained within this container."""
    orientation: Orientation
    """The layout orientation of the container."""
    background: str
    """Background style of the container. This can be a combination of the following, separated by semicolons:
        * `frame:[gumpart_id]` - A frame background using the specified gumpart ID. This will draw a framed background using 9 gumparts. This overrides any `tiled` background.
        * `tiled:[gumpart_id]` - A tiled background using the specified gumpart ID. This will repeat to fill the container.
        * `alpha` - A semi-transparent effect.

        Example 1: `"frame:5054"` will draw a framed window background using gumpart ID 5054 through 5062.

        Example 2: `"tiled:2624; alpha"` will draw a semi-transparent tiled background using gumpart ID 2624.
    """
    halign: HorizontalAlign
    """Horizontal alignment of child blocks within the container."""
    valign: VerticalAlign
    """Vertical alignment of child blocks within the container."""
    spacing: int
    """Spacing between child blocks.

    * If the container is horizontal, this adds horizontal spacing between children.
    * If the container is vertical, this adds vertical spacing between children.
    """
    _padding: Tuple[int, int, int, int]
    """Padding around the container's content. Format: (left, top, right, bottom)"""

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        orientation: Orientation = Orientation.HORIZONTAL,
        halign: HorizontalAlign = HorizontalAlign.CENTER,
        valign: VerticalAlign = VerticalAlign.MIDDLE,
        padding: Union[int, Tuple[int, ...]] = 0,
        spacing: int = 0,
        background: str = "",
    ):
        super().__init__(width, height)
        self.has_children = True
        self.children = []
        self.orientation = orientation
        self.halign = halign
        self.valign = valign
        self.padding = padding
        self.spacing = spacing
        self.background = background

    def append(self, block: _Block):
        self.children.append(block)
        block.parent = self

    def remove(self, block: _Block):
        self.children.remove(block)
        block.parent = None

    @property
    def padding(self) -> Tuple[int, int, int, int]:
        """Padding around the container's content.

        You can set the padding using either an integer or a tuple of integers
        of the form (horizontal, vertical) or (left, top, right, bottom)."""
        return self._padding

    @padding.setter
    def padding(self, value: Union[int, Tuple[int, ...]]):
        if isinstance(value, int):
            self._padding = (value, value, value, value)
        elif isinstance(value, tuple):
            if len(value) == 0:
                self._padding = (0, 0, 0, 0)
            elif len(value) == 1:
                self._padding = (value[0], value[0], value[0], value[0])
            elif len(value) == 2:
                self._padding = (value[0], value[1], value[0], value[1])
            elif len(value) == 3:
                self._padding = (value[0], value[1], value[2], value[1])
            elif len(value) == 4:
                self._padding = value
            else:
                raise ValueError("Padding must be an int or a tuple of 2, 3, or 4 ints.")
        else:
            raise ValueError("Padding must be an int or a tuple of 2, 3, or 4 ints.")

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def compute_size(self) -> Tuple[int, int]:
        # Compute size based on children and orientation
        self._calc_width = 0
        self._calc_height = 0
        if self.orientation == Orientation.HORIZONTAL:
            # If horizontal, stack widths, take max height
            for i, child in enumerate(self.children):
                cw, ch = child.compute_size()
                self._calc_width += cw + (self.spacing if i > 0 else 0)
                self._calc_height = max(self._calc_height, ch)
        elif self.orientation == Orientation.VERTICAL:
            # If vertical, stack heights, take max width
            for i, child in enumerate(self.children):
                cw, ch = child.compute_size()
                self._calc_width = max(self._calc_width, cw)
                self._calc_height += ch + (self.spacing if i > 0 else 0)
        else:
            raise ValueError("Invalid orientation")
        # Add padding
        self._calc_width += self._padding[0] + self._padding[2]
        self._calc_height += self._padding[1] + self._padding[3]
        # Override with fixed size if specified
        if self.width is not None:
            self._calc_width = self.width
        if self.height is not None:
            self._calc_height = self.height
        # Propagate size to child containers if they are set to auto-size
        inner_width = self._calc_width - self._padding[0] - self._padding[2]
        inner_height = self._calc_height - self._padding[1] - self._padding[3]
        for child in self.children:
            if not isinstance(child, _Container):
                continue
            if child.height is None and self.orientation == Orientation.HORIZONTAL:
                # Stretch child height to fit container's inner height
                child._calc_height = inner_height
            elif child.width is None and self.orientation == Orientation.VERTICAL:
                # Stretch child width to fit container's inner width
                child._calc_width = inner_width
        return (self._calc_width, self._calc_height)

    def compute_position(self, left: int = 0, top: int = 0):
        # Nudge the container itself by (dx, dy)
        self._calc_left = left + self.dx
        self._calc_top = top + self.dy
        # Position children within the container
        current_left = left + self._padding[0]
        current_top = top + self._padding[1]
        if self.orientation == Orientation.HORIZONTAL:
            for child in self.children:
                # Calculate vertical alignment
                gap = self._calc_height - self._padding[1] - self._padding[3] - child._calc_height
                if self.valign == VerticalAlign.TOP:
                    ct = current_top
                elif self.valign == VerticalAlign.MIDDLE:
                    ct = current_top + gap // 2
                elif self.valign == VerticalAlign.BOTTOM:
                    ct = current_top + gap
                else:
                    raise ValueError("Invalid vertical alignment")
                child.compute_position(current_left, ct)
                current_left += child._calc_width + self.spacing
        elif self.orientation == Orientation.VERTICAL:
            for child in self.children:
                # Calculate horizontal alignment
                gap = self._calc_width - self._padding[0] - self._padding[2] - child._calc_width
                if self.halign == HorizontalAlign.LEFT:
                    cl = current_left
                elif self.halign == HorizontalAlign.CENTER:
                    cl = current_left + gap // 2
                elif self.halign == HorizontalAlign.RIGHT:
                    cl = current_left + gap
                else:
                    raise ValueError("Invalid horizontal alignment")
                child.compute_position(cl, current_top)
                current_top += child._calc_height + self.spacing
        else:
            raise ValueError("Invalid orientation")

    def compile(self) -> List[str]:
        if not self.background:
            return []
        # Parse background string
        cmds_bg = []
        cmds_alpha = []
        bg_parts = self.background.split(";")
        for part in bg_parts:
            part = part.strip().replace(r"\s+", "").lower()
            if part.startswith("frame:"):
                gumpart_id = int(part.split(":")[1])
                cmds_bg.append(f"resizepic {self._calc_left} {self._calc_top} {gumpart_id} {self._calc_width} {self._calc_height}")
            elif part.startswith("tiled:"):
                gumpart_id = int(part.split(":")[1])
                cmds_bg.append(f"gumppictiled {self._calc_left} {self._calc_top} {self._calc_width} {self._calc_height} {gumpart_id}")
            elif part == "alpha":
                cmds_alpha.append(f"checkertrans {self._calc_left} {self._calc_top} {self._calc_width} {self._calc_height}")
        # Alpha must be last
        return cmds_bg + cmds_alpha

    def clear_children(self):
        """
        Clear all child elements from the container.
        """
        for child in self.children:
            child.parent = None
        self.children = []


class _Root(_Container, _Serializable, _Clickable):
    def __init__(self):
        _Container.__init__(self)
        _Serializable.__init__(self)
        _Clickable.__init__(self)

    def compile(self) -> List[str]:
        # Root has no direct rendering
        return []


class _InteractiveBlock(_Block):
    tooltip: Optional[str] = None
    """Tooltip text to display when hovering over the block. This precedes itemproperty."""
    itemproperty: Optional[int] = None
    """ID of the item of which properties to show when hovering over the block."""

    # Blocks that has graphics and/or interactive features
    def __init__(self, width: int, height: int, tooltip: Optional[str] = None, itemproperty: Optional[int] = None):
        super().__init__(width, height)
        self.tooltip = tooltip
        self.itemproperty = itemproperty

    def compile(self) -> List[str]:
        cmds = []
        if self.tooltip:
            cmds.append(f"tooltip 1114778 @{self.tooltip}@")
        elif self.itemproperty is not None and self.itemproperty != -1:
            cmds.append(f"itemproperty {self.itemproperty}")
        return cmds


class _Text(_InteractiveBlock, _HasText):
    hue: int
    """The 0-based color hue of the text. -1 for default color."""
    cropped: bool
    """Whether the text should be cropped if it exceeds the width."""

    def __init__(
        self,
        text: str = "",
        hue: int = -1,
        width: Optional[int] = None,
        cropped: bool = False,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Represents a text block in the gump.
        """
        if width is None:
            width = 11 * len(text)
        _InteractiveBlock.__init__(self, width, 18, tooltip, itemproperty)
        _HasText.__init__(self, text)
        self.hue = hue
        self.cropped = cropped

    def compile(self) -> List[str]:
        if self._text_index == -1:
            return []
        cmds = []
        if self.cropped:
            cmds.append(f"croppedtext {self._calc_left} {self._calc_top} {self.width} {self.height} {self.hue} {self._text_index}")
        else:
            cmds.append(f"text {self._calc_left} {self._calc_top} {self.hue} {self._text_index}")
        # Add tooltip and itemproperty if any
        cmds.extend(_InteractiveBlock.compile(self))
        return cmds


class _GumpArt(_InteractiveBlock):
    graphics: int
    """The gumpart ID to display."""
    hue: int
    """The 1-based hue to apply to the gumpart. 0 for default color."""

    def __init__(
        self,
        graphics: int = 0,
        width: int = 100,
        height: int = 100,
        hue: int = 0,
        tiled: bool = False,
        crop: Optional[Tuple[int, int]] = None,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Represents a gumpart block in the gump.
        """
        _InteractiveBlock.__init__(self, width, height, tooltip, itemproperty)
        self.graphics = graphics
        self.hue = hue
        self.tiled = tiled
        self.crop = crop

    def compile(self) -> List[str]:
        if self.crop is not None:
            if self.hue == 0:
                cmds = [f"picinpic {self._calc_left} {self._calc_top} {self.graphics} {self.crop[0]} {self.crop[1]} {self._calc_width} {self._calc_height}"]
            else:
                cmds = [f"picinpichue {self._calc_left} {self._calc_top} {self.graphics} {self.crop[0]} {self.crop[1]} {self._calc_width} {self._calc_height} {self.hue}"]
        elif self.tiled:
            cmds = [f"gumppictiled {self._calc_left} {self._calc_top} {self._calc_width} {self._calc_height} {self.graphics}"]
        elif self.hue == 0:
            cmds = [f"gumppic {self._calc_left} {self._calc_top} {self.graphics}"]
        else:
            cmds = [f"gumppichued {self._calc_left} {self._calc_top} {self.graphics} {self.hue}"]
        # Add tooltip and itemproperty if any
        cmds.extend(_InteractiveBlock.compile(self))
        return cmds


class _TileArt(_InteractiveBlock):
    RECT_CACHE: Dict[int, Tuple[int, int, int, int]] = {}

    graphics: int
    """The tileart ID to display."""
    hue: int
    """The 1-based hue to apply to the tileart. 0 for default color."""

    def __init__(
        self,
        graphics: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        hue: int = 0,
        centered: bool = False,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Represents an item (tileart) block in the gump.
        """
        img = Items.GetImage(graphics, 0)
        if width is None:
            width = img.Width if img else 44
        if height is None:
            height = img.Height if img else 44
        _InteractiveBlock.__init__(self, width, height, tooltip, itemproperty)
        self.centered = centered
        self.graphics = graphics
        self.hue = hue

    def compile(self) -> List[str]:
        if self.hue == 0:
            cmds = [f"tilepic {self._calc_left} {self._calc_top} {self.graphics}"]
        else:
            cmds = [f"tilepichue {self._calc_left} {self._calc_top} {self.graphics} {self.hue}"]
        # Add tooltip and itemproperty if any
        cmds.extend(_InteractiveBlock.compile(self))
        return cmds

    def compute_position(self, left: int = 0, top: int = 0):
        super().compute_position(left, top)
        if self.centered:
            rect = self.get_rect(self.graphics)
            cx = self._calc_left + (self._calc_width // 2)
            cy = self._calc_top + (self._calc_height // 2)
            self._calc_left = cx - (rect[2] + rect[0]) // 2
            self._calc_top = cy - (rect[3] + rect[1]) // 2

    @staticmethod
    def get_rect(graphics: int) -> Tuple[int, int, int, int]:
        if graphics not in _TileArt.RECT_CACHE:
            bitmap = Items.GetImage(graphics, 0)
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
            _TileArt.RECT_CACHE[graphics] = (left, top, right, bottom)
        return _TileArt.RECT_CACHE[graphics]


class _Button(_InteractiveBlock, _Serializable, _Clickable):
    up: int
    """The gumpart ID for the button's up state."""
    down: int
    """The gumpart ID for the button's down state."""
    tileart: Optional[_TileArt]
    """Optional tileart to display on the button."""

    def __init__(
        self,
        width: int = 30,
        height: int = 22,
        up: int = 4005,
        down: int = 4007,
        tileart: Optional[_TileArt] = None,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Represents a button block in the gump. This button always submits response.
        (Page navigation is only used for internal gump logic and is not exposed here.)
        """
        _InteractiveBlock.__init__(self, width, height, tooltip, itemproperty)
        _Clickable.__init__(self)
        self.up = up
        self.down = down
        self.tileart = tileart

    def compile(self) -> List[str]:
        if self.tileart is None:
            cmds = [f"button {self._calc_left} {self._calc_top} {self.up} {self.down} 1 0 {self._id}"]
        else:
            if self.width is not None:
                self.tileart._calc_width = self.width
            if self.height is not None:
                self.tileart._calc_height = self.height
            self.tileart.compute_position(0, 0)
            cmds = [f"buttontileart {self._calc_left} {self._calc_top} {self.up} {self.down} 1 0 {self._id} {self.tileart.graphics} {self.tileart.hue} {self.tileart._calc_left} {self.tileart._calc_top}"]
        # Add tooltip and itemproperty if any
        cmds.extend(_InteractiveBlock.compile(self))
        return cmds

    def add_tileart(self, graphics: int, hue: int = 0, centered: bool = True) -> "_Button":
        self.tileart = _TileArt(graphics=graphics, width=self.width, height=self.height, hue=hue, centered=centered)
        return self


class _Checkbox(_Button):
    def __init__(
        self,
        width: int = 30,
        height: int = 22,
        up: int = 4005,
        down: int = 4007,
        checked: bool = False,
        tileart: Optional[_TileArt] = None,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        _Button.__init__(self, width, height, up, down, tileart, tooltip, itemproperty)
        self.checked = checked

    def compile(self) -> List[str]:
        if self.checked:
            self.up, self.down = self.down, self.up
        cmds = super().compile()
        if self.checked:
            self.up, self.down = self.down, self.up
        return cmds


class _Html(_InteractiveBlock, _HasText):
    def __init__(
        self,
        text: str = "",
        width: int = 300,
        height: int = 22,
        color: Optional[str] = None,
        centered: bool = False,
        background: bool = False,
        scrollbar: int = 0,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Represents an HTML block in the gump.
        """
        _InteractiveBlock.__init__(self, width, height, tooltip, itemproperty)
        _HasText.__init__(self, text)
        self.color = color
        self.centered = centered
        self.background = background
        self.scrollbar = scrollbar

    @property
    def text(self) -> str:
        text = self._text
        if self.color is not None:
            text = f"<basefont color={self.color}>{text}</basefont>"
        if self.centered:
            text = f"<center>{text}</center>"
        return text

    @text.setter
    def text(self, value: str):
        self._text = value

    def compile(self) -> List[str]:
        if self._text_index == -1:
            return []
        bg_flag = 1 if self.background else 0
        return [f"htmlgump {self._calc_left} {self._calc_top} {self.width} {self.height} {self._text_index} {bg_flag} {self.scrollbar}"]


class _TextEntry(_InteractiveBlock, _HasText, _Serializable):
    hue: int
    """The 0-based color hue of the text. -1 for default color."""
    max_length: int
    """The maximum length of text that can be entered. -1 for unlimited."""

    def __init__(
        self,
        text: str = "",
        width: Optional[int] = None,
        hue: int = -1,
        max_length: int = -1,
        tooltip: str = "",
        itemproperty: int = -1,
    ):
        if width is None:
            width = 11 * max(len(text), max_length)
        _InteractiveBlock.__init__(self, width, 18, tooltip, itemproperty)
        _HasText.__init__(self, text)
        self.hue = hue
        self.max_length = max_length

    def compile(self) -> List[str]:
        if self._text_index == -1:
            return []
        if self.max_length == -1:
            cmds = [f"textentry {self._calc_left} {self._calc_top} {self.width} {self.height} {self.hue} {self._id} {self._text_index}"]
        else:
            cmds = [f"textentry {self._calc_left} {self._calc_top} {self.width} {self.height} {self.hue} {self._id} {self._text_index} {self.max_length}"]
        # Add tooltip and itemproperty if any
        cmds.extend(_InteractiveBlock.compile(self))
        return cmds


################################################################################
# Public API
################################################################################


class GumpBuilder(_Clickable):
    class Assets:
        # Protocols
        Serializable = _Serializable
        HasText = _HasText
        Clickable = _Clickable
        # Blocks
        Block = _Block
        Spacer = _Spacer
        Container = _Container
        Root = _Root
        Text = _Text
        GumpArt = _GumpArt
        TileArt = _TileArt
        Button = _Button
        Checkbox = _Checkbox
        Html = _Html
        TextEntry = _TextEntry

    class Scope:
        def __init__(self, builder: "GumpBuilder", block: _Container):
            self.builder = builder
            self.block = block

        def __enter__(self):
            self.builder.current.append(self.block)
            self.builder.current = self.block
            return self.block

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.builder.current = self.block.parent if self.block.parent else self.builder.root

    def __init__(self, movable: bool = True, closable: bool = True, disposable: bool = True, id: Optional[Any] = None):
        """
        Initialize a new Gump instance.

        :param movable: Whether the gump can be moved by the user.
        :param closable: Whether the gump can be closed with right-click by the user.
        :param disposable: Whether the gump can be closed with ESC by the user.
        :param id: An optional ID for the gump.
        """

        self.movable: bool = movable
        """Whether the gump can be moved by the user."""
        self.closable: bool = closable
        """Whether the gump can be closed with right-click by the user."""
        self.disposable: bool = disposable
        """Whether the gump can be closed with ESC by the user."""

        if isinstance(id, int) and 0 <= id <= 0xFFFFFFFF:
            self.id: int = id
        elif id is not None:
            self.id: int = hash(id) & 0xFFFFFFFF
        else:
            self.id: int = hash(self) & 0xFFFFFFFF

        self.root: _Root = _Root()
        self.current: _Container = self.root

    def on_exit(self, handler: Callable, args: "Optional[List[_Block]]" = None):
        """
        Set the exit event handler for the gump.
        """
        self.root.click_handler = handler
        self.root.click_args = args
        return self

    def Row(
        self,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        halign: Union[HorizontalAlign, str] = HorizontalAlign.CENTER,
        valign: Union[VerticalAlign, str] = VerticalAlign.MIDDLE,
        padding: Union[int, Tuple[int, ...]] = 0,
        spacing: int = 0,
        background: str = "",
    ):
        """
        Add a horizontal container to the gump.
        Children added within the context will be laid out horizontally.

        :param width: The width of the container in pixels. If None, it will be calculated based on children.
        :param height: The height of the container in pixels. If None, it will be calculated based on children.
        :param halign: Horizontal alignment of child blocks within the container.
        :param valign: Vertical alignment of child blocks within the container.
        :param padding: Padding around the container's content. Can be an int or a tuple of 2, 3, or 4 ints.
        :param background: Background style of the container. See `_Container.background` for details.
        """
        return self.Scope(
            self,
            _Container(
                width=width,
                height=height,
                orientation=Orientation.HORIZONTAL,
                halign=halign if isinstance(halign, HorizontalAlign) else HorizontalAlign(halign),
                valign=valign if isinstance(valign, VerticalAlign) else VerticalAlign(valign),
                padding=padding,
                spacing=spacing,
                background=background,
            ),
        )

    def Column(
        self,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        halign: Union[HorizontalAlign, str] = HorizontalAlign.CENTER,
        valign: Union[VerticalAlign, str] = VerticalAlign.MIDDLE,
        padding: Union[int, Tuple[int, ...]] = 0,
        spacing: int = 0,
        background: str = "",
    ):
        """
        Add a vertical container to the gump.
        Children added within the context will be laid out vertically.

        :param width: The width of the container in pixels. If None, it will be calculated based on children.
        :param height: The height of the container in pixels. If None, it will be calculated based on children.
        :param halign: Horizontal alignment of child blocks within the container.
        :param valign: Vertical alignment of child blocks within the container.
        :param padding: Padding around the container's content. Can be an int or a tuple of 2, 3, or 4 ints.
        :param background: Background style of the container. See `_Container.background` for details.
        """
        return self.Scope(
            self,
            _Container(
                width=width,
                height=height,
                orientation=Orientation.VERTICAL,
                halign=halign if isinstance(halign, HorizontalAlign) else HorizontalAlign(halign),
                valign=valign if isinstance(valign, VerticalAlign) else VerticalAlign(valign),
                padding=padding,
                spacing=spacing,
                background=background,
            ),
        )

    def Spacer(self, spacing: int = 0, orientation: Optional[Orientation] = None):
        """
        Add a spacer block to the gump. This is an invisible block that takes up space.

        :param spacing: The amount of space in pixels.
        :param orientation: The orientation of the spacer. If None, uses the current container's orientation.
        """
        block = _Spacer(spacing, orientation or self.current.orientation)
        self.current.append(block)
        return block

    def GumpArt(
        self,
        graphics: int = 0,
        width: int = 100,
        height: int = 100,
        hue: int = 0,
        tiled: bool = False,
        crop: Optional[Tuple[int, int]] = None,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Add a gumpart (graphic) block to the gump.

        :param graphics: The gumpart ID to display.
        :param width: The width of the gumpart block in pixels.
        :param height: The height of the gumpart block in pixels.
        :param hue: The 1-based hue to apply to the gumpart. 0 for default color.
        :param tiled: Whether to tile the gumpart to fill the block area.
        :param tooltip: Tooltip text to display when hovering over the gumpart block.
        :param itemproperty: Optional item property ID for the gumpart block.
        """
        block = _GumpArt(graphics, width, height, hue, tiled, crop, tooltip, itemproperty)
        self.current.append(block)
        return block

    def TileArt(
        self,
        graphics: int = 0,
        width: int = 44,
        height: int = 44,
        hue: int = 0,
        centered: bool = False,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Add a tileart (item) block to the gump.

        :param graphics: The tileart ID to display.
        :param width: The width of the tileart block in pixels. If None, it will be calculated based on the item's image.
        :param height: The height of the tileart block in pixels. If None, it will be calculated based on the item's image.
        :param hue: The 1-based hue to apply to the tileart. 0 for default color.
        :param centered: Whether to center the tileart within the block.
        :param tooltip: Tooltip text to display when hovering over the tileart block.
        :param itemproperty: ID of the item of which properties to show when hovering over the tileart block.
        :return: The created TileArt block.
        """
        block = _TileArt(graphics, width, height, hue, centered, tooltip, itemproperty)
        self.current.append(block)
        return block

    def Text(
        self,
        text: str = "",
        hue: int = -1,
        width: Optional[int] = None,
        cropped: bool = False,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Add a text block to the gump.

        :param text: The text content to display.
        :param hue: The 0-based color hue of the text. -1 for default color.
        :param width: The width of the text block in pixels. If None, it will be calculated based on text length.
        :param cropped: Whether the text should be cropped if it exceeds the width.
        :param tooltip: Tooltip text to display when hovering over the text block.
        :param itemproperty: ID of the item of which properties to show when hovering over the text block.
        :return: The created Text block.
        """
        block = _Text(text, hue, width, cropped, tooltip, itemproperty)
        self.current.append(block)
        return block

    def Button(
        self,
        width: int = 30,
        height: int = 22,
        up: int = 4005,
        down: int = 4007,
        tileart: Optional[_TileArt] = None,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Add a button to the gump.

        :param width: The width of the button in pixels.
        :param height: The height of the button in pixels.
        :param up: The gumpart ID for the button's up state.
        :param down: The gumpart ID for the button's down state.
        :param tileart: Optional tileart to display on the button.
        :param tooltip: Tooltip text to display when hovering over the button.
        :param itemproperty: ID of the item of which properties to show when hovering over the button.
        :return: The created Button block.
        """
        block = _Button(width, height, up, down, tileart, tooltip, itemproperty)
        self.current.append(block)
        return block

    def Checkbox(
        self,
        width: int = 19,
        height: int = 20,
        up: int = 210,
        down: int = 211,
        checked: bool = False,
        tileart: Optional[_TileArt] = None,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Add a checkbox to the gump.

        :param width: The width of the checkbox in pixels.
        :param height: The height of the checkbox in pixels.
        :param up: The gumpart ID for the checkbox's up state.
        :param down: The gumpart ID for the checkbox's down state.
        :param checked: Initial checked state of the checkbox.
        :param tileart: Optional tileart to display on the checkbox.
        :param tooltip: Tooltip text to display when hovering over the checkbox.
        :param itemproperty: ID of the item of which properties to show when hovering over the checkbox.
        :return: The created Checkbox block.
        """
        block = _Checkbox(width, height, up, down, checked, tileart, tooltip, itemproperty)
        self.current.append(block)
        return block

    def Html(
        self,
        text: str = "",
        width: int = 300,
        height: int = 22,
        color: Optional[str] = None,
        centered: bool = False,
        background: bool = False,
        scrollbar: int = 0,
        tooltip: Optional[str] = None,
        itemproperty: Optional[int] = None,
    ):
        """
        Add an HTML block to the gump.

        :param text: The HTML content to display.
        :param width: The width of the HTML block in pixels.
        :param height: The height of the HTML block in pixels.
        :param color: The RGB color of the text as a #RRGGBB string. None for default color.
        :param centered: Whether to center the text horizontally.
        :param background: Whether to draw a background behind the HTML block.
        :param scrollbar: The scrollbar mode. 0 = none, 1 = normal, 2 = flag
        """
        block = _Html(text, width, height, color, centered, background, scrollbar, tooltip, itemproperty)
        self.current.append(block)
        return block

    def TextEntry(
        self,
        text: str = "",
        width: Optional[int] = None,
        hue: int = -1,
        max_length: int = -1,
        tooltip: str = "",
        itemproperty: int = -1,
    ):
        """
        Add a text entry field to the gump.

        :param text: The initial text content of the entry field.
        :param width: The width of the entry field in pixels. If None, it will be calculated based on text and max_length.
        :param hue: The 0-based color hue of the text. -1 for default color.
        :param max_length: The maximum length of text that can be entered. -1 for unlimited.
        :param tooltip: Tooltip text to display when hovering over the entry field.
        :param itemproperty: ID of the item of which properties to show when hovering over the entry field.
        :return: The created TextEntry block.
        """
        block = _TextEntry(text, width, hue, max_length, tooltip, itemproperty)
        self.current.append(block)
        return block

    def launch(self, response: bool = True, timeout: int = 3600000) -> Tuple[Optional[_Block], Any]:
        """
        Launch the gump and process the response.

        :param response: Whether to wait for and process a response from the user.
        :param timeout: Timeout in milliseconds to wait for a response. Default is 1 hour.
        :return: A tuple of (clicked block, handler result) if a clickable block was activated, else (None, None).
        """
        # Compute sizes
        self.root.compute_size()
        # Compute positions
        self.root.compute_position(0, 0)
        # Assign IDs and text indices
        current_id = 1
        serialized: Dict[int, _Block] = {0: self.root}  # ID 0 is reserved for root
        texts: List[str] = []
        texts_inv: Dict[str, int] = {}
        for block in self.root.walk():
            if isinstance(block, _Serializable):
                block._id = current_id
                serialized[current_id] = block
                current_id += 1
            if isinstance(block, _HasText):
                if block.text:
                    if block.text in texts_inv:
                        block._text_index = texts_inv[block.text]
                        continue
                    block._text_index = len(texts_inv)
                    texts.append(block.text)
                    texts_inv[block.text] = block._text_index
                else:
                    block._text_index = -1
        # Compile commands
        cmds: List[str] = []
        if not self.movable:
            cmds.append("nomove")
        if not self.closable:
            cmds.append("noclose")
        if not self.disposable:
            cmds.append("nodispose")

        cmds.append("page 0")
        for block in self.root.walk():
            cmds.extend(block.compile())
        cmds_body = "".join(f"{{ {cmd} }}" for cmd in cmds)

        Gumps.SendGump(self.id, Player.Serial, 100, 100, cmds_body, CList[str](texts))

        # Process the response
        if not response:
            return None, None
        if not Gumps.WaitForGump(self.id, timeout):
            return None, None
        gd = Gumps.GetGumpData(self.id)
        if gd is None:
            return None, None

        # Update text fields
        for i, text_index in enumerate(gd.textID):
            if text_index not in serialized:
                continue
            block = serialized[text_index]
            if isinstance(block, _HasText):
                block.text = gd.text[i]

        # Handle button clicks
        if gd.buttonid in serialized:
            block = serialized[gd.buttonid]
            if isinstance(block, _Checkbox):
                block.checked = not block.checked
            if isinstance(block, _Clickable):
                if isinstance(block.click_handler, Callable):
                    return block, block.click_handler(*(block.click_args or []))
                return block, block.click_handler

        return None, None


__export__ = [
    "Orientation",
    "HorizontalAlign",
    "VerticalAlign",
    "GumpBuilder",
]
