from AutoComplete import *
from typing import Optional, Tuple
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte, Int32  # type: ignore
from typing import List, Callable, Set, Any
from enum import Enum
import math
import sys
import os


REPEAT = 100
USE_HIDING = False


################################################################################
# Pathfind Module
################################################################################


script_path = os.path.dirname(__file__)


x0, y0 = 5631, 1775
tiles = {}
with open(os.path.join(script_path, "assets/solen_map.txt"), "r", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        for j, c in enumerate(line):
            if c not in (" ", "X"):
                tiles[(x0 + j, y0 + i)] = c


def execute_step():
    pos = Player.Position
    pos = (pos.X, pos.Y)
    if pos not in tiles:
        Misc.SendMessage("Out of bound!", 33)
        return False
    tile = tiles[pos]
    if tile == "@":
        # Reached the end
        return True
    if tile == "→":
        Player.Run("East")
    elif tile == "←":
        Player.Run("West")
    elif tile == "↑":
        Player.Run("North")
    elif tile == "↓":
        Player.Run("South")
    elif tile == "↗":
        Player.Run("Right")
    elif tile == "↙":
        Player.Run("Left")
    elif tile == "↖":
        Player.Run("Up")
    elif tile == "↘":
        Player.Run("Down")
    else:
        Misc.SendMessage("Unknown direction", 33)
        return False


################################################################################
# Quest Module
################################################################################


def get_player_pos() -> Tuple[int, int, int]:
    return (Player.Position.X, Player.Position.Y, Player.Position.Z)


def get_dist_to(x: int, y: int) -> int:
    x0, y0, _ = get_player_pos()
    dist = max(abs(x - x0), abs(y - y0))
    return dist


def is_in_ant_cave():
    x, y, _ = get_player_pos()
    if x < 5631 or x > 5938:
        return False
    if y < 1775 or y > 2036:
        return False
    if Player.Map != 1:
        return False
    return True


def wait_until_move(delay: int = 3000):
    pos = get_player_pos()
    Timer.Create("wait-move", 3000)
    while Timer.Check("wait-move"):
        if get_player_pos() != pos:
            return True
        Misc.Pause(100)
    return False
    


def recall_by(serial: int, pos: Tuple[int, int, int]):
    """Implement a recall function to a specific serial."""
    while get_player_pos() != pos:
        Spells.Cast("Sacred Journey")
        if not Target.WaitForTarget(3000, False):
            return False
        Target.TargetExecute(serial)
        wait_until_move()
    return True


def find_enemies(include: Set) -> List["Mobile"]:  # type: ignore
    def _test(enemy: "Mobile") -> bool:
        if Player.DistanceTo(enemy) > 6:
            return False
        if enemy.Graphics in (0x030D, 0x030E, 0x030F):  # red solen
            return False
        if enemy.Graphics in (0x000B,):  # spiders, ugh
            return True
        if enemy.Serial in include:
            return True
        return False

    filter = Mobiles.Filter()
    filter.Enabled = True
    filter.Notorieties = CList[Byte](b"\x03\x04\x05\x06")
    # filter.Warmode = True
    enemies = [enemy for enemy in Mobiles.ApplyFilter(filter) if _test(enemy)]
    return enemies


def attack_enemies(enemies: List["Mobile"]) -> None:
    if Timer.Check("attack-delay"):
        return
    if len(enemies) == 0:
        return
    enemies = sorted(enemies, key=lambda e: Player.DistanceTo(e))
    enemy_near = enemies[0]
    pos = enemy_near.Position
    Player.Attack(enemy_near)
    Player.WeaponPrimarySA()
    Timer.Create("attack-delay", 500)


def flow_in_solen_cave(tolerance: int = 1) -> bool:
    """Move to a specific coordinate."""

    engaged = set()
    while True:
        # Enter the hole if there is one
        if get_dist_to(5661, 1955) <= 10 or get_dist_to(5901, 1878) <= 10:  # Tunnels
            hole = Items.FindByID(0x0495, 1, -1, 3)
            if hole is not None:
                Items.UseItem(hole.Serial)
                wait_until_move()

        # Check if we have reached the destination
        if get_dist_to(5868, 1795) <= tolerance:  # Minoc
            return True
        if get_dist_to(5742, 1820) <= tolerance:  # Yew
            return True
        if get_dist_to(5739, 1941) <= tolerance:  # Trinsic
            return True
        if get_dist_to(5912, 1944) <= tolerance:  # Desert
            return True
        if get_dist_to(5671, 1866) <= tolerance:  # Secret
            return True

        # Handle potential enemies on the way
        enemies = find_enemies(engaged)
        if enemies:
            cur_enemy = attack_enemies(enemies)
            if cur_enemy is not None:
                engaged.add(cur_enemy)
        else:
            execute_step()
        Misc.Pause(100)

    return True


def move_to(x: int, y: int, z: int, tolerance: int = 1) -> bool:
    """Move to a specific coordinate."""
    x0, y0, z0 = get_player_pos()
    engaged = set()
    while True:
        enemies = find_enemies(engaged)
        if enemies:
            cur_enemy = attack_enemies(enemies)
            if cur_enemy is not None:
                engaged.add(cur_enemy)
            Misc.Pause(100)
            continue
        if get_dist_to(x, y) <= tolerance:
            return True
        if get_dist_to(x, y) > 12:
            return False
        if not Timer.Check("move-wait"):
            Player.PathFindTo(x, y, z)
            Timer.Create("move-wait", 2000)
        Misc.Pause(100)
    return True


def sort_seeds():
    for i, seed in enumerate(Items.FindAllByID(0x0DCF, -1, Player.Backpack.Serial, 0)):
        row = i // 10
        col = i % 10
        x = 43 + 10 * col
        y = 79 + 10 * row
        if seed.Position.X == x and seed.Position.Y == y:
            continue
        Items.Move(seed.Serial, Player.Backpack.Serial, -1, x, y)
        Misc.Pause(1000)


def wait_for_record():
    if Journal.WaitJournal("You glance at the Egg Nest, realizing you've already studied this one.", 1000):
        return True
    if not Journal.WaitJournal("You begin studying the Solen Egg Nest to gather information.", 3000):
        return False
    if not Journal.WaitJournal("You begin recording your completed notes on a bit of parchment.", 15000):
        return False
    if not Journal.WaitJournal("You have completed your study of this Solen Egg Nest. You put your notes away.", 15000):
        return False
    return True


def wait_for_special_record():
    if Journal.WaitJournal("You glance at the Egg Nest, realizing you've already studied this one.", 1000):
        return True
    if not Journal.WaitJournal("You notice something very odd about this Solen Egg Nest.", 3000):
        return False
    if not Journal.WaitJournal("You complete your examination of this bizarre Egg Nest.", 60000):
        return False
    return True


def find_gump_by_def(gump_def: str) -> Optional[int]:
    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        if gd is None:
            continue
        if gd.gumpLayout.startswith(gump_def):
            return gumpid


def wait_for_gump(callback: Callable[[], Optional[int]], timeout: int = 10000) -> Optional[int]:
    Timer.Create("wait-for-gump", timeout)
    while Timer.Check("wait-for-gump"):
        gumpid = callback()
        if gumpid is not None:
            return gumpid
        Misc.Pause(100)


def find_quest_gump() -> Optional[int]:
    return find_gump_by_def("{ noclose }{ page 0 }{ gumppictiled 50 20 400 400 2624 }")


def find_quest_conversation_gump() -> Optional[int]:
    return find_gump_by_def("{ noclose }{ page 0 }{ gumppic 349 10 9392 }")


def find_quest_view_log_gump() -> Optional[int]:
    return find_gump_by_def("{ noclose }{ page 0 }{ gumppic 0 0 3600 }")


def wait_for_quest_gump(timeout: int = 10000) -> Optional[int]:
    return wait_for_gump(find_quest_gump, timeout)


def wait_for_quest_conversation_gump(timeout: int = 10000) -> Optional[int]:
    return wait_for_gump(find_quest_conversation_gump, timeout)


def wait_for_quest_view_log_gump(timeout: int = 10000) -> Optional[int]:
    return wait_for_gump(find_quest_view_log_gump, timeout)


def read_quest_progress() -> Optional[int]:
    response = None
    for entry in Misc.WaitForContext(Player.Serial, 1000, False):
        if entry.Entry == "View Quest Log":
            response = entry.Response
    if response is None:
        return None
    Misc.ContextReply(Player.Serial, response)

    gump_id = wait_for_quest_view_log_gump(1000)
    if gump_id is None:
        return 0

    gd = Gumps.GetGumpData(gump_id)
    Gumps.CloseGump(gump_id)
    if gd is None:
        return 0
    if len(gd.gumpData) != 3 or gd.gumpData[2] != "4":
        return 0

    return int(gd.gumpData[0])


# Quest Accept
def quest_accept():
    if not recall_by(0x5E145DE3, (1494, 1728, 0)):
        return False

    if not Misc.WaitForContext(0x00064FE2, 1000, False):
        return False
    Misc.ContextReply(0x00064FE2, 1)

    gump_id = wait_for_quest_gump(1000)
    if gump_id is None:
        return False
    Gumps.SendAdvancedAction(gump_id, 1, [1], [], [])

    gump_id = wait_for_quest_conversation_gump(1000)
    if gump_id is None:
        return False
    Gumps.SendAction(gump_id, 1)

    return True


def quest_complete():
    global REPEAT
    if not recall_by(0x5E145DE3, (1494, 1728, 0)):
        return False

    if not Misc.WaitForContext(0x00064FE2, 1000, False):
        return False
    Misc.ContextReply(0x00064FE2, 1)

    gump_id = wait_for_quest_conversation_gump(1000)
    if gump_id is None:
        return False
    Gumps.SendAction(gump_id, 1)

    Misc.Pause(1000)
    sort_seeds()

    REPEAT = max(0, REPEAT - 1)


def check_encounters():
    if Journal.Search("You have been ambushed!"):
        Misc.SendMessage("You have an encounter, be prepared!", 0x481)
        sys.exit(0)
    if Journal.Search("You found a treasure chest guarded by monsteres!"):
        Misc.SendMessage("You have an encounter, be prepared!", 0x481)
        sys.exit(0)
    if Journal.Search("A portal to the abyss has opened nearby!"):
        Misc.SendMessage("You have an encounter, be prepared!", 0x481)
        sys.exit(0)

    filter = Mobiles.Filter()
    filter.Enabled = True
    filter.Notorieties = CList[Byte](b"\x03\x04\x05\x06")
    filter.RangeMax = 64
    mobs = Mobiles.ApplyFilter(filter)
    for mob in mobs:
        Mobiles.WaitForProps(mob.Serial, 1000)
        for line in Mobiles.GetPropStringList(mob.Serial):
            if line.lower() == "encounter enemy":
                Misc.SendMessage("You have an encounter, be prepared!", 0x481)
                sys.exit(0)


# To Minoc Entrance
def tour_minoc_side():
    Journal.Clear()
    # Recall to the entrance and enter the hive
    if not recall_by(0x4008F0BB, (2604, 764, 0)):
        return False
    if not move_to(2608, 764, 0):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x4000316B)  # Entrance
    wait_until_move()
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    flow_in_solen_cave()
    return wait_for_record()


def tour_yew_side():
    Journal.Clear()
    if not recall_by(0x419AA5B3, (721, 1451, 0)):
        return False
    if not move_to(730, 1451, 0):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x400032A9)  # Entrance
    wait_until_move()
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    flow_in_solen_cave()
    return wait_for_record()


def tour_trinsic_side():
    Journal.Clear()
    if not recall_by(0x4010C97C, (1690, 2796, 0)):
        return False
    if not move_to(1690, 2791, 0):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x4000321C)  # Entrance
    wait_until_move()
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    flow_in_solen_cave()
    return wait_for_record()


def tour_desert_side():
    Journal.Clear()
    if not recall_by(0x4C11E643, (1729, 815, 0)):
        return False
    if not move_to(1726, 815, 0):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x40003277)  # Entrance
    wait_until_move()
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    flow_in_solen_cave()
    return wait_for_record()


def tour_secret_hole():
    Journal.Clear()
    thorns = Items.FindAllByID(0x0F42, 0x0042, Player.Backpack.Serial, 2)
    if len(thorns) == 0:
        return False

    # Recall to a sandy area
    if not recall_by(0x4010CB6E, (1510, 1873, 0)):
        return False
    Misc.Pause(1000)

    # Use the thorns to create a hole
    hole = Items.FindByID(0x0913, 1, -1, 3)
    if hole is None:
        Journal.Clear()
        Items.UseItem(thorns[0].Serial)
        if not Target.WaitForTarget(1000, False):
            return False
        Target.TargetExecute(1511, 1872, 0)

        Timer.Create("wait-for-hole", 20000)
        hole = None
        while Timer.Check("wait-for-hole"):
            hole = Items.FindByID(0x0913, 1, -1, 3)
            if hole is not None:
                break
            Misc.Pause(100)

    check_encounters()

    if hole is None:
        return False
    Items.UseItem(hole.Serial)
    wait_until_move()
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    flow_in_solen_cave()
    return wait_for_special_record()


def tour_all_sides():
    progress = read_quest_progress()
    if progress is None:
        Misc.SendMessage("Receiving the quest...", 68)
        quest_accept()
        progress = 0

    if progress == 0:
        Misc.SendMessage("Progressing to the nest #1...", 68)
        while not tour_trinsic_side():
            pass
        progress = 1

    if progress == 1:
        Misc.SendMessage("Progressing to the nest #2...", 68)
        while not tour_minoc_side():
            pass
        progress = 2

    if progress == 2:
        Misc.SendMessage("Progressing to the nest #3...", 68)
        while not tour_yew_side():
            pass
        progress = 3

    if progress == 3:
        Misc.SendMessage("Progressing to the nest #4...", 68)
        while not tour_desert_side():
            pass
        Misc.SendMessage("Progressing to the secret nest...", 68)
        tour_secret_hole()
        progress = 4

    if progress == 4:
        Misc.SendMessage("Completing the quest...", 68)
        quest_complete()


GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
SHORTCUT_GUMP_ID = hash("NaturalistQeustGump") & 0xFFFFFFFF


def ask_to_run() -> bool:
    """
    A minimized gump with a button to run a round.
    """
    Gumps.CloseGump(SHORTCUT_GUMP_ID)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Naturalist Quest"), False, False)

    Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WT.format(text="Run A Round"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, 3600000):
        return False
    gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
    if gd is None:
        return False
    return gd.buttonid == 1


if __name__ == "__main__":
    while Player.Connected:
        if REPEAT or ask_to_run():
            tour_all_sides()
