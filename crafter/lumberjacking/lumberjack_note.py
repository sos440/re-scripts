################################################################################
# User Setting
################################################################################


# When this is set to True, the script will highlight the newly found trees
HIGHLIGHT_NEW = True

# When this is set to True, the script will highlight the deplete locations
HIGHLIGHT_DEPLETE = True

# Duration (in MINUTES) for the deplete location to be ignored
# Example: 20 minutes = 20.0
LUMBER_COOLDOWN = 20.0

# When this is set to True, the script will export the deplete locations to a file
# and load it when the script starts.
SAVE_HISTORY = True


################################################################################
# Script starts here. You do not need to modify anything below this line.
################################################################################


import threading
import time
import os
import xml.etree.ElementTree as ET
from enum import Enum
from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte, Int32  # type: ignore
from typing import Union, Optional, Any, Tuple, Dict, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


################################################################################
# TreeHistory Class
################################################################################


TreeHistoryHash = Tuple[int, int, int, int]
"""A hash for the tree history, consisting of the x, y, z coordinates and the tile ID."""

TreeHistoryDict = Dict[TreeHistoryHash, "TreeHistory"]
"""A dictionary for the tree history, where the key is the hash and the value is the TreeHistory object."""


class TreeHistory:
    """
    A class for storing the logging history of trees.
    """

    tileid: int
    """The tile ID of the tree."""
    pos: Tuple[int, int, int]
    """The position of the tree."""
    depleted: bool
    """Whether the tree is depleted or not."""
    ignore: bool
    """Whether the tree should be ignored or not.
    Mostly used for ignoring the type of trees that cannot be logged."""
    time_depleted: float
    """Timestamp of when the tree was depleted."""
    time_highlight: float
    """Timestamp of when the tree was depleted."""

    def __init__(
        self,
        tileid: int,
        pos: Tuple[int, int, int],
        depleted: bool = False,
        ignore: bool = False,
        time_depleted: float = 0.0,
    ):
        self.tileid = tileid
        self.pos = pos
        self.depleted = depleted
        self.ignore = ignore
        self.time_depleted = time_depleted
        self.time_highlight = 0

    @property
    def hash(self) -> TreeHistoryHash:
        return (self.pos[0], self.pos[1], self.pos[2], self.tileid)

    @property
    def is_in_cooldown(self) -> bool:
        """Check if the tree is in cooldown."""
        return self.depleted and time.time() < (self.time_depleted + (LUMBER_COOLDOWN * 60))

    @property
    def is_ignored(self) -> bool:
        """Check if the tree should be ignored while searching for trees."""
        return self.ignore or self.is_in_cooldown

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    @property
    def z(self) -> int:
        return self.pos[2]

    def to_xml(self) -> ET.Element:
        """
        Exports the current tree history to an XML element.
        """
        element = ET.Element("TreeHistory")
        element.set("tileid", str(self.tileid))
        element.set("x", str(self.pos[0]))
        element.set("y", str(self.pos[1]))
        element.set("z", str(self.pos[2]))
        element.set("depleted", str(self.depleted))
        element.set("ignore", str(self.ignore))
        element.set("time_depleted", str(self.time_depleted))
        return element

    @classmethod
    def from_xml(cls, element: ET.Element) -> "TreeHistory":
        """
        Parses the tree history from an XML element.
        """
        assert element.tag == "TreeHistory"
        assert element.attrib, "Missing attributes in TreeHistory XML element"
        assert "tileid" in element.attrib, "Missing tileid attribute in TreeHistory XML element"
        assert "x" in element.attrib, "Missing x attribute in TreeHistory XML element"
        assert "y" in element.attrib, "Missing y attribute in TreeHistory XML element"
        assert "z" in element.attrib, "Missing z attribute in TreeHistory XML element"
        assert "depleted" in element.attrib, "Missing depleted attribute in TreeHistory XML element"
        assert "ignore" in element.attrib, "Missing ignore attribute in TreeHistory XML element"
        assert "time_depleted" in element.attrib, "Missing time_depleted attribute in TreeHistory XML element"

        tileid = int(element.attrib["tileid"])
        x = int(element.attrib["x"])
        y = int(element.attrib["y"])
        z = int(element.attrib["z"])
        depleted = element.attrib["depleted"].lower() == "true"
        ignore = element.attrib["ignore"].lower() == "true"
        time_depleted = float(element.attrib["time_depleted"])
        return cls(
            tileid,
            (x, y, z),
            depleted=depleted,
            ignore=ignore,
            time_depleted=time_depleted,
        )


################################################################################
# File System
################################################################################


PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(PATH, "data")
RECORD_PATH = os.path.join(SAVE_DIR, "lumber_history.xml")

# Create the directory if it doesn't exist
if SAVE_HISTORY and not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)


def load_history() -> TreeHistoryDict:
    if os.path.exists(RECORD_PATH):
        try:
            with open(RECORD_PATH, "r") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                history: TreeHistoryDict = {}
                for elem in root.findall("TreeHistory"):
                    entry = TreeHistory.from_xml(elem)
                    history[entry.hash] = entry
                return history
        except:
            Misc.SendMessage("Failed to open the file.", 0x21)
            return {}
    else:
        return {}


def save_history(history: TreeHistoryDict):
    with open(RECORD_PATH, "wb") as f:
        root = ET.Element("TreeHistoryList")
        for entry in history.values():
            root.append(entry.to_xml())
        tree = ET.ElementTree(root)
        tree.write(f, encoding="utf-8", xml_declaration=True)


################################################################################
# Visual Effect Module - For Fun!
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
    Type = GraphicEffectType
    BlendMode = GraphicEffectBlendMode
    Args = GraphicEffectArgs

    @classmethod
    def Render(cls, args: Args) -> None:
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
        PacketLogger.SendToClient(GenList[Byte](packet.build()))

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

    @classmethod
    def SoundEffect(cls, sound_model: int):
        """
        Plays a sound effect at the player's position.

        :param sound_model: The sound model ID.
        """
        packet = PacketBuilder(0x54)
        packet.add_byte(0x01)
        packet.add_short(sound_model)
        packet.add_short(0x0000)
        packet.add_short(Player.Position.X)
        packet.add_short(Player.Position.Y)
        packet.add_short(Player.Position.Z)

        PacketLogger.SendToClient(GenList[Byte](packet.build()))


################################################################################
# Main Script
################################################################################


# History of the trees
history = load_history()

# Gump-related constants
GUMP_MENU = hash("LumberjackHelperGump") & 0xFFFFFFFF
GUMP_BUTTONTEXT_WRAP = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""

# Static IDs for the loggable trees
TREE_STATIC_IDS = [
    0x0C95,
    0x0C96,
    0x0C99,
    0x0C9B,
    0x0C9C,
    0x0C9D,
    0x0C8A,
    0x0CA6,
    0x0CA8,
    0x0CAA,
    0x0CAB,
    0x0CC3,
    0x0CC4,
    0x0CC8,
    0x0CC9,
    0x0CCA,
    0x0CCB,
    0x0CCC,
    0x0CCD,
    0x0CD0,
    0x0CD3,
    0x0CD6,
    0x0CD8,
    0x0CDA,
    0x0CDD,
    0x0CE0,
    0x0CE3,
    0x0CE6,
    0x0CF8,
    0x0CFB,
    0x0CFE,
    0x0D01,
    0x0D25,
    0x0D27,
    0x0D35,
    0x0D37,
    0x0D38,
    0x0D42,
    0x0D43,
    0x0D59,
    0x0D70,
    0x0D85,
    0x0D94,
    0x0D96,
    0x0D98,
    0x0D9A,
    0x0D9C,
    0x0D9E,
    0x0DA0,
    0x0DA2,
    0x0DA4,
    0x0DA8,
]


def iter_neighbors(
    max_distance: int = 2,
    include_center: bool = False,
):
    d = max_distance
    if d < 1:
        raise ValueError("max_distance must be greater than 0")

    x, y = Player.Position.X, Player.Position.Y
    for dx in range(-d, d + 1):
        for dy in range(-d, d + 1):
            if not include_center and dx == 0 and dy == 0:
                continue
            yield (x + dx, y + dy)


def find_trees_nearby(ignore_list: List[TreeHistoryHash]) -> List[TreeHistory]:
    trees: List[TreeHistory] = []
    for x, y in iter_neighbors(2):
        for tile in Statics.GetStaticsTileInfo(x, y, Player.Map):
            if tile.StaticID not in TREE_STATIC_IDS:
                continue
            tree = TreeHistory(tile.StaticID, (x, y, tile.StaticZ))
            if tree.hash not in ignore_list:
                trees.append(tree)
    return trees


def find_trees_at(x: int, y: int, z: int) -> Optional[TreeHistory]:
    for tile in Statics.GetStaticsTileInfo(x, y, Player.Map):
        if tile.StaticID not in TREE_STATIC_IDS:
            continue
        if tile.StaticZ != z:
            continue
        return TreeHistory(tile.StaticID, (x, y, tile.StaticZ))


def highlight_cooldown(history: TreeHistoryDict):
    x0, y0 = Player.Position.X, Player.Position.Y
    for entry in history.values():
        if not entry.is_ignored:
            continue
        dist = max(abs(entry.x - x0), abs(entry.y - y0))
        if dist > 64:
            continue
        Effects.AtFixedPos(entry.pos, entry.tileid, 60, 1165)


def get_last_target(delay: int = 1000):
    def delayed_last():
        Target.WaitForTarget(delay, True)
        Target.Last()
    daemon_thread = threading.Thread(target=delayed_last)
    daemon_thread.daemon = True
    daemon_thread.start()
    res = Target.PromptGroundTarget("")
    daemon_thread.join()
    return res


# def gump_menu():
#     Gumps.CloseGump(GUMP_MENU)

#     # Create the gump
#     gd = Gumps.CreateGump(movable=True)
#     Gumps.AddPage(gd, 0)
#     Gumps.AddBackground(gd, 0, 0, 146, 90, 30546)
#     Gumps.AddAlphaRegion(gd, 0, 0, 146, 90)

#     Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Lumberjack's Note"), False, False)

#     Gumps.AddButton(gd, 10, 30, 40021, 40031, 1001, 1, 0)
#     Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Mark as Depleted"), False, False)

#     Gumps.AddButton(gd, 10, 55, 40297, 40298, 1002, 1, 0)
#     Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Remove Mark"), False, False)

#     # Send the gump and listen for the response
#     Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


Journal.Clear()
# gump_menu()
while Player.Connected:
    if HIGHLIGHT_DEPLETE:
        highlight_cooldown(history)

    trees = find_trees_nearby([entry.hash for entry in history.values() if entry.is_ignored])
    for entry in trees:
        if entry.hash not in history:
            history[entry.hash] = entry
        else:
            entry = history[entry.hash]
            
        if HIGHLIGHT_NEW and entry.time_highlight <= time.time():
            Effects.AtFixedPos(entry.pos, entry.tileid, 10, 88, Effects.BlendMode.Screen)
            entry.time_highlight = time.time() + 1.0

    
    if Journal.WaitJournal("There's not enough wood here to harvest.", 250):
        Journal.Clear()
        target = get_last_target()
        target = (target.X, target.Y, target.Z)
        if target == (-1, -1, 0):
            pass
        else:
            tree = find_trees_at(*target)
            if tree is None:
                Misc.SendMessage("No tree found at the target location.", 0x21)
            else:
                history[tree.hash].depleted = True
                history[tree.hash].time_depleted = time.time()
                if SAVE_HISTORY:
                    save_history(history)

    
    # if not Gumps.WaitForGump(GUMP_MENU, 100):
    #     continue

    # gd = Gumps.GetGumpData(GUMP_MENU)
    # if gd is None or gd.buttonid == 0:
    #     pass
    # elif gd.buttonid == 1001:
    #     target = Target.PromptGroundTarget("Choose the tree to mark as depleted.", 0x47E)
    #     target = (target.X, target.Y, target.Z)
    #     if target == (-1, -1, 0):
    #         pass
    #     else:
    #         tree = find_trees_at(*target)
    #         if tree is None:
    #             Misc.SendMessage("No tree found at the target location.", 0x21)
    #         else:
    #             history[tree.hash].depleted = True
    #             history[tree.hash].time_depleted = time.time()
    #             save_history(history)
    # elif gd.buttonid == 1002:
    #     target = Target.PromptGroundTarget("Choose the tree to remove the mark.", 0x47E)
    #     target = (target.X, target.Y, target.Z)
    #     if target == (-1, -1, 0):
    #         pass
    #     else:
    #         tree = find_trees_at(*target)
    #         if tree is None:
    #             Misc.SendMessage("No tree found at the target location.", 0x21)
    #         else:
    #             history[tree.hash].depleted = False
    #             save_history(history)

    # gump_menu()