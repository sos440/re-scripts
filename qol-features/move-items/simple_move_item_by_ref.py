import sys
from typing import Optional


def main():
    serial = Target.PromptTarget("Select the refernce item.", 0x3B2)
    if serial == 0:
        Misc.SendMessage("No target selected.", 0x3B2)
        quit()
    item_ref = Items.FindBySerial(serial)
    if item_ref is None:
        Misc.SendMessage("Failed to find the item.", 0x21)
        quit()
    
    serial = Target.PromptTarget("Select the container to move to.", 0x3B2)
    if serial == 0:
        Misc.SendMessage("No target selected.", 0x3B2)
        quit()
    cont = Items.FindBySerial(serial)
    if cont is None:
        Misc.SendMessage("Failed to find the item.", 0x21)
        quit()
    if cont.RootContainer != Player.Backpack.Serial and Player.DistanceTo(cont) > 2:
        Misc.SendMessage("The target is too far.", 0x21)
        quit()
    
    item_list = Items.FindAllByID(item_ref.ItemID, -1, item_ref.Container, 0)
    n = len(item_list)
    for i, item in enumerate(item_list):
        Misc.SendMessage(f"Moving ({(i+1)}/{n}): {item.Name}", 68)
        Items.Move(item.Serial, cont.Serial, 1)
        Misc.Pause(1000)
    
    Misc.SendMessage("Done", 68)


if __name__ == "__main__":
    main()