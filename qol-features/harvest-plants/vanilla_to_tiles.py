from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from typing import List, Dict, Tuple, Any, Optional, Callable, Union


################################################################################
# Helper Functions
################################################################################


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


def render_object(
    serial: int,
    itemid: int,
    x: int,
    y: int,
    z: int,
    amount: int = 1,
    color: int = 0,
    flag: int = 0,
    facing: int = 0,
    itemid_inc: int = 0,
    data_type: int = 0,
):
    assert data_type in [0, 2], "Invalid data type. Must be 0 or 2."

    packet = PacketBuilder(0xF3)
    packet.add_short(0x0001)
    packet.add_byte(data_type)
    packet.add_int(serial)
    packet.add_short(itemid)
    packet.add_byte(itemid_inc)
    packet.add_short(amount)
    packet.add_short(amount)
    packet.add_short(x)
    packet.add_short(y)
    packet.add_byte(z)
    packet.add_byte(facing)
    packet.add_short(color)
    packet.add_byte(flag)
    packet.add_bytes(b"\x00\x00")

    PacketLogger.SendToClient(CList[Byte](packet.build()))


PLANTS = [10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467, 3273, 6810, 3204, 6815, 3265, 3326, 3215, 3272, 3214, 3365, 3255, 3262, 3521, 3323, 3512, 6817, 9324, 19340, 3230, 3203, 3206, 3208, 3220, 3211, 3237, 3239, 3223, 3231, 3238, 3228, 3377, 3332, 3241, 3372, 3366, 3367]

for plant in Items.FindAllByID(PLANTS, -1, -1, 64):
    pos = plant.Position
    render_object(plant.Serial, 0x0EEF, pos.X, pos.Y, pos.Z)

# Vanilla to spellbook
for plant in Items.FindAllByID(0x4B8C, 0, -1, 64):
    pos = plant.Position
    render_object(plant.Serial, 0x0EFA, pos.X, pos.Y, pos.Z)

# Sugar cane to Chivalry book
for plant in Items.FindAllByID(0x246C, 0, -1, 64):
    pos = plant.Position
    render_object(plant.Serial, 0x2252, pos.X, pos.Y, pos.Z)

# Cocoa tree to runebook
for plant in Items.FindAllByID(0x0C9E, 0, -1, 64):
    pos = plant.Position
    render_object(plant.Serial, 0x9C16, pos.X, pos.Y, pos.Z)
