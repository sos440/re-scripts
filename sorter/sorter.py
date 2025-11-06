################################################################################
# Settings

VERSION = "1.1"
SETTING_DIR = "Data/Sorter/"

MOVE_DELAY = 1000

################################################################################
# Imports

import os
import sys

# Ensure we can import from the current directory
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(SCRIPT_DIR)

# Import
from modules import *

# standard imports
from AutoComplete import *
from typing import List, Dict, Set, Tuple, Any, Optional, Union, Iterable
import threading
import re
import xml.etree.ElementTree as ET

################################################################################
# SortRules Class


class SortRules:
    """
    Represents a set of sorting rules and target container rules.
    """

    sort_rules: List[BaseMatch]
    """A list of match rules for sorting items."""
    cont_rules: List[BaseMatch]
    """A list of match rules for the target container."""

    def __init__(self, name: str, desc: Optional[str] = None):
        self.sort_rules = []
        self.cont_rules = []
        self.name = name
        self.desc = desc
        self.enabled = True
        self.notify = False

    def to_xml(self, e: Optional[ET.Element] = None) -> ET.Element:
        if e is None:
            e = ET.Element("SortRules")
        e.set("name", self.name)
        if self.desc is not None:
            e.set("desc", self.desc)
        e.set("enabled", "true" if self.enabled else "false")
        e.set("notify", "true" if self.notify else "false")

        sort_rules_elem = ET.SubElement(e, "SortRules")
        for match in self.sort_rules:
            sort_rules_elem.append(match.to_xml())

        cont_rules_elem = ET.SubElement(e, "ContRules")
        for match in self.cont_rules:
            cont_rules_elem.append(match.to_xml())

        return e

    @classmethod
    def from_xml(cls, e: ET.Element) -> "SortRules":
        name = e.get("name", "Unnamed Rule Set")
        desc = e.get("desc", None)
        rule_set = cls(name, desc)

        rule_set.enabled = e.get("enabled", "true").lower() == "true"
        rule_set.notify = e.get("notify", "false").lower() == "true"

        for child in e:
            if child.tag == "SortRules":
                for match_elem in child:
                    match = parse_element(match_elem)
                    rule_set.sort_rules.append(match)
            elif child.tag == "ContRules":
                for match_elem in child:
                    match = parse_element(match_elem)
                    rule_set.cont_rules.append(match)

        return rule_set

    def test(self, item: "Item") -> bool:
        """
        Test if the item matches any of the sort rules.
        """
        for match in self.sort_rules:
            if match.test(item):
                return True
        return False

    def find_contall(self) -> Generator["Item", None, None]:
        """
        Find all container items in range that match the container rules.
        """
        filter = Items.Filter()
        filter.Enabled = True
        for item in Items.ApplyFilter(filter):
            if not any(match.test(item) for match in self.cont_rules):
                continue

            if item.RootContainer == 0:
                top_cont = item
            else:
                top_cont = Items.FindBySerial(item.RootContainer)

            if top_cont is None:
                continue
            if not top_cont.OnGround:
                continue
            if Player.DistanceTo(top_cont) > 2:
                continue
            yield top_cont


################################################################################
# I/O Functions


def load_sort_rules(filepath: str) -> List[SortRules]:
    """
    Load sort rules from an XML file.
    """
    if not os.path.exists(filepath):
        return []
    tree = ET.parse(filepath)
    root = tree.getroot()
    sort_rules_list = []
    for rule_elem in root.findall("SortRules"):
        sort_rules = SortRules.from_xml(rule_elem)
        sort_rules_list.append(sort_rules)
    return sort_rules_list


def save_sort_rules(filepath: str, sort_rules_list: List[SortRules]) -> None:
    """
    Save sort rules to an XML file.
    """
    dir = os.path.dirname(filepath)
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)

    root = ET.Element("SortRulesList")
    for sort_rules in sort_rules_list:
        root.append(sort_rules.to_xml())
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)


################################################################################
# Interface


def get_field_value(
    field: Optional[CraftingGumpBuilder.Assets.TextEntry],
    default: Any = None,
    value_type: type = str,
) -> Any:
    try:
        if field is None:
            return default
        if not field.text:
            return default
        if field.text.lower().strip("() ") in ("", "none", "null", "empty"):
            return default
        if value_type == str:
            return field.text
        if value_type == int:
            return int(field.text, 0)
        return value_type(field.text) or default
    except ValueError:
        return default


class Logging:
    @staticmethod
    def Message(message: str) -> None:
        Misc.SendMessage(f"{message}", 0x3B2)

    @staticmethod
    def Info(message: str) -> None:
        Misc.SendMessage(f"{message}", 68)

    @staticmethod
    def Error(message: str) -> None:
        Misc.SendMessage(f"{message}", 33)


class Sorter:
    STOP_EVENT: Optional[threading.Event] = None
    """The stopping event for the sorting thread."""
    RULE_SETS: List[SortRules] = []
    """The list of sorting rules."""
    RULES_FILEPATH = os.path.join(SETTING_DIR, f"sort_rules.xml")

    README = "<br>".join(
        map(
            lambda s: s.strip(),
            re.split(
                r"\n",
                """
                <b>Welcome to the Rule Editor!</b>

                This tool allows you to create and manage sorting rules for your items.

                1. Creating Rule Sets:
                There are two ways to create a new rule set. You can either scan an existing container to automatically generate rules based on its contents, or you can manually create a new rule set from scratch.

                2. Basic Rule Set Properties:
                Once you have a rule set, you can edit its properties, including its name, description, and whether it's enabled or not. You can also choose to receive notifications when items are sorted using this rule set.

                3. Setting Target Container (Sortbag) Rules:
                You can also set the target container (sortbag) rules, which determine the container where matched items will be moved. You can specify a specific container or use match rules to identify suitable containers.

                4. Managing Match Rules:
                Each rule set consists of match rules that determine which items get sorted. You can add new match rules, edit existing ones, rearrange their order, or delete them as needed.
                """.strip(),
            ),
        )
    )

    class ContainerInfo:
        def __init__(self, serial: int, contents: int, max_contents: int, weight: float = 0.0, max_weight: float = float("inf")):
            self.serial = serial
            self.contents = contents
            self.max_contents = max_contents
            self.weight = weight
            self.max_weight = max_weight

    @classmethod
    def get_contents(cls, serial: int) -> Optional["ContainerInfo"]:
        """
        Scan the item property and get container contents info.
        """
        cont = Items.FindBySerial(serial)
        if cont is None:
            return None

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
    def move_item(cls, item: "Item", rule_set: SortRules) -> bool:
        """
        Fail-safe move item based on rule set.
        """
        for target_cont in rule_set.find_contall():
            target_info = cls.get_contents(target_cont.Serial)
            if target_info is None:
                Logging.Error(f"Failed to get info for target container {hex(target_cont.Serial)}.")
                continue
            if target_info.contents >= target_info.max_contents:
                Logging.Error(f"Target container {hex(target_cont.Serial)} is full.")
                continue
            if target_info.weight + item.Weight > target_info.max_weight:
                Logging.Error(f"Target container {hex(target_cont.Serial)} is overweight.")
                continue
            if rule_set.notify:
                Logging.Info(f"Sorting item '{item.Name}' using rule set '{rule_set.name}'.")
            Items.Move(item.Serial, target_cont.Serial, -1)
            Misc.Pause(MOVE_DELAY)
            return True
        Logging.Error(f"No suitable target container found for item '{item.Name}'.")
        return False

    @classmethod
    def sort(cls, stop_event: threading.Event) -> None:
        """
        Scan the player's inventory and sort items based on the defined rules.
        """
        filter = Items.Filter()
        filter.Enabled = True
        filter.OnGround = False
        for item in Items.ApplyFilter(filter):
            if stop_event.is_set():
                break
            if item.RootContainer != Player.Backpack.Serial:
                continue
            for rule_set in cls.RULE_SETS:
                if not rule_set.enabled:
                    continue
                if not rule_set.test(item):
                    continue
                if cls.move_item(item, rule_set):
                    break

        Misc.Pause(100)
        cls.STOP_EVENT = None
        Logging.Info("Sorting done.")
        gb = CraftingGumpBuilder(id="SorterShortcutGump")
        Gumps.SendAction(gb.id, 0)

    @classmethod
    def scan_rule_set(cls) -> Optional[SortRules]:
        """
        Scan the targeted container and create a rule set based on its contents.
        """
        target = Target.PromptTarget("Target a container to scan for items to add as rules.")
        if target == -1:
            return None
        cont = Items.FindBySerial(target)
        if cont is None:
            Logging.Error("Invalid container targeted.")
            return None

        rule_set = SortRules(name=f"Scanned")

        # Add container match rule
        match_cont = SingleSerialMatch(serial=cont.Serial, itemid=cont.ItemID, color=cont.Color, name=cont.Name)
        rule_set.cont_rules.append(match_cont)

        # Add item match rules
        Items.WaitForContents(cont.Serial, 1000)
        check_duplicates = set()
        for item in cont.Contains:
            if (item.ItemID, item.Color) in check_duplicates:
                continue
            match = SingleTypeMatch(itemid=item.ItemID, color=item.Color, name=item.Name)
            rule_set.sort_rules.append(match)
            check_duplicates.add((item.ItemID, item.Color))

        return rule_set

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

    @classmethod
    def gump_shortcut(cls) -> bool:
        """
        A minimized gump with shortcut buttons to start/stop sorting and open the rule editor.

        Returns True if the gump was interacted with, False otherwise.
        """

        gb = CraftingGumpBuilder(id="SorterShortcutGump")
        with gb.MinimalFrame(spacing=0):
            # Title
            gb.Html(f"Sorter v{VERSION}", centered=True, color="#FFFFFF", width=125)
            if cls.STOP_EVENT is None:
                gb.UOStoreButton("Begin Sort", tooltip="Click to start sorting.").on_click("start")
                gb.UOStoreButton("Open Rule Editor", tooltip="Click to open the rule editor.", style="green").on_click("edit")
                gb.UOStoreButton("Exit", tooltip="Click to stop sorting.", style="red").on_click("exit")
            else:
                gb.UOStoreButton("Stop Sort", tooltip="Click to stop sorting.", style="red").on_click("stop")

        block, response = gb.launch().wait_response().unpack()
        if response == "start":
            if cls.STOP_EVENT is None:
                stop_event = threading.Event()
                cls.STOP_EVENT = stop_event
                sort_thread = threading.Thread(target=cls.sort, args=(stop_event,))
                sort_thread.start()
            return True
        if response == "stop":
            if cls.STOP_EVENT is not None:
                Logging.Info("Stopping sorting...")
                cls.STOP_EVENT.set()
                cls.STOP_EVENT = None
            return True
        if response == "edit":
            cls.gump_edit_rule_set()
            return True
        if response == "exit":
            return False
        return True

    @classmethod
    def gump_edit_rule_new(cls) -> Optional[BaseMatch]:
        """
        Open the rule type selection gump.
        """

        gb = CraftingGumpBuilder(id="SorterRuleTypeSelectGump")
        with gb.MainFrame():
            with gb.ShadedColumn():
                with gb.Column():
                    gb.Html("Select Match Rule Type", centered=True, color="#FFFFFF")
                gb.Spacer(10)
                btn_single_serial = gb.CraftingButton("Serial Match", width=150, tooltip="Match a specific item by its serial number.")
                btn_single_type = gb.CraftingButton("Type Match", width=150, tooltip="Match items by their item ID and optional color.")
                gb.CraftingButton("Cancel", width=80, tooltip="Cancel and return to the rule editor.")

        block, _ = gb.launch().wait_response().unpack()

        if block == btn_single_serial:
            return cls.gump_edit_rule_single_serial(SingleSerialMatch(serial=0, itemid=0, color=0, name="", desc=""), mode="new")[1]

        if block == btn_single_type:
            return cls.gump_edit_rule_single_type(SingleTypeMatch(itemid=0, color=None, name="", desc=""), mode="new")[1]

        return None

    @classmethod
    def gump_edit_rule_single_serial(cls, match: SingleSerialMatch, mode: str = "edit") -> Tuple[str, Optional[SingleSerialMatch]]:
        """
        Open the rule editor for a single rule.
        """

        new_match = SingleSerialMatch(serial=match.serial, itemid=match.itemid, color=match.color, name=match.name, desc=match.desc)

        gb = CraftingGumpBuilder(id="SorterSingleSerialMatchEditorGump")
        with gb.MainFrame():
            with gb.ShadedColumn():
                with gb.Column():
                    gb.Html("Edit Single Serial Match", centered=True, color="#FFFFFF")
                with gb.Row(spacing=5):
                    with gb.Column():
                        field_tileart = gb.TileArt(graphics=new_match.itemid, hue=new_match.color or 0, width=100, height=100, centered=True)
                    with gb.Column(spacing=5):
                        with gb.Row(spacing=5):
                            gb.Text("Serial:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_serial = gb.TextEntry("", width=100, hue=0, max_length=10, tooltip="The serial number to match.")
                        with gb.Row(spacing=5):
                            gb.Text("Item ID:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_itemid = gb.TextEntry("", width=100, hue=0, max_length=10, tooltip="The item ID to match.")
                        with gb.Row(spacing=5):
                            gb.Text("Color (Hue):", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_color = gb.TextEntry("", width=100, hue=0, max_length=10, tooltip="The color (hue) to match. Leave blank or set -1 for any color.")
                        with gb.Row(spacing=5):
                            gb.Text("Name:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_name = gb.TextEntry("", width=150, hue=0, max_length=50, tooltip="The name of the rule.")
                        with gb.Row(spacing=5):
                            gb.Text("Description:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_desc = gb.TextEntry("", width=200, hue=0, max_length=200, tooltip="A description of the rule.")
                gb.Spacer(10)
                with gb.Row(spacing=10):
                    btn_update = gb.CraftingButton("Update", width=80, tooltip="Update the preview tile art.")
                    btn_pick = gb.CraftingButton("Picker", width=80, tooltip="Pick an item to set the serial number, item ID, and color.")
                    btn_save = gb.CraftingButton("Save", width=80, hue=88, tooltip="Save the current match rule.")
                    gb.CraftingButton("Cancel", width=80, tooltip="Cancel and return to the rule editor.")
                with gb.Row(spacing=10) as c:
                    row_edit_only = c
                    btn_left = gb.CraftingButton("Move Left", width=80, tooltip="Move this match rule left in the rule set.")
                    btn_right = gb.CraftingButton("Move Right", width=80, tooltip="Move this match rule right in the rule set.")
                    btn_delete = gb.CraftingButton("Delete", width=80, hue=33, tooltip="Delete this match rule from the rule set.")
                if mode != "edit":
                    row_edit_only.clear_children()

        while True:
            field_tileart.graphics = new_match.itemid
            field_tileart.hue = new_match.color
            field_serial.text = hex(new_match.serial)
            field_itemid.text = hex(new_match.itemid)
            field_color.text = str(new_match.color) if new_match.color is not None else "-1"
            field_name.text = new_match.name or "(Empty)"
            field_desc.text = new_match.desc or "(Empty)"

            block, _ = gb.launch().wait_response().unpack()

            if block == btn_save or block == btn_update:
                new_match.serial = get_field_value(field_serial, new_match.serial, int)
                new_match.itemid = get_field_value(field_itemid, new_match.itemid, int)
                new_match.color = get_field_value(field_color, 0, int)
                new_match.name = get_field_value(field_name, "(Unnamed Rule)")
                new_match.desc = get_field_value(field_desc, None)
                if block == btn_save:
                    return "save", new_match
                continue

            if block == btn_pick:
                target = Target.PromptTarget("Target an item to set the serial number, item ID, and color.", 0x3B2)
                if target == -1:
                    continue
                item = Items.FindBySerial(target)
                if item is None:
                    Logging.Error("Invalid item targeted.")
                    continue
                new_match.serial = item.Serial
                new_match.itemid = item.ItemID
                new_match.color = item.Color
                new_match.name = item.Name
                new_match.desc = None
                continue

            if block == btn_delete:
                confirm_delete = cls.confirm(
                    text="Are you sure you want to delete this match rule?",
                    title="Confirm Delete Match Rule",
                    yes_text="Delete",
                    no_text="Cancel",
                    height=66,
                    centered=True,
                )
                if confirm_delete:
                    return "delete", None
                continue

            if block == btn_left:
                return "move_left", None

            if block == btn_right:
                return "move_right", None

            return "cancel", None

    @classmethod
    def gump_edit_rule_single_type(cls, match: SingleTypeMatch, mode: str = "edit") -> Tuple[str, Optional[SingleTypeMatch]]:
        """
        Open the rule editor for a single rule.
        """

        new_match = SingleTypeMatch(itemid=match.itemid, color=match.color, name=match.name, desc=match.desc)

        gb = CraftingGumpBuilder(id="SorterSingleTypeMatchEditorGump")
        with gb.MainFrame():
            with gb.ShadedColumn():
                with gb.Column():
                    gb.Html("Edit Single Type Match", centered=True, color="#FFFFFF")
                with gb.Row(spacing=5):
                    with gb.Column():
                        field_tileart = gb.TileArt(graphics=new_match.itemid, hue=new_match.color or 0, width=100, height=100, centered=True)
                    with gb.Column(spacing=5):
                        with gb.Row(spacing=5):
                            gb.Text("Item ID:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_itemid = gb.TextEntry("", width=100, hue=0, max_length=10, tooltip="The item ID to match.")
                        with gb.Row(spacing=5):
                            gb.Text("Color (Hue):", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_color = gb.TextEntry("", width=100, hue=0, max_length=10, tooltip="The color (hue) to match. Leave blank or set -1 for any color.")
                        with gb.Row(spacing=5):
                            gb.Text("Name:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_name = gb.TextEntry("", width=150, hue=0, max_length=50, tooltip="The name of the rule.")
                        with gb.Row(spacing=5):
                            gb.Text("Description:", hue=1152, width=80)
                            with gb.Row(background="tiled:9354", padding=2):
                                field_desc = gb.TextEntry("", width=200, hue=0, max_length=200, tooltip="A description of the rule.")
                gb.Spacer(10)
                with gb.Row(spacing=10):
                    btn_update = gb.CraftingButton("Update", width=80, tooltip="Update the preview tile art.")
                    btn_pick = gb.CraftingButton("Picker", width=80, tooltip="Pick an item to set the item ID and color.")
                    btn_save = gb.CraftingButton("Save", width=80, hue=88, tooltip="Save the current match rule.")
                    gb.CraftingButton("Cancel", width=80, tooltip="Cancel and return to the rule editor.")
                with gb.Row(spacing=10) as c:
                    row_edit_only = c
                    btn_left = gb.CraftingButton("Move Left", width=80, tooltip="Move this match rule left in the rule set.")
                    btn_right = gb.CraftingButton("Move Right", width=80, tooltip="Move this match rule right in the rule set.")
                    btn_delete = gb.CraftingButton("Delete", width=80, hue=33, tooltip="Delete this match rule from the rule set.")
                if mode != "edit":
                    row_edit_only.clear_children()

        while True:
            field_tileart.graphics = new_match.itemid
            field_tileart.hue = new_match.color or 0
            field_itemid.text = hex(new_match.itemid)
            field_color.text = str(new_match.color) if new_match.color is not None else "-1"
            field_name.text = new_match.name or "(Empty)"
            field_desc.text = new_match.desc or "(Empty)"

            block, _ = gb.launch().wait_response().unpack()

            if block == btn_save or block == btn_update:
                new_match.itemid = get_field_value(field_itemid, new_match.itemid, int)
                color_value = get_field_value(field_color, -1, int)
                new_match.color = color_value if color_value != -1 else None
                new_match.name = get_field_value(field_name, "(Unnamed Rule)")
                new_match.desc = get_field_value(field_desc, None)
                if block == btn_save:
                    return "save", new_match
                continue

            if block == btn_pick:
                target = Target.PromptTarget("Target an item to set the item ID and color.", 0x3B2)
                if target == -1:
                    continue
                item = Items.FindBySerial(target)
                if item is None:
                    Logging.Error("Invalid item targeted.")
                    continue
                new_match.itemid = item.ItemID
                new_match.color = item.Color
                new_match.name = item.Name
                continue

            if block == btn_delete:
                confirm_delete = cls.confirm(
                    text="Are you sure you want to delete this match rule?",
                    title="Confirm Delete Match Rule",
                    yes_text="Delete",
                    no_text="Cancel",
                    height=66,
                    centered=True,
                )
                if confirm_delete:
                    return "delete", None
                continue

            if block == btn_left:
                return "move_left", None

            if block == btn_right:
                return "move_right", None

            return "cancel", None

    @classmethod
    def gump_draw_rule(cls, gb: CraftingGumpBuilder, rule: Optional[BaseMatch]) -> Optional[CraftingGumpBuilder.Assets.Button]:
        """
        Draw a single rule in the rule editor.
        """
        RULE_CELL_WIDTH = 225

        if rule is None:
            gb.Spacer(RULE_CELL_WIDTH)
            return

        with gb.Row(width=RULE_CELL_WIDTH, spacing=5):
            button = gb.Checkbox(up=2328, down=2329, width=80, height=60)
            desc = rule.desc or ""

            if isinstance(rule, SingleTypeMatch):
                button.add_tileart(graphics=rule.itemid, hue=rule.color or 0)
                if rule.desc is None:
                    if rule.color is not None:
                        desc = f"Color: {rule.color}"
                    else:
                        desc = "Any Colors"

            elif isinstance(rule, SingleSerialMatch):
                graphics = rule.itemid
                hue = rule.color
                item = Items.FindBySerial(rule.serial)
                if item is not None:
                    graphics = item.ItemID
                    hue = item.Color
                    button.itemproperty = item.Serial
                button.add_tileart(graphics=graphics, hue=hue)

            with gb.Column(halign="left", spacing=2):
                gb.Text(rule.name or "(Unnamed)", hue=1152, width=RULE_CELL_WIDTH - 85, cropped=True)
                gb.Html(desc, color="#FFFFFF", width=RULE_CELL_WIDTH - 85, height=42)

        return button

    @classmethod
    def gump_edit_rule_set(cls) -> None:
        """
        Open the rule editor.
        """

        RULE_SETS_PER_PAGE = 12
        RULE_GRID_ROWS = 5
        RULE_GRID_COLS = 3
        RULE_GRID_CELLS = RULE_GRID_ROWS * RULE_GRID_COLS

        RULE_SET_PAGE = 0
        RULE_SET_SELECTED = -1
        RULE_GRID_PAGE = 0

        gb = CraftingGumpBuilder(id="SorterRuleEditorGump")

        # Build Gump
        with gb.MainFrame():
            # Header
            with gb.ShadedColumn(halign="center"):
                gb.Html("Rule Editor", centered=True, color="#FFFFFF")
            # Body
            with gb.Row(spacing=5):
                # Rule Sets Column
                with gb.ShadedColumn():
                    gb.Html("RULE SETS", width=200, centered=True, color="#FFFFFF")
                    gb.Spacer(5)
                    with gb.Column(halign="left", spacing=5) as c:
                        rule_set_col = c
                    gb.Spacer(22)
                    with gb.Row():
                        btn_rule_set_prev = gb.CraftingButton("PREV", width=65, style="left")
                        btn_rule_set_next = gb.CraftingButton("NEXT", width=65)
                    with gb.Row():
                        btn_rule_set_new = gb.CraftingButton("New", width=65, hue=88)
                        btn_rule_set_del = gb.CraftingButton("Delete", width=65, hue=33)
                    with gb.Row():
                        btn_rule_set_scan = gb.CraftingButton("Add By Scan", width=165, hue=88)
                # Controls Column
                with gb.ShadedColumn():
                    with gb.Column(halign="left", spacing=5) as c:
                        controls_col = c
                    gb.Spacer(10)
                    with gb.Column():
                        with gb.Row():
                            btn_save = gb.UOStoreButton("Save Rules", style="blue")
                            btn_exit = gb.UOStoreButton("Exit", style="red")

        while True:
            if RULE_SET_SELECTED != -1:
                RULE_SET_PAGE = RULE_SET_SELECTED // RULE_SETS_PER_PAGE
            # Populate Rule Sets
            btn_rule_sets = {}
            rule_set_col.clear_children()
            gb.current = rule_set_col
            for i in range(RULE_SETS_PER_PAGE):
                rule_set_index = RULE_SET_PAGE * RULE_SETS_PER_PAGE + i
                if rule_set_index >= len(cls.RULE_SETS):
                    gb.Spacer(22)
                    continue
                rule_set = cls.RULE_SETS[rule_set_index]
                if RULE_SET_SELECTED == rule_set_index:
                    button = gb.CraftingButton(rule_set.name, width=165, hue=68)
                else:
                    button = gb.CraftingButton(rule_set.name, width=165)
                btn_rule_sets[button] = rule_set_index

            # Populate Controls
            btn_rule_name = None
            btn_rule_desc = None
            field_name = None
            field_desc = None
            checkbox_enabled = None
            checkbox_notify = None
            btn_edit_cont_rules = None
            btn_rule_grid_next = None
            btn_rule_grid_prev = None
            btn_rule_grid_add = None
            btn_rule_grid = {}
            controls_col.clear_children()
            gb.current = controls_col
            if RULE_SET_SELECTED == -1:
                with gb.Column():
                    gb.Html(cls.README, width=550, height=400, color="#FFFFFF", background=True, scrollbar=True)
                with gb.Row():
                    for col in range(RULE_GRID_COLS):
                        cls.gump_draw_rule(gb, None)
            else:
                selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                # Rule Set Name
                with gb.Row(spacing=5):
                    btn_rule_name = gb.CraftingButton("Name:", width=65)
                    with gb.Row(background="tiled:9354", padding=2):
                        field_name = gb.TextEntry(selected_rule_set.name, width=165, hue=0, max_length=10, tooltip="The name of the rule set to be displayed in the sorter.")

                # Rule Set Description
                with gb.Row(spacing=5):
                    btn_rule_desc = gb.CraftingButton("Desc:", width=65, tooltip="Description")
                    with gb.Row(background="tiled:9354", padding=2):
                        field_desc = gb.TextEntry(selected_rule_set.desc or "(Empty)", width=300, hue=0, max_length=200, tooltip="A description of the rule set.")

                with gb.Row(spacing=5):
                    # Enabled Checkbox
                    checkbox_enabled = gb.Checkbox(checked=selected_rule_set.enabled)
                    gb.Text("Enabled", hue=1152, width=100)
                    # Notify Checkbox
                    checkbox_notify = gb.Checkbox(checked=selected_rule_set.notify)
                    gb.Text("Notify on Sort", hue=1152, width=150)
                    # Edit Container Rules Button
                    cont_rules = selected_rule_set.cont_rules
                    if len(cont_rules) == 0:
                        btn_edit_cont_rules = gb.CraftingButton("Set Sortbag Rule", width=150)
                    else:
                        if cont_rules[0].name is None:
                            btn_edit_cont_rules = gb.CraftingButton(f"Edit Sortbag Rule (Current: Untitled)", width=150)
                        else:
                            btn_edit_cont_rules = gb.CraftingButton(f"Edit Sortbag Rule (Current: {str(cont_rules[0].name)})", width=150)

                # Draw Sort Rules Grid
                gb.Spacer(10)
                with gb.Row():
                    gb.Text("Match Rules:", hue=1152, width=100)
                    btn_rule_grid_prev = gb.CraftingButton("PREV", width=80, style="left")
                    btn_rule_grid_next = gb.CraftingButton("NEXT", width=80)
                    btn_rule_grid_add = gb.CraftingButton("ADD", width=80)
                for row in range(RULE_GRID_ROWS):
                    with gb.Row(spacing=5, height=60):
                        for col in range(RULE_GRID_COLS):
                            rule_index = (RULE_GRID_PAGE * RULE_GRID_CELLS) + (row * RULE_GRID_COLS) + col
                            if rule_index >= len(selected_rule_set.sort_rules):
                                rule = None
                            else:
                                rule = selected_rule_set.sort_rules[rule_index]
                            button = cls.gump_draw_rule(gb, rule)
                            btn_rule_grid[button] = rule_index

            # Launch Gump and Wait for Response
            block, response = gb.launch().wait_response().unpack()

            if block is None or block is gb.root or block == btn_exit:
                confirm = cls.confirm(
                    text="Are you sure you want to exit the rule editor? Unsaved changes will be lost.",
                    title="Confirm Exit",
                    yes_text="Exit",
                    no_text="Cancel",
                    height=66,
                    centered=True,
                )
                if confirm:
                    cls.RULE_SETS = load_sort_rules(cls.RULES_FILEPATH)
                    return
                continue

            if block == btn_save:
                confirm = cls.confirm(
                    text="Are you sure you want to save the current rule sets? This will overwrite the existing rules file.",
                    title="Confirm Save",
                    yes_text="Save",
                    no_text="Cancel",
                    height=66,
                    centered=True,
                )
                if confirm:
                    if RULE_SET_SELECTED != -1:
                        # Save current selected rule set edits
                        selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                        selected_rule_set.name = get_field_value(field_name, "Unnamed Rule Set")
                        selected_rule_set.desc = get_field_value(field_desc, None)
                    save_sort_rules(cls.RULES_FILEPATH, cls.RULE_SETS)
                    Logging.Info("Rule sets saved successfully.")
                continue

            if block == btn_rule_set_prev:
                # Navigate to previous page of rule sets
                if RULE_SET_PAGE > 0:
                    RULE_SET_PAGE -= 1
                continue

            if block == btn_rule_set_next:
                # Navigate to next page of rule sets
                if (RULE_SET_PAGE + 1) * RULE_SETS_PER_PAGE < len(cls.RULE_SETS):
                    RULE_SET_PAGE += 1
                continue

            if block in btn_rule_sets:
                # Select a rule set
                RULE_SET_SELECTED = btn_rule_sets[block]
                RULE_GRID_PAGE = 0
                continue

            if block == btn_rule_set_new:
                # Create a new rule set
                new_rule_set = SortRules(name="New Rule Set")
                cls.RULE_SETS.append(new_rule_set)
                RULE_SET_SELECTED = len(cls.RULE_SETS) - 1
                continue

            if block == btn_rule_set_del:
                # Delete the selected rule set
                if RULE_SET_SELECTED != -1:
                    confirm_delete = cls.confirm(
                        text=f"Are you sure you want to delete the rule set '{cls.RULE_SETS[RULE_SET_SELECTED].name}'?",
                        title="Confirm Delete Rule Set",
                        yes_text="Delete",
                        no_text="Cancel",
                        height=66,
                        centered=True,
                    )
                    if confirm_delete:
                        del cls.RULE_SETS[RULE_SET_SELECTED]
                        RULE_SET_SELECTED = min(RULE_SET_SELECTED, len(cls.RULE_SETS) - 1)
                continue

            if block == btn_rule_set_scan:
                # Scan a container to create a new rule set
                rule_set = cls.scan_rule_set()
                if rule_set is None:
                    continue
                cls.RULE_SETS.append(rule_set)
                RULE_SET_SELECTED = len(cls.RULE_SETS) - 1
                Logging.Info(f"Scanned {len(rule_set.sort_rules)} items from the target container into new rule set.")
                continue

            if block == btn_rule_name:
                # Update rule set name
                if RULE_SET_SELECTED != -1 and field_name is not None:
                    selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                    selected_rule_set.name = get_field_value(field_name, "Unnamed Rule Set")
                continue

            if block == btn_rule_desc:
                # Update rule set description
                if RULE_SET_SELECTED != -1 and field_desc is not None:
                    selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                    selected_rule_set.desc = get_field_value(field_desc, None)
                continue

            if block == checkbox_enabled:
                # Toggle enabled state of the selected rule set
                if RULE_SET_SELECTED != -1:
                    selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                    selected_rule_set.enabled = not selected_rule_set.enabled
                continue

            if block == checkbox_notify:
                # Toggle notify state of the selected rule set
                if RULE_SET_SELECTED != -1:
                    selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                    selected_rule_set.notify = not selected_rule_set.notify
                continue

            if block == btn_edit_cont_rules:
                # Edit container rules of the selected rule set
                if RULE_SET_SELECTED == -1:
                    continue
                selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                cont_rules = selected_rule_set.cont_rules
                if len(cont_rules) == 0:
                    new_match = cls.gump_edit_rule_new()
                    if new_match is not None:
                        cont_rules.append(new_match)
                else:
                    first_rule = cont_rules[0]
                    if isinstance(first_rule, SingleSerialMatch):
                        cmd, new_match = cls.gump_edit_rule_single_serial(first_rule)
                    elif isinstance(first_rule, SingleTypeMatch):
                        cmd, new_match = cls.gump_edit_rule_single_type(first_rule)
                    else:
                        continue
                    if cmd == "save" and new_match is not None:
                        cont_rules[0] = new_match
                    elif cmd == "delete":
                        del cont_rules[0]
                continue

            if block == btn_rule_grid_prev:
                # Navigate to previous page of rule grid
                if RULE_GRID_PAGE > 0:
                    RULE_GRID_PAGE -= 1
                continue

            if block == btn_rule_grid_next:
                # Navigate to next page of rule grid
                if RULE_SET_SELECTED != -1:
                    selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                    if (RULE_GRID_PAGE + 1) * RULE_GRID_CELLS < len(selected_rule_set.sort_rules):
                        RULE_GRID_PAGE += 1
                continue

            if block == btn_rule_grid_add:
                # Add a new rule to the grid
                if RULE_SET_SELECTED == -1:
                    continue
                selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                new_match = SingleTypeMatch(itemid=0x0000, color=None, name="New Rule")
                cmd, new_match = cls.gump_edit_rule_single_type(new_match, mode="new")
                if cmd == "save" and new_match is not None:
                    selected_rule_set.sort_rules.append(new_match)
                    RULE_GRID_PAGE = (len(selected_rule_set.sort_rules) - 1) // RULE_GRID_CELLS

            if block in btn_rule_grid:
                # Edit a specific rule in the grid
                if RULE_SET_SELECTED == -1:
                    continue
                selected_rule_set = cls.RULE_SETS[RULE_SET_SELECTED]
                sort_rules = selected_rule_set.sort_rules
                rule_index = btn_rule_grid[block]
                match = sort_rules[rule_index]
                cmd, new_match = cls.gump_edit_rule_single_type(match)
                if cmd == "delete":
                    # Delete rule
                    del sort_rules[rule_index]
                    RULE_GRID_PAGE = min(RULE_GRID_PAGE, (len(sort_rules) - 1) // RULE_GRID_CELLS)
                elif cmd == "save" and new_match is not None:
                    # Update rule
                    sort_rules[rule_index] = new_match
                elif cmd == "move_left" and rule_index > 0:
                    # Move rule left:
                    sort_rules[rule_index], sort_rules[rule_index - 1] = (
                        sort_rules[rule_index - 1],
                        sort_rules[rule_index],
                    )
                    RULE_GRID_PAGE = (rule_index - 1) // RULE_GRID_CELLS
                elif cmd == "move_right" and rule_index < len(sort_rules) - 1:
                    # Move rule right:
                    sort_rules[rule_index], sort_rules[rule_index + 1] = (
                        sort_rules[rule_index + 1],
                        sort_rules[rule_index],
                    )
                    RULE_GRID_PAGE = (rule_index + 1) // RULE_GRID_CELLS
                continue


if __name__ == "__main__":
    # Load existing rules
    Sorter.RULE_SETS = load_sort_rules(Sorter.RULES_FILEPATH)

    # Open shortcut gump
    while Player.Connected:
        result = Sorter.gump_shortcut()
        if not result:
            break

    Logging.Info("Bye!")
