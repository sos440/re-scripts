GUMP_MENU = 0x1234ABCD
GUMP_BUTTONTEXT_WRAP = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""

is_running = True


def gump_menu() -> None:
    global is_running
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 115, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 115)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Lootmaster"), False, False)

    Gumps.AddButton(gd, 10, 30, 40020, 40030, 1001, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Manual Loot"), False, False)

    if is_running:
        Gumps.AddButton(gd, 10, 55, 40297, 40298, 1003, 1, 0)
        Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Disable Autoloot"), False, False)
    else:
        Gumps.AddButton(gd, 10, 55, 40021, 40031, 1002, 1, 0)
        Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Enable Autoloot"), False, False)

    Gumps.AddButton(gd, 10, 80, 40299, 40300, 1004, 1, 0)
    Gumps.AddHtml(gd, 10, 82, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Edit Profile"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def gump_action():
    gd = Gumps.GetGumpData(GUMP_MENU)
    if gd is None:
        return
    if gd.buttonid == 0:
        return
    if gd.buttonid == 1001:
        # Manual loot
        Misc.SendMessage("Manual loot selected.")
        return
    if gd.buttonid == 1002:
        # Enable autoloot
        is_running = True
        Misc.SendMessage("Autoloot enabled.")
        return
    if gd.buttonid == 1003:
        # Disable autoloot
        is_running = False
        Misc.SendMessage("Autoloot disabled.")
        return
    if gd.buttonid == 1004:
        # Edit profile
        Misc.SendMessage("Edit profile selected.")
        # Open the profile editor here
        return


gump_menu()
while Player.Connected:
    if not Gumps.WaitForGump(GUMP_MENU, 1):
        Misc.Pause(1000)
        continue

    gump_action()
    gump_menu()
