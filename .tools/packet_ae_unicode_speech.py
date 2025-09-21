from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple


def unicode_speech(serial: int, msg: str, hue: int = 0x3B2, type: int = 0, font: int = 3):
    model = 0
    name = ""
    if Misc.IsMobile(serial):
        mob = Mobiles.FindBySerial(serial)
        if mob is not None:
            model = mob.Graphics
            name = mob.Name
    elif Misc.IsItem(serial):
        item = Items.FindBySerial(serial)
        if item is not None:
            model = item.ItemID
            name = item.Name
    
    packet_body = b""
    packet_body += serial.to_bytes(4, "big")
    packet_body += model.to_bytes(2, "big")
    packet_body += type.to_bytes(1, "big")
    packet_body += hue.to_bytes(2, "big")
    packet_body += font.to_bytes(2, "big")
    packet_body += b"\x45\x4E\x55\x00"  # ENU
    packet_body += name.encode("ascii").ljust(30, b"\x00")
    packet_body += msg.encode("utf-16be")
    packet_body += b"\x00\x00"  # Null-terminating
    
    packet_len = len(packet_body) + 3
    packet = b"\xAE"
    packet += packet_len.to_bytes(2, "big")
    packet += packet_body
    PacketLogger.SendToClient(List[Byte](packet))


while Player.Connected:
    serial = Target.PromptTarget("Choose the target!", 0x47E)
    unicode_speech(serial, "Hello, world!", 1153)
    break
