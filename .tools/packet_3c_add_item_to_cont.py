from System.Collections.Generic import List
from System import Byte
from typing import Union, Tuple
import random


def build_packet_24(cont_serial: int, cont_id1: int, cont_id2: int) -> bytes:
    packet = b"\x24"
    packet += cont_serial.to_bytes(4, "big")
    packet += cont_id1.to_bytes(2, "big")
    packet += cont_id2.to_bytes(2, "big")
    return packet


def build_packet_3c(contents, cont_serial: int) -> bytes:
    packet_len = 5 + len(contents) * 20
    
    # Header
    packet = b"\x3C"
    packet += packet_len.to_bytes(2, "big")
    packet += len(contents).to_bytes(2, "big")
    
    for i, item in enumerate(contents):
        x = random.randint(0, 250)
        y = random.randint(0, 250)
        packet += item.Serial.to_bytes(4, "big")
        packet += item.ItemID.to_bytes(2, "big")
        packet += b"\x00"
        packet += item.Amount.to_bytes(2, "big")
        packet += x.to_bytes(2, "big")
        packet += y.to_bytes(2, "big")
        packet += i.to_bytes(1, "big")
        packet += cont_serial.to_bytes(4, "big")
        packet += item.Color.to_bytes(2, "big")
    
    return packet


def get_equipped_items(mob):
    layers = [
        "RightHand",
        "LeftHand",
        "Shoes",
        "Pants",
        "Shirt",
        "Head",
        "Gloves",
        "Ring",
        "Neck",
        "Waist",
        "InnerTorso",
        "Bracelet",
        "MiddleTorso",
        "Earrings",
        "Arms",
        "Cloak",
        "OuterTorso",
        "OuterLegs",
        "InnerLegs",
        "Talisman",
    ]
    contents = []
    for layer in layers:
        item = mob.GetItemOnLayer(layer)
        if item is not None:
            contents.append(item)
    return contents


def test():
    backpack = Player.Backpack.Serial
    serial = Target.PromptTarget("Choose the target.")
    mob = Mobiles.FindBySerial(serial)
    if mob is None:
        return
    
    contents = get_equipped_items(mob)
    
    packet = build_packet_24(backpack, 0x3C, 0x7D)
    PacketLogger.SendToClient(List[Byte](packet))
    
    packet = build_packet_3c(contents, backpack)
    PacketLogger.SendToClient(List[Byte](packet))


Misc.SendMessage(f"Test Initiated", 0x47E)
test()