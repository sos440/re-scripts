GUMP_ID = 0xBABED0D0
GUMP_ASSET_ID = 0

Gumps.CloseGump(GUMP_ID)


def show_gump_viewer():
    global GUMP_ASSET_ID

    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    # Background
    Gumps.AddBackground(gd, 0, 0, 800, 600, 9270)
    Gumps.AddBackground(gd, 10, 10, 780, 580, 3000)

    # Menubar
    Gumps.AddBackground(gd, 10, 10, 780, 53, 3500)
    Gumps.AddTextEntry(gd, 35, 28, 80, 18, 0, 1101, f"{GUMP_ASSET_ID}")
    # GoTo
    Gumps.AddButton(gd, 110, 26, 1531, 1532, 1001, 1, 0)
    # Previous
    Gumps.AddButton(gd, 140, 26, 1545, 1546, 1002, 1, 0)
    # Next
    Gumps.AddButton(gd, 160, 26, 1543, 1544, 1003, 1, 0)
    # Previous 12
    Gumps.AddButton(gd, 180, 26, 1541, 1542, 1004, 1, 0)
    # Next 12
    Gumps.AddButton(gd, 200, 26, 1539, 1540, 1005, 1, 0)
    # Close
    Gumps.AddButton(gd, 745, 26, 1535, 1536, 0, 1, 0)

    # Display
    Gumps.AddPage(gd, 1)

    for id_mod in range(12):
        row = id_mod // 4
        col = id_mod % 4
        x = 20 + col * 200
        y = 75 + row * 200
        Gumps.AddLabel(gd, x, y, 0, f"{GUMP_ASSET_ID + id_mod}")
        Gumps.AddImage(gd, x, y + 20, GUMP_ASSET_ID + id_mod)

    Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd.gumpDefinition, gd.gumpStrings)

    # Response
    Gumps.WaitForGump(GUMP_ID, 3600000)
    gd = Gumps.GetGumpData(GUMP_ID)

    if gd.buttonid == 0:
        Misc.SendMessage("Viewer has been closed.", 0x47E)
        return False
    elif gd.buttonid == 1001:
        goto_id = int(gd.text[0])
        if goto_id is None:
            Misc.SendMessage("Input must be an integer!", 0x21)
        elif goto_id < 0 or goto_id >= 65536:
            Misc.SendMessage("Input is out of range!", 0x21)
        else:
            GUMP_ASSET_ID = goto_id
        return True
    elif gd.buttonid == 1002:
        GUMP_ASSET_ID = max(0, GUMP_ASSET_ID - 1)
        return True
    elif gd.buttonid == 1003:
        GUMP_ASSET_ID = min(65535, GUMP_ASSET_ID + 1)
        return True
    elif gd.buttonid == 1004:
        GUMP_ASSET_ID = max(0, GUMP_ASSET_ID - 12)
        return True
    elif gd.buttonid == 1005:
        GUMP_ASSET_ID = min(65535, GUMP_ASSET_ID + 12)
        return True


while Player.Connected:
    res = show_gump_viewer()
    if not res:
        break
