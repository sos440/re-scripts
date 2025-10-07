from AutoComplete import *

COLORS = [0, 33, 1645, 43, 1135, 56, 2213, 66, 1435, 5, 1341, 16, 13, 1166, 1173, 1158, 1161, 1153, 1109]
PLANTS = [10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467, 3273, 6810, 3204, 6815, 3265, 3326, 3215, 3272, 3214, 3365, 3255, 3262, 3521, 3323, 3512, 6817, 9324, 19340, 3230, 3203, 3206, 3208, 3220, 3211, 3237, 3239, 3223, 3231, 3238, 3228, 3377, 3332, 3241, 3372, 3366, 3367]

plants = Items.FindAllByID(PLANTS, -1, Player.Backpack.Serial, 3)

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
