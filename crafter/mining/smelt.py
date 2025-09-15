################################################################################
# Settings
################################################################################


DO_NOT_CLOSE = True


################################################################################
# Script starts here
# You do not need to modify anything beyond this point
################################################################################


from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import List, Optional, Union


# Ores of these colors will be smelted one at a time
ORE_DATA = {
    0: {"max-skill": 75, "metal": "iron"},
    2419: {"max-skill": 90, "metal": "dull copper"},
    2406: {"max-skill": 95, "metal": "shadow iron"},
    2413: {"max-skill": 100, "metal": "copper"},
    2418: {"max-skill": 105, "metal": "bronze"},
    2213: {"max-skill": 110, "metal": "golden"},
    2425: {"max-skill": 115, "metal": "agapite"},
    2207: {"max-skill": 120, "metal": "verite"},
    2219: {"max-skill": 124, "metal": "valorite"},
}

# Some constants
ORE_SMALL = [0x19B7]
ORE_LARGE = [0x19B8, 0x19B9, 0x19BA]
ORE = ORE_SMALL + ORE_LARGE
BACKPACK = Player.Backpack.Serial


def get_valuable_ores() -> List[int]:
    cur_mining = Player.GetSkillValue("Mining")
    return [color for color, entry in ORE_DATA.items() if entry["max-skill"] > cur_mining]


def find_forge() -> Optional[int]:
    # Scan for nearby fire beetles
    filter = Mobiles.Filter()
    filter.RangeMax = 2
    filter.Hues = CList[Int32]([0x0489])
    filter.Bodies = CList[Int32]([0x00A9])
    filter.Enabled = True
    fire_beetle = Mobiles.ApplyFilter(filter)
    if len(fire_beetle) > 0:
        return fire_beetle[0].Serial

    # Scan for nearby forges
    filter = Items.Filter()
    filter.RangeMax = 2
    filter.Graphics = CList[Int32]([0x0FB1] + list(range(0x197A, 0x19AA)))
    filter.OnGround = True
    filter.Enabled = True
    forges = Items.ApplyFilter(filter)
    if len(forges) > 0:
        return forges[0].Serial

    return None


def find_top_obj(item: "Item") -> Union["Item", "Mobile", None]:
    while item.RootContainer:
        if Misc.IsItem(item.RootContainer):
            obj = Items.FindBySerial(item.RootContainer)
            if obj is None:
                return
            item = obj
            continue
        elif Misc.IsMobile(item.RootContainer):
            return Mobiles.FindBySerial(item.RootContainer)
        else:
            return
    return item


def is_near(item: "Item") -> bool:
    obj = find_top_obj(item)
    if obj is None:
        return False
    elif Misc.IsMobile(obj.Serial):
        return obj.Serial == Player.Serial
    else:
        return Player.DistanceTo(item) <= 2


def find_near(itemid: Union[int, List[int]], color: Union[int, List[int]]) -> List["Item"]:
    """
    Return the list of items matching the given itemid and color,
    whose top-level container is within 2 tiles of the player.
    """

    filter = Items.Filter()

    if isinstance(itemid, int):
        itemid = [itemid]
    filter.Graphics = CList[Int32](itemid)

    if color != -1:
        if isinstance(color, int):
            color = [color]
        filter.Hues = CList[Int32](color)

    filter.Enabled = True
    scanned = [item for item in Items.ApplyFilter(filter) if is_near(item)]
    return scanned


def use_onto(ore: "Item", target: int) -> bool:
    Items.UseItem(ore.Serial)
    if not Target.WaitForTarget(400, True):
        return False
    Misc.Pause(400)
    Target.TargetExecute(target)
    Misc.Pause(400)
    return True


def merge_valuable() -> bool:
    # Scan for small ores with valuable colors
    for color in get_valuable_ores():
        scan_ores = find_near(ORE_SMALL, color)

        # Attempt to merge ores with amounts other than 2
        scan_merge = [ore for ore in scan_ores if ore.Amount != 2]
        if len(scan_merge) > 1:
            Items.Move(scan_merge[0].Serial, scan_merge[1].Serial, -1)
            Misc.Pause(800)
            return True
    return False


def smelt_small() -> bool:
    FORGE = find_forge()
    if FORGE is None:
        return False
    for ore in find_near(ORE_SMALL, list(ORE_DATA.keys())):
        if ore.Amount < 2:
            continue
        if ore.Amount > 3 and ore.Color in get_valuable_ores():
            continue
        use_onto(ore, FORGE)
        return True
    return False


def split_small_valuable() -> bool:
    for ore in find_near(ORE_SMALL, list(ORE_DATA.keys())):
        if ore.Amount > 3 and ore.Color in get_valuable_ores():
            Items.Move(ore.Serial, BACKPACK, 2, 0, 0)
            Misc.Pause(800)
            return True
    return False


def smelt_large() -> bool:
    FORGE = find_forge()
    if FORGE is None:
        return False
    for ore in find_near(ORE_LARGE, list(ORE_DATA.keys())):
        if ore.Amount > 1 and ore.Color in get_valuable_ores():
            continue
        use_onto(ore, FORGE)
        return True
    return False


def split_large_valuable() -> bool:
    for ore in find_near(ORE_LARGE, -1):
        if ore.Color in get_valuable_ores():
            Items.Move(ore.Serial, BACKPACK, 1, 0, 0)
            Misc.Pause(800)
            return True
    return False


def smelt():
    while True:
        if find_forge() is None:
            Player.HeadMessage(0x21, "No forge found nearby!")
            return
        if merge_valuable():
            continue
        if smelt_small():
            continue
        if split_small_valuable():
            continue
        if smelt_large():
            continue
        if split_large_valuable():
            continue
        break

    Player.HeadMessage(0x481, "Done!")


GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
SHORTCUT_GUMP_ID = hash("SmeltOreGump") & 0xFFFFFFFF


def ask_to_smelt() -> bool:
    """
    A minimized gump with a button to initiate the smelting process.
    """
    Gumps.CloseGump(SHORTCUT_GUMP_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Auto Smelt"), False, False)

    Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text="Start"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, 3600000):
        return False
    gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
    if gd is None:
        return False
    return gd.buttonid == 1


if __name__ == "__main__":
    while Player.Connected:
        response = ask_to_smelt()
        if response:
            smelt()
        elif not DO_NOT_CLOSE:
            break
