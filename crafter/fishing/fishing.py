from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import List, Dict, Tuple, Optional, Any, Callable
import re


MAX_FISHING_DIST = 12
AUTO_ADVANCE = False
ORGANIZE_CONTS = [0x5A253F1C]
TRASH_CANS = [0x5B2C82C5]


def norm_linf(p: Tuple[int, int]) -> int:
    return max(abs(p[0]), abs(p[1]))


def get_player_pos() -> Tuple[int, int, int]:
    pos = Player.Position
    return (pos.X, pos.Y, pos.Z)


GUMP_MENU = hash("FishingGump") & 0xFFFFFFFF
GUMP_BC = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
FISH = [2508, 2509, 2510, 2511, 17154, 17155, 17158, 17159, 17603, 17604, 17605, 17606]
FISH_SMALL = [3542]
FOOTWEAR = [5899, 5900, 5901, 5902, 5903, 5904, 5905, 5906]

def ask_action() -> Optional[str]:
    Gumps.CloseGump(GUMP_MENU)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 90, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 90)
    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_BC.format(text="Fishing Helper"), False, False)
    Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
    Gumps.AddHtml(gd, 10, 33, 126, 18, GUMP_BC.format(text="Fish Spot"), False, False)
    Gumps.AddButton(gd, 10, 55, 40021, 40031, 2, 1, 0)
    Gumps.AddHtml(gd, 10, 58, 126, 18, GUMP_BC.format(text="Organize"), False, False)
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
    if not Gumps.WaitForGump(GUMP_MENU, 3600000):
        return
    gd = Gumps.GetGumpData(GUMP_MENU)
    if gd is None:
        return
    if gd.buttonid == 1:
        return "fish spot"
    if gd.buttonid == 2:
        return "organize" 


class Fishing:
    LAST_SPOT = (-1, -1, 0)
    
    class ContainerFullError(Exception):
        pass

    class NoFishingPoleError(Exception):
        pass

    class ActionDelayError(Exception):
        pass

    class NoTargetCursorError(Exception):
        pass

    class InvalidTargetError(Exception):
        pass

    class MountedError(Exception):
        pass

    class DepleteError(Exception):
        pass

    class AlreadyFishingError(Exception):
        pass

    class EnemyFoundError(Exception):
        pass
    
    @staticmethod
    def dismount():
        if Player.Mount is not None:
            Mobiles.UseMobile(Player.Serial)
            Misc.Pause(1000)

    @classmethod
    def find_fishing_pole(cls) -> Optional["Item"]:
        filter = Items.Filter()
        filter.Enabled = True
        filter.Graphics = CList[Int32]([0x0DC0])
        filter.OnGround = False
        owners = (Player.Serial, Player.Backpack.Serial)
        for item in Items.ApplyFilter(filter):
            if item.RootContainer in owners:
                return item

    @staticmethod
    def get_water(pos: Tuple[int, int, int]) -> Optional[Tuple[int, int, int, Optional[int]]]:
        """
        Check if the player is on a water land tile.
        """
        x, y, z = pos
        arg = (x, y, Player.Map)
        land_tile = Statics.GetLandID(*arg)
        if Statics.GetLandFlag(land_tile, "Wet"):
            return (x, y, Statics.GetLandZ(*arg), None)
        for tile in Statics.GetStaticsTileInfo(*arg):
            if Statics.GetTileFlag(tile.StaticID, "Wet"):
                return (x, y, tile.Z, tile.StaticID)

    @classmethod
    def use_fishing_pole(cls):
        if not cls.check_available():
            raise cls.ContainerFullError()
            
        pole = cls.find_fishing_pole()
        if pole is None:
            raise cls.NoFishingPoleError()

        water_info = cls.get_water(get_player_pos())
        if water_info:
            cls.LAST_SPOT = get_player_pos()
        elif cls.LAST_SPOT == (-1, -1, 0):
            pos = Target.PromptGroundTarget("Select fishing spot (max 12 tiles away):", 0x3B2)
            cls.LAST_SPOT = (pos.X, pos.Y, pos.Z)
            if cls.LAST_SPOT == (-1, -1, 0):
                raise cls.InvalidTargetError()
            water_info = cls.get_water(cls.LAST_SPOT)
        if water_info is None:
            raise cls.InvalidTargetError()

        Journal.Clear()
        Items.UseItem(pole.Serial)
        Timer.Create("fishing-delay", 9000)
        success = Journal.WaitJournal("What water do you want to fish in?", 1000)
        if Journal.Search("You must wait to perform another action."):
            raise cls.ActionDelayError()
        if Journal.Search("You can't fish while riding or flying!"):
            raise cls.MountedError()
        if not success:
            raise Exception("Unknown error after using fishing pole.")

        if not Target.WaitForTarget(1000, False):
            raise cls.NoTargetCursorError()

        x, y, z, tile = water_info
        if tile is None:
            Target.TargetExecute(x, y, z)
        else:
            Target.TargetExecute(x, y, z, tile)

        Timer.Create("wait-journal", 1000)
        while Timer.Check("wait-journal"):
            if Journal.Search("Target cannot be seen."):
                raise cls.InvalidTargetError()
            if Journal.Search("You need to be closer to the water to fish!"):
                raise cls.InvalidTargetError()
            if Journal.Search("The fish don't seem to be biting here."):
                raise cls.DepleteError()
            if Journal.Search("You are already fishing"):
                raise cls.AlreadyFishingError()
            Misc.Pause(100)
        
        if Sound.WaitForSound(CList[Int32]([0x0364]), 3000):
            return
        raise Exception("Unknown error after targeting fishing spot.")

    @classmethod
    def find_enemy(cls) -> bool:
        enemies = []
        # Find any hostile enemies
        filter = Mobiles.Filter()
        filter.Enabled = True
        filter.Warmode = True
        enemies.extend(Mobiles.ApplyFilter(filter))
        # Find water elementals or sea serpents
        filter = Mobiles.Filter()
        filter.Bodies = CList[Int32]([10, 150])
        filter.Enabled = True
        filter.RangeMax = 10
        enemies.extend(Mobiles.ApplyFilter(filter))
        
        return len(enemies) > 0
    
    @classmethod
    def check_available(cls) -> bool:
        Items.WaitForProps(Player.Backpack.Serial, 1000)
        cont, max_cont, weight, max_weight = 0, 0, 0, 0
        for prop in Items.GetPropStringList(Player.Backpack.Serial):
            matchres = re.match(r"contents: (\d+)/(\d+) items, (\d+)/(\d+) stones", prop.lower())
            if not matchres:
                continue
            cont = int(matchres.group(1))
            max_cont = int(matchres.group(2))
            weight = int(matchres.group(3))
            max_weight = int(matchres.group(4))
            break
        if cont == max_cont:
            Misc.SendMessage("Your inventory cannot hold more items.", 33)
            return False
        if weight + 10 >= max_weight:
            Misc.SendMessage("Your inventory cannot hold more weight.", 33)
            return False
        return True

    @classmethod
    def handle_response(cls):
        while Timer.Check("fishing-delay"):
            if cls.find_enemy():
                raise cls.EnemyFoundError()
            if Journal.Search("You fish a while, but fail to catch anything."):
                return
            if Journal.Search("You pull out"):
                return
            Misc.Pause(100)

    @classmethod
    def fish_spot(cls):
        cls.dismount()
        cls.LAST_SPOT = (-1, -1, 0)
        while True:
            try:
                cls.use_fishing_pole()
                cls.handle_response()
                if AUTO_ADVANCE:
                    Player.ChatSay("one forward")
            except cls.ContainerFullError:
                return
            except cls.NoFishingPoleError:
                Misc.SendMessage("No fishing pole found in backpack or equipped.", 33)
                return
            except cls.ActionDelayError:
                Misc.Pause(500)
                continue
            except cls.MountedError:
                cls.dismount()
                continue
            except cls.NoTargetCursorError:
                Misc.SendMessage("No target cursor appeared after using fishing pole.", 33)
                return
            except cls.InvalidTargetError:
                Misc.SendMessage("Invalid fishing target.", 33)
                return
            except cls.DepleteError:
                Misc.SendMessage("Fishing spot depleted.", 68)
                return
            except cls.AlreadyFishingError:
                Misc.Pause(500)
                continue
            except cls.EnemyFoundError:
                Misc.SendMessage("Enemy detected! Stopping fishing.", 0x481)
                return
            except Exception as e:
                Misc.SendMessage(f"Error using fishing pole: {e}", 33)
                return

    @classmethod
    def find_any_nearby(cls, serials: List[int]) -> Optional["Item"]:
        for serial in serials:
            item = Items.FindBySerial(serial)
            if item is None:
                continue
            if Player.DistanceTo(item) > 2:
                continue
            return item
    
    @classmethod
    def organize(cls) -> None:
        # Organize fish
        cont = cls.find_any_nearby(ORGANIZE_CONTS)
        if cont is None:
            Misc.SendMessage("Failed to find any organizer bag nearby.", 33)
        else:
            for item in Items.FindAllByID(FISH, -1, Player.Backpack.Serial, 2):
                Items.Move(item.Serial, cont.Serial, -1)
                Misc.Pause(1000)
        # Toss away shoes and small fish
        cont = cls.find_any_nearby(TRASH_CANS)
        if cont is None:
            Misc.SendMessage("Failed to find any trash can nearby.", 33)
        else:
            for item in Items.FindAllByID(FOOTWEAR + FISH_SMALL, -1, Player.Backpack.Serial, 2):
                Items.Move(item.Serial, cont.Serial, -1)
                Misc.Pause(1000)
        


if __name__ == "__main__":
    while Player.Connected:
        response = ask_action()
        if response == "fish spot":
            Fishing.fish_spot()
            continue
        if response == "organize":
            Fishing.organize()