from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple


def test(sound_model: int):
    Misc.SendMessage(f"Playing sound: {sound_model}", 0x47E)
    pos = Player.Position
    packet = b"\x54"
    packet += b"\x01"
    packet += sound_model.to_bytes(2, "big")
    packet += b"\x00\x00"
    packet += pos.X.to_bytes(2, "big")
    packet += pos.Y.to_bytes(2, "big")
    packet += (pos.Z & 0xFFFF).to_bytes(2, "big")
    PacketLogger.SendToClient(List[Byte](packet))


Misc.Pause(1000)
test(0x29)
