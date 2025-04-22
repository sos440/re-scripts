from enum import Enum
from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte  # type: ignore
from typing import Union, Optional, Any, Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


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


if __name__ == "__main__":
    # Example usage of the VisualEffect functions
    if Player.Connected:
        x, y, z = Player.Position.X, Player.Position.Y, Player.Position.Z
        for count in range(3, 0, -1):
            Misc.SendMessage(f"Countdown: {count}", 0x47E)
            Misc.Pause(1000)

        Effects.SoundEffect(0x29)  # thundr02.wav
        Effects.Lightning(Player.Serial)
        Misc.Pause(1000)

        Effects.SoundEffect(0x101)  # sfx16_l.wav
        Effects.Moving((x - 10, y - 10, z + 10), Player, 14036, 3, 12, 1152, Effects.BlendMode.ScreenMore)
        Effects.Moving((x - 15, y - 10, z + 10), Player, 14036, 3, 12, 1152, Effects.BlendMode.ScreenMore)
        Effects.Moving((x - 10, y - 15, z + 10), Player, 14036, 3, 12, 1152, Effects.BlendMode.ScreenMore)
        Misc.Pause(1500)

        Effects.SoundEffect(0x207)  # explode.wav
        Effects.AtFixedPos((x + 1, y, z), 14120, 13, 253, Effects.BlendMode.Screen)
        Effects.AtFixedPos((x, y + 1, z), 14120, 13, 253, Effects.BlendMode.Screen)
        Effects.AtFixedPos((x - 1, y, z), 14120, 13, 253, Effects.BlendMode.Screen)
        Effects.AtFixedPos((x, y - 1, z), 14120, 13, 253, Effects.BlendMode.Screen)
        Misc.Pause(750)

        Effects.SoundEffect(0x208)  # framstrk.wav
        Effects.OnFixedObj(Player, 14089, 30, 1152)
