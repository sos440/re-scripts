from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


def GetGumpByText(text: str) -> int:
    """Find the ID of a gump containing the provided text."""
    for gump_id in Gumps.AllGumpIDs():
        for line in Gumps.GetLineList(gump_id, False):
            if text in line:
                return gump_id
    return 0


def WaitForGumpByText(text: str, delay: int) -> int:
    """Wait until the ID of a gump containing the provided text is found."""
    Timer.Create("gump-detect", delay)
    while Timer.Check("gump-detect"):
        gump_id = GetGumpByText(text)
        if gump_id != 0:
            return gump_id
        Misc.Pause(100)
    return 0


def WaitForRemoveTrapGump(delay: int) -> int:
    return WaitForGumpByText("Thou hast failed to solve the puzzle!", delay)


gumpid = WaitForRemoveTrapGump(15000)
if gumpid != 0:
    gd = Gumps.GetGumpData(gumpid)
    with open("./Data/rt_cylinder_result.txt", "w") as f:
        for line in gd.layoutPieces:
            f.write(line + "\n")
    Misc.SendMessage("Done!")
