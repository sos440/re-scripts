from AutoComplete import *
import os
import sys
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import modules.match as match


def test_target():
    serial = Target.PromptTarget("Select an item to test presets against.", 0x3B2)
    if serial == -1:
        return False

    item = Items.FindBySerial(serial)
    if item is None:
        Misc.SendMessage("Item not found.", 0x21)
        return True

    for preset_key, preset in match.PRESETS.items():
        if preset.test(item):
            Misc.SendMessage(f"Item matches preset: {preset_key}", 68)
    return True


if __name__ == "__main__":
    while test_target():
        ...