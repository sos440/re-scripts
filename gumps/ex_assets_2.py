GUMP_ID = 0xBABED0D0

Gumps.CloseGump(GUMP_ID)

gd = Gumps.CreateGump(movable=True) 
Gumps.AddPage(gd, 0)

# Background
Gumps.AddBackground(gd, 0, 0, 800, 600, 9270)
# Menubar
Gumps.AddBackground(gd, 10, 10, 780, 53, 3500)
# Rules
Gumps.AddBackground(gd, 10, 55, 170, 535, 3500)


Gumps.AddButton(gd, 25, 25, 5540, 5541, 1, 1, 0)
Gumps.AddHtmlLocalized(gd, 55, 24, 400, 60, 1156863, 1, 1)
Gumps.AddButton(gd, 400, 400, 2073, 2072, 0, 1, 0)

Gumps.AddPage(gd, 1)
Gumps.AddButton(gd, 25, 85, 4005, 4007, 0, 0, 2)
Gumps.AddHtml(gd, 60, 88, 150, 18, "Next Page", 0, 0)
Gumps.AddButton(gd, 25, 105, 4011, 4012, 3, 1, 0)
Gumps.AddTextEntry(gd, 25, 145, 200, 25, 0, 1, "Hello, World!")

Gumps.AddPage(gd, 2)
Gumps.AddButton(gd, 25, 85, 4005, 4007, 0, 0, 1)
Gumps.AddHtml(gd, 60, 88, 150, 18, "Previous Page", 0, 0)
Gumps.AddButton(gd, 25, 105, 4011, 4012, 3, 1, 0)

Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd.gumpDefinition, gd.gumpStrings)

# Response
Gumps.WaitForGump(GUMP_ID, 3600000)
gd = Gumps.GetGumpData(GUMP_ID)

if gd.buttonid == 3:
    print(gd.text)