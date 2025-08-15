WORKBENCH_MENU = 0


def _get_gump_by_layout(cmd: str) -> int:
    """Find the ID of a gump containing the provided command in its layout."""
    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        for line in gd.layoutPieces:
            if cmd in line:
                return gumpid
    return 0


def wait_for_workbench_gump(delay: int) -> bool:
    global WORKBENCH_MENU
    if WORKBENCH_MENU is None:
        Timer.Create("gump-detect", delay)
        while Timer.Check("gump-detect"):
            WORKBENCH_MENU = _get_gump_by_layout("xmfhtmltok 10 10 350 18 0 0 0 1114513 @#1158860@")
            if WORKBENCH_MENU != 0:
                return True
            Misc.Pause(100)
        return False
    else:
        return Gumps.WaitForGump(WORKBENCH_MENU, delay)


if not wait_for_workbench_gump(600000):
    Misc.SendMessage("Gump not found!")
else:
    Gumps.SendAction(WORKBENCH_MENU, 1)