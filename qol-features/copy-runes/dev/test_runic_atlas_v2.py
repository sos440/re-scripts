################################################################################
# User Settings
################################################################################

CAST_CHIVALRY_SKILL_MIN = 100.0
"""Minimum skill required to cast Sacred Journey"""

CAST_CHIVALRY_MANA_MIN = 5
"""Minimum mana required to cast Sacred Journey"""

CAST_MAGERY_SKILL_MIN = 100.0
"""Minimum skill required to cast Recall"""

CAST_MAGERY_MANA_MIN = 18
"""Minimum mana required to cast Recall"""

################################################################################
# Imports
################################################################################

from AutoComplete import *
import sys
import re
from typing import List, Tuple, Optional

################################################################################
# Helper functions
################################################################################


def decode_sextant(msg: str) -> Optional[Tuple[int, int]]:
    # Constants
    N_WIDTH = 5120
    N_HEIGHT = 4096
    N_CENTER_X = 1323
    N_CENTER_Y = 1624

    # Parse message
    pattern = r"<center>(\d+)° (\d+)'([NS]), (\d+)° (\d+)'([EW])</center>"
    match = re.search(pattern, msg)
    if not match:
        return

    xdegree = int(match.group(4))
    xminute = int(match.group(5))
    x_type = match.group(6).upper()
    ydegree = int(match.group(1))
    yminute = int(match.group(2))
    y_type = match.group(3).upper()

    # Convert types and normalize input
    xdegree = xdegree + (xminute / 60)
    ydegree = ydegree + (yminute / 60)

    # Apply direction adjustments
    if x_type == "W":
        xdegree = -xdegree
    if y_type == "N":
        ydegree = -ydegree

    # Adjust to Lord British's throne coordinates
    x = int(round(xdegree * N_WIDTH / 360) + N_CENTER_X) % N_WIDTH
    y = int(round(ydegree * N_HEIGHT / 360) + N_CENTER_Y) % N_HEIGHT

    return x, y


def find_runic_atlas_gump() -> Optional[Gumps.GumpData]:
    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        if gd is None:
            continue

        # Checks if the gump is runic atlas
        if not gd.gumpLayout.startswith("{ gumppic 0 0 39923 }"):
            continue
        if len(gd.gumpText) == 0 or not gd.gumpText[0].startswith("Charges:"):
            continue

        return gd
    return None


def wait_for_runic_atlas_gump(delay: int = 1500) -> Optional[Gumps.GumpData]:
    global GUMP_RUNIC_ATLAS

    # If the gump ID is already known
    if GUMP_RUNIC_ATLAS != 0:
        if not Gumps.WaitForGump(GUMP_RUNIC_ATLAS, delay):
            return None
        return Gumps.GetGumpData(GUMP_RUNIC_ATLAS)

    # Otherwise, use some tricks to identify the gump
    for _ in range(delay // 100):
        gd = find_runic_atlas_gump()
        if gd is not None:
            GUMP_RUNIC_ATLAS = gd.gumpId
            return gd
        Misc.Pause(100)

    return None


def open_runic_atlas(serial: int, delay: int = 1500) -> bool:
    obj = Items.FindBySerial(serial)
    if obj is None:
        return False
    if obj.ItemID not in (0x9C16, 0x9C17):
        return False
    Items.UseItem(serial)
    return True


GUMP_RUNIC_ATLAS = 0

################################################################################
# Helper functions
################################################################################


class Rune:
    name: str
    marked: bool
    x: int
    y: int
    facet: int

    def __init__(self):
        self.name = ""
        self.marked = False
        self.x = -1
        self.y = -1
        self.facet = -1


class RunicAtlasSnapshot:
    """
    Represents a static snapshot of the runic atlas.
    """

    page: int
    runes: List[Rune]
    selected_index: int

    def __init__(self):
        self.page = 1
        self.runes = [Rune() for _ in range(48)]
        self.selected_index = -1


class RunicAtlasControl:
    class Buttons:
        @staticmethod
        def close():
            Gumps.CloseGump(GUMP_RUNIC_ATLAS)

        @staticmethod
        def rename():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 1)

        @staticmethod
        def set_default():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 2)

        @staticmethod
        def drop_rune():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 3)

        @staticmethod
        def replace_rune():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 8)

        @staticmethod
        def recall():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 4)

        @staticmethod
        def gate_travel():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 6)

        @staticmethod
        def sacred_journey():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 7)

        @staticmethod
        def next_page():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 1150)

        @staticmethod
        def prev_page():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 1151)

        @staticmethod
        def select_rune(index: int):
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 100 + index)

        @staticmethod
        def move_up(index: int):
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 2000 + index)

        @staticmethod
        def move_down(index: int):
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 3000 + index)

    @classmethod
    def update_snapshot(cls, snapshot: RunicAtlasSnapshot, gd: Gumps.GumpData) -> None:
        """
        Read the current state of the runic atlas from the gump data.
        """
        sextant: Optional[Tuple[int, int]] = None

        last_button_id = -1
        last_button_ln = -1
        has_selected_entry = False
        for line_no, line_str in enumerate(gd.layoutPieces):
            line_str = line_str.strip()
            args = line_str.split()
            if args[0] == "button":
                last_button_id = int(args[-1])
                last_button_ln = line_no
                if last_button_id == 100:
                    snapshot.page = 1
                elif last_button_id == 116:
                    snapshot.page = 2
                elif last_button_id == 132:
                    snapshot.page = 3
            elif args[0] == "croppedtext":
                if last_button_id < 100 or last_button_id >= 148:
                    continue
                if last_button_ln + 1 != line_no:
                    continue
                index = last_button_id - 100
                rune = snapshot.runes[index]
                text_id = int(args[-1])
                color = int(args[-2])
                rune.name = gd.stringList[text_id]
                if color == 331:
                    snapshot.selected_index = index
                    has_selected_entry = True
                elif color == 81:
                    rune.facet = 0  # Felucca
                elif color == 10:
                    rune.facet = 1  # Trammel
                elif color == 0:
                    rune.facet = 2  # Illshenar
                elif color == 1102:
                    rune.facet = 3  # Malas
                elif color == 1154:
                    rune.facet = 4  # Tokuno
                elif color == 1645:
                    rune.facet = 5  # Ter Mur
            elif line_str.startswith("htmlgump 25 254 182 18"):
                text_id = int(args[5])
                sextant = decode_sextant(gd.stringList[text_id])

        if has_selected_entry and sextant is not None:
            snapshot.runes[snapshot.selected_index].x = sextant[0]
            snapshot.runes[snapshot.selected_index].y = sextant[1]

    @classmethod
    def goto_page(cls, snapshot: RunicAtlasSnapshot, page: int, delay: int = 1500) -> bool:
        """
        Move to the specified page in the runic atlas, if the gump is open.
        """
        assert page in (1, 2, 3), "Invalid page number"

        for trial in range(4):
            if trial == 3:
                # This is normally impossible
                return False
            gd = wait_for_runic_atlas_gump()
            if gd is None:
                return False
            cls.update_snapshot(snapshot, gd)
            if snapshot.page < page:
                cls.Buttons.next_page()
            elif snapshot.page > page:
                cls.Buttons.prev_page()
            else:
                break

        return True

    @staticmethod
    def close():
        """
        Close the current runic atlas gump if it is open.
        """
        gd = find_runic_atlas_gump()
        if gd is not None:
            Gumps.CloseGump(gd.gumpId)

    @classmethod
    def read_all(cls, read_coordinates: bool = True) -> Optional[RunicAtlasSnapshot]:
        """
        Move to the specified page in the runic atlas, if the gump is open.
        """
        # Read all pages
        snapshot = RunicAtlasSnapshot()
        if not cls.goto_page(snapshot, 3):
            return None
        if not cls.goto_page(snapshot, 1):
            return None

        # Read all coordinates
        if read_coordinates:
            prev_page = 0
            for index in range(48):
                if snapshot.runes[index].name == "Empty":
                    break
                page = 1 + (index // 16)
                if prev_page != page and not cls.goto_page(snapshot, page):
                    return None
                prev_page = page
                cls.Buttons.select_rune(index)
                if not cls.goto_page(snapshot, page):
                    return None

        return snapshot


def get_runic_atlas() -> Optional["Item"]:
    """
    Ask the player to target the runic atlas and return its serial.
    """
    serial = Target.PromptTarget("Target the runic atlas to use for your journey.", 0x3B2)
    item = Items.FindBySerial(serial)
    if serial == 0:
        Misc.SendMessage("No target selected.", 0x3B2)
        return
    if item is None:
        Misc.SendMessage("Invalid target.", 33)
        return
    if item.ItemID not in (0x9C16, 0x9C17):
        Misc.SendMessage("That is not a runic atlas!", 33)
        return
    if item.RootContainer != Player.Backpack.Serial:
        Misc.SendMessage("The runic atlas must be in your inventory.", 33)
        return
    return item


def main():
    runic_atlas = get_runic_atlas()
    if runic_atlas is None:
        Misc.SendMessage(f"Failed to find runic atlas.", 0x21)
        return

    # Continue with the main logic using the runic_atlas
    Misc.SendMessage(f"Using runic atlas: {runic_atlas.Serial}", 0x3B2)
    Items.UseItem(runic_atlas.Serial)

    snapshot = RunicAtlasControl.read_all(read_coordinates=False)
    RunicAtlasControl.close()

    if snapshot is None:
        Misc.SendMessage(f"Failed to read runic atlas: {runic_atlas.Serial}", 0x21)
        return

    for rune in snapshot.runes:
        Misc.SendMessage(f"{rune.name}", 0x3B2)


if __name__ == "__main__":
    main()
