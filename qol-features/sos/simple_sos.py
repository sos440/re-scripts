from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
import re
from typing import Optional, Tuple


# Gump constants
GUMP_ID = hash("SOSGump") & 0xFFFFFFFF
ID_RECORD = 1
ID_TOGGLE_TRACK = 2
ID_NEAREST_SOS = 3

# State variables
REF_POS = (-1, -1)
TRACKING_POS = (-1, -1)
IS_TRACKING = False


def show_gump():
    Gumps.CloseGump(GUMP_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 240, 107, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 240, 107)

    if REF_POS == (-1, -1):
        Gumps.AddLabel(gd, 10, 10, 33, "Reference position not set")
    else:
        Gumps.AddLabelCropped(gd, 10, 10, 220, 18, 88, f"Reference: {REF_POS[0]}, {REF_POS[1]}")

    # Buttons
    Gumps.AddButton(gd, 10, 35, 4005, 4007, ID_RECORD, 1, 0)
    Gumps.AddLabelCropped(gd, 45, 37, 180, 18, 1153, "Set reference position")
    Gumps.AddButton(gd, 10, 55, 4005, 4007, ID_TOGGLE_TRACK, 1, 0)
    Gumps.AddLabelCropped(gd, 45, 57, 180, 18, 1153, "Toggle tracking")
    Gumps.AddButton(gd, 10, 75, 4005, 4007, ID_NEAREST_SOS, 1, 0)
    Gumps.AddLabelCropped(gd, 45, 77, 180, 18, 1153, "Pick up nearest SOS")

    Gumps.SendGump(GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def read_loc(item: "Item") -> Optional[Tuple[int, int]]:
    Items.WaitForProps(item.Serial, 1000)
    props = Items.GetPropStringList(item.Serial)
    for prop in props:
        res = re.search(r"Location: \((\d+), (\d+)\)", prop)
        if res is not None:
            return (int(res.group(1)), int(res.group(2)))
    return None


def iter_sos():
    filter = Items.Filter()
    filter.Enabled = True
    filter.Graphics = CList[Int32]([0x14EE])
    sos_all = Items.ApplyFilter(filter)

    for sos in sos_all:
        cont = Items.FindBySerial(sos.RootContainer)
        if cont is None:
            continue
        is_owned = cont.Serial == Player.Backpack.Serial
        if cont is None:
            continue
        if not (cont.OnGround or is_owned):
            continue
        if not is_owned and Player.DistanceTo(cont) > 2:
            continue

        yield sos


def export_sos_map():
    with open("Data/Client/SOS.map", "w") as f:
        f.write("3\n")
        for sos in iter_sos():
            loc = read_loc(sos)
            if loc is None:
                continue
            if sos.Color == 0x0481:
                f.write(f"+SOSA: {loc[0]} {loc[1]} 0 Ancient SOS\n")
                f.write(f"+SOSA: {loc[0]} {loc[1]} 1 Ancient SOS\n")
            else:
                f.write(f"+SOS: {loc[0]} {loc[1]} 0 SOS\n")
                f.write(f"+SOS: {loc[0]} {loc[1]} 1 SOS\n")


def get_nearest_sos(x, y) -> Tuple[Optional["Item"], float]:
    sos_nearest = None
    min_dist = float("inf")
    for sos in iter_sos():
        loc = read_loc(sos)
        if loc is None:
            continue

        dist = Misc.Distance(x, y, loc[0], loc[1])
        if dist < min_dist:
            min_dist = dist
            sos_nearest = sos

    return sos_nearest, min_dist


if __name__ == "__main__":
    while Player.Connected:
        show_gump()

        while not Gumps.WaitForGump(GUMP_ID, 1000):
            for mast in Items.FindAllByID([0x4030, 0x4031, 0x4032, 0x4033], -1, -1, 10):
                if Player.DistanceTo(mast) <= 10:
                    REF_POS = (Player.Position.X, Player.Position.Y)
                    show_gump()
                    break
            continue

        gd = Gumps.GetGumpData(GUMP_ID)
        if gd is None:
            continue

        if gd.buttonid == 0:
            continue

        if gd.buttonid == ID_RECORD:
            if IS_TRACKING:
                Player.TrackingArrow(REF_POS[0], REF_POS[1], False, 0)
                IS_TRACKING = False
                Misc.SendMessage("Tracking stopped.", 68)
            REF_POS = (Player.Position.X, Player.Position.Y)
            Misc.SendMessage(f"New reference position set: {REF_POS[0]}, {REF_POS[1]}", 68)
            continue

        if gd.buttonid == ID_TOGGLE_TRACK:
            if IS_TRACKING:
                Player.TrackingArrow(TRACKING_POS[0], TRACKING_POS[1], False, 0)
                IS_TRACKING = False
                Misc.SendMessage("Tracking stopped.", 68)
                continue
            sos_nearest, dist = get_nearest_sos(Player.Position.X, Player.Position.Y)
            if sos_nearest is None:
                Misc.SendMessage("No SOS found nearby.", 33)
                continue
            loc = read_loc(sos_nearest)
            if loc is None:
                Misc.SendMessage("Failed to read SOS location.", 33)
                continue
            TRACKING_POS = loc
            Player.TrackingArrow(TRACKING_POS[0], TRACKING_POS[1], True, 0)
            IS_TRACKING = True
            Misc.SendMessage(f"Tracking started. (Distance={dist})", 68)
            continue

        if gd.buttonid == ID_NEAREST_SOS:
            if REF_POS == (-1, -1):
                Misc.SendMessage("No reference position set.", 33)
                continue
            export_sos_map()
            sos_nearest, dist = get_nearest_sos(REF_POS[0], REF_POS[1])
            if sos_nearest is None:
                Misc.SendMessage("No SOS found nearby.", 33)
                continue
            if sos_nearest.RootContainer == Player.Backpack.Serial:
                Misc.SendMessage("Nearest SOS is already in your backpack.", 68)
                continue
            Items.Move(sos_nearest.Serial, Player.Backpack.Serial, -1)
            Misc.Pause(1000)
            sos_new = Items.FindBySerial(sos_nearest.Serial)
            if sos_new is not None and sos_new.RootContainer == Player.Backpack.Serial:
                Misc.SendMessage(f"SOS picked up successfully. (Distance={dist})", 68)
            else:
                Misc.SendMessage("Failed to pick up SOS.", 33)
            continue
