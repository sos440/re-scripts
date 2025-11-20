################################################################################
# User Setting
################################################################################

# Automatically make the plant decorative when possible
AUTO_DECORATIVE = True

# Delay between actions in milliseconds
ACTION_DELAY = 1000


################################################################################
# Script Starts Here
################################################################################

from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum
import re


COLORS = [0, 33, 1645, 43, 1135, 56, 2213, 66, 1435, 5, 1341, 16, 13, 1166, 1173, 1158, 1161, 1153, 1109]
PLANTS = [10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467, 3273, 6810, 3204, 6815, 3265, 3326, 3215, 3272, 3214, 3365, 3255, 3262, 3521, 3323, 3512, 6817, 9324, 19340, 3230, 3203, 3206, 3208, 3220, 3211, 3237, 3239, 3223, 3231, 3238, 3228, 3377, 3332, 3241, 3372, 3366, 3367]

MAP_GUMP_COLOR_TO_NAME = {
    2101: "plain",
    36: "bright red",
    0x066D: "red",
    0x002B: "bright orange",
    46: "orange",
    53: "bright yellow",
    56: "yellow",
    63: "bright green",
    66: "green",
    6: "bright blue",
    0x053D: "blue",
    0x0010: "bright purple",
    0x000D: "purple",
    0x0481: "white",
    0: "black",
}


def _namespace_garden_bed():
    RAISED_BED = [
        0x4B22,  # top left
        0x4B28,  # top center
        0x4B23,  # top right
        0x4B24,  # middle left
        0x4B29,  # middle center
        0x4B25,  # middle right
        0x4B26,  # bottom left
        0x4B2A,  # bottom center
        0x4B27,  # bottom right
    ]

    FIELD_BED = [
        0xA30D,  # top left
        0xA313,  # top center
        0xA30E,  # top right
        0xA30F,  # middle left
        0xA314,  # middle center
        0xA310,  # middle right
        0xA311,  # bottom left
        0xA315,  # bottom center
        0xA312,  # bottom right
    ]

    PLANTS = [
        0x0913,  # dirt
        0x0C62,  # sapling
        10460,
        10461,
        10462,
        10463,
        10464,
        10465,
        10466,
        10467,
        3273,
        6810,
        3204,
        6815,
        3265,
        3326,
        3215,
        3272,
        3214,
        3365,
        3255,
        3262,
        3521,
        3323,
        3512,
        6817,
        9324,
        19340,
        3230,
        3203,
        3206,
        3208,
        3220,
        3211,
        3237,
        3239,
        3223,
        3231,
        3238,
        3228,
        3377,
        3332,
        3241,
        3372,
        3366,
        3367,
    ]

    def detect_bed(serial: int) -> Optional[Tuple[int, int, int, int, int]]:
        # Sanity check
        cur_item = Items.FindBySerial(serial)
        if cur_item is None:
            return
        if not cur_item.OnGround:
            return

        # Record some states
        # x, y, z = coords of the current "garden bed" piece
        # zp = the z coordinate where the plants should lie at
        # bed_type = the current bed type. ("plant" is an alias for "not determined yet")
        cur_pos = cur_item.Position
        x, y, z = cur_pos.X, cur_pos.Y, cur_pos.Z
        zp = z
        if cur_item.ItemID in RAISED_BED:
            bed_type = "raised"
            zp += 5
        elif cur_item.ItemID in FIELD_BED:
            bed_type = "field"
            zp += 1
        elif cur_item.ItemID in PLANTS:
            bed_type = "plant"
        else:
            return

        # List of coordinates of top-left corners
        coord_TLs = []
        # List of coordinates of bottom-right corners
        coord_BRs = []

        # For all scanned garden bed pieces
        filter = Items.Filter()
        filter.Enabled = True
        filter.Graphics = CList[Int32](RAISED_BED + FIELD_BED)
        filter.OnGround = True
        for item in Items.ApplyFilter(filter):
            pos = item.Position
            coords = (pos.X, pos.Y, pos.Z)
            # If the bed_type is still undetermined,
            if bed_type == "plant":
                # Guess the bed_type and the z coordinate of the garden bed piece beneath the plant
                if item.ItemID in FIELD_BED and (x, y, z - 1) == coords:
                    bed_type = "field"
                    z = z - 1
                elif item.ItemID in RAISED_BED and (x, y, z - 5) == coords:
                    bed_type = "raised"
                    z = z - 5
            # Record the coordinates of the top-left corners
            if item.ItemID in (RAISED_BED[0], FIELD_BED[0]):
                coord_TLs.append(coords)
            # Record the coordinates of the bottom-right corners
            elif item.ItemID in (RAISED_BED[8], FIELD_BED[8]):
                coord_BRs.append(coords)

        # If the bed_type is stilll undetermined, then it defaults to None
        if bed_type == "plant":
            return

        # For the x, y, z, coordinates of each top-left piece,
        for x0, y0, z0 in coord_TLs:
            # If its z-height is different from the height of the "current" bed piece, skip
            if z != z0:
                continue
            # For each of the possible bed shapes,
            for dx, dy in [(2, 2), (1, 2), (2, 1), (1, 1)]:
                # Compute the bottom-right coordinates
                x1, y1 = x0 + dx, y0 + dy
                # If that coordinates do not exist in the recorded list, skip
                if (x1, y1, z) not in coord_BRs:
                    continue
                # If the "current" piece does not lie in the rect, skip
                if x < x0 or x > x1 or y < y0 or y > y1:
                    continue
                return (x0, y0, x1, y1, zp)

    def get_plants_on_bed(serial: int) -> Optional[List["Item"]]:
        """
        A function that retuns the list of plants on a garden bed.
        """
        if serial == -1:
            return

        result = detect_bed(serial)
        if result is None:
            item = Items.FindBySerial(serial)
            if item is None:
                return
            if item.ItemID not in PLANTS:
                return [item]
            return

        x0, y0, x1, y1, zp = result
        plants = []

        filter = Items.Filter()
        filter.Enabled = True
        filter.Graphics = CList[Int32](PLANTS)
        filter.OnGround = True
        for item in Items.ApplyFilter(filter):
            pos = item.Position
            x, y, z = pos.X, pos.Y, pos.Z
            if z != zp:
                continue
            if x < x0 or x > x1 or y < y0 or y > y1:
                continue
            plants.append(item)

        return plants

    return get_plants_on_bed


get_plants_on_bed = _namespace_garden_bed()


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

        # Extract the seed color from the gump layout
        seed_color = None
        for line in gd.gumpLayout.strip("{} ").split("}{"):
            line = line.strip()
            args = line.split(" ")
            if line.startswith("text 199 116"):
                match = re.search(r"text 199 116 (\d+) \d+", line)
                if match is None:
                    continue
                seed_color = int(match.group(1))
                break

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

        return {"id": gd.gumpId, "res-left": res_left, "res-max": res_max, "seed-left": seed_left, "seed-max": seed_max, "seed-color": seed_color}

    @staticmethod
    def is_confirm(gd: Gumps.GumpData) -> Optional[Dict[str, Any]]:
        if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ tilepic 25 45 3307 }"):
            return
        if len(gd.gumpData) != 7 or gd.gumpData[4] != "Set plant":
            return

        return {"id": gd.gumpId}


def handle_gardening_gumps(plant: int, color: int, auto_deco: bool = False, metadata: Optional[Dict] = None) -> GardeningGumps.States:
    """
    Interact with gardening gumps.
    """
    if metadata is None:
        metadata = dict()

    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        if gd is None:
            continue

        match_main = GardeningGumps.is_main(gd)
        if match_main is not None:
            plant_matched = match_main["plant"] == plant
            color_matched = match_main["color"] == color
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
            if match_repro["seed-max"] > 0 and match_repro["seed-color"] is not None and "seed-color" not in metadata:
                color = match_repro["seed-color"]
                color_name = MAP_GUMP_COLOR_TO_NAME.get(color, f"unknown color ({color})")
                metadata["seed-color"] = color
                Misc.SendMessage(f"Seed color: {color_name}", 0x481)
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
    metadata = dict()
    while Timer.Check("gardening"):
        state = handle_gardening_gumps(item.ItemID, item.Color, auto_deco, metadata)
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


def move_plants():
    serial = Target.PromptTarget("Select the box to move plants to.", 0x3B2)
    if serial == -1:
        return
    if not Misc.IsItem(serial):
        return
    for item in Items.FindAllByID(PLANTS, -1, Player.Backpack.Serial, 2):
        Items.Move(item.Serial, serial, -1)
        Misc.Pause(1000)


def cut_plants():
    serial = Target.PromptTarget("Choose the container.", 0x3B2)
    if not Misc.IsItem(serial):
        return

    plants = Items.FindAllByID(PLANTS, -1, serial, 3)
    for item in plants:
        serial = item.Serial
        while True:
            scan = Items.FindBySerial(serial)
            if scan is None:
                break
            clipper = Items.FindByID(0x0DFC, 0, Player.Backpack.Serial, 0)
            if clipper is None:
                break
            Items.UseItem(clipper.Serial)
            if not Target.WaitForTarget(1000, False):
                continue
            Target.TargetExecute(scan.Serial)
            Misc.Pause(1000)


GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
SHORTCUT_GUMP_ID = hash("HarvestGump") & 0xFFFFFFFF


def ask_to_harvest(harvesting: bool = False):
    """
    A minimized gump with a button to run.
    """
    Gumps.CloseGump(SHORTCUT_GUMP_ID)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 165, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 165)
    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WT.format(text="Harvest Helper"), False, False)

    if harvesting:
        Gumps.AddButton(gd, 10, 30, 40297, 40298, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 33, 126, 18, GUMP_WT.format(text="Stop Harvesting"), False, False)
    else:
        Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 33, 126, 18, GUMP_WT.format(text="Harvest Batch"), False, False)

    Gumps.AddButton(gd, 10, 55, 40021, 40031, 2, 1, 0)
    Gumps.AddHtml(gd, 10, 58, 126, 18, GUMP_WT.format(text="Harvest Each"), False, False)

    Gumps.AddButton(gd, 10, 80, 40021, 40031, 3, 1, 0)
    Gumps.AddHtml(gd, 10, 83, 126, 18, GUMP_WT.format(text="Move Plants"), False, False)

    Gumps.AddButton(gd, 10, 105, 40021, 40031, 4, 1, 0)
    Gumps.AddHtml(gd, 10, 108, 126, 18, GUMP_WT.format(text="Cut Plants"), False, False)

    Gumps.AddCheck(gd, 10, 135, 210, 211, AUTO_DECORATIVE, 10)
    Gumps.AddLabel(gd, 35, 135, 1152, "Auto Decorative")

    Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def parse_response(delay: int = 500) -> Tuple[int, bool]:
    if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, delay):
        return 0, AUTO_DECORATIVE
    gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
    auto_deco = 10 in gd.switches
    if gd is None:
        return 0, auto_deco
    return gd.buttonid, auto_deco


if __name__ == "__main__":
    while Player.Connected:
        ask_to_harvest()
        response, AUTO_DECORATIVE = parse_response(1000 * 60 * 60)

        # Find all plants to tend
        if response == 0:
            Misc.SendMessage("Bye!", 68)
            break
        elif response == 1:
            serial = Target.PromptTarget("Target the garden bed or plant to tend.", 0x3B2)
            if serial == -1:
                continue
            plants = get_plants_on_bed(serial)
            if plants is None:
                Misc.SendMessage("Failed to find the garden bed.", 33)
                continue
            for plant in plants:
                if plant.ItemID not in PLANTS:
                    continue
                if plant.Color not in COLORS:
                    continue
                # Tend the plant
                Misc.SendMessage(f"Tending the plant: {plant.Name}", 68)
                while True:
                    state = tend_plant(plant.Serial, AUTO_DECORATIVE)
                    Misc.Pause(Timer.Remaining("plant-used"))
                    if state == GardeningGumps.States.INTERRUPT:
                        continue
                    if state in (GardeningGumps.States.COMPLETED, GardeningGumps.States.INCOMPLETE):
                        break

        elif response == 2:
            while True:
                serial = Target.PromptTarget("Choose the plant to tend.")
                if serial == -1:
                    break
                plant = Items.FindBySerial(serial)
                if plant is None:
                    continue
                if plant.ItemID not in PLANTS:
                    continue
                if plant.Color not in COLORS:
                    continue
                state = tend_plant(plant.Serial, AUTO_DECORATIVE)

        elif response == 3:
            move_plants()

        elif response == 4:
            cut_plants()
