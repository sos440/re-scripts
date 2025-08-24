from AutoComplete import *


plants = []
plants.extend(Items.FindAllByID(0x0C86, 0x002B, Player.Backpack.Serial, 3))  # bright orange poppies
plants.extend(Items.FindAllByID(0x0CA9, 0x0042, Player.Backpack.Serial, 3))  # bright green snake plant

for item in plants:
    serial = item.Serial
    while True:
        scan = Items.FindBySerial(serial)
        if scan is None:
            break
        clipper = Items.FindByID(0x0DFC, 0, Player.Backpack.Serial, 0)
        if clipper is None:
            break
        Items.UseItem(clipper.Serial)
        if not Target.WaitForTarget(1000, False):
            continue
        Target.TargetExecute(scan.Serial)
        Misc.Pause(1000)
