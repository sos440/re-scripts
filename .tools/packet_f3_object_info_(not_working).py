from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple


def object_info():
    packet = b"\xF3"
    packet += b"\x00\x01"
    packet += b"\x00"  # DataType
    packet += b"\x4F\xFF\xFF\xFF"  # Serial
    packet += b"\x0E\x75"  # ItemID
    packet += b"\x00"  # Facing
    packet += b"\x00\x01"  # Amount
    packet += b"\x00\x01"  # Amount
    packet += Player.Position.X.to_bytes(2, "big")
    packet += Player.Position.Y.to_bytes(2, "big")
    packet += (Player.Position.Z & 0xFF).to_bytes(1, "big")
    packet += b"\x00"  # Layer
    packet += b"\x04\x7E"  # Color
    packet += b"\x20"  # Flags
    PacketLogger.SendToClient(List[Byte](packet))


object_info()