def dist_to_topcont(serial):
    """
    Calculate the distance between the player and the top container of the object with the provided serial.
    """
    item = Items.FindBySerial(serial)
    mob = None
    
    while item is not None and not item.OnGround:
        serial = item.RootContainer
        item = Items.FindBySerial(item.RootContainer)

    player = Mobiles.FindBySerial(Player.Serial)
    if item is None:
        mob = Mobiles.FindBySerial(serial)
        if mob is None:
            return None
        else:
            return mob.DistanceTo(player)
    else:
        return item.DistanceTo(player)


def inspect():
    target = Target.PromptTarget("Select the target.", 0x47E)
    dist = dist_to_topcont(target)
    if dist is not None:
        Misc.SendMessage(f"Distance: {dist}", 0x47E)


while True:
    inspect()