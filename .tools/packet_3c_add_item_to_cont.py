################################################################################
# Core Library
################################################################################


from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte  # type: ignore
from typing import Union, Tuple
import random


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

    def build(self, add_length: bool = False) -> bytes:
        if add_length:
            packet_len = len(self.packet) + 3
            packet = packet_len.to_bytes(2, "big") + self.packet
        else:
            packet = self.packet
        return bytes(self.header.to_bytes(1, "big") + packet)


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
    """
    This function sends a packet to the client to render an object in the game world.
    It is used to create a visual representation of an object, such as a corpse or item.

    Parameters
    ----------
    :param serial: The serial number of the object to render.
    :param itemid: The item ID (graphic) of the object to render.
    :param x: The X coordinate of the object's position in the game world.
    :param y: The Y coordinate of the object's position in the game world.
    :param z: The Z coordinate (height) of the object's position in the game world.
    :param amount: The amount of the item (default is 1). This is also used for the body ID of corpses.
    :param color: The color of the object (default is 0). This is used for the hue of the item.
    :param flag: The flag for the object (default is 0). Consult any UO packet guide for details.
    :param facing: The facing direction of the object (default is 0).
    :param itemid_inc: The item ID increment (default is 0). I guess this is for animation or graphic alias.
    :param data_type: The type of data being sent (default is 0). 0 for items, 2 for multis.
    """
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

    PacketLogger.SendToClient(GenList[Byte](packet.build()))  # type: ignore


def build_packet_24(cont_serial: int, cont_id1: int, cont_id2: int) -> bytes:
    packet = PacketBuilder(0x24)
    packet.add_int(cont_serial)
    packet.add_short(cont_id1)
    packet.add_short(cont_id2)
    PacketLogger.SendToClient(GenList[Byte](packet.build()))


def build_packet_25(
    cont_serial: int,
    serial: int,
    itemid: int,
    x: int,
    y: int,
    amount: int = 1,
    color: int = 0,
    itemid_inc: int = 0,
):

    packet = PacketBuilder(0x25)
    packet.add_int(serial)
    packet.add_short(itemid)
    packet.add_byte(itemid_inc)
    packet.add_short(amount)
    packet.add_short(x)
    packet.add_short(y)
    packet.add_byte(0)
    packet.add_int(cont_serial)
    packet.add_short(color)

    PacketLogger.SendToClient(GenList[Byte](packet.build()))  # type: ignore



def build_packet_3c(contents, cont_serial: int) -> bytes:
    packet = PacketBuilder(0x3C)
    packet.add_short(len(contents))
    for i, item in enumerate(contents):
        x = random.randint(0, 250)
        y = random.randint(0, 250)
        packet.add_int(item.Serial)
        packet.add_short(item.ItemID)
        packet.add_byte(0)
        packet.add_short(item.Amount)
        packet.add_short(x)
        packet.add_short(y)
        packet.add_byte(i)
        packet.add_int(cont_serial)
        packet.add_short(item.Color)
    PacketLogger.SendToClient(GenList[Byte](packet.build(True)))


################################################################################
# Test Code
################################################################################


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
    serial = Target.PromptTarget("Choose the target.")
    
    if Misc.IsItem(serial):
        item = Items.FindBySerial(serial)
        if item is None:
            return
        if not item.IsContainer:
            return
        if not (item.ContainerOpened or Items.WaitForContents(serial, 1000)):
            return
        contents = item.Contains
    elif Misc.IsMobile(serial):
        mob = Mobiles.FindBySerial(serial)
        if mob is None:
            return
        contents = get_equipped_items(mob)

    fake_serial = 0x4FFFFFFF
    build_packet_25(
        Player.Serial,
        serial=fake_serial,
        itemid=0x09AB,
        x=0,
        y=0,
        amount=1,
        color=1153,
    )
    packet = build_packet_24(fake_serial, 0x4A, 0x7D)
    packet = build_packet_3c(contents, fake_serial)


Misc.SendMessage(f"Test Initiated", 0x47E)
test()