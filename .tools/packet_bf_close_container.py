from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore


def close_container(serial: int):
    packet = b"\xbf"  # command
    packet += b"\x00\x0d"  # length
    packet += b"\x00\x16"  # subcommand
    packet += b"\x00\x00\x00\x0c"  # close container
    packet += serial.to_bytes(4, "big")
    PacketLogger.SendToClient(CList[Byte](packet))


while True:
    serial = Target.PromptTarget("Target the container to close.", 0x3B2)
    if serial != -1:
        close_container(serial)
