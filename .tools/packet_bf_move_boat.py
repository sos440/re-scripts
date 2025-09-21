from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple


def move_boat(dir: int, speed: int = 2):
    assert dir in (0, 1, 2, 3, 4, 5, 6, 7)
    assert speed in (0, 1, 2)
    packet = b"\xBF"
    packet += b"\x00\x0C"  # length (12)
    packet += b"\x00\x33"  # length (12)
    packet += Player.Serial.to_bytes(4, "big")
    packet += dir.to_bytes(1, "big")
    packet += dir.to_bytes(1, "big")
    packet += speed.to_bytes(1, "big")
    PacketLogger.SendToServer(List[Byte](packet))


def stop_boat():
    move_boat(0, 0)


move_boat(0)
Misc.Pause(1000)
stop_boat()