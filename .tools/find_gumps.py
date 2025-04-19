import time


def get_gump_by_text(text: str) -> int:
    """Find the ID of a gump containing the provided text."""
    for gump_id in Gumps.AllGumpIDs():
        for line in Gumps.GetLineList(gump_id, False):
            if text in line:
                return gump_id
    return 0


def wait_for_gump_by_text(text: str, delay: int) -> int:
    """Wait until the ID of a gump containing the provided text is found."""
    t_expire = time.time() + delay / 1000
    while time.time() < t_expire:
        gump_id = get_gump_by_text(text)
        if gump_id != 0:
            return gump_id
        Misc.Pause(100)
    return 0


# Example: Detecting the imbuing gump
Player.UseSkill("Imbuing")
IMBUING_GUMP = wait_for_gump_by_text("Unravel Container - Unravels all items in a container", 1500)
if IMBUING_GUMP == 0:
    # Failed to find the gump
    Misc.SendMessage("Failed to find the imbuing gump!", 33)
else:
    # Add whatever actions you wish to perform
    Misc.SendMessage("Found the imbuing gump!", 68)
    gd = Gumps.GetGumpData(IMBUING_GUMP)
    print(gd.gumpLayout)