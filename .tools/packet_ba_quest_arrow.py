from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple


def quest_arrow(mob, active: bool = True):
    packet = b"\xBA"
    packet += b"\x01" if active else b"\x00"
    packet += mob.Position.X.to_bytes(2, "big")
    packet += mob.Position.Y.to_bytes(2, "big")
    packet += mob.Serial.to_bytes(4, "big")
    PacketLogger.SendToClient(List[Byte](packet))


while Player.Connected:
    serial = Target.PromptTarget("Choose the target!", 0x47E)
    mob = Mobiles.FindBySerial(serial)
    if mob is None:
        continue
    quest_arrow(mob)
    Misc.Pause(3000)
    quest_arrow(mob, False)
    break
