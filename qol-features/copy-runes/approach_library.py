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

# Position related
LIB_RUNE_POS = (762, 744, 0)
LIB_BOOK_POS = (761, 728, 7)
DIR_TO_POS = {
    "Up": (-1, -1),
    "North": (0, -1),
    "Right": (1, -1),
    "East": (1, 0),
    "Down": (1, 1),
    "West": (-1, 0),
    "Left": (-1, 1),
    "South": (0, 1),
}

# State variables
LIB_RUNE = 0
LIB_BOOK_TO_COPY = 0
LIB_BOOK_NEW = 0
BEST_SKILL = None
RUNE_INDEX = 1  # 1-48

if Player.GetSkillValue("Chivalry") >= 100.0:
    BEST_SKILL = "Chivalry"
elif Player.GetSkillValue("Magery") >= 100.0:
    BEST_SKILL = "Magery"


def get_player_pos() -> Tuple[int, int, int]:
    p = Player.Position
    return (p.X, p.Y, p.Z)


def obtain_runic_atlas():
    global LIB_BOOK_TO_COPY
    if LIB_BOOK_TO_COPY != 0:
        return

    serial = Target.PromptTarget("Target the runic atlas to copy from.", 0x3B2)
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
    if Player.DistanceTo(item) > 2:
        Misc.SendMessage("You are too far away from the runic atlas!", 33)
        sys.exit(0)

    LIB_BOOK_TO_COPY = serial


def obtain_lib_rune():
    global LIB_RUNE
    if LIB_RUNE != 0:
        return

    serial = Target.PromptTarget("Target the rune for the library.", 0x3B2)
    item = Items.FindBySerial(serial)
    if serial == 0:
        Misc.SendMessage("No target selected.", 0x3B2)
        sys.exit(0)
    if item is None:
        Misc.SendMessage("Invalid target.", 33)
        sys.exit(0)
    if item.ItemID not in (0x1F14, 0x22C5, 0x9C16, 0x9C17):
        Misc.SendMessage("You cannot recall with this object.", 33)
        sys.exit(0)
    if item.Container != Player.Backpack.Serial:
        Misc.SendMessage("The object must be in your inventory.", 33)
        sys.exit(0)

    LIB_RUNE = serial


def obtain_new_book():
    global LIB_BOOK_NEW
    if LIB_BOOK_NEW != 0:
        return

    serial = Target.PromptTarget("Target the new runic atlas to fill in.", 0x3B2)
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
        Misc.SendMessage("The book must be in your inventory.", 33)
        sys.exit(0)

    LIB_BOOK_NEW = serial


def player_run_steps(dir: str, steps: int):
    if dir not in DIR_TO_POS:
        raise ValueError("Invalid direction!")
    x0, y0, _ = get_player_pos()
    dx, dy = DIR_TO_POS[dir]
    xp, yp = x0 + steps * dx, y0 + steps * dy
    for _ in range(steps):
        Player.Run(dir)
    while True:
        x1, y1, _ = get_player_pos()
        if (x1, y1) == (xp, yp):
            return
        if Misc.Distance(x1, y1, xp, yp) == 1:
            Misc.Pause(200)
        Player.Run(dir)


def mark_rune(rune_text: str):
    global LIB_BOOK_NEW
    while Player.Connected:
        response = show_button(f"Please mark: {rune_text}", "Mark")
        if not response:
            continue
        # Obtain a blank rune
        rune = None
        for item in Items.FindAllByID(0x1F14, 0, Player.Backpack.Serial, 2):
            props = Items.GetProperties(item.Serial, 1000)
            if len(props) == 2:
                rune = item
                break
        if rune is None:
            Misc.SendMessage("You need a blank rune to mark!", 33)
            continue
        # Cast mark
        Target.Cancel()
        scroll_mark = Items.FindByID(0x1F59, -1, Player.Backpack.Serial, 0)
        if BEST_SKILL == "Magery":
            # Check if enough mana
            if Player.Mana < 18:
                Misc.SendMessage("You don't have enough mana to mark the rune!", 33)
                continue
            Spells.Cast("Mark")
        elif scroll_mark is not None:
            # Check if enough mana
            if Player.Mana < 10:
                Misc.SendMessage("You don't have enough mana to mark the rune!", 33)
                continue
            Items.UseItem(scroll_mark.Serial)
        else:
            Misc.SendMessage("You don't have a mark scroll to use!", 33)
            continue
        if not Target.WaitForTarget(3000, False):
            Misc.SendMessage("Failed to cast mark.", 33)
            continue
        Target.TargetExecute(rune.Serial)
        Misc.Pause(1000)
        # Rename the rune
        while not Misc.HasPrompt():
            Items.UseItem(rune.Serial)
            Misc.Pause(1000)
        Misc.ResponsePrompt(rune_text)
        Items.SetColor(rune.Serial, 1153)
        # Move the rune to the new book
        obtain_new_book()
        Items.Move(rune.Serial, LIB_BOOK_NEW, -1)
        break


def move_to_library():
    obtain_lib_rune()
    if get_player_pos() != LIB_BOOK_POS:
        while get_player_pos() != LIB_RUNE_POS:
            if BEST_SKILL == "Chivalry":
                Spells.CastChivalry("Sacred Journey")
            elif BEST_SKILL == "Magery":
                Spells.Cast("Recall")
            else:
                Misc.SendMessage("You need either 100 Chivalry or 100 Magery to use this script!", 33)
                Misc.Pause(10000)
            Target.WaitForTarget(3300, False)
            Target.TargetExecute(LIB_RUNE)
            Misc.Pause(2000)
        player_run_steps("North", 16)
        player_run_steps("West", 1)

    obtain_runic_atlas()

    global RUNE_INDEX
    while Player.Connected:
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

    if not open_runic_atlas(LIB_BOOK_TO_COPY):
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

    if ctx.selected_index != rune_no:
        Misc.SendMessage("Failed to select the rune!", 33)
        return

    Misc.SendMessage(f"Recalling rune: {ctx.runes[rune_no].name}", 0x3B2)
    if BEST_SKILL == "Chivalry":
        RunicAtlasActions.sacred_journey()
    elif BEST_SKILL == "Magery":
        RunicAtlasActions.recall()
    else:
        Misc.SendMessage("You need either 100 Chivalry or 100 Magery to use this script!", 33)
        return

    # Wait for the player to mark the rune
    mark_rune(ctx.runes[rune_no].name)

    # Increment the rune index for next time
    RUNE_INDEX = min(48, RUNE_INDEX + 1)


def show_button(text: str = "", button_text: str = "Execute") -> bool:
    Gumps.CloseGump(GUMP_MOVETO_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text=text), False, False)

    Gumps.AddButton(gd, 10, 30, 40021, 40031, ID_EXECUTE, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text=button_text), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MOVETO_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    # Wait for the response
    if not Gumps.WaitForGump(GUMP_MOVETO_ID, 3600000):
        return False
    gd = Gumps.GetGumpData(GUMP_MOVETO_ID)
    if gd is None:
        return False
    if gd.buttonid == ID_EXECUTE:
        return True
    return False


def show_index(index: int) -> Tuple[bool, int]:
    """
    Show a gump to select the rune index.

    Returns a tuple (apply: bool, index: int)
    """
    Gumps.CloseGump(GUMP_INDEX_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 90, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 90)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Choose the index"), False, False)

    Gumps.AddTextEntry(gd, 10, 32, 100, 18, 1153, ID_INPUT_INDEX, str(index))
    Gumps.AddButton(gd, 115, 32, 2435, 2436, ID_INDEX_UP, 1, 0)
    Gumps.AddButton(gd, 125, 32, 2437, 2438, ID_INDEX_DOWN, 1, 0)

    Gumps.AddButton(gd, 10, 55, 40021, 40031, ID_EXECUTE, 1, 0)
    Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_WT.format(text="Apply"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_INDEX_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    # Wait for the response
    if not Gumps.WaitForGump(GUMP_INDEX_ID, 3600000):
        return False, index

    gd = Gumps.GetGumpData(GUMP_INDEX_ID)
    if gd is None:
        Misc.SendMessage("Failed to get the index gump data.", 33)
        return False, index
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
    if gd.buttonid == ID_INDEX_UP:
        return False, index + 1
    if gd.buttonid == ID_INDEX_DOWN:
        return False, index - 1
    return False, index


if __name__ == "__main__":
    while Player.Connected:
        response = show_button("To Rune Library", "Move")
        if response:
            move_to_library()
