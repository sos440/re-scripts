from AutoComplete import *

CUTTER = 0x59BD3E8A
POCKER = 0x650BA143

GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
SHORTCUT_GUMP_ID = hash("PokeCorpsesGump") & 0xFFFFFFFF


def ask() -> bool:
    Gumps.CloseGump(SHORTCUT_GUMP_ID)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)
    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Corpse Poker"), False, False)
    Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text="Poke Poke"), False, False)
    Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
    if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, 3600000):
        return False
    gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
    if gd is None:
        return False
    return gd.buttonid == 1


def use_on(serial_src, serial_dst):
    Items.UseItem(serial_src)
    Target.WaitForTarget(1000, False)
    Target.TargetExecute(serial_dst)
    Misc.Pause(1000)


def find_davy_jones_poker():
    return Items.FindByID(0x0F62, 0x07f3, Player.Backpack.Serial, 0)


def find_harvester_blade():
    return Items.FindByID(0x2D20, 0x04a7, Player.Backpack.Serial, 0)


while Player.Connected:
    if ask():
        POCKER = find_davy_jones_poker()
        CUTTER = find_harvester_blade()
        if POCKER is None:
            Misc.SendMessage("You do not have a Davy Jone's iron poker.", 33)
            continue
        if CUTTER is None:
            Misc.SendMessage("You do not have a harvester's blade.", 33)
            continue
        for corpse in Items.FindAllByID(0x2006, -1, -1, 2):
            name = corpse.Name.lower()
            if "sea serpent" in name:
                use_on(CUTTER, corpse.Serial)
            use_on(POCKER, corpse.Serial)