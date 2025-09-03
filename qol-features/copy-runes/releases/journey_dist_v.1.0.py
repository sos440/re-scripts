################################################################################
# Imports
################################################################################

from AutoComplete import *
import sys
import re
from typing import List, Tuple, Optional

################################################################################
# User Settings
################################################################################

CAST_CHIVALRY_SKILL_MIN = 100.0
CAST_CHIVALRY_MANA_MIN = 5
CAST_MAGERY_SKILL_MIN = 100.0
CAST_MAGERY_MANA_MIN = 18

################################################################################
# Core Library
################################################################################

GUMP_MOVETO_ID = 0


class RunicAtlasActions:
    @classmethod
    def close(cls):
        Gumps.CloseGump(GUMP_MOVETO_ID)

    @classmethod
    def rename(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 1)

    @classmethod
    def set_default(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 2)

    @classmethod
    def drop_rune(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 3)

    @classmethod
    def replace_rune(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 8)

    @classmethod
    def recall(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 4)

    @classmethod
    def gate_travel(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 6)

    @classmethod
    def sacred_journey(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 7)

    @classmethod
    def next_page(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 1150)

    @classmethod
    def prev_page(cls):
        Gumps.SendAction(GUMP_MOVETO_ID, 1151)

    @classmethod
    def select_rune(cls, index: int):
        Gumps.SendAction(GUMP_MOVETO_ID, 100 + index)

    @classmethod
    def move_up(cls, index: int):
        Gumps.SendAction(GUMP_MOVETO_ID, 2000 + index)

    @classmethod
    def move_down(cls, index: int):
        Gumps.SendAction(GUMP_MOVETO_ID, 3000 + index)


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


class RunicAtlasContext:
    page: int
    runes: List[Rune]
    selected_index: int

    def __init__(self):
        self.page = 1
        self.runes = [Rune() for _ in range(48)]
        self.selected_index = -1

    def update(self, gd: Gumps.GumpData) -> None:
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
                    self.page = 1
                elif last_button_id == 116:
                    self.page = 2
                elif last_button_id == 132:
                    self.page = 3
            elif args[0] == "croppedtext":
                if last_button_id < 100 or last_button_id >= 148:
                    continue
                if last_button_ln + 1 != line_no:
                    continue
                index = last_button_id - 100
                rune = self.runes[index]
                text_id = int(args[-1])
                color = int(args[-2])
                rune.name = gd.stringList[text_id]
                if color == 331:
                    self.selected_index = index
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
            self.runes[self.selected_index].x = sextant[0]
            self.runes[self.selected_index].y = sextant[1]

    def open_page(self, page: int, delay: int = 1500) -> bool:
        assert page in (1, 2, 3), "Invalid page number"

        for trial in range(4):
            if trial == 3:
                # This is normally impossible
                return False
            gd = wait_for_runic_atlas_gump()
            if gd is None:
                return False
            self.update(gd)
            if self.page < page:
                RunicAtlasActions.next_page()
            elif self.page > page:
                RunicAtlasActions.prev_page()
            else:
                break

        return True


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
    global GUMP_MOVETO_ID

    # If the gump ID is already known
    if GUMP_MOVETO_ID != 0:
        if not Gumps.WaitForGump(GUMP_MOVETO_ID, delay):
            return None
        return Gumps.GetGumpData(GUMP_MOVETO_ID)

    # Otherwise, use some tricks to identify the gump
    for _ in range(delay // 100):
        gd = find_runic_atlas_gump()
        if gd is not None:
            GUMP_MOVETO_ID = gd.gumpId
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


################################################################################
# Applications
################################################################################

# Gump related
GUMP_INDEX_ID = hash("RuneIndexGump") & 0xFFFFFFFF
GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
ID_EXECUTE = 1
ID_INPUT_INDEX = 2
ID_INDEX_UP = 3
ID_INDEX_DOWN = 4
ID_RESET = 5
ID_EXIT = 6

# State variables
RUNIC_ATLAS = 0
BEST_SKILL = None
RUNE_INDEX = 1  # 1-48

if Player.GetSkillValue("Chivalry") >= CAST_CHIVALRY_SKILL_MIN:
    BEST_SKILL = "Chivalry"
elif Player.GetSkillValue("Magery") >= CAST_MAGERY_SKILL_MIN:
    BEST_SKILL = "Magery"


def get_player_pos() -> Tuple[int, int, int]:
    p = Player.Position
    return (p.X, p.Y, p.Z)


def obtain_journey_book():
    global RUNIC_ATLAS
    if RUNIC_ATLAS != 0:
        return

    serial = Target.PromptTarget("Target the runic atlas to use for your journey.", 0x3B2)
    item = Items.FindBySerial(serial)
    if serial == 0:
        Misc.SendMessage("No target selected.", 0x3B2)
        sys.exit(0)
    if item is None:
        Misc.SendMessage("Invalid target.", 33)
        sys.exit(0)
    if item.ItemID not in (0x9C16, 0x9C17):
        Misc.SendMessage("That is not a runic atlas!", 33)
        sys.exit(0)
    if item.Container != Player.Backpack.Serial:
        Misc.SendMessage("The runic atlas must be in your inventory.", 33)
        sys.exit(0)

    RUNIC_ATLAS = serial


def move_next():
    global RUNIC_ATLAS, RUNE_INDEX
    while Player.Connected:
        obtain_journey_book()
        success, index = show_index(RUNE_INDEX)
        RUNE_INDEX = max(1, min(48, index))
        if success:
            break

    rune_no = RUNE_INDEX
    if rune_no < 1 or rune_no > 48:
        Misc.SendMessage("Rune number must be between 1 and 48.", 33)
        return

    # Close any existing page for safety
    gd = find_runic_atlas_gump()
    if gd is not None:
        Gumps.CloseGump(gd.gumpId)
        Misc.Pause(500)

    if not open_runic_atlas(RUNIC_ATLAS):
        Misc.SendMessage("Failed to find the runic atlas!", 33)
        return

    # Initial scan
    rune_no = rune_no - 1
    rune_page = 1 + (rune_no // 16)
    ctx = RunicAtlasContext()
    if not ctx.open_page(rune_page):
        Misc.SendMessage("Failed to open the page!", 33)
        return

    RunicAtlasActions.select_rune(rune_no)
    Misc.Pause(250)
    if not ctx.open_page(rune_page):
        Misc.SendMessage("Failed to open the page!", 33)
        return

    rune = ctx.runes[rune_no]
    if ctx.selected_index != rune_no:
        if rune.name == "Empty":
            Misc.SendMessage(f"I guess we reached the end of the runebook. Choose another runic atlas.", 68)
            RUNIC_ATLAS = 0
            RUNE_INDEX = 1
        else:
            Misc.SendMessage("Failed to select the rune!", 33)
        return

    Misc.SendMessage(f"Recalling rune: {rune.name}", 0x3B2)
    if BEST_SKILL == "Chivalry":
        if Player.Mana < CAST_CHIVALRY_MANA_MIN:
            Misc.SendMessage(f"Not enough mana to cast Sacred Journey. Required: {CAST_CHIVALRY_MANA_MIN}", 33)
            return
        RunicAtlasActions.sacred_journey()
    elif BEST_SKILL == "Magery":
        if Player.Mana < CAST_MAGERY_MANA_MIN:
            Misc.SendMessage(f"Not enough mana to cast Recall. Required: {CAST_MAGERY_MANA_MIN}", 33)
            return
        RunicAtlasActions.recall()
    else:
        Misc.SendMessage(f"You need either {CAST_CHIVALRY_SKILL_MIN} Chivalry or {CAST_MAGERY_SKILL_MIN} Magery to use this script!", 33)
        return

    # Increment the rune index for next time
    if RUNE_INDEX >= 48:
        RUNIC_ATLAS = 0
        RUNE_INDEX = 1
    else:
        RUNE_INDEX = min(48, RUNE_INDEX + 1)


def show_index(index: int) -> Tuple[bool, int]:
    """
    Show a gump to select the rune index.

    Returns a tuple (apply: bool, index: int)
    """
    global RUNE_INDEX, RUNIC_ATLAS
    Gumps.CloseGump(GUMP_INDEX_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 140, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 140)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Choose the index"), False, False)

    Gumps.AddTextEntry(gd, 10, 32, 100, 18, 1153, ID_INPUT_INDEX, str(index))
    Gumps.AddButton(gd, 115, 32, 2435, 2436, ID_INDEX_UP, 1, 0)
    Gumps.AddButton(gd, 125, 32, 2437, 2438, ID_INDEX_DOWN, 1, 0)

    Gumps.AddButton(gd, 10, 55, 40021, 40031, ID_EXECUTE, 1, 0)
    Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_WT.format(text="Apply"), False, False)

    Gumps.AddButton(gd, 10, 80, 40297, 40298, ID_RESET, 1, 0)
    Gumps.AddHtml(gd, 10, 82, 126, 18, GUMP_WT.format(text="Reset"), False, False)

    Gumps.AddButton(gd, 10, 105, 40297, 40298, ID_EXIT, 1, 0)
    Gumps.AddHtml(gd, 10, 107, 126, 18, GUMP_WT.format(text="Quit"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_INDEX_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    # Wait for the response
    if not Gumps.WaitForGump(GUMP_INDEX_ID, 3600000):
        return False, index

    gd = Gumps.GetGumpData(GUMP_INDEX_ID)
    if gd is None:
        Misc.SendMessage("Failed to get the index gump data.", 33)
        return False, index
    if gd.buttonid == ID_EXIT:
        Misc.SendMessage("Bye!", 68)
        sys.exit(0)
    if gd.buttonid == ID_EXECUTE and len(gd.text) > 0:
        try:
            new_index = int(gd.text[0])
        except Exception:
            Misc.SendMessage("Input must be a number.", 33)
            return False, index
        if new_index is not None:
            return True, new_index
        else:
            Misc.SendMessage("Input must be a number.", 33)
            return False, index
    if gd.buttonid == ID_RESET:
        RUNE_INDEX = 1
        RUNIC_ATLAS = 0
        Misc.SendMessage("Resetting the runic atlas and index.", 68)
        return False, 1
    if gd.buttonid == ID_INDEX_UP:
        return False, index + 1
    if gd.buttonid == ID_INDEX_DOWN:
        return False, index - 1
    return False, index


################################################################################
# Main
################################################################################


if __name__ == "__main__":
    while Player.Connected:
        move_next()
