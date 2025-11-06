from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import Optional, Tuple, List


RAISED_BED = [
    0x4B22,  # top left
    0x4B28,  # top center
    0x4B23,  # top right
    0x4B24,  # middle left
    0x4B29,  # middle center
    0x4B25,  # middle right
    0x4B26,  # bottom left
    0x4B2A,  # bottom center
    0x4B27,  # bottom right
]

FIELD_BED = [
    0xA30D,  # top left
    0xA313,  # top center
    0xA30E,  # top right
    0xA30F,  # middle left
    0xA314,  # middle center
    0xA310,  # middle right
    0xA311,  # bottom left
    0xA315,  # bottom center
    0xA312,  # bottom right
]


PLANTS = [
    0x0913,  # dirt
    0x0C62,  # sapling
    10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467, 3273, 6810, 3204, 6815, 3265, 3326, 3215, 3272, 3214, 3365, 3255, 3262, 3521, 3323, 3512, 6817, 9324, 19340, 3230, 3203, 3206, 3208, 3220, 3211, 3237, 3239, 3223, 3231, 3238, 3228, 3377, 3332, 3241, 3372, 3366, 3367,
]


def detect_bed(serial: int) -> Optional[Tuple[int, int, int, int, int]]:
    # Sanity check
    cur_item = Items.FindBySerial(serial)
    if cur_item is None:
        return
    if not cur_item.OnGround:
        return
    
    # Record some states
    # x, y, z = coords of the current "garden bed" piece
    # zp = the z coordinate where the plants should lie at
    # bed_type = the current bed type. ("plant" is an alias for "not determined yet")
    cur_pos = cur_item.Position
    x, y, z = cur_pos.X, cur_pos.Y, cur_pos.Z
    zp = z
    if cur_item.ItemID in RAISED_BED:
        bed_type = "raised"
        zp += 5
    elif cur_item.ItemID in FIELD_BED:
        bed_type = "field"
        zp += 1
    elif cur_item.ItemID in PLANTS:
        bed_type = "plant"
    else:
        return
    
    # List of coordinates of top-left corners
    coord_TLs = []
    # List of coordinates of bottom-right corners
    coord_BRs = []
    
    # For all scanned garden bed pieces
    filter = Items.Filter()
    filter.Enabled = True
    filter.Graphics = CList[Int32](RAISED_BED + FIELD_BED)
    filter.OnGround = True
    for item in Items.ApplyFilter(filter):
        pos = item.Position
        coords = (pos.X, pos.Y, pos.Z)
        # If the bed_type is still undetermined,
        if bed_type == "plant":
            # Guess the bed_type and the z coordinate of the garden bed piece beneath the plant
            if item.ItemID in FIELD_BED and (x, y, z - 1) == coords:
                bed_type = "field"
                z = z - 1
            elif item.ItemID in RAISED_BED and (x, y, z - 5) == coords:
                bed_type = "raised"
                z = z - 5
        # Record the coordinates of the top-left corners
        if item.ItemID in (RAISED_BED[0], FIELD_BED[0]):
            coord_TLs.append(coords)
        # Record the coordinates of the bottom-right corners
        elif item.ItemID in (RAISED_BED[8], FIELD_BED[8]):
            coord_BRs.append(coords)
    
    # If the bed_type is stilll undetermined, then it defaults to None
    if bed_type == "plant":
        return
    
    # For the x, y, z, coordinates of each top-left piece,
    for x0, y0, z0 in coord_TLs:
        # If its z-height is different from the height of the "current" bed piece, skip
        if z != z0:
            continue
        # For each of the possible bed shapes,
        for dx, dy in [(2, 2), (1, 2), (2, 1), (1, 1)]:
            # Compute the bottom-right coordinates
            x1, y1 = x0 + dx, y0 + dy
            # If that coordinates do not exist in the recorded list, skip
            if (x1, y1, z) not in coord_BRs:
                continue
            # If the "current" piece does not lie in the rect, skip
            if x < x0 or x > x1 or y < y0 or y > y1:
                continue
            return (x0, y0, x1, y1, zp)


def get_plants_on_bed(serial: int) -> Optional[List["Item"]]:
    """
    A function that retuns the list of plants on a garden bed.
    """
    if serial == -1:
        return
    
    result = detect_bed(serial)
    if result is None:
        return
    
    x0, y0, x1, y1, zp = result
    plants = []
    
    filter = Items.Filter()
    filter.Enabled = True
    filter.Graphics = CList[Int32](PLANTS)
    filter.OnGround = True
    for item in Items.ApplyFilter(filter):
        pos = item.Position
        x, y, z = pos.X, pos.Y, pos.Z
        if z != zp:
            continue
        if x < x0 or x > x1 or y < y0 or y > y1:
            continue
        plants.append(item)
    
    return plants


if __name__ == "__main__":
    while True:
        serial = Target.PromptTarget("Choose a garden bed piece.", 0x3B2)
        if serial == -1:
            break
        
        result = get_plants_on_bed(serial)
        if result is None:
            Misc.SendMessage("You must target either a garden bed or a plant on it.", 33)
        elif not result:
            Misc.SendMessage("No plant found.", 0x3B2)
        else:
            Misc.SendMessage(f"{len(result)} plants found on the bed!", 68)
            for item in result:
                Items.Message(item, 0x481, item.Name)