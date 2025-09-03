from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from typing import Union, Tuple


def VisualEffect(
    type: int,
    src_id: int,
    dst_id: int,
    tile_type: int,
    src_pos: Tuple[int, int, int],
    dst_pos: Tuple[int, int, int],
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
    packet += (type & 0xFF).to_bytes(1, "big")
    packet += (src_id & 0xFFFFFFFF).to_bytes(4, "big")
    packet += (dst_id & 0xFFFFFFFF).to_bytes(4, "big")
    packet += (tile_type & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[0] & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[1] & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[2] & 0xFF).to_bytes(1, "big")
    packet += (dst_pos[0] & 0xFFFF).to_bytes(2, "big")
    packet += (dst_pos[1] & 0xFFFF).to_bytes(2, "big")
    packet += (dst_pos[2] & 0xFF).to_bytes(1, "big")
    packet += (speed & 0xFF).to_bytes(1, "big")
    packet += (duration & 0xFF).to_bytes(1, "big")
    packet += (unk1 & 0xFF).to_bytes(1, "big")
    packet += (unk2 & 0xFF).to_bytes(1, "big")
    packet += (int(fixed_dir) & 0xFF).to_bytes(1, "big")
    packet += (int(explodes) & 0xFF).to_bytes(1, "big")
    packet += (hue & 0xFFFFFFFF).to_bytes(4, "big")
    packet += (render_mode & 0xFFFFFFFF).to_bytes(4, "big")

    PacketLogger.SendToClient(CList[Byte](packet))


def VisualEffectMissile(
    src: Union[int, Tuple[int, int, int]],
    dst: Union[int, Tuple[int, int, int]],
    tile_type: int,
    speed: int,
    duration: int,
    hue: int = 0,
    render_mode: int = 0,
    fixed_dir: bool = False,
    explodes: bool = False,
) -> None:
    """
    Creates a missile effect from the source to the destination.

    :param src: The ID or position of the source object.
    :param dst: The ID or position of the destination object.
    :param tile_type: The tile ID of the missile.
    :param speed: The speed of the missile.
    :param duration: The number of frames in a single cycle of the animation.
    :param hue: The hue of the missile.
    :param render_mode: The render mode of the missile. (0 to 7)
    """
    src_id = 0
    src_pos = (0, 0, 0)
    dst_id = 0
    dst_pos = (0, 0, 0)

    if isinstance(src, int):
        src_id = src
    else:
        src_pos = src

    if isinstance(dst, int):
        dst_id = dst
    else:
        dst_pos = dst

    VisualEffect(0, src_id, dst_id, tile_type, src_pos, dst_pos, speed, duration, 0, 0, fixed_dir, explodes, hue, render_mode)


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
    VisualEffect(3, src, 0, tile_type, (0, 0, 0), (0, 0, 0), speed, duration, unk1, unk2, False, False, hue, render_mode)


def SoundEffect(sound_model: int):
    pos = Player.Position
    packet = b"\x54"
    packet += b"\x01"
    packet += sound_model.to_bytes(2, "big")
    packet += b"\x00\x00"
    packet += pos.X.to_bytes(2, "big")
    packet += pos.Y.to_bytes(2, "big")
    packet += (pos.Z & 0xFFFF).to_bytes(2, "big")
    PacketLogger.SendToClient(CList[Byte](packet))


# Example usage of the VisualEffect functions
if Player.Connected:
    pos = Player.Position
    x, y, z = pos.X, pos.Y, pos.Z

    SoundEffect(0x29)  # thundr02.wav
    VisualEffectLightning(Player.Serial)
    Misc.Pause(1000)

    SoundEffect(0x101)  # sfx16_l.wav
    VisualEffectMissile((x - 10, y - 10, z + 10), Player.Serial, 14036, 3, 12, 1152, 3)
    VisualEffectMissile((x - 15, y - 10, z + 10), Player.Serial, 14036, 3, 12, 1152, 3)
    VisualEffectMissile((x - 10, y - 15, z + 10), Player.Serial, 14036, 3, 12, 1152, 3)
    Misc.Pause(1500)

    SoundEffect(0x207)  # explode.wav
    VisualEffectStatic((x + 1, y, z), 14120, 13, 253, 2)
    VisualEffectStatic((x, y + 1, z), 14120, 13, 253, 2)
    VisualEffectStatic((x - 1, y, z), 14120, 13, 253, 2)
    VisualEffectStatic((x, y - 1, z), 14120, 13, 253, 2)
    Misc.Pause(750)

    SoundEffect(0x208)  # framstrk.wav
    VisualEffectSelf(Player.Serial, 14089, 30, 1152, 0)
