from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


GUMP_ID = 0x4BEEFBEE

count = 0
while True:
    if Gumps.WaitForGump(GUMP_ID, 1000):
        # This is true only when the user closes the gump.
        # I am not sure about the logic behind this, but it works!
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)

        Gumps.AddBackground(gd, 0, 0, 250, 250, 30546)
        Gumps.AddAlphaRegion(gd, 0, 0, 250, 250)
        Gumps.AddLabel(gd, 10, 10, 0x47E, f"This is a test gump! {count}")
        Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd.gumpDefinition, gd.gumpStrings)
        count += 1