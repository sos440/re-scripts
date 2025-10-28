from AutoComplete import *
from typing import Optional, Union, Tuple
from enum import Enum
import sys
import os

# Ensure the current directory is in the system path for module resolution
sys.path.append(os.path.dirname(__file__))

# Import gumpradio after modifying sys.path
from main import GumpBuilder


class CraftingGumpBuilder(GumpBuilder):
    """
    This is an example subclass of GumpBuilder that provides custom block types
    for a crafting gump style.
    """

    class _ProgressBar(GumpBuilder.Assets.Container):
        def __init__(self, width: int = 100, height: int = 20, progress: float = 0.0):
            """
            Represents a progress bar block in the gump.

            :param width: The width of the progress bar in pixels.
            :param height: The height of the progress bar in pixels.
            :param progress: The progress value between 0.0 and 1.0.
            """
            super().__init__(width, height)
            self.padding = 3
            self.background = "frame:2620"
            self.progress = max(0.0, min(1.0, progress))
            # Manually add background and bar gumparts
            self._bg = GumpBuilder.Assets.GumpArt(graphics=2624, tiled=True)
            self._bar = GumpBuilder.Assets.GumpArt(graphics=9354, tiled=True)
            self.children = [self._bg, self._bar]

        def compute_size(self):
            # Manually set the size of the background and bar based on progress
            res = super().compute_size()
            self._bg._calc_width = self._calc_width - self.padding[0] - self.padding[2]
            self._bg._calc_height = self._calc_height - self.padding[1] - self.padding[3]
            self._bar._calc_width = int(self._bg._calc_width * self.progress)
            self._bar._calc_height = self._bg._calc_height
            return res

        def compute_position(self, left: int = 0, top: int = 0):
            # Manually position the background and bar within the container
            res = super().compute_position(left, top)
            self._bg.compute_position(self._calc_left + self.padding[0], self._calc_top + self.padding[1])
            self._bar.compute_position(self._calc_left + self.padding[0], self._calc_top + self.padding[1])
            return res

    def ProgressBar(self, width: int = 100, height: int = 20, progress: float = 0.0):
        """
        Add a progress bar with the crafting gump style.

        :param width: The width of the progress bar in pixels.
        :param height: The height of the progress bar in pixels.
        :param progress: The progress value between 0.0 and 1.0.
        """
        bar = self._ProgressBar(width, height, progress)
        self.current.append(bar)
        return bar

    def ItemDisplayButton(self, item: "Union[Item, int]", checked: bool = False):
        """
        A shorthand for adding a button that displays an item (tileart) along with
        its item properties as tooltip.

        :param Item|int item:  The item or item serial to display.
        :param bool checked: Whether the button is in a checked state.
        """
        if isinstance(item, int):
            item_new = Items.FindBySerial(item)
            if item_new is None:
                return self.Checkbox(up=2328, down=2329, width=80, height=60, checked=checked)  # Empty button
            item = item_new
        btn = self.Checkbox(up=2328, down=2329, width=80, height=60, checked=checked, itemproperty=item.Serial)
        btn.add_tileart(graphics=item.ItemID, hue=item.Hue)
        return btn

    def MainFrame(self, spacing: int = 5, padding: Union[int, Tuple[int, int, int, int]] = 10):
        """
        A shorthand for adding the main frame of the crafting gump style.

        :param spacing: The spacing between child blocks within the frame.
        :param padding: The padding inside the frame. Can be a single int or a tuple of four ints
                        representing (left, top, right, bottom) padding.
        """
        return self.Column(padding=padding, background="frame:5054", spacing=spacing, stretch=False)

    def MinimalFrame(self, spacing: int = 5, padding: Union[int, Tuple[int, int, int, int]] = (10, 5, 10, 10)):
        """
        A shorthand for adding a minimal frame with the crafting gump style.

        :param spacing: The spacing between child blocks within the frame.
        :param padding: The padding inside the frame. Can be a single int or a tuple of four ints
                        representing (left, top, right, bottom) padding.
        """
        return self.Column(padding=padding, background="frame:30546; alpha", spacing=spacing)

    def ShadedColumn(self, halign: str = "left", spacing: int = 5):
        """
        A shorthand for adding a column with the crafting gump style.

        :param halign: Horizontal alignment of child blocks within the column. ("left", "center", "right")
        :param spacing: The spacing between child blocks within the column.
        """
        return self.Column(background="tiled:2624; alpha", padding=10, halign=halign, spacing=spacing)

    def ShadedRow(self, valign: str = "top", spacing: int = 5):
        """
        A shorthand for adding a row with the crafting gump style.

        :param valign: Vertical alignment of child blocks within the row. ("top", "middle", "bottom")
        :param spacing: The spacing between child blocks within the row.
        """
        return self.Row(background="tiled:2624; alpha", padding=10, valign=valign, spacing=spacing)

    class CraftingButtonStyle(Enum):
        RIGHT = "right"
        LEFT = "left"
        X = "x"
        NO = "no"
        OK = "ok"

    def CraftingButton(
        self,
        label: str,
        style: Union[CraftingButtonStyle, str] = CraftingButtonStyle.RIGHT,
        hue: int = 1152,
        width: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a button with a text label next to it.

        :param str label: The text label to display next to the button.
        :param style: The style of the button. ("right", "left", "x", "no", "ok")
        :param int hue: The 0-based color hue of the label text.
        :param int width: The width of the label text area. If None, it will auto-size.
        :param str tooltip: The tooltip text for the button and label.
        """
        # Determine the button style
        up, down = 4005, 4007
        if isinstance(style, str):
            style = self.CraftingButtonStyle(style)
        if style == self.CraftingButtonStyle.RIGHT:
            up, down = 4005, 4007
        elif style == self.CraftingButtonStyle.LEFT:
            up, down = 4014, 4016
        elif style == self.CraftingButtonStyle.X:
            up, down = 4017, 4019
        elif style == self.CraftingButtonStyle.NO:
            up, down = 4020, 4022
        elif style == self.CraftingButtonStyle.OK:
            up, down = 4023, 4025
        # Create the button with label, if label is not empty
        with self.Row(spacing=5) as row:
            btn = self.Button(up=up, down=down, tooltip=tooltip)
            if label:
                self.Text(label, hue=hue, width=width, tooltip=tooltip)
        return btn

    class MenuItemStyle(Enum):
        VIEW = "view"
        WRITE = "write"
        EXIT = "exit"
        CHECK = "check"
        DOUBLE_RIGHT = "double_right"
        DOUBLE_LEFT = "double_left"
        SINGLE_RIGHT = "single_right"
        SINGLE_LEFT = "single_left"

    def MenuItem(
        self,
        label: str,
        style: Union[MenuItemStyle, str] = MenuItemStyle.VIEW,
        hue: int = 0,
        width: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a menu item button with a text label next to it.

        :param str label: The text label to display next to the button.
        :param style: The style of the button. ("view", "write", "exit", "check", "double_right", "double_left", "single_right", "single_left")
        :param int hue: The 0-based color hue of the label text.
        :param int width: The width of the label text area. If None, it will auto-size.
        :param str tooltip: The tooltip text for the button and label.
        """
        # Determine the button style
        up, down, bw, bh = 1531, 1532, 23, 21
        if isinstance(style, str):
            style = self.MenuItemStyle(style)
        if style == self.MenuItemStyle.VIEW:
            up, down = 1531, 1532
        elif style == self.MenuItemStyle.WRITE:
            up, down = 1533, 1534
        elif style == self.MenuItemStyle.EXIT:
            up, down = 1535, 1536
        elif style == self.MenuItemStyle.CHECK:
            up, down = 1537, 1538
        elif style == self.MenuItemStyle.DOUBLE_RIGHT:
            up, down = 1539, 1540
        elif style == self.MenuItemStyle.DOUBLE_LEFT:
            up, down = 1541, 1542
        elif style == self.MenuItemStyle.SINGLE_RIGHT:
            up, down = 1543, 1544
            bw, bh = 15, 21
        elif style == self.MenuItemStyle.SINGLE_LEFT:
            up, down = 1545, 1546
            bw, bh = 15, 21
        # Create the button with label, if label is not empty
        with self.Row(spacing=5) as row:
            btn = self.Button(up=up, down=down, width=bw, height=bh, tooltip=tooltip)
            if label:
                self.Text(label, hue=hue, width=width, tooltip=tooltip)
        return btn

    class UOStoreButtonStyle(Enum):
        BLUE = "blue"
        GREEN = "green"
        RED = "red"
        YELLOW = "yellow"

    def UOStoreButton(
        self,
        label: str,
        style: Union[UOStoreButtonStyle, str] = UOStoreButtonStyle.BLUE,
        color: str = "#FFFFFF",
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a UO Store style button with a text label next to it.

        :param str label: The text label to display next to the button.
        :param style: The style of the button. ("blue", "green", "red", "yellow")
        :param str color: The HTML color code of the label text. If None, it will use default color.
        :param int width: The width of the label text area. If None, it will auto-size.
        :param str tooltip: The tooltip text for the button and label.
        """
        # Determine the button style
        up, down, bw, bh = 40021, 40031, 125, 25
        if isinstance(style, str):
            style = self.UOStoreButtonStyle(style)
        if style == self.UOStoreButtonStyle.BLUE:
            up, down = 40021, 40031
        elif style == self.UOStoreButtonStyle.GREEN:
            up, down = 40020, 40030
        elif style == self.UOStoreButtonStyle.RED:
            up, down = 40297, 40298
        elif style == self.UOStoreButtonStyle.YELLOW:
            up, down = 40299, 40300
        # Create the button with label, if label is not empty
        with self.Row() as row:
            btn = self.Button(up=up, down=down, width=0, height=bh, tooltip=tooltip)
            if label:
                self.Html(label, color=color, centered=True, width=bw, height=18)
        return btn

    class SortButtonStyle(Enum):
        ASCENDING = "asc"
        DESCENDING = "dec"

    def SortButton(
        self,
        style: Union[SortButtonStyle, str] = SortButtonStyle.ASCENDING,
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a sort button with ascending and descending states.

        :param style: The style of the button. ("asc", "dec")
        :param str tooltip: The tooltip text for the button.
        """
        # Determine the button style
        if isinstance(style, str):
            style = self.SortButtonStyle(style)
        if style == self.SortButtonStyle.ASCENDING:
            return self.Button(up=2435, down=2436, width=9, height=11, tooltip=tooltip)
        elif style == self.SortButtonStyle.DESCENDING:
            return self.Button(up=2437, down=2438, width=9, height=11, tooltip=tooltip)
        raise ValueError("Invalid SortButtonStyle")

    def BlueJewelButton(self, tooltip: Optional[str] = None):
        return self.Button(up=1209, down=1210, width=14, height=14, tooltip=tooltip)
