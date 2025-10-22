from AutoComplete import *
from typing import Optional, Tuple
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte, Int32  # type: ignore
from typing import List, Callable, Set, Any
from enum import Enum
import math
import sys


REPEAT = 100
USE_HIDING = False


################################################################################
# Visual Effect Module
################################################################################


def is_valid_source(obj: Any) -> bool:
    """
    Check if the object is a RazorEnhanced object.
    """
    if obj == Player:
        return True
    if hasattr(obj, "Serial") and hasattr(obj, "Position"):
        return True
    else:
        return False


class PacketBuilder:
    def __init__(self, header: int) -> None:
        self.header = header
        self.packet = bytearray()

    def add_byte(self, value: int) -> None:
        self.packet.append(value & 0xFF)

    def add_short(self, value: int) -> None:
        value &= 0xFFFF
        self.packet += value.to_bytes(2, "big")

    def add_int(self, value: int) -> None:
        value &= 0xFFFFFFFF
        self.packet += value.to_bytes(4, "big")

    def add_bytes(self, value: bytes) -> None:
        self.packet += value

    def __len__(self) -> int:
        return len(self.packet) + 1

    def build(self, prefix: Optional[bytes] = None) -> bytes:
        if prefix is None:
            prefix = bytes()
        return bytes(self.header.to_bytes(1, "big") + prefix + self.packet)


class GraphicEffectType(Enum):
    Moving = 0x00
    """It is a missile."""
    Lightning = 0x01
    """It is a lightning effect."""
    FixedPos = 0x02
    """It is a static effect."""
    FixedObj = 0x03
    """It is attached to the source object."""
    DragEffect = 0x05
    """It is a drag effect. (ClassicUO only)"""


class GraphicEffectBlendMode(Enum):
    Normal = 0x00
    """Normal, black is transparent."""
    Multiply = 0x01
    """Darken."""
    Screen = 0x02
    """Lighten."""
    ScreenMore = 0x03
    """Lighten more."""
    ScreenLess = 0x04
    """Lighten less."""
    NormalHalfTransparent = 0x05
    """Transparent but with black edges."""
    ShadowBlue = 0x06
    """Complete shadow with blue edges."""
    ScreenRed = 0x07
    """Lighten with red edges."""


class GraphicEffectArgs:
    def __init__(
        self,
        type: GraphicEffectType = GraphicEffectType.Moving,
        src_serial: int = 0,
        dst_serial: int = 0,
        itemid: int = 0,
        src_pos: Tuple[int, int, int] = (0, 0, 0),
        dst_pos: Tuple[int, int, int] = (0, 0, 0),
        speed: int = 0,
        duration: int = 1,
        fixed_dir: bool = False,
        explodes: bool = False,
        hue: int = 0,
        blend_mode: GraphicEffectBlendMode = GraphicEffectBlendMode.Normal,
        source: Any = None,
        target: Any = None,
    ):
        self.type = type
        self.src_serial = src_serial
        self.dst_serial = dst_serial
        self.itemid = itemid
        self.src_pos = src_pos
        self.dst_pos = dst_pos
        self.speed = speed
        self.duration = duration
        self.fixed_dir = fixed_dir
        self.explodes = explodes
        self.hue = hue
        self.blend_mode = blend_mode
        if source is not None:
            self.source = source
        if target is not None:
            self.target = target

    # This field is used to introduce @source.setter.
    @property
    def source(self) -> int:
        return self.src_serial

    @source.setter
    def source(self, value) -> None:
        """
        Sets the source of the effect. It can be an Item, position tuple, or serial ID.
        """
        if is_valid_source(value):
            self.src_serial = value.Serial
            self.src_pos = (value.Position.X, value.Position.Y, value.Position.Z)
        elif isinstance(value, tuple) and len(value) == 3:
            self.src_serial = 0
            self.src_pos = value
        elif isinstance(value, int):
            self.src_serial = value
            obj = Items.FindBySerial(value)
            if obj is not None:
                self.src_pos = (obj.Position.X, obj.Position.Y, obj.Position.Z)
        else:
            raise ValueError("Invalid source value. Must be an Item, position tuple, or serial ID.")

    @property
    def target(self) -> int:
        return self.dst_serial

    @target.setter
    def target(self, value) -> None:
        """
        Sets the target of the effect. It can be an Item, position tuple, or serial ID.
        """
        if is_valid_source(value):
            self.dst_serial = value.Serial
            self.dst_pos = (value.Position.X, value.Position.Y, value.Position.Z)
        elif isinstance(value, tuple) and len(value) == 3:
            self.dst_serial = 0
            self.dst_pos = value
        elif isinstance(value, int):
            self.dst_serial = value
            obj = Items.FindBySerial(value)
            if obj is not None:
                self.dst_pos = (obj.Position.X, obj.Position.Y, obj.Position.Z)
        else:
            raise ValueError("Invalid target value. Must be an Item, position tuple, or serial ID.")


class Effects:
    Type: "TypeAlias" = GraphicEffectType
    BlendMode: "TypeAlias" = GraphicEffectBlendMode
    Args: "TypeAlias" = GraphicEffectArgs

    @staticmethod
    def Render(args: Args) -> None:
        packet = PacketBuilder(0xC0)
        packet.add_byte(args.type.value)
        packet.add_int(args.src_serial)
        packet.add_int(args.dst_serial)
        packet.add_short(args.itemid)
        packet.add_short(args.src_pos[0])
        packet.add_short(args.src_pos[1])
        packet.add_byte(args.src_pos[2])
        packet.add_short(args.dst_pos[0])
        packet.add_short(args.dst_pos[1])
        packet.add_byte(args.dst_pos[2])
        packet.add_byte(args.speed)
        packet.add_byte(args.duration)
        packet.add_byte(0)  # unk1
        packet.add_byte(0)  # unk2
        packet.add_byte(int(args.fixed_dir))
        packet.add_byte(int(args.explodes))
        packet.add_int(args.hue)
        packet.add_int(args.blend_mode.value)
        PacketLogger.SendToClient(CList[Byte](packet.build()))

    @classmethod
    def Moving(
        cls,
        source: Any,
        target: Any,
        itemid: int,
        speed: int = 1,
        duration: int = 1,
        hue: int = 0,
        blend_mode: BlendMode = BlendMode.Normal,
        fixed_dir: bool = False,
        explodes: bool = False,
    ) -> None:
        """
        Creates a missile effect from the source to the target.

        :param source: The source, which can be an Item, position tuple, or serial ID.
        :param target: The target, which can be an Item, position tuple, or serial ID.
        :param itemid: The graphic ID of the missile.
        :param speed: The speed of the missile.
        :param duration: The number of frames in a single cycle of the animation.
        :param hue: The hue of the missile.
        :param blend_mode: The blend mode of the graphic effect.
        :param fixed_dir: If True, the graphic will not be rotated when it moves.
        :param explodes: Whether the missile explodes on impact.
        """
        cls.Render(
            cls.Args(
                type=cls.Type.Moving,
                source=source,
                target=target,
                itemid=itemid,
                speed=speed,
                duration=duration,
                hue=hue,
                blend_mode=blend_mode,
                fixed_dir=fixed_dir,
                explodes=explodes,
            )
        )

    @classmethod
    def DragEffect(
        cls,
        source: Any,
        target: Any,
        itemid: int,
        speed: int = 1,
        duration: int = 1,
        hue: int = 0,
        blend_mode: BlendMode = BlendMode.Normal,
        explodes: bool = False,
    ) -> None:
        """
        Creates a drag effect from the source to the target.

        :param source: The source, which can be an Item, position tuple, or serial ID.
        :param target: The target, which can be an Item, position tuple, or serial ID.
        :param itemid: The graphic ID of the missile.
        :param speed: The speed of the missile.
        :param duration: The number of frames in a single cycle of the animation.
        :param hue: The hue of the missile.
        :param blend_mode: The blend mode of the graphic effect.
        """
        cls.Render(
            cls.Args(
                type=cls.Type.DragEffect,
                source=source,
                target=target,
                itemid=itemid,
                speed=speed,
                duration=duration,
                hue=hue,
                blend_mode=blend_mode,
                explodes=explodes,
            )
        )

    @classmethod
    def Lightning(
        cls,
        source: Any,
        hue: int = 0,
    ) -> None:
        """
        Creates a lightning effect at the source.

        :param source: The source, which can be an Item, position tuple, or serial ID.
        :param hue: The hue of the lightning effect.
        """
        cls.Render(
            cls.Args(
                type=cls.Type.Lightning,
                source=source,
                hue=hue,
            )
        )

    @classmethod
    def AtFixedPos(
        cls,
        source: Any,
        itemid: int,
        duration: int,
        hue: int = 0,
        blend_mode: BlendMode = BlendMode.Normal,
    ):
        """
        Creates a graphical effect at the given position.

        :param source: The source, which can be an Item, position tuple, or serial ID.
        :param itemid: The graphic ID of the effect.
        :param duration: The number of frames in a single cycle of the animation.
        :param hue: The hue of the effect.
        :param blend_mode: The blend mode of the graphic effect.
        """
        cls.Render(
            cls.Args(
                type=cls.Type.FixedPos,
                source=source,
                itemid=itemid,
                duration=duration,
                hue=hue,
                blend_mode=blend_mode,
            )
        )

    @classmethod
    def OnFixedObj(
        cls,
        source: Any,
        itemid: int,
        duration: int,
        hue: int = 0,
        blend_mode: BlendMode = BlendMode.Normal,
    ):
        """
        Creates a graphical effect at the given object.

        :param source: The source, which can be an Item, position tuple, or serial ID.
        :param itemid: The graphic ID of the effect.
        :param duration: The number of frames in a single cycle of the animation.
        :param hue: The hue of the effect.
        :param blend_mode: The blend mode of the graphic effect.
        """
        cls.Render(
            cls.Args(
                type=cls.Type.FixedObj,
                source=source,
                itemid=itemid,
                duration=duration,
                hue=hue,
                blend_mode=blend_mode,
            )
        )


################################################################################
# Quest Module
################################################################################


def get_player_pos() -> Tuple[int, int, int]:
    return (Player.Position.X, Player.Position.Y, Player.Position.Z)


def get_dist_to(x, y) -> int:
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


def recall_by(serial: int, pos: Tuple[int, int, int]):
    """Implement a recall function to a specific serial."""
    while get_player_pos() != pos:
        Spells.Cast("Sacred Journey")
        if not Target.WaitForTarget(3000, False):
            return False
        Target.TargetExecute(serial)
        Misc.Pause(3000)
    return True


def find_enemies(include: Set) -> List["Mobile"]:  # type: ignore
    def _test(enemy: "Mobile") -> bool:
        if Player.DistanceTo(enemy) > 6:
            return False
        if enemy.Graphics in (0x030D, 0x030E, 0x030F):  # red solen
            return False
        if enemy.Graphics in (0x000B, ):  # spiders, ugh
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


def move_to(x1: int, y1: int, z1: int, tolerance: int = 1, cancel_on_enemy: bool = True) -> bool:
    """Move to a specific coordinate."""
    x0, y0, z0 = get_player_pos()
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0

    dist = max(abs(dx), abs(dy))
    steps = math.ceil(dist / 10)
    for i in range(steps):
        ratio = min(1, (i + 1) * 10 / dist)
        x = x0 + math.floor(dx * ratio)
        y = y0 + math.floor(dy * ratio)
        z = z0 + math.floor(dz * ratio)
        if get_dist_to(x, y) > 12:
            return False
        while True:
            Player.PathFindTo(x, y, z)
            Timer.Create("move-wait", 2000)
            Effects.AtFixedPos((x, y, z), 14120, 13, 0x802, Effects.BlendMode.Screen)
            Timer.Create("effect-delay", 1000)
            while Timer.Check("move-wait"):
                if not Timer.Check("effect-delay"):
                    Effects.AtFixedPos((x, y, z), 14120, 13, 0x802, Effects.BlendMode.Screen)
                    Timer.Create("effect-delay", 1000)
                Misc.Pause(100)
                if get_dist_to(x, y) <= tolerance:
                    break
                # If your journey is interruped by an enemy,
                # wait until the enemy is gone and restart
                engaged = set()
                enemies = find_enemies(engaged)
                if enemies:
                    while enemies:
                        cur_enemy = attack_enemies(enemies)
                        if cur_enemy is not None:
                            engaged.add(cur_enemy)
                        Misc.Pause(100)
                        enemies = find_enemies(engaged)
                    if cancel_on_enemy:
                        return False
            if get_dist_to(x, y) > 12:
                return False
            if get_dist_to(x, y) <= tolerance:
                break

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
    Misc.Pause(1000)

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
    Misc.Pause(1000)

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
    if not move_to(2608, 764, 0, cancel_on_enemy=False):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x4000316B)  # Entrance
    Misc.Pause(2000)
    if not is_in_ant_cave():
        return False

    # Move to the next hole and use it
    path = [(5924, 1800, 1), (5921, 1857, 0), (5901, 1878, 0)]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False
    Misc.Pause(1000)
    Items.UseItem(0x4000318E)  # Hole
    Misc.Pause(2000)

    # Move to the nest
    Journal.Clear()
    path = [
        (5894, 1851, 1),
        (5870, 1831, 2),
        (5854, 1820, 7),
        (5844, 1820, 2),
        (5829, 1805, 5),
        (5829, 1795, 1),
        (5868, 1795, 9),
    ]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False

    return wait_for_record()


def tour_yew_side():
    Journal.Clear()
    if not recall_by(0x419AA5B3, (721, 1451, 0)):
        return False
    if not move_to(730, 1451, 0, cancel_on_enemy=False):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x400032A9)  # Entrance
    Misc.Pause(2000)
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    path = [
        (5654, 1799, 2),
        (5654, 1828, 2),
        (5674, 1848, 2),
        (5683, 1848, 0),
        (5694, 1837, 2),
        (5694, 1830, 2),
        (5705, 1819, 4),
        (5714, 1828, 0),
        (5726, 1828, 1),
        (5733, 1820, 4),
        (5742, 1820, 2),
    ]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False

    return wait_for_record()


def tour_trinsic_side():
    Journal.Clear()
    if not recall_by(0x4010C97C, (1690, 2796, 0)):
        return False
    if not move_to(1690, 2791, 0, cancel_on_enemy=False):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x4000321C)  # Entrance
    Misc.Pause(2000)
    if not is_in_ant_cave():
        return False

    # Move to the next hole and use it
    path = [
        (5661, 2023, 0),
        (5668, 2026, 5),
        (5756, 2026, 4),
        (5765, 2023, 4),
        (5764, 2014, 4),
        (5746, 1996, 2),
        (5746, 1986, 3),
        (5740, 1980, 1),
        (5740, 1972, 0),
        (5734, 1966, 1),
        (5724, 1976, 0),
        (5690, 1976, 2),
        (5679, 1965, 3),
        (5679, 1965, 3),
        (5674, 1965, 1),
        (5664, 1955, 0),
        (5661, 1955, 0),
    ]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False
    Misc.Pause(1000)
    Items.UseItem(0x400031F6)  # Hole
    Misc.Pause(2000)

    # Hide to clear the targetting
    if USE_HIDING:
        while not Player.BuffsExist("Hiding", True):
            Player.UseSkill("Hiding")
            Misc.Pause(1000)

    # Move to the nest
    # Deal with potential enemies on the way
    Journal.Clear()
    path = [
        (5707, 1955, 0),
        (5694, 1955, 1),
        (5684, 1945, 4),
        (5678, 1945, 1),
        (5666, 1933, 5),
        (5685, 1914, 0),
        (5695, 1924, 1),
        (5709, 1924, 2),
        (5718, 1915, 1),
        (5742, 1915, 0),
        (5754, 1928, 2),
        (5755, 1933, 1),
        (5755, 1938, 1),
        (5752, 1941, 1),
        (5739, 1941, 4),
    ]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False

    return wait_for_record()


def tour_desert_side():
    Journal.Clear()
    if not recall_by(0x4C11E643, (1729, 815, 0)):
        return False
    if not move_to(1726, 815, 0, cancel_on_enemy=False):
        return False
    Misc.Pause(1000)
    check_encounters()

    Items.UseItem(0x40003277)  # Entrance
    Misc.Pause(2000)
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    path = [
        (5920, 2017, 1),
        (5920, 1983, 1),
        (5914, 1971, 1),
        (5907, 1964, 2),
        (5898, 1968, 0),
        (5883, 1970, 2),
        (5883, 1962, 1),
        (5897, 1949, 3),
        (5907, 1949, 0),
        (5912, 1944, 7),
    ]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False

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

        # Wait for the hole to appear and use it
        # if not Journal.WaitJournal("* You push the strange green thorn into the ground *", 3000):
        #     return fALSE
        # if not Journal.WaitJournal("* The sand collapses, revealing a dark hole. *", 20000):
        #     return

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
    Misc.Pause(2000)
    if not is_in_ant_cave():
        return False

    # Move to the nest
    Journal.Clear()
    path = [
        (5731, 1857, 2),
        (5717, 1855, 0),
        (5707, 1845, -11),
        (5686, 1866, 1),
        (5671, 1866, 6),
    ]
    for x, y, z in path:
        if not move_to(x, y, z):
            return False

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
