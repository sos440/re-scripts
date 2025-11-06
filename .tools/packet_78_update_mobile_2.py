from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from typing import Optional


################################################################################
# Helper Functions
################################################################################


DIR_TO_NUM = {
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

    def build(self, prefix: Optional[bytes] = None) -> bytes:
        if prefix is None:
            prefix = bytes()
        return bytes(self.header.to_bytes(1, "big") + prefix + self.packet)


def render_mobile(
    serial: int,
    body: int,
    x: int,
    y: int,
    z: int,
    facing: int = 0,
    color: int = 0,
    flag: int = 0,
    notoriety: int = 1,
):
    packet = PacketBuilder(0x78)
    packet.add_short(24)
    packet.add_int(serial)
    packet.add_short(body)
    packet.add_short(x)
    packet.add_short(y)
    packet.add_byte(z)
    packet.add_byte(facing)
    packet.add_short(color)
    packet.add_byte(flag)
    packet.add_byte(notoriety)
    packet.add_bytes(b"\x00\x00\x00\x00\x00")

    PacketLogger.SendToClient(CList[Byte](packet.build()))


def test():
    serial = Target.PromptTarget("Choose the target to re-render.", 0x3B2)
    if serial == -1:
        return
    mobile = Mobiles.FindBySerial(serial)
    if mobile is None:
        Misc.SendMessage("Invalid target.", 33)
        return
    pos = mobile.Position
    render_mobile(
        mobile.Serial,
        mobile.Graphics,
        pos.X,
        pos.Y,
        pos.Z,
        DIR_TO_NUM.get(mobile.Direction, 0),
        1153,
        0,
        mobile.Notoriety,
    )


while Player.Connected:
    test()
