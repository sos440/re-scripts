################################################################################
# Script starts here
################################################################################

from AutoComplete import *


GUMP_MENU = hash("RecordPositionGump") & 0xFFFFFFFF
GUMP_WRAPTXT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""


def gump_menu() -> None:
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WRAPTXT.format(text="Record Position"), False, False)
    Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WRAPTXT.format(text="Record"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


gump_menu()
while Player.Connected:
    if Gumps.WaitForGump(GUMP_MENU, 1):
        gd = Gumps.GetGumpData(GUMP_MENU)
        if gd.buttonid == 1:
            print(f"move_to({Player.Position.X}, {Player.Position.Y}, {Player.Position.Z})")
        gump_menu()