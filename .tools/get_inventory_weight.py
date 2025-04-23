################################################################################
# Core Library
################################################################################


import re


def get_invengory_weight(serial):
    """
    This function returns the weight of the contents of the container with the provided serial.
    If not serial is provided, it defaults to the player's backpack.

    When it fails to parse the content weight, it will return None.

    Arguments
    ----------
    `serial` : The serial of the container to check. If not provided, it defaults to the player's backpack.

    Returns
    -------
    `(weight, max_weight) or None` : A tuple containing the current weight and the maximum weight of the container. If the container is not found or the properties cannot be parsed, it returns None.
    """
    # Sanitize the argument
    if not (Player or Player.Backpack):
        return None
    if not serial:
        serial = Player.Backpack.Serial

    # Checks the validity of the target
    obj = Items.FindBySerial(serial)
    if obj is None:
        return None
    if not obj.IsContainer:
        return None

    Items.WaitForProps(serial, 1000)
    # Scans the property and reads out the content weight
    for line in Items.GetPropStringList(serial):
        line = line.lower()
        # If the maximum weight is also provided, match it
        res = re.search(r"^contents: (\d+)/(\d+) items, (\d+)/(\d+) stones", line)
        if res is not None:
            return int(res.group(3)), int(res.group(4))
        # If no maximum weight is provided, assume it's 400
        res = re.search(r"^contents: (\d+)/(\d+) items, (\d+) stones", line)
        if res is not None:
            return int(res.group(3)), 400
    return None


################################################################################
# Test Code
################################################################################


if __name__ == "__main__":

    def test():
        serial = Target.PromptTarget("Choose the container to check.", 0x47E)
        if serial == 0:
            Misc.SendMessage("Cancelled targetting.", 88)
            return
        obj = Items.FindBySerial(serial)
        if obj is None:
            Misc.SendMessage("Invalid target!", 33)
            return

        res = get_invengory_weight(serial)
        if res is None:
            Misc.SendMessage("Failed to parse the properties!", 33)
            return

        weight, max_weight = res
        Misc.SendMessage(f"Content weight: {weight}/{max_weight}", 88)

    if Player.Connected:
        test()
