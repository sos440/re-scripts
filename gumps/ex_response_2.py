setX = 25
setY = 50


def sendgump():
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    Gumps.AddBackground(gd, 0, 0, 450, 53, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 450, 53)
    Gumps.AddButton(gd, 5, 5, 2241, 2241, 1, 1, 0)
    Gumps.AddTooltip(gd, r"Create Food")
    Gumps.AddButton(gd, 49, 5, 2254, 2254, 2, 1, 0)
    Gumps.AddTooltip(gd, r"Protection")
    Gumps.AddButton(gd, 93, 5, 2261, 2261, 3, 1, 0)
    Gumps.AddTooltip(gd, r"Teleport")
    Gumps.AddButton(gd, 137, 5, 2269, 2269, 4, 1, 0)
    Gumps.AddTooltip(gd, r"Lightning")
    Gumps.AddButton(gd, 181, 5, 2271, 2271, 5, 1, 0)
    Gumps.AddTooltip(gd, r"Recall")
    Gumps.AddButton(gd, 225, 5, 2281, 2281, 6, 1, 0)
    Gumps.AddTooltip(gd, r"Energy Bolt")
    Gumps.AddButton(gd, 269, 5, 2283, 2283, 7, 1, 0)
    Gumps.AddTooltip(gd, r"Invisibility")
    Gumps.AddButton(gd, 313, 5, 2284, 2284, 8, 1, 0)
    Gumps.AddTooltip(gd, r"Mark")
    Gumps.AddButton(gd, 357, 5, 2287, 2287, 9, 1, 0)
    Gumps.AddTooltip(gd, r"Reveal")
    Gumps.AddButton(gd, 401, 5, 2291, 2291, 10, 1, 0)
    Gumps.AddTooltip(gd, r"Gate Travel")

    Gumps.SendGump(987654, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)
    buttoncheck()


def buttoncheck():
    Gumps.WaitForGump(987654, 60000)
    Gumps.CloseGump(987654)
    gd = Gumps.GetGumpData(987654)
    if gd.buttonid == 1:
        Spells.CastMagery("Create Food")
    elif gd.buttonid == 2:
        Spells.CastMagery("Protection")
    elif gd.buttonid == 3:
        Spells.CastMagery("Teleport")
    elif gd.buttonid == 4:
        Spells.CastMagery("Lightning")
    elif gd.buttonid == 5:
        Spells.CastMagery("Recall")
    elif gd.buttonid == 6:
        Spells.CastMagery("Energy Bolt")
    elif gd.buttonid == 7:
        Spells.CastMagery("Invisibility")
    elif gd.buttonid == 8:
        Spells.CastMagery("Mark")
    elif gd.buttonid == 9:
        Spells.CastMagery("Reveal")
    elif gd.buttonid == 10:
        Spells.CastMagery("Gate Travel")


while Player.Connected:
    sendgump()
    Misc.Pause(750)
