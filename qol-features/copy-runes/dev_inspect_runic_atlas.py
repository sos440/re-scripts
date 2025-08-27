from AutoComplete import *
import re
from typing import List, Tuple, Optional
import os
import sys

# Load local modules
sys.path.append(os.path.dirname(__file__))
from runic_atlas import *


def main():
    # Close any existing page for safety
    gd = find_runic_atlas_gump()
    if gd is not None:
        Gumps.CloseGump(gd.gumpId)
        Misc.Pause(500)

    # Open the runic atlas
    book_serial = Target.PromptTarget("Select the runic atlas.", 0x47E)
    if not open_runic_atlas(book_serial):
        Misc.SendMessage("Failed to find the runic atlas!", 33)
        return

    # Initial scan
    ctx = RunicAtlasContext()
    if not ctx.open_page(3):
        Misc.SendMessage("Failed to scan the runic atlas!", 33)
        return

    RunicAtlasActions.select_rune(47)

    # Debug: sojourn
    for index, rune in enumerate(ctx.runes):
        if not find_runic_atlas_gump():
            if not open_runic_atlas(book_serial):
                Misc.SendMessage(f"DEBUG|{index}> Failed to use the book.", 33)
                continue

        page = 1 + (index // 16)
        if not ctx.open_page(page):
            Misc.SendMessage(f"DEBUG|{index}> Failed to open the page.", 33)
            continue

        RunicAtlasActions.select_rune(index)
        Misc.Pause(250)
        if not ctx.open_page(page):
            Misc.SendMessage(f"DEBUG|{index}> Failed to select the entry.", 33)
            continue

        if ctx.selected_index != index:
            if rune.name == "Empty":
                Misc.SendMessage(f"DEBUG|{index}> Reached the end?", 68)
            else:
                Misc.SendMessage(f"DEBUG|{index}> Failed to parse the selected index.", 33)
            return

        if rune.x == -1 or rune.y == -1:
            if rune.name == "Empty":
                Misc.SendMessage(f"DEBUG|{index}> Reached the end?", 68)
            else:
                Misc.SendMessage(f"DEBUG|{index}> Failed to parse the coordinates.", 33)
            return

        RunicAtlasActions.recall()
        Misc.Pause(5000)


if __name__ == "__main__":
    main()
