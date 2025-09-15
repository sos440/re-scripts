from AutoComplete import *
from enum import Enum
from typing import List, Optional, Tuple, Union, Callable


def _gb():
    """Namespace for gump builder related classes and functions."""

    class Orientation(Enum):
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"

    class Serializable:
        _id: int = -1
        """The unique ID of the block in the gump."""

    class HasText:
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

    class Block:
        parent: Optional["Container"]
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

        def __init__(self):
            self.parent = None
            self.has_children = False
            self._calc_width = self.width or 0
            self._calc_height = self.height or 0
            self._calc_left = 0
            self._calc_top = 0

        def walk(self):
            """Generator to traverse the block tree."""
            yield self

        def compute_size(self) -> Tuple[int, int]:
            """Compute the size of the block."""
            self._calc_width = self.width or 0
            self._calc_height = self.height or 0
            return (self._calc_width, self._calc_height)

        def compute_position(self, left: int = 0, top: int = 0):
            """Compute the position of the block. Call this after `compute_size()`."""
            self._calc_left = left + self.dx
            self._calc_top = top + self.dy

        def compile(self) -> List[str]:
            """Compile the block into gump commands. Call this after size, position, IDs, and text indices are computed."""
            return []

    class Spacer(Block):
        spacing: int
        orientation: Orientation

        def __init__(self, spacing: int = 0, orientation: Orientation = Orientation.HORIZONTAL):
            super().__init__()
            self.spacing = spacing
            self.orientation = orientation

        def compute_size(self) -> Tuple[int, int]:
            if self.orientation == Orientation.HORIZONTAL:
                self._calc_width = self.spacing
                self._calc_height = 0
            else:
                self._calc_width = 0
                self._calc_height = self.spacing
            return (self._calc_width, self._calc_height)

    class HorizontalSpacer(Spacer):
        def __init__(self, spacing: int = 0):
            super().__init__(spacing, Orientation.HORIZONTAL)

    class VerticalSpacer(Spacer):
        def __init__(self, spacing: int = 0):
            super().__init__(spacing, Orientation.VERTICAL)

    class Container(Block):

        children: List[Block]
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
        _padding: Tuple[int, int, int, int]
        """Padding around the container's content. Format: (left, top, right, bottom)"""

        def __init__(self):
            super().__init__()
            self.has_children = True
            self.children = []
            self.orientation = Orientation.HORIZONTAL
            self.padding = 0

        def append(self, block: Block):
            self.children.append(block)
            block.parent = self

        def remove(self, block: Block):
            self.children.remove(block)
            block.parent = None

        @property
        def padding(self) -> Tuple[int, int, int, int]:
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
            if self.width is not None and self.height is not None:
                return (self.width, self.height)

            self._calc_width = self._padding[0] + self._padding[2]
            self._calc_height = self._padding[1] + self._padding[3]
            if self.orientation == Orientation.HORIZONTAL:
                for child in self.children:
                    cw, ch = child.compute_size()
                    self._calc_width += cw
                    self._calc_height = max(self._calc_height, ch)
            elif self.orientation == Orientation.VERTICAL:
                for child in self.children:
                    cw, ch = child.compute_size()
                    self._calc_width = max(self._calc_width, cw)
                    self._calc_height += ch
            else:
                raise ValueError("Invalid orientation")
            if self.width is not None:
                self._calc_width = self.width
            if self.height is not None:
                self._calc_height = self.height
            return (self._calc_width, self._calc_height)

        def compute_position(self, left: int = 0, top: int = 0):
            self._calc_left = left + self.dx
            self._calc_top = top + self.dy
            current_left = left + self._padding[0]
            current_top = top + self._padding[1]
            if self.orientation == Orientation.HORIZONTAL:
                for child in self.children:
                    child.compute_position(current_left, current_top)  # TODO: implement alignment
                    current_left += child._calc_width
            elif self.orientation == Orientation.VERTICAL:
                for child in self.children:
                    child.compute_position(current_left, current_top)  # TODO: implement alignment
                    current_top += child._calc_height
            else:
                raise ValueError("Invalid orientation")

        def compile(self) -> List[str]:
            if not self.background:
                return []

            commands = []
            bg_parts = self.background.split(";")
            for part in bg_parts:
                part = part.strip().replace(r"\s+", "")
                if part.startswith("frame:"):
                    gumpart_id = int(part.split(":")[1])
                    commands.append(f"resizepic {self._calc_left} {self._calc_top} {gumpart_id} {self._calc_width} {self._calc_height}")
                elif part.startswith("tiled:"):
                    gumpart_id = int(part.split(":")[1])
                    commands.append(f"tilepic {self._calc_left} {self._calc_top} {self._calc_width} {self._calc_height} {gumpart_id}")
                elif part == "alpha":
                    commands.append(f"alpha {self._calc_left} {self._calc_top} {self._calc_width} {self._calc_height}")

            return commands

    class Row(Container):
        def __init__(self):
            super().__init__()

    class Column(Container):
        def __init__(self):
            super().__init__()
            self.orientation = Orientation.VERTICAL

    class InteractiveBlock(Block):
        def __init__(self, tooltip: str = "", itemproperty: int = -1):
            super().__init__()
            self.tooltip = tooltip
            self.itemproperty = itemproperty

    class Text(InteractiveBlock, HasText):
        def __init__(
            self,
            text: str = "",
            hue: int = -1,
            width: int = 100,
            cropped: bool = False,
            tooltip: str = "",
            itemproperty: int = -1,
        ):
            """
            Represents a text block in the gump.

            Args:
                text (str): The text content to display.
                hue (int): The color hue of the text. -1 for default color.
                width (int): The width of the text block.
                cropped (bool): Whether the text should be cropped if it exceeds the width.
            """
            super().__init__(tooltip, itemproperty)
            HasText.__init__(self, text)
            self.hue = hue
            self.width = width
            self.height = 22
            self.cropped = cropped

        def compile(self) -> List[str]:
            if self._text_index == -1:
                return []
            if self.cropped:
                return [f"croppedtext {self._calc_left} {self._calc_top} {self.width} {self.height} {self.hue} {self._text_index}"]
            return [f"text {self._calc_left} {self._calc_top} {self.hue} {self._text_index}"]

    class Button(InteractiveBlock, Serializable, HasText):
        def __init__(
            self,
            text: str = "",
            width: int = 100,
            height: int = 100,
            hue: int = -1,
            tooltip: str = "",
            itemproperty: int = -1,
        ):
            super().__init__(tooltip, itemproperty)
            HasText.__init__(self, text)
            self.width = width
            self.height = height
            self.hue = hue
            self.click_handler: Optional[Callable] = None
            self.click_args: Optional[List[Block]] = None

        def click(self, handler: Callable, args: List[Block]):
            self.click_handler = handler
            self.click_args = args

    class Html(InteractiveBlock, HasText):
        def __init__(
            self,
            text: str = "",
            width: int = 300,
            height: int = 200,
            color: Optional[int] = None,
            centered: bool = False,
            background: bool = False,
            scrollbar: int = 0,
            tooltip: str = "",
            itemproperty: int = -1,
        ):
            super().__init__(tooltip, itemproperty)
            HasText.__init__(self, text)
            self.width = width
            self.height = height
            self.color = color
            self.centered = centered
            self.background = background
            self.scrollbar = scrollbar

        @property
        def text(self) -> str:
            text = self.text
            if self.color is not None:
                text = f'<basefont color="#{self.color:06X}">{text}</basefont>'
            if self.centered:
                text = f"<center>{text}</center>"
            return text

        @text.setter
        def text(self, value: str):
            self._text = value

        def complile(self) -> List[str]:
            if self._text_index == -1:
                return []
            bg_flag = 1 if self.background else 0
            return [f"html {self._calc_left} {self._calc_top} {self.width} {self.height} {self._text_index} {bg_flag} {self.scrollbar}"]

    class TextEntry(InteractiveBlock, HasText, Serializable):
        def __init__(
            self,
            text: str = "",
            width: int = 200,
            height: int = 22,
            hue: int = -1,
            max_length: int = -1,
            tooltip: str = "",
            itemproperty: int = -1,
        ):
            super().__init__(tooltip, itemproperty)
            HasText.__init__(self, text)
            self.width = width
            self.height = height
            self.hue = hue
            self.max_length = max_length

        def compile(self) -> List[str]:
            if self._text_index == -1:
                return []
            if self.max_length == -1:
                return [f"textentry {self._calc_left} {self._calc_top} {self.width} {self.height} {self.hue} {self._id} {self._text_index}"]
            return [f"textentry {self._calc_left} {self._calc_top} {self.width} {self.height} {self.hue} {self._id} {self._text_index} {self.max_length}"]

    class GumpArt(InteractiveBlock): ...

    class TileArt(InteractiveBlock): ...

    class Radio(InteractiveBlock, Serializable): ...

    class Checkbox(InteractiveBlock, Serializable): ...

    class GumpBuilder:
        class Scope:
            def __init__(self, builder: "GumpBuilder", block: Container):
                self.builder = builder
                self.block = block

            def __enter__(self):
                self.builder.current.append(self.block)
                self.builder.current = self.block
                return self.block

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.builder.current = self.block.parent if self.block.parent else self.builder.root

        def __init__(self):
            self.root: Container = Row()
            self.current: Container = self.root

        def Row(self):
            return self.Scope(self, Row())

        def Column(self):
            return self.Scope(self, Column())

        # def Text(
        #     self,
        #     text: str = "",
        #     hue: int = 0,
        #     *args,
        #     **kwargs,
        # ):
        #     block = Text(text, hue, *args, **kwargs)
        #     self.current.append(block)
        #     return block

    class _module:
        """A singleton module-like class to export gump builder related classes and functions."""

        def __init__(self):
            self.GumpBuilder = GumpBuilder

    return _module()


gb = _gb()
"""Namespace for gump builder related classes and functions."""
