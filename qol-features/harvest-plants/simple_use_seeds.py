while True:
    seed = Items.FindByID(0x0DCF, -1, Player.Backpack.Serial, 2)
    if seed is None:
        break
    
    Items.UseItem(seed.Serial)
    Timer.Create("action-delay", 500)
    Target.WaitForTarget(1000, False)
    while Target.HasTarget() or Timer.Check("action-delay"):
        Misc.Pause(100)