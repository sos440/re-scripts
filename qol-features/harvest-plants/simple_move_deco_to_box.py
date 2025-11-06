PLANTS = [10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467, 3273, 6810, 3204, 6815, 3265, 3326, 3215, 3272, 3214, 3365, 3255, 3262, 3521, 3323, 3512, 6817, 9324, 19340, 3230, 3203, 3206, 3208, 3220, 3211, 3237, 3239, 3223, 3231, 3238, 3228, 3377, 3332, 3241, 3372, 3366, 3367]


def move():
    serial = Target.PromptTarget("Select the box to move plants to.", 0x3B2)
    if serial == -1:
        return
    if not Misc.IsItem(serial):
        return
    for item in Items.FindAllByID(PLANTS, -1, Player.Backpack.Serial, 2):
        Items.Move(item.Serial, serial, -1)
        Misc.Pause(1000)


move()