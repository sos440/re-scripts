REFRESH_DURATION = 500
"""Duration (in milliseconds) between refreshes of the durability information."""


DELAY_BETWEEN_EQUIPS = 500
"""Delay between successive equip/unequip commands."""

################################################################################
# Header
################################################################################

from AutoComplete import *
from typing import List, Tuple, Dict, Any, Optional
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

VERSION = "1.0.4"
SETTING_FILEDIR = os.path.join(PATH, "data")
SETTING_FILEPATH = os.path.join(SETTING_FILEDIR, f"{Player.Name} ({Player.Serial}).json")


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
        elif item.Container == Player.Serial:
            state = "equipped"
        elif item.Container == Player.Backpack.Serial:
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
    item = Items.FindBySerial(entry.serial)
    left_hand = Player.GetItemOnLayer("LeftHand")
    right_hand = Player.GetItemOnLayer("RightHand")
    if item.IsTwoHanded:
        to_unequip = []
        if left_hand is not None:
            LAST_LEFT_HAND = left_hand.Serial
            to_unequip.append("LeftHand")
        if right_hand is not None:
            to_unequip.append("RightHand")
        if len(to_unequip) > 0:
            Player.UnEquipUO3D(to_unequip)
            Misc.Pause(DELAY_BETWEEN_EQUIPS)
        Player.EquipUO3D([entry.serial])
    else:
        to_equip = [entry.serial]
        if LAST_LEFT_HAND != 0:
            to_equip.append(LAST_LEFT_HAND)
        if left_hand is not None and left_hand.IsTwoHanded:
            Player.UnEquipUO3D(["LeftHand"])
            Misc.Pause(DELAY_BETWEEN_EQUIPS)
        Player.EquipUO3D(to_equip)
    Misc.SendMessage(f"Equipping: {entry.name}", 68)
    Misc.Pause(450)


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
