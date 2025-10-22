from AutoComplete import *
import re


def get_gump_by_text(text: str) -> int:
    """Find the ID of a gump containing the provided text."""
    for gump_id in Gumps.AllGumpIDs():
        for line in Gumps.GetLineList(gump_id, False):
            if text in line:
                return gump_id
    return 0


def wait_for_gump_by_text(text: str, delay: int) -> int:
    """Wait until the ID of a gump containing the provided text is found."""
    Timer.Create("gump-delay", delay)
    while Timer.Check("gump-delay"):
        gump_id = get_gump_by_text(text)
        if gump_id != 0:
            return gump_id
        Misc.Pause(100)
    return 0


def scan():
    gump_id = wait_for_gump_by_text("<CENTER>BLACKSMITHING MENU</CENTER>", 1000)
    Misc.SendMessage(f"Gump ID: {gump_id}", 68)
    if not gump_id:
        return

    # Read category buttons
    lines = Gumps.GetGumpRawLayout(gump_id).strip(" {}").split(" }{ ")
    cat_buttons = []
    for line in lines:
        args = line.split(" ")
        matchres = re.match(r"button 15 (\d+) 4005 4007 1 0 (\d+)", line)
        if matchres is None:
            continue
        dy = int(matchres.group(1)) - 80
        if dy >= 0 and (dy % 20 == 0):
            cat_buttons.append(int(matchres.group(2)))

    # Read pages
    item_button_map = {}
    for cat_button in cat_buttons:
        Gumps.SendAction(gump_id, cat_button)
        if not Gumps.WaitForGump(gump_id, 1000):
            Misc.SendMessage("Failed to find the gump.", 0x21)
            return

        lines = Gumps.GetGumpRawLayout(gump_id).strip(" {}").split(" }{ ")
        i = 0
        page = 0
        while i < len(lines):
            line = lines[i]
            i += 1

            matchres = re.match(r"page (\d+)", line)
            if matchres is not None:
                page = int(matchres.group(1))
                continue
            if page == 0:
                continue

            matchres = re.match(r"button 220 \d+ 4005 4007 1 0 (\d+)", line)
            if matchres is None:
                continue
            button_make = int(matchres.group(1))
            matchres = re.match(r"xmfhtmlgumpcolor 255 \d+ 220 18 (\d+) 0 0 32767", lines[i])
            if matchres is None:
                Misc.SendMessage("Failed to parse the line.", 0x21)
                continue
            item_make = int(matchres.group(1))
            item_button_map[item_make] = (cat_button, button_make)
            i += 2
            continue

    import json

    with open(Misc.ScriptDirectory() + "/crafting_map.json", "w") as f:
        json.dump(item_button_map, f, indent=4)

    Misc.SendMessage("Done")


scan()
