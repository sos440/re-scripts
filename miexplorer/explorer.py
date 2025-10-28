################################################################################
# Settings
################################################################################

VERSION = "2.1.3"
EXPORT_PATH = "Data/Sheets"
SETTING_PATH = "Data/Sheets/setting.json"

################################################################################
# Imports
################################################################################

import os
import sys

# Ensure we can import from the current directory
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(SCRIPT_DIR)

# Remove old gumpradio module if exists, ensuring the newer version is used
old_script = os.path.join(SCRIPT_DIR, "modules", "gumpradio.py")
if os.path.exists(old_script):
    os.remove(old_script)

# Import
from modules import *


from AutoComplete import *
from typing import List, Dict, Set, Tuple, Any, Optional, Iterable
import time
import csv
import re
import json
from datetime import datetime
from enum import Enum


################################################################################
# Gumpradio Extensions
################################################################################


################################################################################
# Gumps and Handlers
################################################################################


class ExplorerSheetView:
    MAIN_GUMP_ID = hash("ExplorerMainGump") & 0xFFFFFFFF
    COL_WIDTH = 150
    HEADER_HEIGHT = 30
    ITEMS_PER_PAGE = 10
    RARITY_COLOR_MAP = {1: 905, 2: 72, 3: 89, 4: 4, 5: 0x3B2, 6: 13, 7: 53, 8: 43, 9: 33}

    class Mode(Enum):
        NORMAL = 1
        BATCH = 2

    @classmethod
    def close(cls):
        Gumps.CloseGump(cls.MAIN_GUMP_ID)

    @classmethod
    def show_loading(cls, progress: float = 0.0):
        gb = CraftingGumpBuilder(id=cls.MAIN_GUMP_ID)
        with gb.MainFrame():
            with gb.ShadedColumn():
                gb.Html(f"Loading... ({progress:.1%})", width=200, centered=True, color="#FFFFFF")
                gb.ProgressBar(width=200, height=22, progress=progress)
        gb.launch()

    def _build_menubar(self, gb: CraftingGumpBuilder):
        with gb.Column(background="tiled:9354", padding=(10, 5), spacing=5, halign="left"):
            # Title
            with gb.Row():
                gb.Text(f"Name: {self.sheet.name}", hue=0, width=400)
            # Menu buttons
            with gb.Row():
                self.menu_refresh = gb.MenuItem("Refresh", style="view", tooltip="This sheet does not auto-refresh. Click this button to reload the contents of the container.")
                self.menu_export = gb.MenuItem("Rename/Export", width=120, style="write", tooltip="Rename the sheet or export it to a CSV file.")
                self.menu_columns = gb.MenuItem("Load/Save Columns", width=150, style="write", tooltip="Load or save column configurations.")
                if self.mode == self.Mode.NORMAL:
                    self.menu_batch = gb.MenuItem("Batch Actions", width=120, style="double_right", tooltip="Switch to batch action mode, allowing selection of multiple items.")
                else:
                    self.menu_batch = gb.MenuItem("Individual Actions", width=120, style="double_right", tooltip="Switch to individual action mode.")

    def _build_column_header(self, gb: CraftingGumpBuilder):
        with gb.Row(spacing=1):
            # Navigation buttons
            with gb.Row(background="tiled:9354", width=80, height=self.HEADER_HEIGHT):
                self.menu_prev = gb.MenuItem("", style="single_left")
                gb.Html(f"{self.page+1}/{self.total_pages}", centered=True, width=50, height=18)
                self.menu_next = gb.MenuItem("", style="single_right")
            # Column headers
            self.menu_edit_column = []
            self.menu_sort_column = []
            for j, col in enumerate(self.sheet.columns):
                width = col.metadata.get("width", self.COL_WIDTH)
                with gb.Row(background="tiled:9354", width=width, height=self.HEADER_HEIGHT, padding=(5, 0), spacing=2):
                    # Edit button
                    btn_edit = gb.BlueJewelButton().on_click(j)
                    self.menu_edit_column.append(btn_edit)
                    # Column name
                    if col.filter:
                        gb.Html(f"{col.id}*", width=width - 37, height=18, tooltip=f"{col.name} (Filtered)")
                    else:
                        gb.Html(col.id, width=width - 37, height=18, tooltip=col.name)
                    # Sort button
                    if self.col_precedence[j] is None or col.sort_order == SortOrder.UNSORTED:
                        btn_sort = gb.SortButton(style="asc", tooltip="Not sorted")
                    elif col.sort_order == SortOrder.ASCENDING:
                        btn_sort = gb.SortButton(style="asc", tooltip=f"Order: Ascending<BR>Precedence: {self.col_precedence[j]}")
                    elif col.sort_order == SortOrder.DESCENDING:
                        btn_sort = gb.SortButton(style="dec", tooltip=f"Order: Descending<BR>Precedence: {self.col_precedence[j]}")
                    else:
                        raise ValueError("Invalid sort order")
                    btn_sort.on_click(j)
                    self.menu_sort_column.append(btn_sort)
            with gb.Row(background="tiled:9354", height=self.HEADER_HEIGHT, padding=(5, 0), spacing=2):
                self.menu_new_column = gb.BlueJewelButton(tooltip="Add Column")

    def _build_rows(self, gb: CraftingGumpBuilder):
        is_batch_mode = self.mode == self.Mode.BATCH
        self.menu_item_action = []
        for i in range(self.ITEMS_PER_PAGE):
            row_idx = self.page * self.ITEMS_PER_PAGE + i
            with gb.Row(background="tiled:2624; alpha", height=60, spacing=1):
                if row_idx >= len(self.sheet.rows):
                    continue
                row = self.sheet.rows[row_idx]
                # Item button
                self.menu_item_action.append(
                    gb.ItemDisplayButton(
                        row["Serial"],
                        checked=is_batch_mode and (row["Serial"] in self.row_selected),
                    ).on_click(row)
                )
                # Write the content of the row
                for j, col in enumerate(self.sheet.columns):
                    width = col.metadata.get("width", self.COL_WIDTH)
                    hue = 1152
                    if col.id == "Rarity":
                        rarity = row["Rarity"]
                        hue = self.RARITY_COLOR_MAP.get(rarity, 1152)
                    value = col.read(row) or ""
                    with gb.Row(width=width, padding=(10, 0, 0, 0)):
                        gb.Text(value, hue=hue, width=width - 10, tooltip=f"{col.name}: {value}", cropped=True)

    def _build_extra_frame(self, gb: CraftingGumpBuilder):
        self.menu_extra_select_all = None
        self.menu_extra_deselect_all = None
        self.menu_extra_invert = None
        self.menu_extra_move_to = None
        if self.mode == self.Mode.BATCH:
            with gb.MainFrame():
                with gb.ShadedColumn():
                    gb.Html("SELECT ITEMS", color="#FFFFFF", width=150)
                    self.menu_extra_select_all = gb.CraftingButton("Select All", width=130)
                    self.menu_extra_deselect_all = gb.CraftingButton("Deselect All", width=130)
                    self.menu_extra_invert = gb.CraftingButton("Invert Selection", width=130)
                    gb.Spacer(10)
                    gb.Html("BATCH ACTIONS", color="#FFFFFF", width=150)
                    self.menu_extra_move_to = gb.CraftingButton("Move Selected To", width=130, tooltip="Move all selected items to a target container.")

    def __init__(self, sheet: Sheet, page: int = 0, mode: Mode = Mode.NORMAL, col_precedence: Optional[List[Optional[int]]] = None, row_selected: Optional[Set[int]] = None):
        self.sheet = sheet
        self.col_precedence = col_precedence or [None] * len(sheet.columns)
        self.page = page
        self.total_pages = (len(sheet.rows) - 1) // self.ITEMS_PER_PAGE + 1
        self.mode = mode
        self.row_selected = row_selected or set()

        gb = CraftingGumpBuilder(id=self.MAIN_GUMP_ID)
        with gb.Row(valign="top"):
            # Sheet frame
            with gb.MainFrame():
                self._build_menubar(gb)
                with gb.Column(spacing=1, halign="left"):
                    self._build_column_header(gb)
                    self._build_rows(gb)
            # Extra frame on the right
            self._build_extra_frame(gb)

        self.gb = gb


class BatchMoveManager:
    class ItemNotFound(Exception):
        pass

    class ItemTooFar(Exception):
        pass

    class ContainerInfo:
        def __init__(self, serial: int, contents: int, max_contents: int, weight: float = 0.0, max_weight: float = float("inf")):
            self.serial = serial
            self.contents = contents
            self.max_contents = max_contents
            self.weight = weight
            self.max_weight = max_weight

    @classmethod
    def get_topmost_container(cls, serial: int) -> "Item":
        if serial == -1:
            raise cls.ItemNotFound("Invalid serial.")
        topmost_obj = None
        topmost_cont = None

        if Misc.IsMobile(serial):
            topmost_obj = Mobiles.FindBySerial(serial)
            if topmost_obj is None:
                raise cls.ItemNotFound("Mobile not found.")
            topmost_cont = topmost_obj.Backpack
        elif Misc.IsItem(serial):
            while True:
                topmost_cont = Items.FindBySerial(serial)
                if topmost_cont is None:
                    raise cls.ItemNotFound("Item not found.")
                if topmost_cont.OnGround:
                    topmost_obj = topmost_cont
                    break
                root_serial = topmost_cont.RootContainer
                if Misc.IsItem(root_serial):
                    serial = root_serial
                    continue
                if Misc.IsMobile(root_serial):
                    topmost_obj = Mobiles.FindBySerial(root_serial)
                    if topmost_obj is None:
                        raise cls.ItemNotFound("Container mobile not found.")
                    break
                raise cls.ItemNotFound("The item's root container is neither an item nor a mobile.")
        else:
            raise cls.ItemNotFound("This is neither an item nor a mobile.")

        if Player.DistanceTo(topmost_obj) > 2:
            raise cls.ItemTooFar("The object is too far away.")

        return topmost_cont

    @classmethod
    def get_contents(cls, serial: int) -> "BatchMoveManager.ContainerInfo":
        cont = Items.FindBySerial(serial)
        if cont is None:
            raise cls.ItemNotFound()

        Items.WaitForProps(cont.Serial, 1000)

        result = cls.ContainerInfo(cont.Serial, 0, 125)
        for line in Items.GetPropStringList(cont.Serial):
            # Read contents
            matchres = re.match(r"^contents: (\d+)/(\d+) items.*", line.lower())
            if not matchres:
                continue
            result.contents = int(matchres.group(1))
            result.max_contents = int(matchres.group(2))
            # Read weight, type 1
            matchres = re.match(r"^contents: \d+/\d+ items, (\d+)/(\d+) stones$", line.lower())
            if matchres:
                result.weight = int(matchres.group(1))
                result.max_weight = int(matchres.group(2))
                continue
            # Read weight, type 2
            matchres = re.match(r"^contents: \d+/\d+ items, (\d+) stones$", line.lower())
            if matchres:
                result.weight = int(matchres.group(1))
                continue

        return result

    @classmethod
    def execute(cls, cont_serial: int, selected: Iterable[int]):
        if cont_serial == -1:
            return
        num_items = len(list(selected))
        for i, serial in enumerate(selected):
            item = Items.FindBySerial(serial)
            if item is None:
                continue
            # Source check
            try:
                src_topcont = cls.get_topmost_container(serial)
            except cls.ItemNotFound as e:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': Source not found.", 0x21)
                break
            except cls.ItemTooFar as e:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': Source is too far away.", 0x21)
                break
            # Target check
            try:
                dest_topcont = cls.get_topmost_container(cont_serial)
            except cls.ItemNotFound as e:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': Destination not found.", 0x21)
                break
            except cls.ItemTooFar as e:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': Destination is too far away.", 0x21)
                break

            # Content and weight check
            try:
                cont_res = cls.get_contents(dest_topcont.Serial)
            except cls.ItemNotFound:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': Failed to locate the destination.", 0x21)
                break
            if cont_res is None:
                continue
            if cont_res.contents >= cont_res.max_contents:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': The destination is full.", 0x21)
                break
            if cont_res.weight + item.Weight > cont_res.max_weight:
                Misc.SendMessage(f"[{i + 1}/{num_items}] Cannot move '{item.Name}': The destination will be overweight if this item is moved.", 0x21)
                continue

            Items.Move(item.Serial, cont_serial, -1)
            Misc.SendMessage(f"[{i + 1}/{num_items}] Attempting to move '{item.Name}'.", 68)
            Misc.Pause(1000)


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
        gb = CraftingGumpBuilder(id="ConfirmGump")
        with gb.MinimalFrame():
            if title:
                gb.Html(title, width=250, centered=True, color="#FFFFFF")
            gb.Html(text, width=250, height=height, centered=centered, color="#FFFFFF")
            gb.Spacer(5)
            with gb.Row(spacing=10):
                btn_yes = gb.UOStoreButton(yes_text, style="blue")
                btn_no = gb.UOStoreButton(no_text, style="red")

        block, _ = gb.launch().wait_response().unpack()
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
            # Update filter
            try:
                if "filter" in col_json:
                    col.filter = SheetColumnFilters.from_dict(col_json["filter"])
            except:
                Misc.SendMessage(f"Failed to load filter for column '{col.id}'. The filter will be ignored.", 0x21)
            # Update sort order
            try:
                col.sort_order = SortOrder(col_json.get("sort_order", "unsorted"))
            except ValueError:
                col.sort_order = col.prop.default_order
            sheet_header.add_column(col)
        return sheet_header

    @staticmethod
    def encode_column_setting(sheet: Sheet) -> List[Dict[str, Any]]:
        result = []
        for col in sheet.columns:
            col_encoded = {
                "id": col.id,
                "sort_order": col.sort_order.value,
                "metadata": dict(col.metadata),
            }
            if col.filter is not None:
                col_encoded["filter"] = col.filter.to_dict()
            result.append(col_encoded)
        return result

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
    def batch_move_to(cls, selected: Set[int]):
        """
        Move all selected items in the sheet to a target container.
        """
        if len(selected) == 0:
            Misc.SendMessage("No items selected.", 0x21)
            return
        target = Target.PromptTarget("Select the destination to move the selected items.", 0x3B2)
        BatchMoveManager.execute(target, selected)

    @classmethod
    def item_action(cls, row: ItemPropRow):
        """
        Shows the possible intreractions with the item for the given row.
        """
        # Build the gump
        gb = CraftingGumpBuilder(id="SheetActionGump")
        with gb.MainFrame():
            with gb.ShadedColumn(halign="center"):
                gb.TileArt(row["Type"], width=80, height=60, hue=row["Color"], centered=True, itemproperty=row["Serial"])
            with gb.ShadedColumn():
                btn_to_inv = gb.CraftingButton("To Backpack", tooltip="Move the item to your backpack.")
                btn_use = gb.CraftingButton("Use", tooltip="Use the item.")
                btn_equip = gb.CraftingButton("Equip", tooltip="Attempts to equip the item. This may fail if you already have an item in the slot.")
                btn_move = gb.CraftingButton("Move To", tooltip="Move the item to a target container.")
                btn_exit = gb.CraftingButton("Return", style="left", tooltip="Return to the previous menu.")

        # Handle response
        block, _ = gb.launch().wait_response().unpack()
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

    @classmethod
    def edit_column(cls, col_idx: int, sheet: Sheet):
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
        gb = CraftingGumpBuilder(id="SheetEditColumnGump")
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
                    btn_left = gb.CraftingButton("MOVE LEFT", width=165, style="left")
                    btn_right = gb.CraftingButton("MOVE RIGHT", width=165)
                    btn_expand = gb.CraftingButton("EXPAND COLUMN", width=165)
                    btn_narrow = gb.CraftingButton("NARROW COLUMN", width=165)
                with gb.Column(width=200):
                    btn_remove = gb.CraftingButton("REMOVE COLUMN", width=165, hue=0x21)
                    btn_filter = gb.CraftingButton("EDIT FILTER", width=165)
                    gb.Spacer(22)
                    btn_exit = gb.CraftingButton("EXIT", width=165, style="x")

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
                for i in range(lines_per_page - 1):
                    gb.Spacer(22)

            # Handle response
            block, response = gb.launch().wait_response().unpack()
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
            if block == btn_filter:
                prop = col.prop
                result = False
                if isinstance(prop, PropTypes.Boolean):
                    result = cls.edit_filter_boolean(col_idx, sheet)
                elif isinstance(prop, PropTypes.Numeric):
                    result = cls.edit_filter_numeric(col_idx, sheet)
                elif isinstance(prop, PropTypes.Enum):
                    result = cls.edit_filter_enum(col_idx, sheet)
                else:
                    Misc.SendMessage("This property type does not support filtering.", 0x21)
                if result:
                    return
                continue
            return

    @staticmethod
    def edit_filter_boolean(col_idx: int, sheet: Sheet) -> bool:
        """
        Edit the column's filter.
        """
        col = sheet.columns[col_idx]
        expected_value = None
        if isinstance(col.filter, SheetColumnFilters.Boolean):
            expected_value = col.filter.expected_value

        # Build the gump
        gb = CraftingGumpBuilder(id="SheetEditFilterGump")
        with gb.MainFrame():
            with gb.ShadedColumn(halign="center"):
                gb.Html(f"COLUMN {col_idx+1}: {col.name}", centered=True, color="#FFFFFF")
                gb.Spacer(0)
                gb.Html("Choose the criterion. Only the items that match the selected criterion will be displayed.", width=450, height=44, color="#FFFFFF")
                with gb.Row(spacing=5):
                    btn_true = gb.Checkbox()
                    gb.Text("Item has this property.", hue=1152, width=100)
                with gb.Row(spacing=5):
                    btn_false = gb.Checkbox()
                    gb.Text("Item does not have this property.", hue=1152, width=100)
                gb.Spacer(0)
                with gb.Row():
                    btn_apply = gb.CraftingButton("Apply Filter", width=120)
                    btn_clear = gb.CraftingButton("Clear Filter", width=120)
                    btn_exit = gb.CraftingButton("Exit", width=60, style="x")

        while True:
            btn_true.checked = expected_value is True
            btn_false.checked = expected_value is False
            block, response = gb.launch().wait_response().unpack()

            if block == btn_true:
                expected_value = True
                continue
            if block == btn_false:
                expected_value = False
                continue
            if block == btn_exit:
                return False
            if block == btn_clear:
                col.filter = None
                Misc.SendMessage(f"Filter removed from column {col_idx+1}.", 68)
                return True
            if block == btn_apply:
                if expected_value is None:
                    col.filter = None
                    Misc.SendMessage(f"Filter removed from column {col_idx+1}.", 68)
                else:
                    col.filter = SheetColumnFilters.Boolean(expected_value=expected_value)
                    Misc.SendMessage(f"Filter applied to column {col_idx+1}.", 68)
                return True
            return False

    @staticmethod
    def edit_filter_numeric(col_idx: int, sheet: Sheet) -> bool:
        """
        Edit the column's filter.
        """
        col = sheet.columns[col_idx]
        min_value = None
        max_value = None
        if isinstance(col.filter, SheetColumnFilters.Numeric):
            min_value = col.filter.min_value
            max_value = col.filter.max_value

        # Build the gump
        gb = CraftingGumpBuilder(id="SheetEditFilterGump")
        with gb.MainFrame():
            with gb.ShadedColumn(halign="center"):
                gb.Html(f"COLUMN {col_idx+1}: {col.name}", centered=True, color="#FFFFFF")
                gb.Spacer(0)
                gb.Html("Set the min and/or max values to filter the items. Only items with values within this range will be displayed.", width=450, height=44, color="#FFFFFF")
                with gb.Row(spacing=5):
                    gb.Text("Min Value:", hue=1152, width=100)
                    with gb.Row(background="tiled:9354", padding=2):
                        field_min = gb.TextEntry(str(min_value) if min_value is not None else "(none)", width=100, hue=68, max_length=10, tooltip="Minimum value (inclusive). Leave empty for no minimum.")
                with gb.Row(spacing=5):
                    gb.Text("Max Value:", hue=1152, width=100)
                    with gb.Row(background="tiled:9354", padding=2):
                        field_max = gb.TextEntry(str(max_value) if max_value is not None else "(none)", width=100, hue=68, max_length=10, tooltip="Maximum value (inclusive). Leave empty for no maximum.")
                gb.Spacer(0)
                with gb.Row():
                    btn_apply = gb.CraftingButton("Apply Filter", width=120)
                    btn_clear = gb.CraftingButton("Clear Filter", width=120)
                    btn_exit = gb.CraftingButton("Exit", width=60, style="x")

        while True:
            block, response = gb.launch().wait_response().unpack()
            # Check if minimum and maximum values are valid
            try:
                if block == btn_clear or field_min.text == "(none)":
                    field_min.text = ""
                min_value = int(field_min.text) if field_min.text.strip() != "" else None
                if block == btn_clear or field_max.text == "(none)":
                    field_max.text = ""
                max_value = int(field_max.text) if field_max.text.strip() != "" else None
            except:
                Misc.SendMessage("Invalid min/max value.", 0x21)
                continue

            if block == btn_exit:
                return False
            if block == btn_clear:
                col.filter = None
                Misc.SendMessage(f"Filter removed from column {col_idx+1}.", 68)
                return True
            if block == btn_apply:
                if min_value is None and max_value is None:
                    col.filter = None
                    Misc.SendMessage(f"Filter removed from column {col_idx+1}.", 68)
                else:
                    col.filter = SheetColumnFilters.Numeric(min_value=min_value, max_value=max_value)
                    Misc.SendMessage(f"Filter applied to column {col_idx+1}.", 68)
                return True
            return False

    @staticmethod
    def edit_filter_enum(col_idx: int, sheet: Sheet) -> bool:
        """
        Edit the column's filter.
        """
        col = sheet.columns[col_idx]
        prop = col.prop
        if not isinstance(prop, EnumProp):
            Misc.SendMessage("This property is not an enum.", 0x21)
            return False
        vkmap = prop.value_to_str
        kvmap = {v: k for k, v in vkmap.items()}
        if isinstance(col.filter, SheetColumnFilters.Enum):
            selected_values = set(col.filter.allowed_values)
        else:
            selected_values = set(kvmap.values())

        # Build the gump
        gb = CraftingGumpBuilder(id="SheetEditFilterGump")
        with gb.MainFrame():
            with gb.ShadedColumn(halign="center"):
                gb.Html(f"COLUMN {col_idx+1}: {col.name}", centered=True, color="#FFFFFF")
                gb.Spacer(0)
                gb.Html("Choose the values to filter by. Only the items that match the selected values will be displayed.", width=450, height=44, color="#FFFFFF")
                btn_choices: Dict[int, GumpBuilder.Assets.Checkbox] = {}
                values = sorted(kvmap.values())
                num_rows = max(10, (len(values) + 1) // 2)
                with gb.Row():
                    for cur_values in (values[:num_rows], values[num_rows:]):
                        with gb.Column(halign="left", spacing=5, width=225) as c:
                            for enum_value in cur_values:
                                enum_name = vkmap[enum_value]
                                is_checked = enum_value in selected_values
                                with gb.Row(spacing=5):
                                    btn_choices[enum_value] = gb.Checkbox(checked=is_checked)
                                    gb.Text(enum_name, hue=1152, width=300)
                gb.Spacer(0)
                with gb.Row():
                    btn_apply = gb.CraftingButton("Apply Filter", width=120)
                    btn_clear = gb.CraftingButton("Clear Filter", width=120)
                    btn_exit = gb.CraftingButton("Exit", width=60, style="x")

        while True:
            # Update selected values based on checkbox states
            selected_values = set()
            for enum_value, checkbox in btn_choices.items():
                if checkbox.checked:
                    selected_values.add(enum_value)
            # Handle response
            block, response = gb.launch().wait_response().unpack()
            if block in btn_choices.values():
                continue
            if block == btn_exit:
                return False
            if block == btn_clear:
                col.filter = None
                Misc.SendMessage(f"Filter removed from column {col_idx+1}.", 68)
                return True
            if block == btn_apply:
                if selected_values == set(kvmap.values()):
                    col.filter = None
                    Misc.SendMessage(f"Filter removed from column {col_idx+1}.", 68)
                else:
                    col.filter = SheetColumnFilters.Enum(kvmap=kvmap, allowed_values=selected_values)
                    Misc.SendMessage(f"Filter applied to column {col_idx+1}.", 68)
                return True
            return False

    @staticmethod
    def rename_save(sheet: Sheet):
        """
        Show the edit/save gump for the given sheet.
        Here you can change the sheet name or export the sheet.
        """
        gb = CraftingGumpBuilder(id="SheetSaveGump")
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
                btn_export = gb.UOStoreButton("Export", style="blue", tooltip="Export the sheet to a CSV file.")
                btn_rename = gb.UOStoreButton("Rename", style="green", tooltip="Rename the sheet.")
                btn_cancel = gb.UOStoreButton("Cancel", style="red", tooltip="Cancel and close this dialog.")

        while True:
            block, _ = gb.launch().wait_response().unpack()
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
        gb = CraftingGumpBuilder(id="ColumnConfigGump")
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
                        btn_exit = gb.CraftingButton("EXIT", width=115, style="x", tooltip="Exit this dialog.")

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

            block, response = gb.launch().wait_response().unpack()

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
        row_selected: Set[int] = set()
        page: int = 0
        mode: ExplorerSheetView.Mode = ExplorerSheetView.Mode.NORMAL
        while True:
            # Load the sheet if not already loaded
            if sheet is None:
                sheet = Explorer.load_contents(serial, sheet_header)
                sorted_sheet = None
                if sheet is None:
                    Misc.SendMessage("Failed to load the container.", 0x21)
                    return None
                row_selected &= set(row["Serial"] for row in sheet.rows)

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
                        sorted_sheet = col.apply_filter(sorted_sheet)

            # Ensure the current page is within bounds
            last_page = (len(sorted_sheet.rows) - 1) // ExplorerSheetView.ITEMS_PER_PAGE
            if page > last_page:
                page = last_page
            if page < 0:
                page = 0

            esv = ExplorerSheetView(sorted_sheet, page, mode, col_precedence, row_selected)

            block, response = esv.gb.launch().wait_response().unpack()
            if block == esv.menu_refresh:
                # Reload the contents
                sheet = None
                continue
            if block == esv.menu_export:
                # Rename or export the sheet
                Explorer.rename_save(sorted_sheet)
                sheet_header.name = sorted_sheet.name
                continue
            if block == esv.menu_columns:
                # Manage column configurations
                modified = Explorer.manage_columns(sheet_header, setting)
                if modified:
                    sorted_sheet = None
                continue
            if block == esv.menu_prev:
                # Go to the previous page
                if page > 0:
                    page -= 1
                continue
            if block == esv.menu_next:
                # Go to the next page
                if page < esv.total_pages - 1:
                    page += 1
                continue
            if block in esv.menu_item_action:
                # Perform action on the selected item
                if not isinstance(response, ItemPropRow):
                    Misc.SendMessage("Invalid row.", 0x21)
                    continue
                row = response
                if mode == ExplorerSheetView.Mode.BATCH:
                    if row["Serial"] in row_selected:
                        row_selected.remove(row["Serial"])
                    else:
                        row_selected.add(row["Serial"])
                elif mode == ExplorerSheetView.Mode.NORMAL:
                    Explorer.item_action(row)
                    sheet = None
                continue
            if block in esv.menu_edit_column:
                # Edit the selected column
                if not isinstance(response, int):
                    Misc.SendMessage("Invalid column index.", 0x21)
                    continue
                j = response
                Explorer.edit_column(j, sheet)
                sorted_sheet = None
                continue
            if block in esv.menu_sort_column:
                # Sort by the selected column
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
            if block == esv.menu_batch:
                # Toggle between normal and batch mode
                if mode == ExplorerSheetView.Mode.BATCH:
                    mode = ExplorerSheetView.Mode.NORMAL
                else:
                    mode = ExplorerSheetView.Mode.BATCH
                continue
            if esv.menu_extra_select_all is not None and block == esv.menu_extra_select_all:
                row_selected = set(row["Serial"] for row in sorted_sheet.rows)
                continue
            if esv.menu_extra_deselect_all is not None and block == esv.menu_extra_deselect_all:
                row_selected = set()
                continue
            if esv.menu_extra_invert is not None and block == esv.menu_extra_invert:
                current_selection = set(row["Serial"] for row in sorted_sheet.rows)
                row_selected ^= current_selection
                continue
            if esv.menu_extra_move_to is not None and block == esv.menu_extra_move_to:
                Explorer.batch_move_to(row_selected)
                # mode = ExplorerSheetView.Mode.NORMAL
                # row_selected = set()
                sheet = None
                continue
            return None

    @staticmethod
    def dialog_shortcut() -> Any:
        """
        A minimized gump to quickly open the explorer.
        """

        gb = CraftingGumpBuilder(id="SheetShortcutGump")
        with gb.MinimalFrame():
            gb.Html("Item Explorer", centered=True, color="#FFFFFF", width=125)
            gb.UOStoreButton("Inspect", tooltip="Inspect the target container's contents.").on_click(True)

        _, response = gb.launch().wait_response().unpack()
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
