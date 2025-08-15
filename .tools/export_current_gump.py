gd = Gumps.GetGumpData(Gumps.CurrentGump())
if gd is not None:
    with open("./Data/gump_tinkering_menu.txt", "w") as f:
        for line in gd.layoutPieces:
            f.write(line + "\n")
        f.write("\n")
        f.write(f"gd.gumpData = {gd.gumpData}\n")
        f.write(f"gd.gumpStrings = {gd.gumpStrings}\n")
        f.write(f"gd.gumpText = {gd.gumpText}\n")
    Misc.SendMessage("Done!")
else:
    Misc.SendMessage("Gump not found!")