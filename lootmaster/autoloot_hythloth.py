from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from typing import List, Optional


RECT_DICT = {
    "Hythloth 4 Treasure Room": (6079, 40, 6086, 46, 1),
    "Hythloth 4 Barlon Room": (6096, 32, 6110, 46, 1),
    "Trinsic Bank (T)": (1809, 2831, 1817, 2837, 1),
    "Trinsic Bank (F)": (1809, 2831, 1817, 2837, 0),
}

IDLIST_CHEST = [
    0x0E3C,
    0x0E3D,  # large crate
    0x0E3E,
    0x0E3F,  # medium crate
    0x0E7E,
    0x09A9,  # small crate
    0x0E40,
    0x0E41,  # fancy metal crate
    0x0E42,
    0x0E43,  # wooden crate
    0x0E77,  # large barrel
    0x0E7F,  # small barrel
    0x0E7C,
    0x09AB,  # metal crate
]

IGNORE_LIST = [0x4000D1F7, 0x4000D1F8]


def is_in_some_rect(pos) -> Optional[str]:
    for name, rect in RECT_DICT.items():
        (x0, y0, x1, y1, facet) = rect
        if pos.X < x0 or pos.X > x1:
            continue
        if pos.Y < y0 or pos.Y > y1:
            continue
        if facet != Player.Map:
            continue
        return name
    return


def find_enemies() -> List["Mobile"]:  # type: ignore
    enemy = Mobiles.Filter()
    enemy.Enabled = True
    enemy.Notorieties = CList[Byte](b"\x03\x04\x05\x06")
    enemy.RangeMax = 18
    enemy.Warmode = True
    enemies = Mobiles.ApplyFilter(enemy)
    return enemies


while Player.Connected:
    for chest in Items.FindAllByID(IDLIST_CHEST, -1, -1, 10):
        pos = chest.Position
        if find_enemies():
            continue
        player_zone = is_in_some_rect(Player.Position)
        if not player_zone:
            continue
        chest_zone = is_in_some_rect(pos)
        if not chest_zone or (player_zone != chest_zone):
            continue
        if chest.Serial in IGNORE_LIST:
            continue
        if "treasure chest" in chest.Name.lower():
            continue
        if chest.Color != 0:
            continue
        
        while Player.DistanceTo(chest) > 1:
            Player.PathFindTo(pos)
            Misc.Pause(1000)
        
        
        Items.UseItemByID(0x14FC, 0)
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(chest.Serial)
        Misc.Pause(1000)
        
        Misc.Pause(Timer.Remaining("skill-delay"))
        Player.UseSkill("Remove Trap")
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(chest.Serial)
        Timer.Create("skill-delay", 11000)
        Misc.Pause(1000)
        
        Items.UseItem(chest.Serial)
        
        while chest and chest.Color == 0:
            Misc.Pause(1000)
            chest = Items.FindBySerial(chest.Serial)
    
    Misc.Pause(1000)