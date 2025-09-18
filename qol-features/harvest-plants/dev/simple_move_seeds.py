def main():
    serial = Target.PromptTarget("Select the container to move seed to.", 0x3B2)
    if not Misc.IsItem(serial):
        return
    for seed in Items.FindAllByID(0x0DCF, -1, Player.Backpack.Serial, 2):
        Items.Move(seed.Serial, serial, -1)
        Misc.Pause(1000)


main()