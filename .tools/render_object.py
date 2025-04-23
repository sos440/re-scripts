# The code below is purely for type-hinting purposes and is not executed.
# You can safely ignore or remove it if you are not using type hints.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


################################################################################
# Core Library
################################################################################


from System.Collections.Generic import List as GenList  # type: ignore
from System import Byte  # type: ignore


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

    def build(self) -> bytes:
        return bytes(self.header.to_bytes(1, "big") + self.packet)


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


################################################################################
# Test Code
################################################################################


if __name__ == "__main__":
    # This is a test code block that will only run if this script is executed directly.
    # It will not run if this script is imported as a module in another script.

    def test():
        serial = Target.PromptTarget("Choose an item on the ground.", 0x47E)
        obj = Items.FindBySerial(serial)
        if obj is None:
            Misc.SendMessage("That doens't seem like an item.", 0x21)
            return
        if not obj.OnGround:
            Misc.SendMessage("Please target an item on the ground.", 0x21)
            return

        Misc.SendMessage(f"I'll turn \"{obj.Name}\" into a corpse!", 0x47E)
        render_object(
            serial=obj.Serial,
            itemid=0x2006,
            x=obj.Position.X,
            y=obj.Position.Y,
            z=obj.Position.Z,
            amount=0x190,
            color=obj.Color,
        )

    test()
