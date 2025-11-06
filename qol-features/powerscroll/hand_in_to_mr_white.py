for ps in Items.FindAllByID(0x14F0, 0x481, Player.Backpack.Serial, 2):
    Items.Move(ps.Serial, 0x0004C57C, -1)
    Misc.Pause(1000)