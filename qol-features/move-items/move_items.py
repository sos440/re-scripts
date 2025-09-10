ACTION_DELAY = 900  # Delay between item moves in milliseconds
RETRY_DELAY = 250  # Delay between re-trials to move each item
MAX_TRIAL = 3  # Maximum number of trials to move items


################################################################################
# Move Items Script
################################################################################

from AutoComplete import *
from typing import Tuple, Optional
import re


GUMP_MAIN = hash("MoveItemMainGump") & 0xFFFFFFFF
GUMP_PROMPT = hash("MoveItemPromptGump") & 0xFFFFFFFF
GUMP_BUTTONTEXT_WRAP = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""


def find_by_target(msg: str, color: int = 0x3B2):
    serial = Target.PromptTarget(msg, color)
    return Items.FindBySerial(serial)


def to_proper_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def get_prop_html(item) -> str:
    Items.WaitForProps(item.Serial, 1000)
    props = Items.GetPropStringList(item.Serial)
    if len(props) == 0:
        return "<i>No Properties</i>"
    return f'<basefont color="#FFFF00">{to_proper_case(props[0])}</basefont>' + "".join(
        [f"<br />{to_proper_case(line)}" for line in props[1:]]
    )


def add_item_centered(gd: Gumps.GumpData, px: int, py: int, item_id: int, color: int = 0):
    """
    Adds the item graphics to the gump so that it is centered at the provided location.
    """
    bitmap = Items.GetImage(item_id, 0)
    w, h = bitmap.Width, bitmap.Height

    left, top, right, bottom = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            pixel = bitmap.GetPixel(x, y)
            if pixel.R or pixel.G or pixel.B:
                left = min(x, left)
                top = min(y, top)
                right = max(x, right)
                bottom = max(y, bottom)

    if right < left or bottom < top:
        return
    Gumps.AddItem(gd, px - (left + right) // 2, py - (top + bottom) // 2, item_id, color)


def gump_prompt(src_cont, dst_cont):
    Gumps.CloseGump(GUMP_PROMPT)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddBackground(gd, 0, 0, 520, 400, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 520, 400)

    Gumps.AddHtml(gd, 10, 10, 500, 18, GUMP_BUTTONTEXT_WRAP.format(text="CONFIRMATION"), False, False)

    # Src
    Gumps.AddHtml(gd, 10, 30, 240, 18, GUMP_BUTTONTEXT_WRAP.format(text="Source Container"), False, False)
    Gumps.AddBackground(gd, 88, 50, 84, 54, 9350)
    Gumps.AddTooltip(gd, get_prop_html(src_cont))
    add_item_centered(gd, 130, 77, src_cont.ItemID, src_cont.Color)

    # Dst
    Gumps.AddHtml(gd, 260, 30, 240, 18, GUMP_BUTTONTEXT_WRAP.format(text="Target Container"), False, False)
    Gumps.AddBackground(gd, 338, 50, 84, 54, 9350)
    Gumps.AddTooltip(gd, get_prop_html(dst_cont))
    add_item_centered(gd, 380, 77, dst_cont.ItemID, dst_cont.Color)

    # Arrows
    Gumps.AddImage(gd, 240, 67, 5601, 0)
    Gumps.AddImage(gd, 250, 67, 5601, 0)
    Gumps.AddImage(gd, 260, 67, 5601, 0)

    # Contents
    Gumps.AddHtml(gd, 10, 110, 500, 18, GUMP_BUTTONTEXT_WRAP.format(text="Source Contents"), False, False)
    Gumps.AddBackground(gd, 10, 130, 500, 230, 9350)
    left = 0xFFFFFFFF
    top = 0xFFFFFFFF
    right = 0
    bottom = 0
    dims = []
    for item in src_cont.Contains:
        x = item.Position.X
        y = item.Position.Y
        bitmap = Items.GetImage(item.ItemID, 0)
        left = min(left, x)
        top = min(top, y)
        right = max(right, x + bitmap.Width)
        bottom = max(bottom, y + bitmap.Height)
        dims.append((bitmap.Width, bitmap.Height))
    width = right - left
    height = bottom - top
    for item, (w, h) in zip(src_cont.Contains, dims):
        x = round(20 + (480 - w) * (item.Position.X - left) / max(1, width - w))
        y = round(140 + (210 - h) * (item.Position.Y - top) / max(1, height - h))
        Gumps.AddItem(gd, x, y, item.ItemID, item.Color)
        if item.Amount > 1:
            Gumps.AddItem(gd, x + 5, y + 5, item.ItemID, item.Color)

    # Footer
    Gumps.AddCheck(gd, 10, 366, 210, 211, False, 2)
    Gumps.AddHtml(
        gd, 35, 368, 200, 18, """<basefont color="#FFFFFF">Preserves the relative location</basefont>""", False, False
    )
    Gumps.AddButton(gd, 259, 365, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 259, 368, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Proceed"), False, False)
    Gumps.AddButton(gd, 385, 365, 40297, 40298, 0, 1, 0)
    Gumps.AddHtml(gd, 385, 368, 125, 18, GUMP_BUTTONTEXT_WRAP.format(text="Cancel"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_PROMPT, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    # Wait for response
    Gumps.WaitForGump(GUMP_PROMPT, 3600000)
    gd = Gumps.GetGumpData(GUMP_PROMPT)
    if gd.buttonid == 1:
        return True, (2 in gd.switches)
    return False, False


def find_topmost(obj: "Item") -> Optional["Item"]:
    while obj and obj.RootContainer:
        if Misc.IsItem(obj.RootContainer):
            obj = Items.FindBySerial(obj.RootContainer)
        elif Misc.IsMobile(obj.RootContainer):
            return Mobiles.FindBySerial(obj.RootContainer)
    return obj


def find_topmost_obj(obj: "Item") -> Optional["Item"]:
    while obj and obj.RootContainer and Misc.IsItem(obj.RootContainer):
        obj = Items.FindBySerial(obj.RootContainer)
    return obj


def move_items():
    # Obtain the source container
    src_cont = find_by_target("Choose the source container.", 0x47E)
    if src_cont is None:
        Misc.SendMessage("Failed to find the container!", 0x21)
        return
    if not src_cont.IsContainer:
        Misc.SendMessage("That is not a container!", 0x21)
        return

    # Obtain the destination container
    dst_cont = find_by_target("Choose the destination container.", 0x47E)
    if dst_cont is None:
        Misc.SendMessage("Failed to find the container!", 0x21)
        return
    if not dst_cont.IsContainer:
        Misc.SendMessage("That is not a container!", 0x21)
        return

    # Dobule check the source and destination containers
    src_cont = Items.FindBySerial(src_cont.Serial)
    dst_cont = Items.FindBySerial(dst_cont.Serial)
    if src_cont is None:
        Misc.SendMessage("Source container lost!", 0x21)
        return
    if dst_cont is None:
        Misc.SendMessage("Destination container lost!", 0x21)
        return
    if not src_cont.ContainerOpened and not Items.WaitForContents(src_cont.Serial, 1000):
        Misc.SendMessage("Failed to find the container contents!", 0x21)
        return
    if len(src_cont.Contains) == 0:
        Misc.SendMessage("The container is empty!", 68)
        return

    # Display the confirmation gump
    proceed, preserve_pos = gump_prompt(src_cont, dst_cont)
    if not proceed:
        Misc.SendMessage("Operation cancelled!", 68)
        return

    # Move items from source to destination
    num_total = len(src_cont.Contains)
    Misc.SendMessage(f"Moving {num_total} items...", 68)
    for i, item in enumerate(src_cont.Contains):
        item = Items.FindBySerial(item.Serial)
        if item is None:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: Failed to find the item!", 33)
            continue
            
        src_topcont = find_topmost(item)
        if src_topcont is None:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: Failed to find the source container!", 33)
            continue
        if Player.DistanceTo(src_topcont) > 2:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: The source container is too far!", 33)
            continue
            
        dst_cont = Items.FindBySerial(dst_cont.Serial)
        if dst_cont is None:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: Failed to find the destination container!!", 33)
            continue
            
        dst_topcont = find_topmost(dst_cont)
        if dst_topcont is None:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: Failed to find the destination container!!", 33)
            continue
        if Player.DistanceTo(dst_topcont) > 2:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: The destination container is too far!", 33)
            continue
            
        item_count = 0
        max_count = 0
        dst_topcont_obj = find_topmost_obj(dst_cont)
        Items.WaitForProps(dst_topcont_obj.Serial, 1000)
        for line in Items.GetPropStringList(dst_topcont_obj.Serial):
            matchres = re.match(r"^contents: (\d+)/(\d+) items.*", line.lower())
            if not matchres:
                continue
            item_count = int(matchres.group(1))
            max_count = int(matchres.group(2))
            break
        if item_count >= max_count:
            Misc.SendMessage(f"Moving {i + 1} of {num_total}: The target container is full!", 33)
            continue
        
        Misc.SendMessage(f"Moving {i + 1} of {num_total}: {to_proper_case(item.Name)}", 68)
        for trial in range(MAX_TRIAL + 1):
            if trial == MAX_TRIAL:
                Misc.SendMessage(f"Failed to move item {item.Name} after {MAX_TRIAL} trials.", 0x21)
                break

            if preserve_pos:
                x, y = item.Position.X, item.Position.Y
                Items.Move(item.Serial, dst_cont.Serial, -1, x, y)
            else:
                Items.Move(item.Serial, dst_cont.Serial, -1)
            Misc.Pause(ACTION_DELAY)

            item_moved = Items.FindBySerial(item.Serial)
            if item_moved is None:
                break
            if item_moved.Container != src_cont.Serial:
                break
            Misc.Pause(RETRY_DELAY)

    Misc.SendMessage("Operation finished!", 68)


def gump_main():
    Gumps.CloseGump(GUMP_MAIN)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddBackground(gd, 0, 0, 146, 75, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 75)

    Gumps.AddItem(gd, 20, 10, 3701, 0)
    Gumps.AddImage(gd, 60, 15, 5601, 0)
    Gumps.AddImage(gd, 67, 15, 5601, 0)
    Gumps.AddImage(gd, 74, 15, 5601, 0)
    Gumps.AddItem(gd, 83, 10, 3709, 0)

    Gumps.AddButton(gd, 10, 40, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 10, 42, 126, 28, GUMP_BUTTONTEXT_WRAP.format(text="Move Items"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MAIN, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    # Wait for response
    Gumps.WaitForGump(GUMP_MAIN, 3600000)
    gd = Gumps.GetGumpData(GUMP_MAIN)

    return gd.buttonid == 1


# Main loop
if __name__ == "__main__":
    while Player.Connected:
        proceed = gump_main()
        if not proceed:
            Misc.SendMessage("Bye!", 68)
            break
        move_items()
