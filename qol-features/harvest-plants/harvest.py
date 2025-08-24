from AutoComplete import *
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum
import re


class GardeningGumps:
    class States(Enum):
        NOT_FOUND = 0
        ACTION_LEFT = 1
        COMPLETED = 2
        INTERRUPT = 3

    @staticmethod
    def is_main(gd: Gumps.GumpData) -> Optional[Dict[str, Any]]:
        if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ tilepic 45 45 3311 }"):
            return
        if len(gd.gumpData) < 21:
            return
        match = re.search(r"tilepichue 130 96 (\d+) (\d+)", gd.gumpLayout)
        if match is None:
            return
        return {"id": gd.gumpId, "plant": int(match.group(1)), "color": int(match.group(2)), "day": int(gd.gumpData[21])}

    @staticmethod
    def is_reproduction(gd: Gumps.GumpData) -> Optional[Dict[str, Any]]:
        if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ gumppic 60 90 3607 }"):
            return
        if len(gd.gumpData) != 17 or gd.gumpData[5] != "Reproduction":
            return

        text_res = gd.gumpData[11]
        text_seed = gd.gumpData[13]
        match_res = re.search(r"(\d+)/(\d+)", text_res)
        match_seed = re.search(r"(\d+)/(\d+)", text_seed)

        res_left = 0
        res_max = 0
        if text_res == "X":
            res_max = 8
        elif match_res is None:
            return
        else:
            res_left = int(match_res.group(1))
            res_max = int(match_res.group(2))

        seed_left = 0
        seed_max = 0
        if text_seed == "X":
            seed_max = 8
        elif match_seed is None:
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


def handle_gardening_gumps() -> GardeningGumps.States:
    """
    Interact with gardening gumps.
    """
    Journal.Clear()
    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        if gd is None:
            continue

        match_main = GardeningGumps.is_main(gd)
        if match_main is not None:
            # Open the reproduction menu
            Gumps.SendAction(match_main["id"], 1)
            return GardeningGumps.States.ACTION_LEFT

        match_repro = GardeningGumps.is_reproduction(gd)
        if match_repro is not None:
            if Journal.Search("You attempt to gather as many resources as you can hold, but"):
                Gumps.SendAction(match_repro["id"], 0)
                return GardeningGumps.States.INTERRUPT
            if match_repro["res-left"] > 0:
                # Harvest resources
                Gumps.SendAction(match_repro["id"], 7)
                return GardeningGumps.States.ACTION_LEFT
            if match_repro["seed-left"] > 0:
                # Harvest seeds
                Gumps.SendAction(match_repro["id"], 8)
                return GardeningGumps.States.ACTION_LEFT
            if match_repro["res-max"] == 8 and match_repro["seed-max"] == 8:
                # Make this decorative
                Gumps.SendAction(match_repro["id"], 2)
                return GardeningGumps.States.ACTION_LEFT
            # You harvested everything available but the plant can still produce more
            Gumps.SendAction(match_repro["id"], 0)
            return GardeningGumps.States.COMPLETED

        match_confirm = GardeningGumps.is_confirm(gd)
        if match_confirm is not None:
            # The plant is now decorative, everything done!
            Gumps.SendAction(match_confirm["id"], 3)
            return GardeningGumps.States.COMPLETED

    return GardeningGumps.States.NOT_FOUND


def tender_plant(serial):
    """
    Tender the plant through gumps with the given serial number.
    """
    item = Items.FindBySerial(serial)
    if item is None:
        return GardeningGumps.States.NOT_FOUND
    if Player.DistanceTo(item) > 3:
        return GardeningGumps.States.NOT_FOUND

    Items.UseItem(item)
    Timer.Create("gardening", 1000)
    while Timer.Check("gardening"):
        state = handle_gardening_gumps()
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


if __name__ == "__main__":
    if not Player.Connected:
        exit()
    if Player.IsGhost:
        exit()

    # Find all plants to tend
    plants = []
    plants.extend(Items.FindAllByID(0x0C86, 0x002B, -1, 3))  # bright orange poppies
    plants.extend(Items.FindAllByID(0x0CA9, 0x0042, -1, 3))  # bright green snake plant

    for plant in plants:
        state = tender_plant(plant.Serial)
        if state == GardeningGumps.States.INTERRUPT:
            break
        Misc.Pause(1000)
