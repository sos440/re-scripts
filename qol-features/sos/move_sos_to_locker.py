from System.Collections.Generic import List as CList
from System import Int32

filter = Items.Filter()
filter.Enabled = True
filter.Graphics = CList[Int32]([0x14EE])
filter.Hues = CList[Int32]([0])
filter.OnGround = False

for item in Items.ApplyFilter(filter):
    Items.Move(item.Serial, 0x56463F19, 1)
    Misc.Pause(800)
    Target.WaitForTarget(1000, False)
    Target.TargetExecute(item.Serial)