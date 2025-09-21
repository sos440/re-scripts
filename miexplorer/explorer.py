################################################################################
# Settings
################################################################################

VERSION = "2.0.5"


################################################################################
# Imports
################################################################################

from AutoComplete import *
from typing import List, Dict, Tuple, Callable, Generator, Any, Optional, Union, TypeVar, Generic
import os
import sys
import time
import csv
import re
import json
from datetime import datetime
from enum import Enum

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(__file__))

from modules.core import *
from modules.gumpradio import *


################################################################################
# Gumpradio Extensions
################################################################################


class SheetBuilder(GumpBuilder):
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
        """
        if isinstance(item, int):
            item_new = Items.FindBySerial(item)
            if item_new is None:
                return self.Checkbox(up=2328, down=2329, width=80, height=60, checked=checked)  # Empty button
            item = item_new
        btn = self.Checkbox(up=2328, down=2329, width=80, height=60, checked=checked, itemproperty=item.Serial)
        btn.add_tileart(graphics=item.ItemID)
        return btn

    def MainFrame(self, spacing: int = 5, padding: Union[int, Tuple[int, int, int, int]] = 10):
        """
        A shorthand for adding the main frame of the crafting gump style.
        """
        return self.Column(padding=padding, background="frame:5054", spacing=spacing)

    def MinimalFrame(self, spacing: int = 5, padding: Union[int, Tuple[int, int, int, int]] = (10, 5, 10, 10)):
        """
        A shorthand for adding a minimal frame with the crafting gump style.
        """
        return self.Column(padding=padding, background="frame:30546; alpha", spacing=spacing)

    def ShadedColumn(self, halign: str = "left", spacing: int = 5):
        """
        A shorthand for adding a column with the crafting gump style.

        :param halign: Horizontal alignment of child blocks within the column. ("left", "center", "right")
        """
        return self.Column(background="tiled:2624; alpha", padding=10, halign=halign, spacing=spacing)

    def ShadedRow(self, valign: str = "top", spacing: int = 5):
        """
        A shorthand for adding a row with the crafting gump style.

        :param valign: Vertical alignment of child blocks within the row. ("top", "middle", "bottom")
        """
        return self.Row(background="tiled:2624; alpha", padding=10, valign=valign, spacing=spacing)

    def MenuBar(self, spacing: int = 5):
        """
        A shorthand for adding a menu bar with the crafting gump style.

        This is basically a row with white tiled background.
        """
        return self.Row(background="tiled:9354", padding=5, spacing=spacing)

    class CraftingButtonStyle(Enum):
        RIGHT = 1
        LEFT = 2
        X = 3
        NO = 4
        OK = 5

    def CraftingButton(
        self,
        label: str,
        style: CraftingButtonStyle = CraftingButtonStyle.RIGHT,
        hue: int = 1152,
        width: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a button with a text label next to it.

        :param str label: The text label to display next to the button.
        :param int up: The gumpart ID for the button's up state.
        :param int down: The gumpart ID for the button's down state.
        :param int hue: The 0-based color hue of the label text.
        :param int width: The width of the label text area. If None, it will auto-size.
        """
        # Determine the button style
        up, down = 4005, 4007
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
        # Create the button with label
        with self.Row(spacing=5) as row:
            btn = self.Button(up=up, down=down, tooltip=tooltip)
            self.Text(label, hue=hue, width=width, tooltip=tooltip)
        return btn

    class MenuItemStyle(Enum):
        VIEW = 1
        WRITE = 2
        EXIT = 3
        CHECK = 4
        DOUBLE_RIGHT = 5
        DOUBLE_LEFT = 6
        SINGLE_RIGHT = 7
        SINGLE_LEFT = 8

    def MenuItem(
        self,
        label: str,
        style: MenuItemStyle = MenuItemStyle.VIEW,
        hue: int = 0,
        width: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a menu item button with a text label next to it.

        :param str label: The text label to display next to the button.
        :param int up: The gumpart ID for the button's up state.
        :param int down: The gumpart ID for the button's down state.
        :param int hue: The 0-based color hue of the label text.
        :param int width: The width of the label text area. If None, it will auto-size.
        """
        # Determine the button style
        up, down, bw, bh = 1531, 1532, 23, 21
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
        # Create the button with label
        with self.Row(spacing=5) as row:
            btn = self.Button(up=up, down=down, width=bw, height=bh, tooltip=tooltip)
            self.Text(label, hue=hue, width=width, tooltip=tooltip)
        return btn

    class UOStoreButtonStyle(Enum):
        BLUE = 1
        GREEN = 2
        RED = 3
        YELLOW = 4

    def UOStoreButton(
        self,
        label: str,
        style: UOStoreButtonStyle = UOStoreButtonStyle.BLUE,
        color: str = "#FFFFFF",
        tooltip: Optional[str] = None,
    ):
        """
        A shorthand for adding a UO Store style button with a text label next to it.

        :param str label: The text label to display next to the button.
        :param style: The style of the button.
        :param str color: The HTML color code of the label text. If None, it will use default color.
        :param int width: The width of the label text area. If None, it will auto-size.
        """
        # Create the button with label
        up, down, bw, bh = 40021, 40031, 125, 25
        if style == self.UOStoreButtonStyle.BLUE:
            up, down = 40021, 40031
        elif style == self.UOStoreButtonStyle.GREEN:
            up, down = 40020, 40030
        elif style == self.UOStoreButtonStyle.RED:
            up, down = 40297, 40298
        elif style == self.UOStoreButtonStyle.YELLOW:
            up, down = 40299, 40300
        with self.Row() as row:
            btn = self.Button(up=up, down=down, width=0, height=bh, tooltip=tooltip)
            self.Html(label, color=color, centered=True, width=bw, height=18, tooltip=tooltip)
        return btn


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
        """
        Generates a gump ID for the given name.
        """
        return hash(name) & 0xFFFFFFFF

    @staticmethod
    def tooltip_to_itemproperty(gd: Gumps.GumpData) -> str:
        """
        Converts integer-argument tooltips to item properties.
        """
        return re.sub(r"\{ tooltip (\d+) \}", r"{ itemproperty \1 }", gd.gumpDefinition)


# Gump ID
MAIN_GUMP_ID = GumpTools.hashname("ExplorerMainGump")

# Explorer gump settings
ROW_HEIGHT = 60
COL_WIDTH = 150
MENU_HEIGHT = 30
HEADER_HEIGHT = 30
BORDER_WIDTH = 10
ITEMS_PER_PAGE = 10
BG_STYLE = 2624

# Button IDs
ID_MAIN_REFRESH = 1
ID_MAIN_EXPORT = 2
ID_MAIN_TITLE = 3

IDMOD_MAIN_ACTION = 1000
IDMOD_MAIN_SORT = 2000
IDMOD_MAIN_FILTER = 3000


# Gump wrapping text
GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""


class ExplorerDialog:
    RARITY_COLOR_MAP = {1: 905, 2: 72, 3: 89, 4: 4, 101: 13, 102: 53, 103: 43, 104: 33}

    @staticmethod
    def show_loading(progress: float = 0.0):
        """
        This shows a loading screen.
        """
        gb = SheetBuilder(id="ExplorerMainGump")
        with gb.MainFrame():
            with gb.ShadedColumn():
                gb.Html(f"Loading... ({progress:.1%})", width=200, centered=True, color="#FFFFFF")
                gb.ProgressBar(width=200, height=22, progress=progress)
        gb.launch(response=False)

    @staticmethod
    def show_sheet(sheet: Optional[Sheet] = None, metadata: Optional[dict] = None) -> Optional[Tuple[Sheet, List[SheetColumn]]]:
        """
        This shows the main sheet gump. If `sheet` is `None`, it shows a loading screen.
        This returns the filtered sheet for future use, or `None` if it's a loading screen.
        """
        Gumps.CloseGump(MAIN_GUMP_ID)

        if sheet is None:
            ExplorerDialog.show_loading(progress=metadata.get("progress", 0.0) if metadata else 0.0)
            return None

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
        # if sheet is None:
        #     if metadata is not None and "progress" in metadata:
        #         progress = metadata["progress"]
        #         text = f"Loading... ({progress:.1%})"
        #     else:
        #         text = "Loading..."
        #     Gumps.AddImageTiled(gd, BORDER_WIDTH, BORDER_WIDTH, INNER_WIDTH, INNER_HEIGHT, BG_STYLE)
        #     Gumps.AddAlphaRegion(gd, BORDER_WIDTH, BORDER_WIDTH, INNER_WIDTH, INNER_HEIGHT)
        #     Gumps.AddHtml(gd, BORDER_WIDTH, HEIGHT // 2 - 11, INNER_WIDTH, 22, GUMP_WT.format(text=text), False, False)
        #     Gumps.SendGump(MAIN_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
        #     return

        # Sort the columns according to the update time
        idxcol_sorted = sorted(enumerate(sheet.columns), key=lambda c: c[1].metadata.get("update_time", 0))
        col_sorted = [col for _, col in idxcol_sorted]
        col_prec: List[Optional[int]] = [None] * len(idxcol_sorted)  # Column precedence
        for i, idx_col in enumerate(idxcol_sorted):
            if "update_time" in idx_col[1].metadata:
                col_prec[idx_col[0]] = len(idxcol_sorted) - i
                sheet = idx_col[1].filter(sheet)

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
        Gumps.AddLabelCropped(gd, x + 25, y + 2, 100, 18, 0, "Rename/Export")
        x += 150
        Gumps.AddLabelCropped(gd, x, y + 2, 250, 18, 0, f"Name: {sheet.name}")

        # Column headers
        x = BORDER_WIDTH
        y = BORDER_WIDTH + MENU_HEIGHT + 5
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, HEADER_HEIGHT, BG_STYLE)
        # Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, HEADER_HEIGHT)
        Gumps.AddImageTiled(gd, x, y, 80, HEADER_HEIGHT, 9354)
        x += 81
        dy = (HEADER_HEIGHT - 18) // 2
        for i, col in enumerate(sheet.columns):
            Gumps.AddImageTiled(gd, x, y, COL_WIDTH - 1, HEADER_HEIGHT, 9354)
            Gumps.AddButton(gd, x + 4, y + dy + 2, 1209, 1210, IDMOD_MAIN_FILTER + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 22, y + dy, COL_WIDTH - 30, 18, 0, col.id)
            Gumps.AddTooltip(gd, col.name)
            if col.is_reverse():
                Gumps.AddButton(gd, x + COL_WIDTH - 15, y + dy + 4, 2437, 2438, IDMOD_MAIN_SORT + i, 1, 0)
                if col_prec[i] is None:
                    Gumps.AddTooltip(gd, f"Not sorted")
                else:
                    Gumps.AddTooltip(gd, f"Order: Descending<BR>Precedence: {col_prec[i]}")
            else:
                Gumps.AddButton(gd, x + COL_WIDTH - 15, y + dy + 4, 2435, 2436, IDMOD_MAIN_SORT + i, 1, 0)
                if col_prec[i] is None:
                    Gumps.AddTooltip(gd, f"Not sorted")
                else:
                    Gumps.AddTooltip(gd, f"Order: Ascending<BR>Precedence: {col_prec[i]}")
            x += COL_WIDTH
        Gumps.AddImageTiled(gd, x, y, 22, HEADER_HEIGHT, 9354)
        Gumps.AddButton(gd, x + 4, y + dy + 2, 1209, 1210, IDMOD_MAIN_FILTER + len(sheet.columns), 1, 0)

        # Ruled sheet
        x = BORDER_WIDTH
        y = BORDER_WIDTH + MENU_HEIGHT + 5 + HEADER_HEIGHT + 1
        for j in range(ITEMS_PER_PAGE):
            Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, ROW_HEIGHT, BG_STYLE)
            Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, ROW_HEIGHT)
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
        return sheet, col_sorted


class ExplorerHandlers:
    @classmethod
    def dialog_action(cls, row: ItemPropRow):
        """
        Shows the possible intreractions with the item for the given row.
        """
        gb = SheetBuilder(id="SheetActionGump")

        with gb.MainFrame():
            with gb.ShadedColumn(halign="center"):
                gb.TileArt(row["Type"], width=80, height=60, hue=row["Color"], centered=True, itemproperty=row["Serial"])
            with gb.ShadedColumn():
                btn_to_inv = gb.CraftingButton("To Backpack", tooltip="Move the item to your backpack.")
                btn_use = gb.CraftingButton("Use", tooltip="Use the item.")
                btn_equip = gb.CraftingButton("Equip", tooltip="Attempts to equip the item. This may fail if you already have an item in the slot.")
                btn_move = gb.CraftingButton("Move To", tooltip="Move the item to a target container.")
                btn_exit = gb.CraftingButton("Return", style=gb.CraftingButtonStyle.LEFT, tooltip="Return to the previous menu.")

        block, response = gb.launch()
        if block == btn_exit:
            return
        if block == btn_to_inv:
            Items.Move(row["Serial"], Player.Backpack.Serial, -1)
            Misc.Pause(500)
            return
        if block == btn_use:
            Items.UseItem(row["Serial"])
            Misc.Pause(500)
            return
        if block == btn_equip:
            Player.EquipUO3D([row["Serial"]])
            Misc.Pause(500)
            return
        if block == btn_move:
            target = Target.PromptTarget("Select the destination to move the item.", 0x3B2)
            target_cont = Items.FindBySerial(target)
            if target_cont is None:
                Misc.SendMessage("Target not found.", 0x21)
                return
            Items.Move(row["Serial"], target_cont.Serial, -1)
            Misc.Pause(500)
            return

    @staticmethod
    def dialog_edit_column(col_idx: int, sheet: Sheet):
        """
        Edit the column's property or remove the column.
        """
        col = sheet.columns[col_idx]
        all_items = list(PropMaster.ALL_PROPS.iter_group())

        cur_group: Optional[PropGroup] = None
        cur_props: List[BaseProp] = []
        cur_page = 0
        lines_per_page = max(10, len(all_items) - 2)

        gb = SheetBuilder(id="SheetFilterGump")
        with gb.MainFrame():
            # Header
            with gb.ShadedColumn(halign="center"):
                gb.Html(f"COLUMN {col_idx+1}: {col.name}", centered=True, color="#FFFFFF")
            # Body
            with gb.Row(spacing=5):
                # Groups column
                with gb.ShadedColumn():
                    gb.Html("GROUPS", width=200, centered=True, color="#FFFFFF")
                    gb.Spacer(5)
                    for i, group in enumerate(all_items):
                        gb.CraftingButton(group.name).on_click(group)
                # Properties column
                with gb.ShadedColumn():
                    gb.Html("PROPERTIES", width=200, centered=True, color="#FFFFFF")
                    gb.Spacer(5)
                    # Properties list (to be populated later)
                    with gb.Column(halign="left", spacing=5) as c:
                        prop_col = c
                    gb.Spacer(22)
                    with gb.Row():
                        btn_prev = gb.CraftingButton("PREV")
                        btn_next = gb.CraftingButton("NEXT")
            # Footer
            with gb.ShadedRow():
                with gb.Row():
                    btn_remove = gb.CraftingButton("REMOVE COLUMN")
                    btn_exit = gb.CraftingButton("EXIT", style=gb.CraftingButtonStyle.X)

        while True:
            # Populate properties column
            prop_col.clear_children()
            gb.current = prop_col
            if cur_group is not None:
                for i in range(lines_per_page):
                    prop_idx = cur_page * lines_per_page + i
                    if 0 <= prop_idx < len(cur_props):
                        prop = cur_props[prop_idx]
                        gb.CraftingButton(prop.name, width=165).on_click(prop)
                    else:
                        gb.Spacer(22)
            else:
                gb.Html("(No group selected)", width=200, centered=True, color="#FFFFFF")
                for i in range(lines_per_page):
                    gb.Spacer(22)

            # Wait for response
            block, response = gb.launch()

            # Handle response
            if block == btn_exit:
                return
            if block == btn_prev:
                if cur_page > 0:
                    cur_page -= 1
                continue
            if block == btn_next:
                last_page = (len(cur_props) - 1) // lines_per_page
                if cur_page < last_page:
                    cur_page += 1
                continue
            if block == btn_remove:
                Misc.SendMessage(f"Column {col_idx+1} removed.", 68)
                sheet.columns.pop(col_idx)
                return
            if isinstance(response, PropGroup):
                cur_group = response
                cur_props = list(cur_group.iter_prop())
                cur_page = 0
                continue
            if isinstance(response, BaseProp):
                col.prop = response
                col.metadata["update_time"] = time.time()
                col.sort_order = col.prop.default_order
                return
            return

    @staticmethod
    def export_to_csv(sheet: Sheet, verbose: bool = False):
        """
        Exports the given sheet to a CSV file.
        The file is saved to `Data/Sheets/{sheet.name}.csv`.
        """
        # Escape the sheet name so it can be used as a filename
        filename = re.sub(r"[^\w\s-]", "_", sheet.name)
        os.makedirs("Data/Sheets", exist_ok=True)
        filepath = f"Data/Sheets/{filename}.csv"

        if verbose:
            columns = list(PropMaster.ALL_PROPS.walk_prop())
        else:
            columns = list(col.prop for col in sheet.columns)

        with open(filepath, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header
            csvwriter.writerow([col.name for col in columns])
            # Write rows
            for row in sheet.rows:
                csvwriter.writerow([col.stringify(row) for col in columns])
        Misc.SendMessage(f"The sheet has been exported to: {filepath}", 68)

    @staticmethod
    def import_setting() -> Optional[Dict[str, Any]]:
        filepath = "Data/Sheets/setting.json"
        if not os.path.isfile(filepath):
            return
        with open(filepath, "r") as f:
            try:
                setting = json.load(f)
                return setting
            except Exception as e:
                Misc.SendMessage(f"Failed to load setting: {e}", 0x21)
                return

    @staticmethod
    def save_setting(sheet: Sheet):
        filepath = "Data/Sheets/setting.json"
        os.makedirs("Data/Sheets", exist_ok=True)
        setting = {
            "columns": [
                {
                    "id": col.id,
                    "sort_order": col.sort_order.value,
                    "metadata": col.metadata,
                }
                for col in sheet.columns
            ]
        }
        with open(filepath, "w") as f:
            try:
                json.dump(setting, f, indent=4)
            except Exception as e:
                Misc.SendMessage(f"Failed to save setting: {e}", 0x21)

    @staticmethod
    def dialog_edit_save(sheet: Sheet) -> str:
        """
        Show the edit/save gump for the given sheet.
        Here you can change the sheet name or export the sheet.
        """
        gb = SheetBuilder(id="SheetSaveGump")
        with gb.MinimalFrame():
            gb.Html("Edit/Export Sheet", width=320, centered=True, color="#FFFFFF")
            with gb.Row(spacing=5):
                gb.Text("Name:", width=40, hue=1152)
                name = gb.TextEntry(sheet.name, width=280, hue=1152, max_length=200, tooltip="This is the name of the sheet. It will be used as the file name when exporting.")
            with gb.Row(spacing=5):
                chk_verbose = gb.Checkbox(checked=False)
                gb.Text("Verbose (Export every scanned properties)", width=280, hue=1152)
            gb.Spacer(5)
            with gb.Row(spacing=10):
                btn_export = gb.UOStoreButton("Export", style=SheetBuilder.UOStoreButtonStyle.BLUE, tooltip="Export the sheet to a CSV file.")
                btn_rename = gb.UOStoreButton("Rename", style=SheetBuilder.UOStoreButtonStyle.GREEN, tooltip="Rename the sheet.")
                btn_cancel = gb.UOStoreButton("Cancel", style=SheetBuilder.UOStoreButtonStyle.RED, tooltip="Cancel and close this dialog.")

        while True:
            block, response = gb.launch()
            if block == chk_verbose:
                continue
            if block is None or block == btn_cancel:
                return "cancel"
            if block == btn_rename:
                sheet.name = name.text.strip()
                return "rename"
            if block == btn_export:
                sheet.name = name.text.strip()
                if chk_verbose.checked:
                    return "export_verbose"
                return "export"

    @staticmethod
    def explorer(serial: int, sheet_header: Sheet) -> Optional[Sheet]:
        """
        Scans the provided container and shows the explorer gump.

        :return: If a sheet is returned, the explorer gump will be shown again.
        Otherwise, the explorer will be closed.
        """
        cont = Items.FindBySerial(serial)
        if cont is None:
            return None
        if cont.ItemID in (0x9F1C, 0x9F1D):
            Items.UseItem(cont)
            Misc.Pause(500)
        else:
            Items.WaitForContents(serial, 1000)

        # Show the loading screen
        ExplorerDialog.show_sheet()

        # Create an unfiltered sheet using the provided header and the container's contents
        sheet = Sheet(name=sheet_header.name)
        sheet.columns = sheet_header.columns
        Timer.Create("update-loading", 250)
        for row in cont.Contains:
            if not Timer.Check("update-loading"):
                progress = len(sheet.rows) / max(1, len(cont.Contains))
                ExplorerDialog.show_sheet(metadata={"progress": progress})
                Timer.Create("update-loading", 250)
            sheet.add_row_by_serial(row.Serial)

        # Create a filtered sheet for display and interaction
        filtered_sheet = Sheet()
        filtered_sheet.columns = sheet.columns
        output = ExplorerDialog.show_sheet(sheet)
        if output is None:
            return
        filtered_sheet, col_sorted = output

        # Wait for the user's input
        if not Gumps.WaitForGump(MAIN_GUMP_ID, 1000 * 60 * 60):
            return

        # Parse the user's input
        gd = Gumps.GetGumpData(MAIN_GUMP_ID)
        if not gd:
            return

        if gd.buttonid == 0:
            return

        if gd.buttonid == ID_MAIN_REFRESH:
            return sheet

        if gd.buttonid == ID_MAIN_EXPORT:
            choice = ExplorerHandlers.dialog_edit_save(filtered_sheet)
            if choice == "export":
                ExplorerHandlers.export_to_csv(filtered_sheet)
                sheet_header.name = filtered_sheet.name
            elif choice == "export_verbose":
                ExplorerHandlers.export_to_csv(filtered_sheet, verbose=True)
                sheet_header.name = filtered_sheet.name
            elif choice == "rename":
                sheet_header.name = filtered_sheet.name
                Misc.SendMessage(f"The sheet has been renamed to: {sheet_header.name}", 68)
            elif choice == "cancel":
                Misc.SendMessage("The edit/export has been cancelled.", 0x3B2)
            return sheet

        id_action = gd.buttonid - IDMOD_MAIN_ACTION
        is_action = 0 <= id_action < len(filtered_sheet.rows)
        if is_action:
            row = filtered_sheet.rows[id_action]
            ExplorerHandlers.dialog_action(row)
            return sheet

        id_sort = gd.buttonid - IDMOD_MAIN_SORT
        if 0 <= id_sort < len(sheet.columns):
            col = sheet.columns[id_sort]
            col_last = col_sorted[-1] if col_sorted else None  # Last updated column, if any (note that the sheet has no columns)
            # Toggle the sort order only when it is updated most recently
            if col_last == col:
                if col.is_unsorted():
                    col.sort_order = SortOrder.ASCENDING
                else:
                    col.toggle_reverse()
            col.metadata["update_time"] = time.time()
            return sheet

        id_filter = gd.buttonid - IDMOD_MAIN_FILTER
        if 0 <= id_filter < len(sheet.columns):
            ExplorerHandlers.dialog_edit_column(id_filter, sheet)
            return sheet
        if id_filter == len(sheet.columns):
            # The added column is initially of the least priority in the sort orders
            sheet_header.add_column_by_id("Name", {"update_time": 0})
            return sheet

    @staticmethod
    def dialog_shortcut() -> Any:
        """
        A minimized gump to quickly open the explorer.
        """

        gb = SheetBuilder(id="SheetShortcutGump")
        with gb.MinimalFrame():
            gb.Html("Item Explorer", centered=True, color="#FFFFFF", width=126)
            gb.UOStoreButton("Inspect", tooltip="Inspect the target container's contents.").on_click(True)

        _, response = gb.launch()
        return response


################################################################################
# Top-Level Logic
################################################################################


if Player.Connected:
    sheet_header = Sheet()

    # Load the saved setting if any, and add the columns to the sheet header
    setting = ExplorerHandlers.import_setting()
    if setting is not None:
        for col_setting in setting.get("columns", []):
            col = PropMaster.create_col_by_id(col_setting.get("id"), col_setting.get("metadata"))
            if col is None:
                continue
            try:
                col.sort_order = SortOrder(col_setting.get("sort_order", "unsorted"))
            except ValueError:
                col.sort_order = col.prop.default_order
            sheet_header.add_column(col)
    else:
        sheet_header.add_column_by_id("Rarity", {"update_time": time.time()})
        sheet_header.add_column_by_id("Name", {"update_time": 0})

    # Main loop
    while Player.Connected:
        # Wait for the user's input on the shortcut gump
        response = ExplorerHandlers.dialog_shortcut()
        if not response:
            continue

        # If the user wants to inspect a container, prompt for it
        serial = Target.PromptTarget("Select the container to inspect.", 1153)
        if serial == 0:
            continue

        # Start the exploration loop
        sheet_header.name = f"Untitled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        while True:
            unfiltered_sheet = ExplorerHandlers.explorer(serial, sheet_header)
            if unfiltered_sheet is None:
                break
        ExplorerHandlers.save_setting(sheet_header)
