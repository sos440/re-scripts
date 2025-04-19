from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple


def open_paperdoll(serial: int, title: str):
    packet = b"\x88"
    packet += serial.to_bytes(4, "big")
    packet += title.encode("ascii").ljust(60, b"\x00")
    packet += b"\x02"
    PacketLogger.SendToClient(List[Byte](packet))


while Player.Connected:
    serial = Target.PromptTarget("Choose the target!", 0x47E)
    mob = Mobiles.FindBySerial(serial)
    if mob is None:
        continue
    open_paperdoll(mob.Serial, mob.Name)
    break
