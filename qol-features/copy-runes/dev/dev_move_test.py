from typing import Tuple


DIR_MAP = {
    "North": (0, -1),
    "Right": (1, -1),
    "East": (1, 0),
    "Bottom": (1, 1),
    "South": (0, 1),
    "Left": (-1, 1),
    "West": (-1, 0),
    "Top": (-1, -1),
}


def player_pos() -> Tuple[int, int]:
    return Player.Position.X, Player.Position.Y


def is_at_comm_center() -> bool:
    for _ in range(10):
        if Player.Map == 4 and player_pos() == (567, 1338):
            return True
        Misc.Pause(500)
    return False


def move_linear(dir: str, steps: int) -> bool:
    assert dir in DIR_MAP
    
    x0, y0 = player_pos()
    dx, dy = DIR_MAP[dir]
    x1, y1 = x0 + steps * dx, y0 + steps * dy
    
    for _ in range(steps + 1):
        if player_pos() != (x1, y1):
            Player.Run(dir)
            Misc.Pause(100)
    
    # for _ in range(10):
    #     cur_pos = player_pos()
    #     if cur_pos == (x1, y1):
    #         return True
    #     # Misc.SendMessage(f"{dir} -> {steps} ... {cur_pos} vs {(x1, y1)}")
    #     Misc.Pause(50)
    
    return player_pos() == (x1, y1)
    


def goto_runic_atlas() -> bool:
    # Recall to the community center
    Items.UseItem(0x576B2AEF)
    if not Gumps.WaitForGump(0x1f2, 2000):
        return False
    Gumps.SendAction(0x1f2, 4)
    if not is_at_comm_center():
        return False
    
    # Move to the entrance
    inst_list = [
        ("East", 17),
        ("North", 8),
    ]
    if not all(move_linear(*inst) for inst in inst_list):
        return False
    
    # Open the door if necessary
    door = Items.FindBySerial(0x403F5D2C)
    if door is None:
        return False
    if door.ItemID == 0x31A0:
        Items.UseItem()
        Misc.Pause(1000)
    
    # Move to the runic atlas
    inst_list = [   
        ("North", 14),
        ("West", 11),
        ("North", 6),
        ("West", 5),
        ("South", 12),
        ("East", 10),
        ("Right", 1),
        ("North", 8),
    ]
    if not all(move_linear(*inst) for inst in inst_list):
        return False
    
    return True


print(goto_runic_atlas())