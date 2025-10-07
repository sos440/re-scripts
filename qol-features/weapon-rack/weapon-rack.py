REFRESH_DURATION = 500
"""Duration (in milliseconds) between refreshes of the durability information."""

DELAY_BETWEEN_EQUIPS = 500
"""Delay between successive equip/unequip commands."""

RESTORE_POSITION = True
"""Whether to restore the item to its last known position after unequipping."""

################################################################################
# Header
################################################################################

from AutoComplete import *
from typing import List, Tuple, Dict, Any, Optional, Callable, TypeVar
from enum import Enum
import re
import json
import os
import sys

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)


################################################################################
# Settings
################################################################################

VERSION = "1.0.5"
SETTING_FILEDIR = os.path.join(PATH, "data")
SETTING_FILEPATH = os.path.join(SETTING_FILEDIR, f"{Player.Name} ({Player.Serial}).json")


################################################################################
# Logger
################################################################################


class Logger:
    COLOR_INFO = 0x3B2  # light grey
    COLOR_IMPORTANT = 0x44  # bright green
    COLOR_ERROR = 0x21  # red

    @classmethod
    def header(cls) -> str:
        return "[Weapon Rack]"

    @classmethod
    def info(cls, msg: str) -> None:
        Misc.SendMessage(f"{cls.header()} {msg}", cls.COLOR_INFO)

    @classmethod
    def important(cls, msg: str) -> None:
        Misc.SendMessage(f"{cls.header()} {msg}", cls.COLOR_IMPORTANT)

    @classmethod
    def error(cls, msg: str) -> None:
        Misc.SendMessage(f"{cls.header()} {msg}", cls.COLOR_ERROR)


################################################################################
# Rack Entry
################################################################################


class RackEntry:
    def __init__(
        self,
        serial: int,
        type: int,
        color: int = 0,
        name: str = "(Unnamed)",
        state: str = "ready",
    ):
        self.serial = int(serial)
        self.type = int(type)
        self.color = int(color)
        self.name = str(name)
        self.state = str(state)

    def __eq__(self, other: Any) -> bool:
        if other is None:
            return False
        if not isinstance(other, RackEntry):
            return NotImplemented
        return self.serial == other.serial and self.state == other.state

    @classmethod
    def from_serial(cls, serial: int) -> Optional["RackEntry"]:
        item = Items.FindBySerial(serial)
        if item is None:
            return None
        elif item.RootContainer == Player.Serial:
            state = "equipped"
        elif item.RootContainer == Player.Backpack.Serial:
            state = "ready"
        else:
            state = "inaccessible"
        return RackEntry(serial, item.ItemID, item.Color, item.Name, state)

    @classmethod
    def from_entry(cls, entry: "RackEntry") -> "RackEntry":
        new_entry = cls.from_serial(entry.serial)
        if new_entry is None:
            return cls(entry.serial, entry.type, entry.color, entry.name, "not found")
        new_entry.name = entry.name  # Preserve the custom name
        new_entry.type = new_entry.type or entry.type
        return new_entry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "serial": self.serial,
            "type": self.type,
            "color": self.color,
            "name": self.name,
        }


################################################################################
# Equip Manager
################################################################################


T = TypeVar("T")


class EquipManager:
    """
    Manages equipping and unequipping items.

    This manages the equip/unequip queue to ensure that commands
    are not sent too quickly in succession.

    This is because in some situations Player.UO3DEquip and Player.UO3DUnequip
    cannot be used, and the slower Player.Equip and Player.UnEquip must be used instead.
    """

    class Handedness(Enum):
        RIGHT = "right-handed"
        LEFT = "left-handed"
        TWOHAND = "both-handed"

    class HandState(Enum):
        EMPTY = "empty"
        RIGHT = "right-handed"
        LEFT = "left-handed"
        BOTH = "both-handed with left-handed"
        TWOHAND = "both-handed"

    class LastLocation:
        def __init__(self, container: int, x: int, y: int):
            self.container = container
            self.x = x
            self.y = y

    LAST_IN_HAND: Dict[Handedness, int] = {}
    LAST_CONT: Dict[int, LastLocation] = {}

    @classmethod
    def get_handedness(cls, item: Optional["Item"]) -> Optional[Handedness]:
        """
        Determines the handedness of the given item based on its layer.
        """
        if item is None:
            return None
        if item.Layer == "FirstValid":
            return cls.Handedness.RIGHT
        elif item.Layer == "LeftHand":
            tiledata = Statics.GetItemData(item.ItemID)
            if "Weapon" in str(tiledata.Flags):
                return cls.Handedness.TWOHAND
            else:
                return cls.Handedness.LEFT
        else:
            return None

    @classmethod
    def get_current_hands(cls) -> Dict[Handedness, "Item"]:
        """
        Get the currently equipped items in the player's hands.
        """
        cur_hands = {}
        cur_left = Player.GetItemOnLayer("LeftHand")
        cur_right = Player.GetItemOnLayer("RightHand")
        if cur_right is not None:
            cur_hands[cls.Handedness.RIGHT] = cur_right
        if cur_left is not None:
            handedness = cls.get_handedness(cur_left)
            if handedness is not None:
                cur_hands[handedness] = cur_left
        return cur_hands

    @classmethod
    def get_hand_state(cls, cur_hands: Dict[Handedness, "Item"]) -> HandState:
        """
        Determines the current hand state based on equipped items.
        """
        has_left = cls.Handedness.LEFT in cur_hands
        has_right = cls.Handedness.RIGHT in cur_hands
        has_twohand = cls.Handedness.TWOHAND in cur_hands

        if has_twohand:
            return cls.HandState.TWOHAND
        else:
            if has_left and has_right:
                return cls.HandState.BOTH
            elif has_left:
                return cls.HandState.LEFT
            elif has_right:
                return cls.HandState.RIGHT
            else:
                return cls.HandState.EMPTY

    @classmethod
    def delay(cls, f, *args, **kwargs):  # type: (Callable[..., T], *Any, **Any) -> T
        """
        Wraps a function to ensure a delay between successive calls.
        """
        Misc.Pause(Timer.Remaining("action-delay"))
        result = f(*args, **kwargs)
        Timer.Create("action-delay", DELAY_BETWEEN_EQUIPS)
        return result

    @classmethod
    def move_to_last_location(cls, item: Optional["Item"], unequip: bool = False) -> None:
        """
        Moves the item to its last known location if available, otherwise to the backpack.
        """
        item = None if item is None else Items.FindBySerial(item.Serial)
        if item is None:
            return
        if RESTORE_POSITION and item.Serial in cls.LAST_CONT:
            loc = cls.LAST_CONT[item.Serial]
            if item.Container == loc.container and item.Position.X == loc.x and item.Position.Y == loc.y:
                return
            cls.delay(Items.Move, item.Serial, loc.container, -1, loc.x, loc.y)
        elif unequip and item.RootContainer == Player.Serial:
            cls.delay(Items.Move, item.Serial, Player.Backpack.Serial, -1)

    @classmethod
    def delayed_equip(cls, serials: List[int], fast: bool = False) -> None:
        if fast:
            cls.delay(Player.EquipUO3D, serials)
            return
        for serial in serials:
            cls.delay(Player.EquipItem, serial)

    @classmethod
    def delayed_unequip(cls, layers: List[str], fast: bool = False) -> None:
        if fast:
            cls.delay(Player.UnEquipUO3D, layers)
            return
        for layer in layers:
            cls.move_to_last_location(Player.GetItemOnLayer(layer), unequip=True)

    @classmethod
    def equip(cls, serial: int) -> None:
        item = Items.FindBySerial(serial)
        if item is None:
            Logger.error("Item not found.")
            return
        if item.RootContainer == Player.Serial:
            Logger.info("Item is already equipped.")
            return
        if item.RootContainer != Player.Backpack.Serial:
            Logger.error("Item must be in your inventory.")
            return

        cls.LAST_CONT[serial] = cls.LastLocation(item.Container, item.Position.X, item.Position.Y)
        handedness = cls.get_handedness(item)

        cur_hands = cls.get_current_hands()
        cur_left = cur_hands.get(cls.Handedness.LEFT, None)
        cur_right = cur_hands.get(cls.Handedness.RIGHT, None)
        cur_twohand = cur_hands.get(cls.Handedness.TWOHAND, None)
        last_left = Items.FindBySerial(cls.LAST_IN_HAND.get(cls.Handedness.LEFT, 0))

        hand_state = cls.get_hand_state(cur_hands)
        is_in_top = item.Container == Player.Backpack.Serial

        if handedness == cls.Handedness.RIGHT:
            # If we are equipping a right-handed item
            if (handedness == cls.Handedness.RIGHT) and (last_left is not None) and (cur_left is None):
                # If we had a left-hand item before, but don't have it now, try to restore it
                if hand_state == cls.HandState.EMPTY:
                    if is_in_top and (last_left.Container == Player.Backpack.Serial):
                        cls.delayed_equip([serial, last_left.Serial], fast=True)
                    else:
                        cls.delayed_equip([serial, last_left.Serial])
                elif hand_state == cls.HandState.RIGHT:
                    if is_in_top:
                        if last_left.Container == Player.Backpack.Serial:
                            cls.delayed_equip([serial, last_left.Serial], fast=True)
                        else:
                            cls.delayed_equip([serial], fast=True)
                            cls.delayed_equip([last_left.Serial])
                        cls.move_to_last_location(cur_right)
                    else:
                        cls.delayed_unequip(["RightHand"])
                        cls.delayed_equip([serial, last_left.Serial])
                elif hand_state == cls.HandState.TWOHAND:
                    cls.delayed_unequip(["LeftHand"])
                    if is_in_top and (last_left.Container == Player.Backpack.Serial):
                        cls.delayed_equip([serial, last_left.Serial], fast=True)
                    else:
                        cls.delayed_equip([serial, last_left.Serial])
            else:
                # If there is no left-hand item to restore, just equip the right-hand item
                if hand_state in (cls.HandState.EMPTY, cls.HandState.LEFT):
                    cls.delayed_equip([serial])
                elif hand_state == cls.HandState.TWOHAND:
                    cls.delayed_unequip(["LeftHand"])
                    cls.delayed_equip([serial])
                elif is_in_top:
                    cls.delayed_equip([serial], fast=True)
                    cls.move_to_last_location(cur_right)
                else:
                    cls.delayed_unequip(["RightHand"])
                    cls.delayed_equip([serial])

        elif handedness == cls.Handedness.LEFT:
            # If we are equipping a left-handed item
            if hand_state in (cls.HandState.EMPTY, cls.HandState.RIGHT):
                cls.delayed_equip([serial])
            elif is_in_top:
                cls.delayed_equip([serial], fast=True)
                cls.move_to_last_location(cur_left)
                cls.move_to_last_location(cur_twohand)
            else:
                cls.delayed_unequip(["LeftHand"])
                cls.delayed_equip([serial])

        elif handedness == cls.Handedness.TWOHAND:
            # If we are equipping a two-handed item
            if hand_state == cls.HandState.EMPTY:
                cls.delayed_equip([serial])
            elif hand_state == cls.HandState.RIGHT:
                cls.delayed_unequip(["RightHand"])
                cls.delayed_equip([serial])
            else:
                if hand_state == cls.HandState.BOTH:
                    cls.delayed_unequip(["RightHand"])
                if is_in_top:
                    cls.delayed_equip([serial], fast=True)
                    cls.move_to_last_location(cur_left)
                    cls.move_to_last_location(cur_twohand)
                else:
                    cls.delayed_unequip(["LeftHand"])
                    cls.delayed_equip([serial])

        else:
            # If the item has no specific handedness, just equip it
            prev_item = Player.GetItemOnLayer(item.Layer)
            if item.Container == Player.Backpack.Serial:
                cls.delayed_equip([serial], fast=True)
                cls.move_to_last_location(prev_item)
            else:
                cls.delayed_unequip([item.Layer])
                cls.delayed_equip([serial], fast=True)

        cls.LAST_IN_HAND.update({hand: item.Serial for hand, item in cur_hands.items()})


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


# Gump IDs
GUMP_MAIN_ID = GumpTools.hashname("WeaponRackGump")
GUMP_ASK_NAME = GumpTools.hashname("WeaponRackAskNameGump")

# Button IDs
ID_MAIN_ADD = 1
ID_MAIN_EDIT = 2
ID_ASKNAME_ENTRY = 11
ID_ASKNAME_APPLY = 12
ID_ASKNAME_DELETE = 13
IDMOD_MAIN_EQUIP = 1000
IDMOD_MAIN_EDIT = 2000

# Gump formats
GUMP_CB = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""

# Last left hand (shield, for example)
LAST_LEFT_HAND = 0


def gump_edit(rack: List[RackEntry], idx: int) -> None:
    assert 0 <= idx < len(rack)
    entry = rack[idx]

    Gumps.CloseGump(GUMP_ASK_NAME)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 300, 100, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 300, 100)
    Gumps.AddHtml(gd, 10, 5, 290, 18, GUMP_CB.format(text="Enter a name for the weapon:"), False, False)
    Gumps.AddTextEntry(gd, 10, 35, 280, 20, 1153, ID_ASKNAME_ENTRY, entry.name)

    Gumps.AddButton(gd, 12, 65, 40021, 40031, ID_ASKNAME_APPLY, 1, 0)
    Gumps.AddHtml(gd, 12, 67, 126, 18, GUMP_CB.format(text="Rename Entry"), False, False)

    Gumps.AddButton(gd, 162, 65, 40297, 40298, ID_ASKNAME_DELETE, 1, 0)
    Gumps.AddHtml(gd, 162, 67, 126, 18, GUMP_CB.format(text="Delete Entry"), False, False)

    Gumps.SendGump(GUMP_ASK_NAME, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    if not Gumps.WaitForGump(GUMP_ASK_NAME, 60000):
        return

    gd = Gumps.GetGumpData(GUMP_ASK_NAME)
    if gd is None or gd.buttonid == 0:
        Misc.SendMessage(f"You canceled the edit.", 0x3B2)
        return

    if gd.buttonid == ID_ASKNAME_APPLY and len(gd.text) > 0:
        entry.name = gd.text[0]
        Misc.SendMessage(f"Weapon renamed to: {entry.name}", 68)
        return

    if gd.buttonid == ID_ASKNAME_DELETE:
        rack.pop(idx)
        Misc.SendMessage(f"Weapon entry deleted.", 68)
        return


def gump_main(rack: List[RackEntry], mode: str = "view") -> None:
    # parse mode
    if mode == "edit-all":
        IDMOD_BUTTON = IDMOD_MAIN_EDIT
        INNER_WIDTH = max((len(rack) + 1) * 80, 142)
        INNER_HEIGHT = 18 + 60 + 36
    elif mode == "edit":
        rack_filter = [entry for entry in rack if entry.state in ["ready", "equipped"]]
        IDMOD_BUTTON = IDMOD_MAIN_EDIT
        INNER_WIDTH = max((len(rack_filter) + 1) * 80, 142)
        INNER_HEIGHT = 18 + 60 + 36
    elif mode == "view":
        rack_filter = [entry for entry in rack if entry.state in ["ready", "equipped"]]
        IDMOD_BUTTON = IDMOD_MAIN_EQUIP
        INNER_WIDTH = max(len(rack_filter) * 80, 142)
        INNER_HEIGHT = 18 + 60 + 36
    else:
        raise ValueError("Invalid mode")

    WIDTH = 4 + INNER_WIDTH
    HEIGHT = 4 + INNER_HEIGHT

    Gumps.CloseGump(GUMP_MAIN_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, WIDTH, HEIGHT)
    Gumps.AddHtml(gd, 2, 2, INNER_WIDTH, 18, GUMP_CB.format(text="Weapon Rack"), False, False)

    # Items
    x = 2
    y = 2 + 18
    for idx, entry in enumerate(rack):
        px, py = GumpTools.get_centering_pos(entry.type, x, y, 80, 60, abs=False)
        if entry.state == "not found" and mode == "edit-all":
            Gumps.AddHtml(gd, x, y + 60, 80, 36, GUMP_CB.format(text=entry.name), False, False)
            Gumps.AddImageTiledButton(gd, x, y, 2328, 2329, IDMOD_BUTTON + idx, Gumps.GumpButtonType.Reply, 0, entry.type, 33, px, py)
            Gumps.AddTooltip(gd, "Weapon not found.")
            Gumps.AddLabelCropped(gd, x + 28, y + 21, 40, 18, 1153, "EDIT")
            x += 80
        elif entry.state == "inaccessible" and mode == "edit-all":
            Gumps.AddHtml(gd, x, y + 60, 80, 36, GUMP_CB.format(text=entry.name), False, False)
            Gumps.AddImageTiledButton(gd, x, y, 2328, 2329, IDMOD_BUTTON + idx, Gumps.GumpButtonType.Reply, 0, entry.type, entry.color, px, py)
            Gumps.AddTooltip(gd, entry.serial)
            Gumps.AddLabelCropped(gd, x + 28, y + 21, 40, 18, 1153, "EDIT")
            x += 80
        elif entry.state == "equipped":
            Gumps.AddHtml(gd, x, y + 60, 80, 36, GUMP_CB.format(text=entry.name), False, False)
            Gumps.AddImageTiledButton(gd, x, y, 2329, 2329, IDMOD_BUTTON + idx, Gumps.GumpButtonType.Reply, 0, entry.type, entry.color, px, py)
            Gumps.AddTooltip(gd, entry.serial)
            if mode == "edit":
                Gumps.AddLabelCropped(gd, x + 28, y + 21, 40, 18, 1153, "EDIT")
            x += 80
        elif entry.state == "ready":
            Gumps.AddHtml(gd, x, y + 60, 80, 36, GUMP_CB.format(text=entry.name), False, False)
            Gumps.AddImageTiledButton(gd, x, y, 2328, 2329, IDMOD_BUTTON + idx, Gumps.GumpButtonType.Reply, 0, entry.type, entry.color, px, py)
            Gumps.AddTooltip(gd, entry.serial)
            if mode == "edit":
                Gumps.AddLabelCropped(gd, x + 28, y + 21, 40, 18, 1153, "EDIT")
            x += 80

    # Add item
    if mode == "edit":
        Gumps.AddButton(gd, x, y, 2328, 2329, ID_MAIN_ADD, 1, 0)
        Gumps.AddLabelCropped(gd, x + 28, y + 21, 40, 18, 1153, "ADD")
        Gumps.AddButton(gd, WIDTH - 16, y - 16, 1209, 1210, 0, 1, 0)
        Gumps.AddTooltip(gd, "Click this to finish editing.")

    # Edit button
    if mode == "view":
        Gumps.AddButton(gd, WIDTH - 16, y - 16, 1209, 1210, ID_MAIN_EDIT, 1, 0)
        Gumps.AddTooltip(gd, "Click this to edit the weapon rack.")

    # Send the gump and listen for the response
    gd_def = GumpTools.tooltip_to_itemproperty(gd)
    Gumps.SendGump(GUMP_MAIN_ID, Player.Serial, 100, 100, gd_def, gd.gumpStrings)


def prompt_rack_entry() -> Optional[RackEntry]:
    """Prompts the user to select a weapon to add to the rack."""
    serial = Target.PromptTarget("Select a weapon to add to the rack.", 0x481)
    entry = RackEntry.from_serial(serial)
    if entry is None:
        Misc.SendMessage("Item not found.", 0x21)
        return
    return entry


def equip_entry(entry: RackEntry) -> None:
    global LAST_LEFT_HAND
    entry = RackEntry.from_entry(entry)
    if entry.state == "not found":
        Misc.SendMessage("The item is not found.", 0x21)
        return
    if entry.state == "equipped":
        Misc.SendMessage("The item is already equipped.", 0x3B2)
        return
    if entry.state == "inaccessible":
        Misc.SendMessage("The item must be in your inventory.", 0x21)
        return
    Misc.SendMessage(f"Equipping: {entry.name}", 68)
    EquipManager.equip(entry.serial)


if __name__ == "__main__":
    rack: List[RackEntry] = []
    mode: str = "view"

    # Load existing settings
    def _load_settings():
        if not os.path.exists(SETTING_FILEPATH):
            return
        with open(SETTING_FILEPATH, "r") as f:
            data = json.load(f)
            for entry in data:
                rack.append(RackEntry(**entry))

    # Save settings
    def _save_settings():
        os.makedirs(SETTING_FILEDIR, exist_ok=True)
        with open(SETTING_FILEPATH, "w") as f:
            json.dump([entry.to_dict() for entry in rack], f, indent=4)

    # Read the gump responses and process them
    def _loop():
        global rack, mode
        gd = Gumps.GetGumpData(GUMP_MAIN_ID)

        if gd is None or gd.buttonid == 0:
            mode = "view"
            return

        if gd.buttonid == ID_MAIN_EDIT:
            mode = "edit"
            return

        if gd.buttonid == ID_MAIN_ADD:
            new_entry = prompt_rack_entry()
            mode = "view"
            if new_entry is None:
                return
            if any(entry.serial == new_entry.serial for entry in rack):
                Misc.SendMessage("The item is already in the rack.", 0x3B2)
                return
            rack.append(new_entry)
            gump_edit(rack, len(rack) - 1)
            _save_settings()
            return

        entry_id = gd.buttonid - IDMOD_MAIN_EQUIP
        if 0 <= entry_id < len(rack):
            equip_entry(rack[entry_id])
            return

        entry_id = gd.buttonid - IDMOD_MAIN_EDIT
        if 0 <= entry_id < len(rack):
            gump_edit(rack, entry_id)
            _save_settings()
            # mode = "view"
            return

    _load_settings()
    gump_main(rack)
    while Player.Connected:
        if Gumps.WaitForGump(GUMP_MAIN_ID, REFRESH_DURATION):
            _loop()
            gump_main(rack, mode)
            # continue
        new_rack = [RackEntry.from_entry(entry) for entry in rack]
        if new_rack != rack:
            rack = new_rack
            gump_main(rack, mode)
            continue
