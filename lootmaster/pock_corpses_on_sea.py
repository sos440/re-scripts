from AutoComplete import *

CUTTER = 0x59BD3E8A
POCKER = 0x650BA143


def use_on(serial_src, serial_dst):
    Items.UseItem(serial_src)
    Target.WaitForTarget(1000, False)
    Target.TargetExecute(serial_dst)
    Misc.Pause(1000)


for corpse in Items.FindAllByID(0x2006, -1, -1, 2):
    name = corpse.Name.lower()
    if "sea serpent" in name:
        use_on(CUTTER, corpse.Serial)
    use_on(POCKER, corpse.Serial)