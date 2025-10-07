################################################################################
# User Setting
################################################################################

# Automatically make the plant decorative when possible
AUTO_DECORATIVE = False

# Delay between actions in milliseconds
ACTION_DELAY = 1000


################################################################################
# Script Starts Here
################################################################################

from AutoComplete import *
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum
import re


COLORS = [0, 33, 1645, 43, 1135, 56, 2213, 66, 1435, 5, 1341, 16, 13, 1166, 1173, 1158, 1161, 1153, 1109]
PLANTS = [10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467, 3273, 6810, 3204, 6815, 3265, 3326, 3215, 3272, 3214, 3365, 3255, 3262, 3521, 3323, 3512, 6817, 9324, 19340, 3230, 3203, 3206, 3208, 3220, 3211, 3237, 3239, 3223, 3231, 3238, 3228, 3377, 3332, 3241, 3372, 3366, 3367]


class GardeningGumps:
    class States(Enum):
        NOT_FOUND = 0
        ACTION_LEFT = 1
        COMPLETED = 2
        INTERRUPT = 3
        INCOMPLETE = 4

    @staticmethod
    def is_main(gd: Gumps.GumpData) -> Optional[Dict[str, Any]]:
        if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ tilepic 45 45 3311 }"):
            return
        lines = list(map(lambda s: s.strip("{} "), gd.gumpLayout.split("}{")))
        match = re.search(r"tilepichue \d+ \d+ (\d+) (\d+)", lines[5])
        plant = None
        color = None
        if match is not None:
            plant = int(match.group(1))
            color = int(match.group(2))
        match = re.search(r"tilepic \d+ \d+ (\d+)", lines[5])
        if match is not None:
            plant = int(match.group(1))
            color = 0
        if plant is None or color is None:
            return
        return {"id": gd.gumpId, "plant": plant, "color": color, "day": int(gd.gumpData[21])}

    @staticmethod
    def is_reproduction(gd: Gumps.GumpData) -> Optional[Dict[str, Any]]:
        if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ gumppic 60 90 3607 }"):
            return
        if len(gd.gumpData) < 6 or gd.gumpData[5] != "Reproduction":
            return

        if gd.gumpData[6] == "3169" and gd.gumpData[7] == "/":
            text_res = gd.gumpData[11]
            text_seed = gd.gumpData[13]
        else:
            text_res = gd.gumpData[9]
            text_seed = gd.gumpData[11]
        match_res = re.search(r"(\d+)/(\d+)", text_res)
        match_seed = re.search(r"(\d+)/(\d+)", text_seed)

        res_left = 0
        res_max = 8
        if text_res == "X":
            res_max = 0
        elif match_res is None:
            print(f"Failed to parse the resource: {text_res}")
            return
        else:
            res_left = int(match_res.group(1))
            res_max = int(match_res.group(2))

        seed_left = 0
        seed_max = 8
        if text_seed == "X":
            seed_max = 0
        elif match_seed is None:
            print(f"Failed to parse the seed: {text_seed}")
            return
        else:
            seed_left = int(match_seed.group(1))
            seed_max = int(match_seed.group(2))

        return {"id": gd.gumpId, "res-left": res_left, "res-max": res_max, "seed-left": seed_left, "seed-max": seed_max}

    @staticmethod
    def is_confirm(gd: Gumps.GumpData) -> Optional[Dict[str, Any]]:
        if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ tilepic 25 45 3307 }"):
            return
        if len(gd.gumpData) != 7 or gd.gumpData[4] != "Set plant":
            return

        return {"id": gd.gumpId}


def handle_gardening_gumps(plant: int, color: int, auto_deco: bool = False) -> GardeningGumps.States:
    """
    Interact with gardening gumps.
    """
    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        if gd is None:
            continue

        match_main = GardeningGumps.is_main(gd)
        if match_main is not None:
            plant_matched = (match_main["plant"] == plant)
            color_matched = (match_main["color"] == color)
            if match_main["plant"] == 3274:
                plant_matched = plant in (3323, 3326)  # Special case for cypress
            if not plant_matched or not color_matched:
                Misc.SendMessage("This is not the gump for the selected plant, closing it.", 33)
                Gumps.SendAction(match_main["id"], 0)
                return GardeningGumps.States.COMPLETED
            # Open the reproduction menu
            Gumps.SendAction(match_main["id"], 1)
            return GardeningGumps.States.ACTION_LEFT

        match_repro = GardeningGumps.is_reproduction(gd)
        if match_repro is not None:
            if Journal.Search("You attempt to gather as many"):
                Gumps.SendAction(match_repro["id"], 0)
                return GardeningGumps.States.INTERRUPT
            if match_repro["res-left"] > 0:
                # Harvest resources
                Misc.SendMessage("Trying to collect resources.", 68)
                Gumps.SendAction(match_repro["id"], 7)
                return GardeningGumps.States.ACTION_LEFT
            if match_repro["seed-left"] > 0:
                # Harvest seeds
                Misc.SendMessage("Trying to collect seeds.", 68)
                Gumps.SendAction(match_repro["id"], 8)
                return GardeningGumps.States.ACTION_LEFT
            if match_repro["res-max"] == 0 and match_repro["seed-max"] == 0:
                if auto_deco:
                    # Make this decorative
                    Misc.SendMessage("Trying to make it decorative.", 68)
                    Gumps.SendAction(match_repro["id"], 2)
                    return GardeningGumps.States.ACTION_LEFT
                else:
                    Misc.SendMessage("The plant is now exhausted.", 68)
                    Gumps.SendAction(match_repro["id"], 0)
                    return GardeningGumps.States.COMPLETED
            # You harvested everything available but the plant can still produce more
            Misc.SendMessage("Your plant has still can produce more, leaving it.", 68)
            Gumps.SendAction(match_repro["id"], 0)
            return GardeningGumps.States.COMPLETED

        match_confirm = GardeningGumps.is_confirm(gd)
        if match_confirm is not None:
            # The plant is now decorative, everything done!
            Gumps.SendAction(match_confirm["id"], 3)
            return GardeningGumps.States.COMPLETED

    return GardeningGumps.States.NOT_FOUND


def tend_plant(serial, auto_deco: bool = False):
    """
    Tender the plant through gumps with the given serial number.
    """
    item = Items.FindBySerial(serial)
    if item is None:
        return GardeningGumps.States.NOT_FOUND
    if Player.DistanceTo(item) > 3:
        return GardeningGumps.States.NOT_FOUND

    Items.UseItem(item)
    Timer.Create("plant-used", ACTION_DELAY)
    Timer.Create("gardening", 1000)
    Journal.Clear()
    while Timer.Check("gardening"):
        state = handle_gardening_gumps(item.ItemID, item.Color, auto_deco)
        if state == GardeningGumps.States.NOT_FOUND:
            Misc.Pause(100)
            continue
        if state == GardeningGumps.States.ACTION_LEFT:
            Misc.Pause(100)
            Timer.Create("gardening", 1000)
            continue
        if state == GardeningGumps.States.COMPLETED:
            return state
        if state == GardeningGumps.States.INTERRUPT:
            return state
    Misc.SendMessage("Taking too long to handle the gardening gump, skipping this plant.", 33)
    return GardeningGumps.States.INCOMPLETE


GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
SHORTCUT_GUMP_ID = hash("HarvestGump") & 0xFFFFFFFF


def ask_to_harvest(harvesting: bool = False):
    """
    A minimized gump with a button to run.
    """
    Gumps.CloseGump(SHORTCUT_GUMP_ID)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 90, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 90)
    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Harvest Helper"), False, False)
    if harvesting:
        Gumps.AddButton(gd, 10, 30, 40297, 40298, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 33, 126, 18, GUMP_WT.format(text="Stop Harvesting"), False, False)
    else:
        Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 33, 126, 18, GUMP_WT.format(text="Start Harvesting"), False, False)
    Gumps.AddButton(gd, 10, 55, 40021, 40031, 2, 1, 0)
    Gumps.AddHtml(gd, 10, 58, 126, 18, GUMP_WT.format(text="Harvest Individually"), False, False)
    Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def parse_response(delay: int = 500) -> int:
    if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, delay):
        return 0
    gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
    if gd is None:
        return 0
    return gd.buttonid


if __name__ == "__main__":
    plant_done = set()

    while Player.Connected:
        ask_to_harvest()
        response = 0
        while not response:
            response = parse_response()
            continue

        # Find all plants to tend
        if response == 1:
            find_next = True
            while find_next:
                find_next = False
                for plant in Items.FindAllByID(PLANTS, -1, -1, 4):
                    if plant.Serial in plant_done:
                        continue
                    if plant.Color not in COLORS:
                        continue
                    # Tend the plant
                    state = tend_plant(plant.Serial, AUTO_DECORATIVE)
                    if state == GardeningGumps.States.INTERRUPT:
                        break
                    if state in (GardeningGumps.States.COMPLETED, GardeningGumps.States.INCOMPLETE):
                        find_next = True
                        plant_done.add(plant.Serial)
                        break
                    Misc.Pause(Timer.Remaining("plant-used"))
        elif response == 2:
            while True:
                serial = Target.PromptTarget("Choose the plant to tend.")
                if serial == -1:
                    break
                plant = Items.FindBySerial(serial)
                if plant is None:
                    continue
                if plant.Serial in plant_done:
                    continue
                if plant.ItemID not in PLANTS:
                    continue
                if plant.Color not in COLORS:
                    continue
                state = tend_plant(plant.Serial, True)
                if state in (GardeningGumps.States.COMPLETED, GardeningGumps.States.INCOMPLETE):
                    plant_done.add(plant.Serial)