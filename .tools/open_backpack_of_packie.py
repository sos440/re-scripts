from System.Collections.Generic import List
from System import Byte, Int32


def get_backpack_of(serial):
    """
    Obtain the Item instance of the backpack of the specified mob.
    
    Args
    ----
        serial (int): The serial of the mob having a backpack.

    Return
    ------
        pack (Optional[Item]): Returns the Item instance of the backpack if found, otherwise Nothing.
    """
    if not Misc.IsMobile(serial):
        return None
    
    filter = Items.Filter()
    filter.Enabled = True
    filter.Graphics = List[Int32]([0x0E75])
    
    packs = Items.ApplyFilter(filter)
    for pack in packs:
        if pack.RootContainer == serial:
            return pack
    
    return None


def test():
    """
    This is a test script.
    """
    if not Player.Connected:
        return
    
    # Prompt a target cursor and obtain the backpack of the target.
    target = Target.PromptTarget("Target the packie", 0x47E)
    pack = get_backpack_of(target)
    
    # Try to open the backpack if found.
    if pack is None:
        Misc.SendMessage("Nothing found.")
    else:
        Items.WaitForContents(pack.Serial, 1000)


test()