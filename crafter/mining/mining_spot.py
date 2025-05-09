from System.Collections.Generic import List
from System import Byte, Int32
import re


# Your maximum allowed weight minus this value will be used as the threshold for "overweight"
# Since this script aggressively mines the spot, allowing some buffer space is necessary.
WEIGHT_BUFFER = 48

# Serial number for your faithful pack animal, set to 0 if none available
MULE = 0


################################################################################
# Script starts here
# You do not need to modify anything beyond this point
################################################################################


# Ores of these colors will be smelted one at a time
VALUABLE_ORES = {
    0: {"max-skill": 75, "metal": "iron"},
    2419: {"max-skill": 90, "metal": "dull copper"},
    2406: {"max-skill": 95, "metal": "shadow iron"},
    2413: {"max-skill": 100, "metal": "copper"},
    2418: {"max-skill": 105, "metal": "bronze"},
    2213: {"max-skill": 110, "metal": "golden"},
    2425: {"max-skill": 115, "metal": "agapite"},
    2207: {"max-skill": 120, "metal": "verite"},
    2219: {"max-skill": 124, "metal": "valorite"},
}

# Some constants
ORE_SMALL = [0x19B7]
ORE_LARGE = [0x19B8, 0x19B9, 0x19BA]
ORE = ORE_SMALL + ORE_LARGE
MINING_RES = ORE + [0x1BF2]
TOOLS = [0x0E85, 0x0E86, 0x0F39, 0x0F3A]
BACKPACK = Player.Backpack.Serial


def get_valuable_ores() -> list:
    cur_mining = Player.GetSkillValue("Mining")
    return [color for color, entry in VALUABLE_ORES.items() if entry["max-skill"] > cur_mining]


def is_overweight() -> bool:
    Items.WaitForProps(BACKPACK, 100)
    weight, max_weight = None, None
    for prop in Items.GetPropStringList(BACKPACK):
        match_res = re.search(r"(\d+)/(\d+) stones", prop.lower())
        if match_res is None:
            continue
        weight = int(match_res.group(1))
        max_weight = int(match_res.group(2))
        break
    
    if weight is not None and weight >= max_weight - 24:
        return True
    return Player.Weight >= Player.MaxWeight - WEIGHT_BUFFER


def is_near(target_serial: int) -> bool:
    if target_serial == 0:
        return False
    
    player = Mobiles.FindBySerial(Player.Serial)
    target = Items.FindBySerial(target_serial) or Mobiles.FindBySerial(target_serial)
    if target is None:
        return False
    
    return target.DistanceTo(player) <= 2


def find_tool():
    tools = Items.FindAllByID(TOOLS, -1, BACKPACK, 2)
    if len(tools) > 0:
        return tools[0].Serial
    else:
        return None


def find_forge():
    filter = Mobiles.Filter()
    filter.RangeMax = 2
    filter.Hues = List[Int32]([0x0489])
    filter.Bodies = List[Int32]([0x00A9])
    filter.Enabled = True
    fire_beetle = Mobiles.ApplyFilter(filter)
    if len(fire_beetle) > 0:
        return fire_beetle[0].Serial
    else:
        return 0


def find_enemy():
    enemy = Mobiles.Filter()
    enemy.Enabled = True
    enemy.Notorieties = List[Byte](b"\x03\x04\x05\x06")
    enemy.RangeMax = 20
    enemy.Warmode = True
    return Mobiles.ApplyFilter(enemy)


def use_ore_onto(ore, target_serial):
    Items.UseItem(ore.Serial)
    Target.WaitForTarget(400, True)
    Misc.Pause(400)
    Target.TargetExecute(target_serial)
    Misc.Pause(400)


def merge_valuable() -> bool:
    # Scan for small ores with valuable colors
    for color in get_valuable_ores():
        scan_ores = Items.FindAllByID(ORE_SMALL, color, BACKPACK, 0)
        
        # Attempt to merge ores with amounts other than 2
        scan_merge = [ore for ore in scan_ores if ore.Amount != 2]
        if len(scan_merge) > 1:
            Items.Move(scan_merge[0].Serial, scan_merge[1].Serial, -1)
            Misc.Pause(800)
            return True
        
        # Merging larger piles into smaller ones is disabled
        continue
        
        # Set the ore to be merged
        ore_merger = None
        if len(scan_merge) > 0:
            ore_merger = scan_merge[0].Serial
        elif len(scan_ores) > 0:
            ore_merger = scan_ores[0].Serial
        if ore_merger is None:
            continue
        
        # Attempt to merge ores
        for ore in Items.FindAllByID(ORE_LARGE, color, BACKPACK, 0):
            use_ore_onto(ore, ore_merger)
            return True
    return False


def smelt_small() -> bool:
    FORGE = find_forge()
    if FORGE == 0:
        return False
    for ore in Items.FindAllByID(ORE_SMALL, -1, BACKPACK, 0):
        if ore.Amount < 2:
            continue
        if ore.Amount > 3 and ore.Color in get_valuable_ores():
            continue
        use_ore_onto(ore, FORGE)
        return True
    return False


def split_small_valuable() -> bool:
    for ore in Items.FindAllByID(ORE_SMALL, -1, BACKPACK, 0):
        if ore.Amount > 3 and ore.Color in get_valuable_ores():
            Items.Move(ore.Serial, BACKPACK, 2, 0, 0)
            Misc.Pause(800)
            return True
    return False


def smelt_large() -> bool:
    FORGE = find_forge()
    if FORGE == 0:
        return False
    for ore in Items.FindAllByID(ORE_LARGE, -1, BACKPACK, 0):
        if ore.Amount > 1 and ore.Color in get_valuable_ores():
            continue
        use_ore_onto(ore, FORGE)
        return True
    return False


def split_large_valuable() -> bool:
    for ore in Items.FindAllByID(ORE_LARGE, -1, BACKPACK, 0):
        if ore.Color in get_valuable_ores():
            Items.Move(ore.Serial, BACKPACK, 1, 0, 0)
            Misc.Pause(800)
            return True
    return False


def reduce_weight():
    Misc.Pause(800)
    
    # Attempt to smelt ores
    FORGE = find_forge()
    if FORGE == 0:
        return False
    while is_near(FORGE):
        if merge_valuable():
            continue
        if smelt_small():
            continue
        if split_small_valuable():
            continue
        if smelt_large():
            continue
        if split_large_valuable():
            continue
        break
    
    # Attempt to transfer items to mule
    for ore in Items.FindAllByID(MINING_RES, -1, BACKPACK, 0):
        if is_near(MULE):
            Items.Move(ore.Serial, MULE, -1)
            Misc.Pause(800)


# Dismount if the player is currently mounted
if Player.Mount is not None:
    Mobiles.UseMobile(Player.Serial)
    Misc.Pause(800)

# Main loop
while Player.Connected:
    if len(find_enemy()) > 0:
        FORGE = find_forge()
        if FORGE != 0:
            Mobiles.UseMobile(FORGE)
        Misc.Pause(200)
        continue
    
    
    if is_overweight():
        Player.HeadMessage(0x47E, "Overweight!")
        reduce_weight()
        if is_overweight():
            break
    
    # Use mining tool
    tool = find_tool()
    if tool is None:
        Player.HeadMessage(0x21, "I don't have any tools for mining!")
        break
        
    Journal.Clear()
    Items.UseItem(tool)
    if not Target.WaitForTarget(250, True):
        continue
    Misc.Pause(200)
    Target.TargetResource(tool, "ore")
    Misc.Pause(200)
    
    # Process journal messages
    if Journal.Search("There is no metal here to mine"):
        Player.HeadMessage(0x47E, "Depleted!")
        break
    if Journal.Search("Target cannot be seen"):
        break
    if Journal.Search("You can't mine"):
        break
    if Journal.Search("You can't dig while riding or flying"):
        break

reduce_weight()
Target.Cancel()
Player.HeadMessage(0x47E, "Done!")