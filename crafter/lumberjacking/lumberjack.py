import time
import json
import os
from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte  # type: ignore
from typing import Union, Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


# Highlights the depleted trees
HIGHLIGHT_DEPLETE = True

# Duration (in seconds) for the deplete location to be ignored
LUMBER_COOLDOWN = 1200.0  # 20 minutes


################################################################################
# File System
################################################################################


PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_DIR = os.path.join(PATH, "data")
if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

RECORD_PATH = os.path.join(SAVE_DIR, "lumber_history.json")


def load_history():
    if os.path.exists(RECORD_PATH):
        with open(RECORD_PATH, "r") as f:
            record = json.load(f)
            return {
                (x, y, z, tile_id) : t_expire
                for x, y, z, tile_id, t_expire in record
            }
    else:
        return {}


def save_history(history):
    with open(RECORD_PATH, "w") as f:
        record = [
            (x, y, z, tile_id, t_expire)
            for (x, y, z, tile_id), t_expire in history.items()
        ]
        record = json.dump(record, f)


################################################################################
# Visual Effect Module - For Fun!
################################################################################


def VisualEffect(
    type: int,
    src_id: int,
    trg_id: int,
    tile_type: int,
    src_pos: Tuple[int, int, int],
    trg_pos: Tuple[int, int, int],
    speed: int,
    duration: int,
    unk1: int,
    unk2: int,
    fixed_dir: bool,
    explodes: bool,
    hue: int,
    render_mode: int,
) -> None:
    packet = b"\xc0"
    packet += type.to_bytes(1, "big")
    packet += src_id.to_bytes(4, "big")
    packet += trg_id.to_bytes(4, "big")
    packet += (tile_type & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[0] & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[1] & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[2] & 0xFF).to_bytes(1, "big")
    packet += (trg_pos[0] & 0xFFFF).to_bytes(2, "big")
    packet += (trg_pos[1] & 0xFFFF).to_bytes(2, "big")
    packet += (trg_pos[2] & 0xFF).to_bytes(1, "big")
    packet += speed.to_bytes(1, "big")
    packet += duration.to_bytes(1, "big")
    packet += unk1.to_bytes(1, "big")
    packet += unk2.to_bytes(1, "big")
    packet += int(fixed_dir).to_bytes(1, "big")
    packet += int(explodes).to_bytes(1, "big")
    packet += hue.to_bytes(4, "big")
    packet += render_mode.to_bytes(4, "big")

    PacketLogger.SendToClient(GenList[Byte](packet))


def VisualEffectMissile(
    src: Union[int, Tuple[int, int, int]],
    trg: Union[int, Tuple[int, int, int]],
    tile_type: int,
    speed: int,
    duration: int,
    hue: int = 0,
    render_mode: int = 0,
    fixed_dir: bool = False,
    explodes: bool = False,
) -> None:
    """
    Creates a missile effect from the source to the target.

    :param src: The ID or position of the source object.
    :param trg: The ID or position of the target object.
    :param tile_type: The tile ID of the missile.
    :param speed: The speed of the missile.
    :param duration: The number of frames in a single cycle of the animation.
    :param hue: The hue of the missile.
    :param render_mode: The render mode of the missile. (0 to 7)
    """
    src_id = 0
    src_pos = (0, 0, 0)
    trg_id = 0
    trg_pos = (0, 0, 0)

    if isinstance(src, int):
        src_id = src
    else:
        src_pos = src

    if isinstance(trg, int):
        trg_id = trg
    else:
        trg_pos = trg

    VisualEffect(
        0, src_id, trg_id, tile_type, src_pos, trg_pos, speed, duration, 0, 0, fixed_dir, explodes, hue, render_mode
    )


def VisualEffectLightning(src: int):
    """
    Creates a lightning effect at the source object.
    """
    VisualEffect(1, src, 0, 0, (0, 0, 0), (0, 0, 0), 0, 0, 0, 0, False, False, 0, 0)


def VisualEffectStatic(
    pos: Tuple[int, int, int],
    tile_type: int,
    duration: int,
    hue: int = 0,
    render_mode: int = 0,
    speed: int = 1,
    unk1: int = 0,
    unk2: int = 0,
):
    """
    Creates a graphical effect at the given position.

    :param pos: The position of the effect.
    :param tile_type: The tile ID of the effect.
    :param duration: The number of frames in a single cycle of the animation.
    :param hue: The hue of the effect.
    :param render_mode: The render mode of the effect. (0 to 7)
    """
    VisualEffect(2, 0, 0, tile_type, pos, (0, 0, 0), speed, duration, unk1, unk2, False, False, hue, render_mode)


def VisualEffectSelf(
    src: int,
    tile_type: int,
    duration: int,
    hue: int = 0,
    render_mode: int = 0,
    speed: int = 1,
    unk1: int = 0,
    unk2: int = 0,
):
    """
    Creates a graphical effect at the source object.

    :param src: The ID of the source object.
    :param tile_type: The tile ID of the effect.
    :param duration: The number of frames in a single cycle of the animation.
    :param hue: The hue of the effect.
    :param render_mode: The render mode of the effect. (0 to 7)
    """
    VisualEffect(
        3, src, 0, tile_type, (0, 0, 0), (0, 0, 0), speed, duration, unk1, unk2, False, False, hue, render_mode
    )


################################################################################
# Radar Gump
################################################################################


# Axe IDs
AXE_IDS = [
    0x0F43, 0x0F44, # unknown
    0x0F45, 0x0F46, # executioner's axe
    0x0F47, 0x0F48, # battle axe
    0x0F49, 0x0F4A, # axe
    0x0F4B, 0x0F4C, # double axe
    0x13AF, 0x13B0, # war axe
    0x13FA, 0x13FB, # large battle axe
    0x1442, 0x1443, # two handed axe
    0x2D28, 0x2D34, # ornate axe
    #0x48B0, 0x48B1, # gargish battle axe
    #0x48B2, 0x48B3, # gargish axe
    #0x4068, # dual short axes
]

# Obtain the serial for the packy if exists
MY_PACKY = Target.PromptTarget("Select the packy, or cancel to select none.", 0x47E)

# Static IDs for the loggable trees
TREE_STATIC_IDS = [
    0x0C95, 0x0C96, 0x0C99, 0x0C9B, 0x0C9C, 0x0C9D, 0x0C8A, 0x0CA6, 
    0x0CA8, 0x0CAA, 0x0CAB, 0x0CC3, 0x0CC4, 0x0CC8, 0x0CC9, 0x0CCA, 
    0x0CCB, 0x0CCC, 0x0CCD, 0x0CD0, 0x0CD3, 0x0CD6, 0x0CD8, 0x0CDA, 
    0x0CDD, 0x0CE0, 0x0CE3, 0x0CE6, 0x0CF8, 0x0CFB, 0x0CFE, 0x0D01, 
    0x0D25, 0x0D27, 0x0D35, 0x0D37, 0x0D38, 0x0D42, 0x0D43, 0x0D59, 
    0x0D70, 0x0D85, 0x0D94, 0x0D96, 0x0D98, 0x0D9A, 0x0D9C, 0x0D9E, 
    0x0DA0, 0x0DA2, 0x0DA4, 0x0DA8, 
]

# Displacements to the neighboring tiles of distance 1 or 2
NEIGHBORS = [
    (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
    (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
    (0, -2), (0, -1), (0, 1), (0, 2),
    (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
    (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
]


def find_tree(ignore_list) -> Tuple[int, int, int, int]:
    cx, cy = Player.Position.X, Player.Position.Y
    for dx, dy in NEIGHBORS:
        nx, ny = cx + dx, cy + dy
        staticsTileInfo = Statics.GetStaticsTileInfo(nx, ny, Player.Map)
        for tile in staticsTileInfo:
            if tile.StaticID not in TREE_STATIC_IDS:
                continue
            found = (nx, ny, tile.StaticZ, tile.StaticID)
            if found not in ignore_list:
                return found
    return None


def is_packy_near() -> bool:
    if MY_PACKY == -1:
        return False
    
    packy = Mobiles.FindBySerial(MY_PACKY)
    if packy is None:
        return False
    
    pos_me = Player.Position
    pos_mob = packy.Position
    dist = max(abs(pos_me.X - pos_mob.X), abs(pos_me.Y - pos_mob.Y))
    return dist <= 2


def use_axe() -> None:
    # Scan the player's layer
    for layer in ["LeftHand", "RightHand"]:
        cur_axe = Player.GetItemOnLayer(layer)
        if cur_axe is None:
            continue
        if cur_axe.ItemID in AXE_IDS:
            Items.UseItem(cur_axe.Serial)
            return
            
    # Scan the backpack
    scan_axe = Items.FindAllByID(AXE_IDS, -1, Player.Backpack.Serial, 2)
    if len(scan_axe) > 0:
        Player.EquipItem(scan_axe[0].Serial)
        Misc.Pause(800)
        Items.UseItem(scan_axe[0].Serial)
        return
    
    raise Exception("Failed to find an axe!")


def use_axe_on(*args) -> None:
    use_axe()
    Target.WaitForTarget(500, True)
    Misc.Pause(400)
    Target.TargetExecute(*args)
    Misc.Pause(400)


def reduce_weight() -> None:
    # Scan for the logs
    logs = Items.FindAllByID(0x1BDD, -1, Player.Backpack.Serial, 2)
    if len(logs) == 0:
        return
    
    # Process the logs
    for item in logs:
        use_axe_on(item.Serial)
    Target.Cancel()
    
    # Move boards to the packy if available
    for board in Items.FindAllByID(0x1BD7, -1, Player.Backpack.Serial, 2):
        if is_packy_near():
            Items.Move(board.Serial, MY_PACKY, board.Amount)
            Misc.Pause(800)


def highlight_ignored(ignore_list):
    x0, y0 = Player.Position.X, Player.Position.Y
    for x, y, z, tile_id in ignore_list:
        dx, dy = x - x0, y - y0
        dist = max(abs(dx), abs(dy))
        if dist >= 28:
            continue
        VisualEffectStatic((x, y, z), tile_id, 255, 1165, 0)


deplete_list = load_history()
t_highlight = time.time()
while True:
    # Scan trees nearby
    ignore_list = [tree for tree, expire in deplete_list.items() if expire > time.time()]
    if HIGHLIGHT_DEPLETE and time.time() >= t_highlight:
        highlight_ignored(ignore_list)
        t_highlight = time.time() + 1.5
    tree = find_tree(ignore_list)
    if tree is None:
        Misc.Pause(250)
        continue
    
    # Hack the tree
    Journal.Clear()
    if HIGHLIGHT_DEPLETE:
        x, y, z, tile_id = tree
        VisualEffectStatic((x, y, z), tile_id, 10, 88, 2)
    use_axe_on(*tree)
    
    # Process the response
    if Journal.Search("There's not enough wood here to harvest"):
        Player.HeadMessage(0x47E, "I'm done here!")
        deplete_list[tree] = time.time() + LUMBER_COOLDOWN
        save_history(deplete_list)
        reduce_weight()
        continue
    if Journal.Search("You can't use an axe on that"):
        # completely ignore the current target (for a one week, technically...)
        deplete_list[tree] = time.time() + 604800
        save_history(deplete_list)
        reduce_weight()
        continue
    if Journal.Search("The axe must be equipped for any serious wood chopping"):
        # `use_axe_on()` method automatically handles this case
        continue
    if Player.Weight + 20 >= Player.MaxWeight:
        reduce_weight()