GUMP_MENU = hash("IngotCounterGump") & 0xFFFFFFFF
GUMP_CB = "<CENTER><BASEFONT COLOR=\"#FFFFFF\">{text}</BASEFONT></COLOR>"


INGOT_BY_COLOR = [
    (0, "Iron"),
    (2419, "Dull Copper"),
    (2406, "Shadow Iron"),
    (2413, "Copper"),
    (2418, "Bronze"),
    (2213, "Golden"),
    (2425, "Agapite"),
    (2207, "Verite"),
    (2219, "Valorite"),
    (-1, "All"),
]


def get_ingot_count():
    # Get ingot counts
    ingot_map = {}
    for ingot in Items.FindAllByID(0x1BF2, -1, Player.Backpack.Serial, 1):
        prev_count = ingot_map.get(ingot.Color, 0)
        new_count = prev_count + ingot.Amount
        ingot_map[ingot.Color] = new_count
    
    return ingot_map


def show_ingot_count(ingot_map) -> None:
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 170, 280, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 170, 280)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_CB.format(text="Ingot Counter"), False, False)

    for i, entry in enumerate(INGOT_BY_COLOR):
        x = 5
        y = 30 + 25 * i
        if entry[0] == -1:
            Gumps.AddLabel(gd, x + 40, y, 1153, str(sum(ingot_map.values())))
            Gumps.AddLabel(gd, x + 80, y, 1153, entry[1])
        else:
            Gumps.AddItem(gd, x, y, 0x1BF2, entry[0])
            Gumps.AddItem(gd, x + 5, y + 5, 0x1BF2, entry[0])
            Gumps.AddLabel(gd, x + 40, y, 1153, str(ingot_map.get(entry[0], 0)))
            Gumps.AddLabel(gd, x + 80, y, 1153, entry[1])

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def main():
    ingot_map = {}
    
    while Player.Connected:
        new_ingot_map = get_ingot_count()
        if ingot_map != new_ingot_map:
            ingot_map = new_ingot_map
            show_ingot_count(ingot_map)
        if Gumps.WaitForGump(GUMP_MENU, 500):
            show_ingot_count(ingot_map)


if __name__ == "__main__":
    main()