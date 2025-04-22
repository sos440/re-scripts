from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte  # type: ignore

import time
from typing import Union, Tuple, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


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


def quest_arrow(show: bool = True, x: int = 0, y: int = 0, serial: int = 0):
    packet = PacketBuilder(0xBA)
    packet.add_byte(int(show))
    packet.add_short(x)
    packet.add_short(y)
    packet.add_int(serial)
    PacketLogger.SendToClient(GenList[Byte](packet.build()))


track_list = {}


while Player.Connected:
    for serial in list(track_list.keys()):
        t = track_list[serial]
        if t <= time.time():
            quest_arrow(False, 0, 0, serial)
            del track_list[serial]
    
    serial = Target.PromptTarget("Choose the target!", 0x47E)
    mob = Mobiles.FindBySerial(serial)
    if mob is None:
        continue

    x, y = mob.Position.X, mob.Position.Y
    if serial in track_list:
        quest_arrow(False, 0, 0, serial)
        del track_list[serial]
    else:
        quest_arrow(True, x, y, serial)
        track_list[serial] = time.time() + 3
    