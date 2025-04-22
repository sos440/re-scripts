from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte  # type: ignore
from typing import Union, Tuple, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


DIR_MAP = {
    "North": 0,
    "Right": 1,
    "East": 2,
    "Down": 3,
    "South": 4,
    "Left": 5,
    "West": 6,
    "Up": 7,
}


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

    def build(self, include_len: bool = False) -> bytes:
        packet = self.packet
        if include_len:
            calc_len = 1 + 2 + len(self.packet)
            packet = bytearray(calc_len.to_bytes(2, "big")) + packet
        return bytes(self.header.to_bytes(1, "big") + packet)


# 78    : Command
# 00 17 : Length
# 06 BA 03 75 : Serial
# 01 2E : Body
# 03 BA : X
# 01 61 : Y
# A8    : Z
# 06    : Direction
# 00 00 : Color
# 00    : Flags
# 03    : Notoriety
# 00 00 00 00 : Layers terminator

def render_object(mob):
    packet = PacketBuilder(0x78)
    
    packet.add_int(mob.Serial)
    packet.add_short(0x191)
    packet.add_short(mob.Position.X)
    packet.add_short(mob.Position.Y)
    packet.add_byte(mob.Position.Z)
    packet.add_byte(DIR_MAP.get(mob.Direction, 0))
    packet.add_short(mob.Hue)
    packet.add_byte(0)
    packet.add_byte(mob.Notoriety)
    packet.add_int(0)
    
    packet_built = packet.build(True)
    print(" ".join(f"{v:02X}" for v in packet_built))
    
    PacketLogger.SendToClient(GenList[Byte](packet_built))


def test():
    serial = Target.PromptTarget("Choose the target.", 0x47E)
    obj = Mobiles.FindBySerial(serial)
    if obj is None:
        return

    Misc.SendMessage(f"Transmogging: {obj.Name}")
    render_object(obj)
    Misc.SendMessage("Done")


test()
