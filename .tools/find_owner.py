from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte, Int32  # type: ignore
from typing import List, Optional, Union


def find_owner(item: "Item") -> Optional[Union["Item", "Mobile"]]:
    while True:
        cont_serial = item.RootContainer
        if cont_serial is None:
            return item
        if Misc.IsItem(cont_serial):
            item = Items.FindBySerial(cont_serial)
            continue
        if Misc.IsMobile(cont_serial):
            return Mobiles.FindBySerial(cont_serial)


def main():
    filter = Items.Filter()
    filter.Enabled = True
    filter.Graphics = CList[Int32]([0x0E21])
    filter.OnGround = False
    bandages = Items.ApplyFilter(filter)
    for bandage in bandages:
        owner = find_owner(bandage)
        if owner is None:
            print(f"Could not find the owner of {bandage.Name}")
        else:
            print(f"Owner of {bandage.Name} is {owner.Name}")


main()