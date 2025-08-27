from AutoComplete import *
from typing import Tuple
import os
import sys
import re

# Load local modules
sys.path.append(os.path.dirname(__file__))
from runic_atlas import *


# Gump related
GUMP_ID = hash("MoveToLibraryGump") & 0xFFFFFFFF
GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
ID_EXECUTE = 1

# Position related
LIB_RUNE = 0x40F8CB9D
LIB_RUNE_POS = (762, 744, 0)
LIB_BOOK_POS = (761, 728, 7)
LIB_BOOK_TO_COPY = 0x40CECC14  # Tram 1
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


def get_player_pos() -> Tuple[int, int, int]:
    p = Player.Position
    return (p.X, p.Y, p.Z)


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


def move_to_library():
    if get_player_pos() != LIB_BOOK_POS:
        while get_player_pos() != LIB_RUNE_POS:
            Spells.CastChivalry("Sacred Journey")
            Target.WaitForTarget(10000, False)
            Target.TargetExecute(LIB_RUNE)
            Misc.Pause(2000)
        player_run_steps("North", 16)
        player_run_steps("West", 1)

    Journal.Clear()
    success = Journal.WaitJournal("copy rune", 3600000)
    if not success:
        Misc.SendMessage("No rune selected.", 33)
        return

    res = Journal.GetLineText("copy rune", False)
    rune_match = re.search(r"copy rune (\d+)", res)
    if not rune_match:
        Misc.SendMessage("Failed to parse the selected rune.", 33)
        return

    rune_no = int(rune_match.group(1))
    if rune_no < 1 or rune_no > 48:
        Misc.SendMessage("Rune number must be between 1 and 48.", 33)
        return
    Misc.SendMessage(f"Selected rune: {rune_no}", 0x3B2)

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
    RunicAtlasActions.sacred_journey()
    Misc.Pause(5000)


def show_button():
    Gumps.CloseGump(GUMP_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="To Rune Library"), False, False)

    Gumps.AddButton(gd, 10, 30, 40021, 40031, ID_EXECUTE, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text="Inspect"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


if __name__ == "__main__":
    while Player.Connected:
        show_button()
        if Gumps.WaitForGump(GUMP_ID, 3600000):
            gd = Gumps.GetGumpData(GUMP_ID)
            if gd is None or gd.buttonid == 0:
                continue
            if gd.buttonid == ID_EXECUTE:
                move_to_library()
                continue
