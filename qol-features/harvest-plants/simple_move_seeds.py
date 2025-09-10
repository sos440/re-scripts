for seed in Items.FindAllByID(0x0DCF, -1, Player.Backpack.Serial, 2):
    Items.Move(seed.Serial, 0x593A5667, -1)
    Misc.Pause(1000)