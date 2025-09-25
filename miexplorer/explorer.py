################################################################################
# Settings
################################################################################

VERSION = "2.1.1"
EXPORT_PATH = "Data/Sheets"
SETTING_PATH = "Data/Sheets/setting.json"

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
        # Create the button with label, if label is not empty
        with self.Row(spacing=5) as row:
            btn = self.Button(up=up, down=down, tooltip=tooltip)
            if label:
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
        # Create the button with label, if label is not empty
        with self.Row(spacing=5) as row:
            btn = self.Button(up=up, down=down, width=bw, height=bh, tooltip=tooltip)
            if label:
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
        # Determine the button style
        up, down, bw, bh = 40021, 40031, 125, 25
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
        ASCENDING = 1
        DESCENDING = 2

    def SortButton(self, style: SortButtonStyle = SortButtonStyle.ASCENDING, tooltip: Optional[str] = None):
        """
        A shorthand for adding a sort button with ascending and descending states.
        """
        if style == self.SortButtonStyle.ASCENDING:
            return self.Button(up=2435, down=2436, width=9, height=11, tooltip=tooltip)
        elif style == self.SortButtonStyle.DESCENDING:
            return self.Button(up=2437, down=2438, width=9, height=11, tooltip=tooltip)
        raise ValueError("Invalid SortButtonStyle")

    def BlueJewelButton(self, tooltip: Optional[str] = None):
        return self.Button(up=1209, down=1210, width=14, height=14, tooltip=tooltip)


################################################################################
# Gumps and Handlers
################################################################################


class ExplorerSheetView:
    MAIN_GUMP_ID = hash("ExplorerMainGump") & 0xFFFFFFFF
    COL_WIDTH = 150
    MENU_HEIGHT = 30
    HEADER_HEIGHT = 30
    ITEMS_PER_PAGE = 10
    RARITY_COLOR_MAP = {1: 905, 2: 72, 3: 89, 4: 4, 101: 13, 102: 53, 103: 43, 104: 33}

    @classmethod
    def close(cls):
        Gumps.CloseGump(cls.MAIN_GUMP_ID)

    @classmethod
    def show_loading(cls, progress: float = 0.0):
        gb = SheetBuilder(id=cls.MAIN_GUMP_ID)
        with gb.MainFrame():
            with gb.ShadedColumn():
                gb.Html(f"Loading... ({progress:.1%})", width=200, centered=True, color="#FFFFFF")
                gb.ProgressBar(width=200, height=22, progress=progress)
        gb.launch(response=False)

    def __init__(self, sheet: Sheet, col_precedence: List[Optional[int]], page: int = 0):
        self.sheet = sheet
        self.col_precedence = col_precedence
        self.page = page
        self.total_pages = (len(sheet.rows) - 1) // self.ITEMS_PER_PAGE + 1

        gb = SheetBuilder(id=self.MAIN_GUMP_ID)
        with gb.MainFrame():
            # Menubar
            with gb.Row(background="tiled:9354", height=self.MENU_HEIGHT, padding=5):
                self.menu_refresh = gb.MenuItem("Refresh", style=SheetBuilder.MenuItemStyle.VIEW)
                self.menu_export = gb.MenuItem("Rename/Export", width=120, style=SheetBuilder.MenuItemStyle.WRITE)
                self.menu_columns = gb.MenuItem("Load/Save Columns", width=150, style=SheetBuilder.MenuItemStyle.WRITE)
                gb.Text(f"Name: {sheet.name}", hue=0, width=250)
            # Sheet area
            with gb.Column(spacing=1):
                # Column headers
                with gb.Row(spacing=1):
                    # Navigation buttons
                    with gb.Row(background="tiled:9354", width=80, height=self.HEADER_HEIGHT):
                        self.menu_prev = gb.MenuItem("", style=SheetBuilder.MenuItemStyle.SINGLE_LEFT)
                        gb.Html(f"{self.page+1}/{self.total_pages}", centered=True, width=50, height=18)
                        self.menu_next = gb.MenuItem("", style=SheetBuilder.MenuItemStyle.SINGLE_RIGHT)
                    self.menu_edit_column = []
                    self.menu_sort_column = []
                    for j, col in enumerate(sheet.columns):
                        width = col.metadata.get("width", self.COL_WIDTH)
                        with gb.Row(background="tiled:9354", width=width, height=self.HEADER_HEIGHT, padding=(5, 0), spacing=2):
                            # Edit button
                            btn_edit = gb.BlueJewelButton().on_click(j)
                            self.menu_edit_column.append(btn_edit)
                            # Column name
                            gb.Html(col.id, width=width - 37, height=18, tooltip=col.name)
                            # Sort button
                            if col_precedence[j] is None or col.sort_order == SortOrder.UNSORTED:
                                btn_sort = gb.SortButton(style=SheetBuilder.SortButtonStyle.ASCENDING, tooltip="Not sorted")
                            elif col.sort_order == SortOrder.ASCENDING:
                                btn_sort = gb.SortButton(style=SheetBuilder.SortButtonStyle.ASCENDING, tooltip=f"Order: Ascending<BR>Precedence: {col_precedence[j]}")
                            elif col.sort_order == SortOrder.DESCENDING:
                                btn_sort = gb.SortButton(style=SheetBuilder.SortButtonStyle.DESCENDING, tooltip=f"Order: Descending<BR>Precedence: {col_precedence[j]}")
                            else:
                                raise ValueError("Invalid sort order")
                            btn_sort.on_click(j)
                            self.menu_sort_column.append(btn_sort)
                    with gb.Row(background="tiled:9354", height=self.HEADER_HEIGHT, padding=(5, 0), spacing=2):
                        self.menu_new_column = gb.BlueJewelButton(tooltip="Add Column")
                # Rows
                self.menu_item_action = []
                for i in range(self.ITEMS_PER_PAGE):
                    row_idx = self.page * self.ITEMS_PER_PAGE + i
                    with gb.Row(background="tiled:2624; alpha", height=60, spacing=1):
                        if row_idx >= len(sheet.rows):
                            continue
                        row = sheet.rows[row_idx]
                        # Item button
                        self.menu_item_action.append(gb.ItemDisplayButton(row["Serial"]).on_click(row))
                        # Write the content of the row
                        for j, col in enumerate(sheet.columns):
                            width = col.metadata.get("width", self.COL_WIDTH)
                            hue = 1152
                            if col.id == "Rarity":
                                rarity = row["Rarity"]
                                hue = self.RARITY_COLOR_MAP.get(rarity, 1152)
                            value = col.read(row) or ""
                            with gb.Row(width=width, padding=(10, 0, 0, 0)):
                                gb.Text(value, hue=hue, width=width - 10, tooltip=f"{col.name}: {value}", cropped=True)

        self.gb = gb


class Explorer:

    @staticmethod
    def confirm(
        text: str,
        title: Optional[str] = None,
        yes_text: str = "Confirm",
        no_text: str = "Cancel",
        height: int = 22,
        centered: bool = True,
    ) -> bool:
        """
        Show a confirmation dialog with the given text and title.
        """
        gb = SheetBuilder(id="ConfirmGump")
        with gb.MinimalFrame():
            if title:
                gb.Html(title, width=250, centered=True, color="#FFFFFF")
            gb.Html(text, width=250, height=height, centered=centered, color="#FFFFFF")
            gb.Spacer(5)
            with gb.Row(spacing=10):
                btn_yes = gb.UOStoreButton(yes_text, style=SheetBuilder.UOStoreButtonStyle.BLUE)
                btn_no = gb.UOStoreButton(no_text, style=SheetBuilder.UOStoreButtonStyle.RED)

        block, response = gb.launch()
        return block == btn_yes

    @staticmethod
    def parse_column_setting(cols_json: List[Dict[str, Any]]) -> Sheet:
        sheet_header = Sheet()
        for col_json in cols_json:
            if "id" not in col_json:
                continue
            col = PropMaster.create_col_by_id(col_json["id"], col_json.get("metadata"))
            if col is None:
                continue
            try:
                col.sort_order = SortOrder(col_json.get("sort_order", "unsorted"))
            except ValueError:
                col.sort_order = col.prop.default_order
            sheet_header.add_column(col)
        return sheet_header

    @staticmethod
    def encode_column_setting(sheet: Sheet) -> List[Dict[str, Any]]:
        return [
            {
                "id": col.id,
                "sort_order": col.sort_order.value,
                "metadata": dict(col.metadata),
            }
            for col in sheet.columns
        ]

    @staticmethod
    def export_to_csv(sheet: Sheet, verbose: bool = False):
        """
        Exports the given sheet to a CSV file.
        The file is saved to `Data/Sheets/{sheet.name}.csv`.
        """
        try:
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
        except Exception as e:
            Misc.SendMessage(f"Failed to export the sheet: {e}", 0x21)

    @staticmethod
    def import_setting() -> Optional[Dict[str, Any]]:
        try:
            if not os.path.isfile(SETTING_PATH):
                return
            with open(SETTING_PATH, "r") as f:
                setting = json.load(f)
                return setting
        except Exception as e:
            Misc.SendMessage(f"Failed to load setting: {e}", 0x21)

    @staticmethod
    def export_setting(sheet: Sheet, old_setting: Optional[Dict[str, Any]] = None):
        try:
            os.makedirs("Data/Sheets", exist_ok=True)
            setting = old_setting or {}
            setting["columns"] = Explorer.encode_column_setting(sheet)
            # First try exporting as string, to ensure it's serializable
            # This also prevents from setting file being corrupted
            _ = json.dumps(setting)
            # Export to JSON file
            with open(SETTING_PATH, "w") as f:
                json.dump(setting, f, indent=4)
        except Exception as e:
            Misc.SendMessage(f"Failed to save setting: {e}", 0x21)

    @classmethod
    def item_action(cls, row: ItemPropRow):
        """
        Shows the possible intreractions with the item for the given row.
        """
        # Build the gump
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

        # Handle response
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
    def edit_column(col_idx: int, sheet: Sheet):
        """
        Edit the column's property or remove the column.
        """
        col = sheet.columns[col_idx]
        all_items = list(PropMaster.ALL_PROPS.iter_group())

        # Current state
        cur_group: Optional[PropGroup] = None
        cur_props: List[BaseProp] = []
        cur_page = 0
        lines_per_page = max(10, len(all_items) - 2)

        # Build the gump
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
                        gb.CraftingButton(group.name, width=165).on_click(group)
                # Properties column
                with gb.ShadedColumn():
                    gb.Html("PROPERTIES", width=200, centered=True, color="#FFFFFF")
                    gb.Spacer(5)
                    # Properties list (to be populated later)
                    with gb.Column(halign="left", spacing=5) as c:
                        prop_col = c
                    gb.Spacer(22)
                    with gb.Row():
                        btn_prev = gb.CraftingButton("PREV", style=gb.CraftingButtonStyle.LEFT)
                        btn_next = gb.CraftingButton("NEXT")
            # Footer
            with gb.ShadedRow(spacing=25):
                with gb.Column(width=200):
                    btn_left = gb.CraftingButton("MOVE LEFT", width=165, style=gb.CraftingButtonStyle.LEFT)
                    btn_right = gb.CraftingButton("MOVE RIGHT", width=165)
                    btn_expand = gb.CraftingButton("EXPAND COLUMN", width=165)
                    btn_narrow = gb.CraftingButton("NARROW COLUMN", width=165)
                with gb.Column(width=200):
                    btn_remove = gb.CraftingButton("REMOVE COLUMN", width=165)
                    btn_exit = gb.CraftingButton("EXIT", width=165, style=gb.CraftingButtonStyle.X)

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

            # Handle response
            block, response = gb.launch()
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
            if block == btn_left:
                if col_idx > 0:
                    sheet.columns[col_idx], sheet.columns[col_idx - 1] = sheet.columns[col_idx - 1], sheet.columns[col_idx]
                    Misc.SendMessage(f"Column {col_idx+1} moved left.", 68)
                    return
                else:
                    Misc.SendMessage("This column is already the leftmost column.", 0x21)
                return
            if block == btn_right:
                if col_idx < len(sheet.columns) - 1:
                    sheet.columns[col_idx], sheet.columns[col_idx + 1] = sheet.columns[col_idx + 1], sheet.columns[col_idx]
                    Misc.SendMessage(f"Column {col_idx+1} moved right.", 68)
                    return
                else:
                    Misc.SendMessage("This column is already the rightmost column.", 0x21)
            if block == btn_narrow:
                width = col.metadata.get("width", ExplorerSheetView.COL_WIDTH)
                if width > 50:
                    col.metadata["width"] = width - 10
                else:
                    Misc.SendMessage("Column width cannot be less than 50px.", 0x21)
                return
            if block == btn_expand:
                width = col.metadata.get("width", ExplorerSheetView.COL_WIDTH)
                if width < 500:
                    col.metadata["width"] = width + 10
                else:
                    Misc.SendMessage("Column width cannot be more than 500px.", 0x21)
                return
            return

    @staticmethod
    def rename_save(sheet: Sheet):
        """
        Show the edit/save gump for the given sheet.
        Here you can change the sheet name or export the sheet.
        """
        gb = SheetBuilder(id="SheetSaveGump")
        with gb.MinimalFrame():
            gb.Html("Rename/Export Sheet", width=320, centered=True, color="#FFFFFF")
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
                Misc.SendMessage("The edit/export has been cancelled.", 0x3B2)
                return
            if block == btn_rename:
                sheet.name = name.text.strip()
                Misc.SendMessage(f"The sheet has been renamed to: {sheet.name}", 68)
                return
            if block == btn_export:
                sheet.name = name.text.strip()
                Explorer.export_to_csv(sheet, verbose=chk_verbose.checked)
                return

    @staticmethod
    def manage_columns(sheet_header: Sheet, setting: Dict[str, Any]) -> bool:
        """
        Manage saved column configurations.

        :param sheet: The sheet to manage columns for.
        :param setting: The setting dictionary to store/load configurations.
        :return: True if the sheet was modified, False otherwise.
        """
        # Build the gump
        gb = SheetBuilder(id="ColumnConfigGump")
        with gb.MainFrame():
            # Header
            with gb.ShadedColumn(halign="center"):
                gb.Html("MANAGE COLUMN CONFIGURATION", centered=True, color="#FFFFFF")
            # Body
            with gb.ShadedColumn():
                btn_select = []
                with gb.Column(spacing=5) as c:
                    config_col = c
                with gb.Row(spacing=5):
                    btn_new = gb.Checkbox(checked=False)
                    gb.Text("(New)", 67, cropped=True, tooltip="This is an empty configuration. You can save the current configuration to this entry.")
            # Footer
            with gb.ShadedColumn():
                with gb.Row():
                    with gb.Column(width=150, spacing=5):
                        btn_save = gb.CraftingButton("SAVE", width=115, tooltip="Save the current configuration.")
                        btn_load = gb.CraftingButton("LOAD", width=115, tooltip="Load the selected configuration.")
                    with gb.Column(width=150, spacing=5):
                        btn_move_up = gb.CraftingButton("MOVE UP", width=115, tooltip="Move the selected configuration up in the list.")
                        btn_move_down = gb.CraftingButton("MOVE DOWN", width=115, tooltip="Move the selected configuration down in the list.")
                with gb.Row():
                    btn_rename = gb.CraftingButton("RENAME:", width=60, tooltip="Rename the selected configuration.")
                    name_entry = gb.TextEntry("", width=200, hue=87, max_length=64, tooltip="Enter the new name for the selected configuration here.")
                with gb.Row():
                    with gb.Column(width=150, spacing=5):
                        btn_delete = gb.CraftingButton("DELETE", width=115, tooltip="Delete the selected configuration.")
                    with gb.Column(width=150, spacing=5):
                        btn_exit = gb.CraftingButton("EXIT", width=115, style=gb.CraftingButtonStyle.X, tooltip="Exit this dialog.")

        selected_index = -1
        while True:
            # Populate configurations column
            config_col.clear_children()
            gb.current = config_col
            saved_configs = setting.setdefault("saved_configs", [])
            for i, config in enumerate(saved_configs):
                if "name" not in config:
                    continue
                name = config["name"]
                cols = Explorer.parse_column_setting(config.get("columns", []))
                txt_tooltip = "Name : " + name + "<BR>Columns: " + ", ".join(col.id for col in cols.columns) if cols.columns else "(No columns)"
                with gb.Row(spacing=5):
                    btn_select.append(gb.Checkbox(checked=(i == selected_index)).on_click(i))
                    gb.Text(name, hue=(87 if i == selected_index else 1152), width=250, cropped=True, tooltip=txt_tooltip)

            block, response = gb.launch()

            if block == btn_exit or block is None:
                return False
            if block == btn_save:
                if len(sheet_header.columns) == 0:
                    Misc.SendMessage("Cannot save an empty configuration.", 0x21)
                    continue
                if btn_new.checked:
                    name = name_entry.text.strip() or "(Unnamed)"
                    config = Explorer.encode_column_setting(sheet_header)
                    saved_configs.append({"name": name, "columns": config})
                    Explorer.export_setting(sheet_header, setting)
                    Misc.SendMessage(f"The current configuration has been added to the list.", 68)
                else:
                    if selected_index < 0 or selected_index >= len(saved_configs):
                        Misc.SendMessage("No configuration selected.", 0x21)
                        continue
                    config = saved_configs[selected_index]
                    confirm = Explorer.confirm(
                        f"This action will overwrite the selected configuration:<br>'{config['name']}'<br>Are you sure you want to proceed?",
                        yes_text="Save",
                        no_text="Cancel",
                        height=88,
                    )
                    if not confirm:
                        continue
                    config["name"] = name_entry.text.strip() or "(Unnamed)"
                    config["columns"] = Explorer.encode_column_setting(sheet_header)
                    Explorer.export_setting(sheet_header, setting)
                    Misc.SendMessage(f"The configuration '{config['name']}' has been updated.", 68)
                continue
            if block == btn_load:
                if selected_index < 0 or selected_index >= len(saved_configs):
                    Misc.SendMessage("No configuration selected.", 0x21)
                    continue
                config = saved_configs[selected_index]
                cols = Explorer.parse_column_setting(config.get("columns", []))
                if len(cols.columns) == 0:
                    Misc.SendMessage("The selected configuration is empty.", 0x21)
                    continue
                confirm = Explorer.confirm(
                    f"This action will replace the current column configuration with:<br>'{config['name']}'<br>Are you sure you want to proceed?",
                    yes_text="Load",
                    no_text="Cancel",
                    height=88,
                )
                sheet_header.columns.clear()
                sheet_header.columns.extend(cols.columns)
                Misc.SendMessage(f"The configuration '{config['name']}' has been loaded.", 68)
                return True
            if block == btn_delete:
                if selected_index < 0 or selected_index >= len(saved_configs):
                    Misc.SendMessage("No configuration selected.", 0x21)
                    continue
                confirm = Explorer.confirm(
                    f"This action will permanently delete the configuration:<br>'{saved_configs[selected_index]['name']}'<br>Are you sure you want to proceed?",
                    yes_text="Delete",
                    no_text="Cancel",
                    height=88,
                )
                if confirm:
                    config = saved_configs.pop(selected_index)
                    Explorer.export_setting(sheet_header, setting)
                    Misc.SendMessage(f"The configuration '{config['name']}' has been deleted.", 68)
                    selected_index = -1
                continue
            if block == btn_rename:
                if selected_index < 0 or selected_index >= len(saved_configs):
                    Misc.SendMessage("No configuration selected.", 0x21)
                    continue
                new_name = name_entry.text.strip()
                if not new_name:
                    Misc.SendMessage("The new name cannot be empty.", 0x21)
                    continue
                config = saved_configs[selected_index]
                old_name = config["name"]
                config["name"] = new_name
                Explorer.export_setting(sheet_header, setting)
                Misc.SendMessage(f"The configuration '{old_name}' has been renamed to '{new_name}'.", 68)
                name_entry.text = new_name
                continue
            if block == btn_move_up:
                if selected_index < 0 or selected_index >= len(saved_configs):
                    Misc.SendMessage("No configuration selected.", 0x21)
                    continue
                if selected_index == 0:
                    Misc.SendMessage("The selected configuration is already at the top.", 0x21)
                    continue
                saved_configs[selected_index], saved_configs[selected_index - 1] = saved_configs[selected_index - 1], saved_configs[selected_index]
                selected_index -= 1
                Explorer.export_setting(sheet_header, setting)
                Misc.SendMessage("The selected configuration has been moved up.", 68)
                continue
            if block == btn_move_down:
                if selected_index < 0 or selected_index >= len(saved_configs):
                    Misc.SendMessage("No configuration selected.", 0x21)
                    continue
                if selected_index == len(saved_configs) - 1:
                    Misc.SendMessage("The selected configuration is already at the bottom.", 0x21)
                    continue
                saved_configs[selected_index], saved_configs[selected_index + 1] = saved_configs[selected_index + 1], saved_configs[selected_index]
                selected_index += 1
                Explorer.export_setting(sheet_header, setting)
                Misc.SendMessage("The selected configuration has been moved down.", 68)
                continue
            if block == btn_new:
                if btn_new.checked:
                    selected_index = -1
                    name_entry.text = "(Unnamed)"
                continue
            if block in btn_select:
                if not isinstance(response, int):
                    continue
                selected_index = response
                if not (0 <= selected_index < len(saved_configs)):
                    selected_index = -1
                    continue
                btn_new.checked = False
                name_entry.text = saved_configs[selected_index]["name"]
                continue

    @staticmethod
    def load_contents(serial: int, sheet_header: Sheet, show_loading: bool = True) -> Optional[Sheet]:
        """
        Load the contents of a container into a sheet.

        :param serial: The serial of the container to load.
        :param sheet_header: The header of the sheet to use.
        :param show_loading: Whether to show the loading screen.
        :return: The loaded sheet, or None if failed.
        """
        # Open the container
        cont = Items.FindBySerial(serial)
        if cont is None:
            return None
        if cont.ItemID in (0x9F1C, 0x9F1D):
            Items.UseItem(cont)
            Misc.Pause(500)
        else:
            Items.WaitForContents(serial, 1000)

        # Create an unfiltered sheet using the provided header and the container's contents
        sheet = Sheet(name=sheet_header.name)
        sheet.columns = sheet_header.columns

        # Show the loading screen
        for row in cont.Contains:
            if show_loading and not Timer.Check("update-loading"):
                progress = len(sheet.rows) / max(1, len(cont.Contains))
                ExplorerSheetView.show_loading(progress=progress)
                Timer.Create("update-loading", 250)
            sheet.add_row_by_serial(row.Serial)

        ExplorerSheetView.close()
        return sheet

    @staticmethod
    def explorer(serial: int, sheet_header: Sheet, setting: Dict[str, Any]) -> Optional[Sheet]:
        """
        The main loop of the explorer.

        :param serial: The serial of the container to explore.
        :param sheet_header: The header of the sheet to use.
        :param setting: The current setting to save changes to.
        """
        sheet: Optional[Sheet] = None
        sorted_sheet: Optional[Sheet] = None
        col_precedence: List[Optional[int]] = []
        col_sorted: List[SheetColumn] = []
        page: int = 0
        while True:
            # Load the sheet if not already loaded
            if sheet is None:
                sheet = Explorer.load_contents(serial, sheet_header)
                sorted_sheet = None
                if sheet is None:
                    Misc.SendMessage("Failed to load the container.", 0x21)
                    return None

            # Check if the sheet is empty
            if len(sheet.rows) == 0:
                Misc.SendMessage("Either the container is empty or the items have not been loaded yet.", 0x3B2)
                return None

            # Sort the sheet if not already sorted
            if sorted_sheet is None:
                sorted_sheet = sheet
                # Sort the columns according to the update time
                idxcol_sorted = sorted(enumerate(sheet.columns), key=lambda c: c[1].metadata.get("update_time", 0))
                col_sorted = list(map(lambda c: c[1], idxcol_sorted))
                # Calculate column precedence and sort the sheet
                col_precedence: List[Optional[int]] = [None] * len(idxcol_sorted)
                for i, idxcol in enumerate(idxcol_sorted):
                    idx, col = idxcol
                    if "update_time" in col.metadata:
                        col_precedence[idx] = len(idxcol_sorted) - i
                        sorted_sheet = col.filter(sorted_sheet)

            # Ensure the current page is within bounds
            last_page = (len(sorted_sheet.rows) - 1) // ExplorerSheetView.ITEMS_PER_PAGE
            if page > last_page:
                page = last_page
            if page < 0:
                page = 0

            esv = ExplorerSheetView(sorted_sheet, col_precedence, page)

            block, response = esv.gb.launch()
            if block == esv.menu_refresh:
                sheet = None
                continue
            if block == esv.menu_export:
                Explorer.rename_save(sorted_sheet)
                sheet_header.name = sorted_sheet.name
                continue
            if block == esv.menu_columns:
                modified = Explorer.manage_columns(sheet_header, setting)
                if modified:
                    sorted_sheet = None
                continue
            if block == esv.menu_prev:
                if page > 0:
                    page -= 1
                continue
            if block == esv.menu_next:
                if page < esv.total_pages - 1:
                    page += 1
                continue
            if block in esv.menu_item_action:
                if not isinstance(response, ItemPropRow):
                    Misc.SendMessage("Invalid row.", 0x21)
                    continue
                row = response
                Explorer.item_action(row)
                sheet = None
                continue
            if block in esv.menu_edit_column:
                if not isinstance(response, int):
                    Misc.SendMessage("Invalid column index.", 0x21)
                    continue
                j = response
                Explorer.edit_column(j, sheet)
                sorted_sheet = None
                continue
            if block in esv.menu_sort_column:
                if not isinstance(response, int):
                    Misc.SendMessage("Invalid column index.", 0x21)
                    continue
                j = response
                col = sheet.columns[j]
                col_last = col_sorted[-1] if col_sorted else None  # Last updated column, if any (note that the sheet has no columns)
                # Toggle the sort order only when it is updated most recently
                if col_last == col:
                    if col.is_unsorted():
                        col.sort_order = SortOrder.ASCENDING
                    else:
                        col.toggle_reverse()
                col.metadata["update_time"] = time.time()
                sorted_sheet = None
                continue
            if block == esv.menu_new_column:
                # The added column is initially of the least priority in the sort orders
                sheet_header.add_column_by_id("Name", {"update_time": 0})
                sorted_sheet = None
                continue
            return None

    @staticmethod
    def dialog_shortcut() -> Any:
        """
        A minimized gump to quickly open the explorer.
        """

        gb = SheetBuilder(id="SheetShortcutGump")
        with gb.MinimalFrame():
            gb.Html("Item Explorer", centered=True, color="#FFFFFF", width=125)
            gb.UOStoreButton("Inspect", tooltip="Inspect the target container's contents.").on_click(True)

        _, response = gb.launch()
        return response


################################################################################
# Top-Level Logic
################################################################################


if Player.Connected:
    # Load the saved setting if any, and add the columns to the sheet header
    setting = Explorer.import_setting() or {}
    if setting is not None and "columns" in setting:
        sheet_header = Explorer.parse_column_setting(setting["columns"])
    else:
        sheet_header = Sheet()
        sheet_header.add_column_by_id("Rarity", {"update_time": time.time()})
        sheet_header.add_column_by_id("Name", {"update_time": 0})

    # Main loop
    while Player.Connected:
        # Wait for the user's input on the shortcut gump
        response = Explorer.dialog_shortcut()
        if not response:
            continue

        # If the user wants to inspect a container, prompt for it
        serial = Target.PromptTarget("Select the container to inspect.", 1153)
        if serial == 0:
            continue

        # Start the exploration loop
        sheet_header.name = f"Untitled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        Explorer.explorer(serial, sheet_header, setting)
        Explorer.export_setting(sheet_header, setting)
