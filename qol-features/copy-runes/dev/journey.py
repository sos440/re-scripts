from AutoComplete import *
from typing import Tuple
import os
import sys
import re

# Load local modules
sys.path.append(os.path.dirname(__file__))
from runic_atlas import *


# Gump related
GUMP_MOVETO_ID = hash("MoveToLibraryGump") & 0xFFFFFFFF
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

if Player.GetSkillValue("Chivalry") >= 100.0:
    BEST_SKILL = "Chivalry"
elif Player.GetSkillValue("Magery") >= 100.0:
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
        RunicAtlasActions.sacred_journey()
    elif BEST_SKILL == "Magery":
        RunicAtlasActions.recall()
    else:
        Misc.SendMessage("You need either 100 Chivalry or 100 Magery to use this script!", 33)
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


if __name__ == "__main__":
    while Player.Connected:
        move_next()
