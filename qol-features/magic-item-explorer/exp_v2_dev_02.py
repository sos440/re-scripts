################################################################################
# Imports
################################################################################

from AutoComplete import *
from typing import List, Tuple, Dict, Optional
import os
import sys
import re
import time
import csv

# This allows the RazorEnhanced to correctly identify the path of the module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

from exp_module import ItemPropRow, BaseProp, PropMaster, SheetColumn, Sheet


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
        return hash(name) & 0xFFFFFFFF

    @staticmethod
    def tooltip_to_itemproperty(gd: Gumps.GumpData) -> str:
        """
        Converts integer-argument tooltips to item properties.
        """
        return re.sub(r"\{ tooltip (\d+) \}", r"{ itemproperty \1 }", gd.gumpDefinition)


# Gump ID
MAIN_GUMP_ID = GumpTools.hashname("ExplorerMainGump")
ACTION_GUMP_ID = GumpTools.hashname("ExplorerActionGump")
FILTER_GUMP_ID = GumpTools.hashname("ExplorerFilterGump")
SHORTCUT_GUMP_ID = GumpTools.hashname("ExplorerShortcutGump")

# Explorer gump settings
ROW_HEIGHT = 60
COL_WIDTH = 150
MENU_HEIGHT = 30
HEADER_HEIGHT = 30
BORDER_WIDTH = 10
ITEMS_PER_PAGE = 10

# Button IDs
ID_MAIN_REFRESH = 1
ID_MAIN_EXPORT = 2
ID_MAIN_TITLE = 3

IDMOD_MAIN_ACTION = 1000
IDMOD_MAIN_SORT = 2000
IDMOD_MAIN_FILTER = 3000

ID_ACTION_PICKUP = 1000
ID_ACTION_USE = 1001
ID_ACTION_EQUIP = 1002

ID_FILTER_REMOVE = 10001
IDMOD_FILTER_GROUP = 11000
IDMOD_FILTER_CHANGE = 12000

ID_SHORTCUT_INSPECT = 1

# Gump wrapping text
GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""


class ExplorerDialog:
    @staticmethod
    def show_item_actions(row: ItemPropRow):
        Gumps.CloseGump(ACTION_GUMP_ID)
        gd = Gumps.CreateGump(True)

        # Main page layout
        INNER_WIDTH = 160
        INNER_HEIGHT = 218
        WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
        HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT

        # Background
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)
        x, y = BORDER_WIDTH, BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, INNER_HEIGHT, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, INNER_HEIGHT)

        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 100, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 100)
        px, py = GumpTools.get_centering_pos(row["Type"], x, y, INNER_WIDTH, 100)
        Gumps.AddItem(gd, px, py, row["Type"], row["Color"])
        Gumps.AddTooltip(gd, row["Serial"])

        y += 105
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 113, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 113)
        x += 5
        y += 5
        Gumps.AddButton(gd, x, y, 4005, 4007, ID_ACTION_PICKUP, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Move to Backpack")
        y += 27
        Gumps.AddButton(gd, x, y, 4005, 4007, ID_ACTION_USE, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Use")
        y += 27
        Gumps.AddButton(gd, x, y, 4005, 4007, ID_ACTION_EQUIP, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Equip")
        y += 27
        Gumps.AddButton(gd, x, y, 4014, 4016, 0, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y + 2, 100, 18, 1153, "Return")

        # Send gump
        gd_gumpdef = GumpTools.tooltip_to_itemproperty(gd)
        Gumps.SendGump(ACTION_GUMP_ID, Player.Serial, 100, 100, gd_gumpdef, gd.gumpStrings)

    @staticmethod
    def show_filter(col_idx: int, col: SheetColumn, group_idx: Optional[int] = None):
        Gumps.CloseGump(FILTER_GUMP_ID)
        gd = Gumps.CreateGump(True)

        all_items = list(PropMaster.ALL_PROPS.iter_group())
        cur_group = None
        cur_props = []
        if group_idx is not None and 0 <= group_idx < len(all_items):
            cur_group = all_items[group_idx]
            cur_props = list(cur_group.iter_prop())

        # Main page layout
        INNER_WIDTH = 400
        INNER_HEIGHT = 70 + 27 * max(11, len(all_items) + 2)
        WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
        HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT

        # Background
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)
        x, y = BORDER_WIDTH, BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, INNER_HEIGHT, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, INNER_HEIGHT)
        x += 5
        y += 5

        # Title
        Gumps.AddHtml(gd, x, y, INNER_WIDTH - 10, 22, GUMP_WT.format(text=f"COLUMN {col_idx+1}: {col.id}"), False, False)
        y += 30

        # Group Section
        Gumps.AddHtml(gd, x, y, 195, 22, GUMP_WT.format(text="GROUPS"), False, False)
        y_g = y + 30
        for i, group in enumerate(all_items):
            Gumps.AddButton(gd, x, y_g, 4005, 4007, IDMOD_FILTER_GROUP + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 35, y_g + 2, 180, 18, 1153, group.name)
            y_g += 27
        y_g += 27
        Gumps.AddButton(gd, x, y_g, 4017, 4019, ID_FILTER_REMOVE, 1, 0)
        Gumps.AddLabelCropped(gd, x + 35, y_g + 2, 100, 18, 1153, "REMOVE")

        # Properties Section
        x = 200
        Gumps.AddHtml(gd, x, y, 195, 22, GUMP_WT.format(text="PROPERTIES"), False, False)
        PROPS_PER_PAGE = max(10, len(all_items))
        TOTAL_PAGES = (len(cur_props) + PROPS_PER_PAGE - 1) // PROPS_PER_PAGE
        for i, prop in enumerate(cur_props):
            page = i // PROPS_PER_PAGE
            i_rel = i % PROPS_PER_PAGE
            if i_rel == 0:
                y_g = y + 30
                page_1based = page + 1
                Gumps.AddPage(gd, page_1based)
                y_p = y + 30 + 27 * PROPS_PER_PAGE
                if page_1based > 1:
                    Gumps.AddButton(gd, x, y_p, 4014, 4016, 0, 0, page_1based - 1)
                    Gumps.AddLabelCropped(gd, x + 35, y_p + 2, 180, 18, 1153, "PREV")
                if page_1based < TOTAL_PAGES:
                    Gumps.AddButton(gd, x + 100, y_p, 4005, 4007, 0, 0, page_1based + 1)
                    Gumps.AddLabelCropped(gd, x + 135, y_p + 2, 180, 18, 1153, "NEXT")
            Gumps.AddButton(gd, x, y_g, 4005, 4007, IDMOD_FILTER_CHANGE + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 35, y_g + 2, 180, 18, 1153, prop.name)
            y_g += 27

        Gumps.SendGump(FILTER_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    @staticmethod
    def show_sheet(sheet: Optional[Sheet] = None) -> Optional[Sheet]:
        Gumps.CloseGump(MAIN_GUMP_ID)
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
        if sheet is None:
            Gumps.AddImageTiled(gd, BORDER_WIDTH, BORDER_WIDTH, INNER_WIDTH, INNER_HEIGHT, 9274)
            Gumps.AddAlphaRegion(gd, BORDER_WIDTH, BORDER_WIDTH, INNER_WIDTH, INNER_HEIGHT)
            Gumps.AddHtml(gd, BORDER_WIDTH, HEIGHT // 2 - 11, INNER_WIDTH, 22, GUMP_WT.format(text="Loading..."), False, False)
            Gumps.SendGump(MAIN_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
            return

        # Sort the columns according to the update time
        col_sorted = sorted(sheet.columns, key=lambda c: c.metadata.get("update_time", 0))
        for col in col_sorted:
            if "update_time" in col.metadata:
                sheet = col.filter(sheet)

        # Menubar
        x = BORDER_WIDTH
        y = BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, MENU_HEIGHT, 9354)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, MENU_HEIGHT)
        x += 5
        y += 4
        Gumps.AddButton(gd, x, y, 1531, 1532, ID_MAIN_REFRESH, 1, 0)
        Gumps.AddLabelCropped(gd, x + 25, y + 2, 100, 18, 1153, "Refresh")
        x += 100
        Gumps.AddButton(gd, x, y, 1533, 1534, ID_MAIN_EXPORT, 1, 0)
        Gumps.AddLabelCropped(gd, x + 25, y + 2, 100, 18, 1153, "Export")
        x += 100
        Gumps.AddTextEntry(gd, x, y + 2, 200, 18, 1153, ID_MAIN_TITLE, sheet.name)

        # Column headers
        x = BORDER_WIDTH
        y = BORDER_WIDTH + MENU_HEIGHT + 5
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, HEADER_HEIGHT, 3004)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, HEADER_HEIGHT)
        Gumps.AddImageTiled(gd, x, y, 80, HEADER_HEIGHT, 9354)
        x += 81
        dy = (HEADER_HEIGHT - 18) // 2
        for i, col in enumerate(sheet.columns):
            Gumps.AddImageTiled(gd, x, y, COL_WIDTH - 1, HEADER_HEIGHT, 9354)
            Gumps.AddButton(gd, x + 4, y + dy + 2, 1209, 1210, IDMOD_MAIN_FILTER + i, 1, 0)
            Gumps.AddLabelCropped(gd, x + 22, y + dy, COL_WIDTH - 30, 18, 58, col.id)
            if col.is_reverse():
                Gumps.AddButton(gd, x + COL_WIDTH - 15, y + dy + 4, 2437, 2438, IDMOD_MAIN_SORT + i, 1, 0)
            else:
                Gumps.AddButton(gd, x + COL_WIDTH - 15, y + dy + 4, 2435, 2436, IDMOD_MAIN_SORT + i, 1, 0)
            x += COL_WIDTH
        Gumps.AddImageTiled(gd, x, y, 22, HEADER_HEIGHT, 9354)
        Gumps.AddButton(gd, x + 4, y + dy + 2, 1209, 1210, IDMOD_MAIN_FILTER + len(sheet.columns), 1, 0)

        # Ruled sheet
        x = BORDER_WIDTH
        y = BORDER_WIDTH + MENU_HEIGHT + 5 + HEADER_HEIGHT + 1
        for j in range(ITEMS_PER_PAGE):
            Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, ROW_HEIGHT, 9274)
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
                    if rarity == 0:
                        value_color = 905
                    elif rarity == 1:
                        value_color = 72
                    elif rarity == 2:
                        value_color = 89
                    elif rarity == 3:
                        value_color = 4
                    elif rarity == 5:
                        value_color = 13
                    elif rarity == 6:
                        value_color = 53
                    elif rarity == 7:
                        value_color = 43
                    elif rarity == 8:
                        value_color = 33
                value = col.read(row) or ""
                Gumps.AddLabelCropped(gd, x + 4, y, COL_WIDTH - 10, 18, value_color, value)
                Gumps.AddTooltip(gd, f"{col.name}: {value}")
                x += COL_WIDTH

        # Send gump
        gd_gumpdef = GumpTools.tooltip_to_itemproperty(gd)
        Gumps.SendGump(MAIN_GUMP_ID, Player.Serial, 100, 100, gd_gumpdef, gd.gumpStrings)
        return sheet

    @staticmethod
    def shortcut() -> None:
        Gumps.CloseGump(SHORTCUT_GUMP_ID)

        # Create the gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
        Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

        Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Item Explorer"), False, False)

        Gumps.AddButton(gd, 10, 30, 40021, 40031, ID_SHORTCUT_INSPECT, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text="Inspect"), False, False)

        # Send the gump and listen for the response
        Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


class ExplorerHandlers:
    @staticmethod
    def actions(row: ItemPropRow):
        ExplorerDialog.show_item_actions(row)

        if not Gumps.WaitForGump(ACTION_GUMP_ID, 1000 * 60 * 60):
            return
        gd = Gumps.GetGumpData(ACTION_GUMP_ID)
        if not gd:
            return
        if gd.buttonid == 0:
            return
        if gd.buttonid == ID_ACTION_PICKUP:
            Items.Move(row["Serial"], Player.Backpack.Serial, -1)
            return
        if gd.buttonid == ID_ACTION_USE:
            Items.UseItem(row["Serial"])
            return
        if gd.buttonid == ID_ACTION_EQUIP:
            Player.EquipItem(row["Serial"])
            return

    @staticmethod
    def filter(col_idx: int, sheet: Sheet):
        col = sheet.columns[col_idx]
        group_idx = None
        all_items = list(PropMaster.ALL_PROPS.iter_group())
        while True:
            ExplorerDialog.show_filter(col_idx, col, group_idx)
            if not Gumps.WaitForGump(FILTER_GUMP_ID, 1000 * 60 * 60):
                return
            gd = Gumps.GetGumpData(FILTER_GUMP_ID)
            if not gd:
                return

            if gd.buttonid == 0:
                return

            # Check if the user wants to remove the column
            if gd.buttonid == ID_FILTER_REMOVE:
                sheet.columns.pop(col_idx)
                return

            # Calculate current group and properties
            cur_group = None
            cur_props = []
            if group_idx is not None and 0 <= group_idx < len(all_items):
                cur_group = all_items[group_idx]
                cur_props = list(cur_group.iter_prop())

            # Check if the user wants to change the filter
            id_change = gd.buttonid - IDMOD_FILTER_CHANGE
            if 0 <= id_change < len(cur_props):
                col.prop = cur_props[id_change]
                # col.metadata["update_time"] = time.time()
                return

            # Check if the user wants to select a group
            id_group = gd.buttonid - IDMOD_FILTER_GROUP
            if 0 <= id_group < len(all_items):
                group_idx = id_group
                continue

    @staticmethod
    def export_to_csv(sheet: Sheet):
        # Escape the sheet name so it can be used as a filename
        filename = re.sub(r"[^\w\s-]", "_", sheet.name)
        os.makedirs("Data/Sheets", exist_ok=True)
        filepath = f"Data/Sheets/{filename}.csv"

        with open(filepath, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header
            csvwriter.writerow([col.name for col in sheet.columns])
            # Write rows
            for row in sheet.rows:
                csvwriter.writerow([col.read(row) for col in sheet.columns])
        Misc.SendMessage(f"The sheet has been exported to: {filepath}", 1153)

    @staticmethod
    def explorer(serial: int, old_sheet: Optional[Sheet] = None) -> Optional[Sheet]:
        cont = Items.FindBySerial(serial)
        if cont is None:
            return None
        Items.WaitForContents(serial, 1000)

        # Show the loading screen
        ExplorerDialog.show_sheet()

        # Create an "abstract" sheet that doesn't contain actual rows
        sheet = Sheet(f"Untitled_{time.time()}")
        if old_sheet is not None:
            sheet.name = old_sheet.name
            sheet.columns = old_sheet.columns
        else:
            sheet.add_column_by_id("Rarity", {"update_time": time.time()})
            sheet.add_column_by_id("Name")
            sheet.columns[0].toggle_reverse()

        # Retrieve a sorted sheet
        filtered_sheet = Sheet()
        for row in cont.Contains:
            sheet.add_row_by_serial(row.Serial)
        filtered_sheet.columns = sheet.columns
        filtered_sheet = ExplorerDialog.show_sheet(sheet)
        if filtered_sheet is None:
            return

        # Wait for the user's input
        if not Gumps.WaitForGump(MAIN_GUMP_ID, 1000 * 60 * 60):
            return

        # Parse the user's input
        gd = Gumps.GetGumpData(MAIN_GUMP_ID)
        if not gd:
            return

        sheet.name = gd.text[0]
        if gd.buttonid == 0:
            return

        if gd.buttonid == ID_MAIN_REFRESH:
            return sheet

        if gd.buttonid == ID_MAIN_EXPORT:
            ExplorerHandlers.export_to_csv(filtered_sheet)
            return sheet

        id_action = gd.buttonid - IDMOD_MAIN_ACTION
        is_action = 0 <= id_action < len(filtered_sheet.rows)
        if is_action:
            row = filtered_sheet.rows[id_action]
            ExplorerHandlers.actions(row)
            return sheet

        id_sort = gd.buttonid - IDMOD_MAIN_SORT
        if 0 <= id_sort < len(sheet.columns):
            col = sheet.columns[id_sort]
            col_sorted = sorted(sheet.columns, key=lambda c: c.metadata.get("update_time", 0))
            col_last = col_sorted[-1] if col_sorted else None
            # Toggle the sort order only when it is updated most recently
            if col_last == col:
                col.toggle_reverse()
            col.metadata["update_time"] = time.time()
            return sheet

        id_filter = gd.buttonid - IDMOD_MAIN_FILTER
        if 0 <= id_filter < len(sheet.columns):
            ExplorerHandlers.filter(id_filter, sheet)
            return sheet
        if id_filter == len(sheet.columns):
            # The added column is initially of the least priority in the sort orders
            sheet.add_column_by_id("Name")
            return sheet


################################################################################
# Top-Level Logic
################################################################################


if Player.Connected:
    open_next = True
    old_sheet = None
    while Player.Connected:
        if open_next:
            ExplorerDialog.shortcut()
            open_next = False
        if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, 100):
            continue

        open_next = True
        gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
        if not gd or gd.buttonid != ID_SHORTCUT_INSPECT:
            continue

        serial = Target.PromptTarget("Select the container to inspect.", 1153)
        if serial == 0:
            continue

        while True:
            old_sheet = ExplorerHandlers.explorer(serial, old_sheet)
            if old_sheet is None:
                break
