from AutoComplete import *
from enum import Enum
from typing import Optional
import re
import json
import os


CUR_PATH = os.path.dirname(os.path.abspath(__file__))


class Profession(Enum):
    NoneType = "None"
    Alchemy = "Alchemy"
    Blacksmithing = "Blacksmithing"
    Carpentry = "Carpentry"
    Cartography = "Cartography"
    Cooking = "Cooking"
    Fletching = "Fletching"
    Imbuing = "Imbuing"
    Inscription = "Inscription"
    Tailoring = "Tailoring"
    Tinkering = "Tinkering"


class Material(Enum):
    NoneType = "None"
    DullCopper = "Dull Copper"
    ShadowIron = "Shadow Iron"
    Copper = "Copper"
    Bronze = "Bronze"
    Gold = "Gold"
    Agapite = "Agapite"
    Verite = "Verite"
    Valorite = "Valorite"


class BODSize(Enum):
    Small = "Small"
    Large = "Large"


TOOLS = {
    Profession.Blacksmithing: [0x0FB4, 0x0FB5, 0x0FBB, 0x0FBC, 0x13E3, 0x13E4],
}


with open(CUR_PATH + "/crafting_buttons.json") as f:
    ITEM_BUTTON_MAP = json.load(f)


class BODEntry:
    item: int
    amount_filled: int

    def __init__(
        self,
        item: int = 0,
        amount_filled: int = 0,
    ):
        self.item = item
        self.amount_filled = amount_filled


class BOD:
    profession: Profession
    exceptional: bool
    material: Material
    amount_to_make: int
    size: BODSize
    entries: list[BODEntry]

    def __init__(
        self,
        profession: Profession = Profession.NoneType,
        exceptional: bool = False,
        material: Material = Material.NoneType,
        amount_to_make: int = 0,
        size: BODSize = BODSize.Small,
    ):
        self.profession = profession
        self.exceptional = exceptional
        self.material = material
        self.size = size
        self.amount_to_make = amount_to_make
        self.entries = []


def parse_item(item_id: int) -> Optional["BOD"]:
    item = Items.FindBySerial(item_id)
    if not item:
        return None
    if item.ItemID != 0x2258:
        return None

    res = Items.GetProperties(item_id, 1000)
    if not res:
        return None
    if res[0].Number != 1045151:
        return None

    bod = BOD()
    if item.Color == 0x044E:
        bod.profession = Profession.Blacksmithing

    for line in res:
        args = line.Args.split("\t")
        # Parse size
        if line.Number == 1060654:
            bod.size = BODSize.Small
        elif line.Number == 1060655:
            bod.size = BODSize.Large
        # Parse if exceptional
        elif line.Number == 1045141:
            bod.exceptional = True
            continue
        # Parse amount to make
        elif line.Number == 1060656:
            bod.amount_to_make = int(args[0])
        # Parse entries
        elif line.Number in (1060658, 1060659, 1060660, 1060661, 1060662, 1060663):
            bod.entries.append(BODEntry(item=int(args[0].strip("#")), amount_filled=int(args[1])))
        # Parse material
        elif line.Number == 1045142:
            bod.material = Material.DullCopper
        elif line.Number == 1045143:
            bod.material = Material.ShadowIron
        elif line.Number == 1045144:
            bod.material = Material.Copper
        elif line.Number == 1045145:
            bod.material = Material.Bronze
        elif line.Number == 1045146:
            bod.material = Material.Gold
        elif line.Number == 1045147:
            bod.material = Material.Agapite
        elif line.Number == 1045148:
            bod.material = Material.Verite
        elif line.Number == 1045149:
            bod.material = Material.Valorite

    return bod


class CraftingGump:
    @staticmethod
    def get_gump_by_text(text: str) -> int:
        for gump_id in Gumps.AllGumpIDs():
            for line in Gumps.GetLineList(gump_id, False):
                if text in line:
                    return gump_id
        return 0

    @classmethod
    def wait(cls, profession: Profession, delay: int) -> int:
        text = ""
        if profession == Profession.Blacksmithing:
            text = "<CENTER>BLACKSMITHING MENU</CENTER>"
        else:
            return 0

        Timer.Create("gump-delay", delay)
        while Timer.Check("gump-delay"):
            gump_id = cls.get_gump_by_text(text)
            if gump_id != 0:
                return gump_id
            Misc.Pause(100)
        return 0


def main():
    target = Target.PromptTarget("Choose the item to investigate.", 0x3B2)
    if not Misc.IsItem(target):
        Misc.SendMessage("You must target an item!", 0x21)
        return

    res = parse_item(target)
    if not res:
        Misc.SendMessage("Failed to parse the selected item.", 0x21)
        return

    Misc.SendMessage(f"Profession: {res.profession.value}", 68)
    Misc.SendMessage(f"Size: {res.size.value}", 68)
    Misc.SendMessage(f"Exceptional: {'Yes' if res.exceptional else 'No'}", 68)
    Misc.SendMessage(f"Material: {res.material.value}", 68)
    Misc.SendMessage(f"Amount to make: {res.amount_to_make}", 68)
    for entry in res.entries:
        Misc.SendMessage(f"Item: #{entry.item}", 68)
        Misc.SendMessage(f"Amount filled: {entry.amount_filled}", 68)

    if res.size == BODSize.Small:
        if not res.entries:
            Misc.SendMessage("No entries found in the BOD.", 0x21)
            return
        if res.profession not in TOOLS:
            Misc.SendMessage("No tools available for this profession.", 0x21)
            return
        tools = Items.FindAllByID(TOOLS[res.profession], -1, Player.Backpack.Serial, 3)
        if not tools:
            Misc.SendMessage("No suitable tools found in backpack.", 0x21)
            return
        buttons = ITEM_BUTTON_MAP.get(str(res.entries[0].item), [])
        if not buttons:
            Misc.SendMessage("No button mapping found for the item.", 0x21)
            return

        Items.UseItem(tools[0].Serial)
        for i in range(res.entries[0].amount_filled, res.amount_to_make):
            Misc.SendMessage(f"Making item {i + 1} of {res.amount_to_make}", 68)
            gump_id = CraftingGump.wait(res.profession, 3000)
            if gump_id == 0:
                Misc.SendMessage("Failed to find the crafting gump.", 0x21)
                return
            Gumps.SendAction(gump_id, buttons[0])
            if not Gumps.WaitForGump(gump_id, 1000):
                Misc.SendMessage("Failed to find the gump after action.", 0x21)
                return
            Gumps.SendAction(gump_id, buttons[1])
            Misc.Pause(500)

    Misc.SendMessage("Finished processing the BOD.")


if __name__ == "__main__":
    main()
