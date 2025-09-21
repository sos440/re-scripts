from AutoComplete import *
from typing import Optional, List, Dict, Tuple, Any
import re
from enum import Enum
import json


################################################################################
# Helpers
################################################################################


# Useful function
class GumpTools:
    CENTER_POS_CACHE: Dict[int, Tuple[int, int]] = {}

    @classmethod
    def get_centering_pos(
        cls,
        item_id: int,
        px: int = 0,
        py: int = 0,
        pw: int = 0,
        ph: int = 0,
        abs: bool = True,
    ) -> Tuple[int, int]:
        """
        Calculates the left-top position for the item to be centered at the given position or rect:
        * If only `px` and `py` are given, it centers the item at `(px, py)`.
        * If `pw` and `ph` are also given, it centers the item at the center of the rect with left-top `(px, py)` and size `(pw, ph)`.
        """
        if item_id not in cls.CENTER_POS_CACHE:
            bitmap = Items.GetImage(item_id, 0)
            w, h = bitmap.Width, bitmap.Height
            # Find the rectangle bounds
            left, top, right, bottom = w, h, 0, 0
            for y in range(h):
                for x in range(w):
                    pixel = bitmap.GetPixel(x, y)
                    if pixel.R or pixel.G or pixel.B:
                        left = min(x, left)
                        top = min(y, top)
                        right = max(x, right)
                        bottom = max(y, bottom)
            # Calculate the relative posotion of the left-top corner
            if right < left or bottom < top:
                dx, dy = 0, 0
            else:
                dx = -(left + right) // 2
                dy = -(top + bottom) // 2
            cls.CENTER_POS_CACHE[item_id] = (dx, dy)

        x, y = cls.CENTER_POS_CACHE[item_id]
        if abs:
            x, y = x + px, y + py
        x, y = x + (pw // 2), y + (ph // 2)
        return (x, y)

    @staticmethod
    def hashname(name: str) -> int:
        """
        Generates a gump ID for the given name.
        """
        return hash(name) & 0xFFFFFFFF

    @staticmethod
    def tooltip_to_itemproperty(gd: Gumps.GumpData) -> str:
        """
        Converts integer-argument tooltips to item properties.
        """
        return re.sub(r"\{ tooltip (\d+) \}", r"{ itemproperty \1 }", gd.gumpDefinition)


################################################################################
# Parsers
################################################################################


class SeedEntry:
    def __init__(self, index: int = 0, color: int = 0, amount: int = 1, color_cliloc: str = "", graphics_cliloc: str = "", graphics: int = 0):
        self.index = index
        self.color = color
        self.amount = amount
        self.color_cliloc = color_cliloc
        self.graphics_cliloc = graphics_cliloc
        self.graphics = graphics

    def __repr__(self):
        return f"SeedEntry(index={self.index}, color={self.color}, amount={self.amount}, color_cliloc='{self.color_cliloc}', graphics={self.graphics})"


class SeedBoxParser:
    GUMP_ID: Optional[int] = None

    @classmethod
    def find_seedbox_gump(cls, delay: int = 1000) -> Optional[Gumps.GumpData]:
        if cls.GUMP_ID is None:
            Timer.Create("scan-gumps", delay)
            while Timer.Check("scan-gumps"):
                for gump_id in Gumps.AllGumpIDs():
                    gd = Gumps.GetGumpData(gump_id)
                    if gd is None:
                        continue
                    if gd.gumpLayout.startswith("{ page 0 }{ gumppic 30 30 2172 }{ page 1 }"):
                        cls.GUMP_ID = gump_id
                        return gd
                Misc.Pause(100)
            return None
        else:
            if not Gumps.WaitForGump(cls.GUMP_ID, 1000):
                return None
            return Gumps.GetGumpData(cls.GUMP_ID)

    @staticmethod
    def parse_seedbox_gump(gd: Gumps.GumpData) -> Tuple[List[SeedEntry], bool]:
        lines = re.split(r"\}\{", gd.gumpLayout)
        entries: List[SeedEntry] = []
        is_last_page = True
        last_entry: Optional[SeedEntry] = None
        for line in lines:
            line = re.split(r"\s+", line.strip("{} "))
            if line[0] == "buttontileart" and len(line) == 12:
                index = int(line[7]) - 100
                color = int(line[9])
                last_entry = SeedEntry(index=index, color=color)
                entries.append(last_entry)
                continue
            if last_entry is not None:
                # Example: tooltip 1113492 @15  #1060813    #1023214@
                if line[0] == "tooltip":
                    if len(line) == 4:
                        last_entry.amount = 1
                        last_entry.color_cliloc = line[2]
                        last_entry.graphics_cliloc = line[3].strip("@")
                        last_entry.graphics = int(line[3].strip("#@")) - 1020000
                    elif len(line) == 5:
                        last_entry.amount = int(line[2].strip("#@"))
                        last_entry.color_cliloc = line[3]
                        last_entry.graphics_cliloc = line[4].strip("@")
                        last_entry.graphics = int(line[4].strip("#@")) - 1020000
                    if last_entry.graphics_cliloc == "#1098212":
                        last_entry.graphics = 19340  # vanilla's graphic need a fix
                last_entry = None
            if line[0] == "xmfhtmltok" and len(line) >= 10 and line[8] == "1151850":
                # Example: xmfhtmltok 136 373 100 25 0 0 28539 1151850 @@1@2@
                page, total_pages = map(int, line[9].strip("@").split("@"))
                if page < total_pages:
                    is_last_page = False
                continue

        return entries, is_last_page


################################################################################
# Gump
################################################################################


class SeedboxStyle(Enum):
    BLACK = 1
    WHITE = 2
    YELLOW = 3


class SeedViewer:
    GUMP_ID = GumpTools.hashname("SeedboxReimaginedGump")
    GUMP_CELL_W = 125
    GUMP_CELL_H = 150
    GUMP_NUM_ROWS = 5
    GUMP_NUM_COLS = 4
    GUMP_OUTER_BORDER = 10
    GUMP_INNER_BORDER = 5

    STYLE_GUMP_ID = GumpTools.hashname("SeedboxReimaginedStyleGump")
    STYLE_CHOICE = SeedboxStyle.BLACK
    STYLE_ALPHA = True

    @classmethod
    def render(cls, entries: List[SeedEntry]):
        Gumps.CloseGump(cls.GUMP_ID)

        # Calculate gump size
        GUMP_INNER_W = cls.GUMP_CELL_W * cls.GUMP_NUM_COLS + cls.GUMP_INNER_BORDER * (cls.GUMP_NUM_COLS - 1)
        GUMP_INNER_H = (cls.GUMP_CELL_H + cls.GUMP_INNER_BORDER) * cls.GUMP_NUM_ROWS + 30  # Extra space for the page text
        GUMP_W = GUMP_INNER_W + cls.GUMP_OUTER_BORDER * 2
        GUMP_H = GUMP_INNER_H + cls.GUMP_OUTER_BORDER * 2
        GUMP_BG = 2624  # background
        GUMP_TC = 28539  # text color
        if cls.STYLE_CHOICE == SeedboxStyle.BLACK:
            GUMP_BG = 2624
        elif cls.STYLE_CHOICE == SeedboxStyle.WHITE:
            GUMP_BG = 9354
            if not cls.STYLE_ALPHA:
                GUMP_TC = 0
        elif cls.STYLE_CHOICE == SeedboxStyle.YELLOW:
            GUMP_BG = 9304
            if not cls.STYLE_ALPHA:
                GUMP_TC = 0

        # Create the gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, GUMP_W, GUMP_H, 5054)
        y = cls.GUMP_OUTER_BORDER
        for i in range(cls.GUMP_NUM_ROWS):
            for j in range(cls.GUMP_NUM_COLS):
                x = cls.GUMP_OUTER_BORDER + j * (cls.GUMP_CELL_W + cls.GUMP_INNER_BORDER)
                Gumps.AddImageTiled(gd, x, y, cls.GUMP_CELL_W, cls.GUMP_CELL_H, GUMP_BG)
            y += cls.GUMP_CELL_H + cls.GUMP_INNER_BORDER
        Gumps.AddImageTiled(gd, cls.GUMP_OUTER_BORDER, y, GUMP_INNER_W, 30, 2624)
        if cls.STYLE_ALPHA:
            Gumps.AddAlphaRegion(gd, cls.GUMP_OUTER_BORDER, cls.GUMP_OUTER_BORDER, GUMP_INNER_W, GUMP_INNER_H)

        # Add pages
        num_pages = (len(entries) - 1) // (cls.GUMP_NUM_ROWS * cls.GUMP_NUM_COLS) + 1
        for page in range(num_pages):
            page_1based = page + 1
            Gumps.AddPage(gd, page_1based)

            # Add entries
            for i in range(cls.GUMP_NUM_ROWS):
                for j in range(cls.GUMP_NUM_COLS):
                    index = page * (cls.GUMP_NUM_ROWS * cls.GUMP_NUM_COLS) + i * cls.GUMP_NUM_COLS + j
                    if index >= len(entries):
                        break
                    entry = entries[index]
                    x = cls.GUMP_OUTER_BORDER + j * (cls.GUMP_CELL_W + cls.GUMP_INNER_BORDER)
                    y = cls.GUMP_OUTER_BORDER + i * (cls.GUMP_CELL_H + cls.GUMP_INNER_BORDER)

                    # Item image
                    img_x, img_y = GumpTools.get_centering_pos(entry.graphics, x, y, cls.GUMP_CELL_W, cls.GUMP_CELL_H)
                    Gumps.AddItem(gd, img_x, img_y, entry.graphics, entry.color)

                    # Amount text
                    if entry.amount > 1:
                        args = [str(entry.amount), entry.color_cliloc, entry.graphics_cliloc]
                        cliloc = 1113493 if COLOR_MAP.get(entry.color, 0) in (1, 3, 5, 7, 9, 11) else 1113492  # bright or dull
                        if entry.graphics == 9324:  # sugar cane
                            cliloc = 1113715
                        if entry.graphics == 3230:  # cocoa tree
                            cliloc = 1113716
                        Gumps.AddHtmlLocalized(gd, x + 5, y, cls.GUMP_CELL_W - 10, 60, cliloc, f"@{'@'.join(args)}@", GUMP_TC, False, False)
                    else:
                        args = [entry.color_cliloc, entry.graphics_cliloc]
                        cliloc = 1061918 if COLOR_MAP.get(entry.color, 0) in (1, 3, 5, 7, 9, 11) else 1061917
                        if entry.graphics == 9324:  # sugar cane
                            cliloc = 1095221
                        if entry.graphics == 3230:  # cocoa tree
                            cliloc = 1080533
                        Gumps.AddHtmlLocalized(gd, x + 5, y, cls.GUMP_CELL_W - 10, 60, cliloc, f"@{'@'.join(args)}@", GUMP_TC, False, False)

            # Next / Previous page buttons
            y = cls.GUMP_OUTER_BORDER + cls.GUMP_NUM_ROWS * (cls.GUMP_CELL_H + cls.GUMP_INNER_BORDER)
            if page_1based > 1:
                Gumps.AddButton(gd, cls.GUMP_OUTER_BORDER + 5, y + 4, 4014, 4016, 0, 0, page_1based - 1)
                Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 40, y + 6, 100, 18, 1153, "PREV")
            if page_1based < num_pages:
                Gumps.AddButton(gd, cls.GUMP_OUTER_BORDER + 105, y + 4, 4005, 4007, 0, 0, page_1based + 1)
                Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 140, y + 6, 100, 18, 1153, "NEXT")
            Gumps.AddButton(gd, cls.GUMP_OUTER_BORDER + 205, y + 4, 4005, 4007, 1, 1, 0)
            Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 240, y + 6, 100, 18, 1153, "CHANGE STYLE")

        Gumps.SendGump(cls.GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    @classmethod
    def choose_style(cls):
        global STYLE_CHOICE, STYLE_ALPHA
        Gumps.CloseGump(cls.STYLE_GUMP_ID)

        # Calculate gump size
        GUMP_INNER_W = 200
        GUMP_INNER_H = 4 + 5 * 26
        GUMP_W = GUMP_INNER_W + cls.GUMP_OUTER_BORDER * 2
        GUMP_H = GUMP_INNER_H + cls.GUMP_OUTER_BORDER * 2

        # Create the gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, GUMP_W, GUMP_H, 5054)
        Gumps.AddImageTiled(gd, cls.GUMP_OUTER_BORDER, cls.GUMP_OUTER_BORDER, GUMP_INNER_W, GUMP_INNER_H, 2624)
        Gumps.AddAlphaRegion(gd, cls.GUMP_OUTER_BORDER, cls.GUMP_OUTER_BORDER, GUMP_INNER_W, GUMP_INNER_H)

        Gumps.AddGroup(gd, 1)
        y = cls.GUMP_OUTER_BORDER + 4
        Gumps.AddRadio(gd, cls.GUMP_OUTER_BORDER + 5, y, 208, 209, cls.STYLE_CHOICE == SeedboxStyle.BLACK, 1)
        Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 35, y, 100, 18, 1153, "Black")
        y += 26
        Gumps.AddRadio(gd, cls.GUMP_OUTER_BORDER + 5, y, 208, 209, cls.STYLE_CHOICE == SeedboxStyle.WHITE, 2)
        Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 35, y, 100, 18, 1153, "White")
        y += 26
        Gumps.AddRadio(gd, cls.GUMP_OUTER_BORDER + 5, y, 208, 209, cls.STYLE_CHOICE == SeedboxStyle.YELLOW, 3)
        Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 35, y, 100, 18, 1153, "Yellow")
        y += 26
        Gumps.AddCheck(gd, cls.GUMP_OUTER_BORDER + 5, y, 210, 211, cls.STYLE_ALPHA, 0)
        Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 35, y, 200, 18, 1153, "Apply transparency")
        y += 26
        Gumps.AddButton(gd, cls.GUMP_OUTER_BORDER + 5, y, 4014, 4016, 1, 1, 0)
        Gumps.AddLabelCropped(gd, cls.GUMP_OUTER_BORDER + 40, y + 2, 100, 18, 1153, "APPLY")

        Gumps.SendGump(cls.STYLE_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

        if not Gumps.WaitForGump(cls.STYLE_GUMP_ID, 3600000):
            return

        gd = Gumps.GetGumpData(cls.STYLE_GUMP_ID)
        if gd is None:
            return

        if gd.buttonid == 1:
            cls.STYLE_ALPHA = 0 in gd.switches
            if 1 in gd.switches:
                cls.STYLE_CHOICE = SeedboxStyle.BLACK
            elif 2 in gd.switches:
                cls.STYLE_CHOICE = SeedboxStyle.WHITE
            elif 3 in gd.switches:
                cls.STYLE_CHOICE = SeedboxStyle.YELLOW


################################################################################
# Main
################################################################################

COLOR_MAP = {
    0: 0,
    33: 1,
    1645: 2,
    43: 3,
    1135: 4,
    56: 5,
    2213: 6,
    66: 7,
    1435: 8,
    5: 9,
    1341: 10,
    16: 11,
    13: 12,
    1166: 13,
    1173: 14,
    1158: 15,
    1161: 16,
    1153: 17,
    1109: 18,
}

PLANT_MAP = {
    "bonsai": [10460, 10461, 10462, 10463, 10464, 10465, 10466, 10467],
    "peculiar group 1": [3273, 6810, 3204, 6815, 3265],
    "peculiar group 2": [3326, 3215, 3272, 3214],
    "peculiar group 3": [3365, 3255, 3262, 3521],
    "peculiar group 4": [3323, 3512, 6817, 9324],
    "peculiar group 5": [19340],
    "cocoa": [3230],
    "campion flower": [3203],
    "poppies": [3206],
    "snowdrop": [3208],
    "bulrushes": [3220],
    "lilies": [3211],
    "pampas grass": [3237],
    "rushes": [3239],
    "elephant ear plant": [3223],
    "fern": [3231],
    "ponytail palm": [3238],
    "small palm": [3228],
    "century plant": [3377],
    "water plant": [3332],
    "snake plant": [3241],
    "prickly pear cactus": [3372],
    "barrel cactus": [3366],
    "tribarrel cactus": [3367],
}


def is_empty_seedbox(item: "Item") -> bool:
    return item.ItemID in (0x4B58, 0x4B5A)


def is_filled_seedbox(item: "Item") -> bool:
    return item.ItemID in (0x4B59, 0x4B5B)


def prompt_target() -> Optional[int]:
    serial = Target.PromptTarget("Target your seed box or container to investigate.", 0x3B2)
    item = Items.FindBySerial(serial)

    if item is None:
        Misc.SendMessage("Invalid seed box.", 33)
        return None
    return serial


def scan_seedbox(serial: int) -> Optional[List[SeedEntry]]:
    """
    Parse the seed box contents and return a list of SeedEntry.
    """
    entries: List[SeedEntry] = []

    gd = SeedBoxParser.find_seedbox_gump(1000)
    if gd is not None:
        Gumps.CloseGump(gd.gumpId)

    Items.UseItem(serial)
    while True:
        gd = SeedBoxParser.find_seedbox_gump(1000)
        if gd is None:
            return
        entries_new, is_last_page = SeedBoxParser.parse_seedbox_gump(gd)
        entries.extend(entries_new)
        if is_last_page:
            Gumps.CloseGump(gd.gumpId)
            break
        Gumps.SendAction(gd.gumpId, 2)

    entries = sorted(entries, key=lambda e: e.index)
    if not all(e.index == i for i, e in enumerate(entries)):
        Misc.SendMessage("Failed to parse seed box entries.", 33)
        return

    return entries


def scan_container(serial: int) -> Optional[List[SeedEntry]]:
    entries: List[SeedEntry] = []

    cont = Items.FindBySerial(serial)
    if cont is None or not cont.IsContainer:
        Misc.SendMessage("Invalid container.", 33)
        return None

    Items.WaitForContents(cont.Serial, 1000)
    for item in cont.Contains:
        if item.ItemID != 0x0DCF:
            continue
        props = Items.GetProperties(item.Serial, 1000)
        if not props:
            continue
        cliloc = props[0].Number
        args = re.split("\t", props[0].Args)
        # Multiple seeds
        entry = SeedEntry()
        entry.amount = item.Amount
        entry.color = item.Color
        # Multiple seeds
        if cliloc in (1113492, 1113493, 1113715, 1113716):
            if len(args) < 3:
                continue
            entry.color_cliloc = args[1]
            entry.graphics_cliloc = args[2]
            entry.graphics = int(args[2].strip("#@")) - 1020000
        # Single seed
        elif cliloc in (1061917, 1061918, 1095221, 1080533):
            if len(args) < 2:
                continue
            entry.color_cliloc = args[0]
            entry.graphics_cliloc = args[1]
            entry.graphics = int(args[1].strip("#@")) - 1020000
        if entry.graphics_cliloc == "#1098212":
            entry.graphics = 19340  # vanilla's graphic need a fix

        if entry.graphics > 0:
            entries.append(entry)

        entries = sorted(entries, key=lambda e: (e.graphics, COLOR_MAP.get(e.color, 0)))

    return entries


def show_seed_viewer(serial):
    # Scan the seedbox
    item = Items.FindBySerial(serial)
    if item is None:
        Misc.SendMessage("Invalid seed box.", 33)
        return
    if is_empty_seedbox(item):
        Misc.SendMessage("The seed box is empty.", 33)
        return
    entries: Optional[List[SeedEntry]] = None
    if is_filled_seedbox(item):
        entries = scan_seedbox(serial)
    elif item.IsContainer:
        entries = scan_container(serial)
    if entries is None:
        Misc.SendMessage("Failed to read the container.", 33)
        return
    if not entries:
        Misc.SendMessage("The container has no identified seeds.", 33)
        return

    with open("Data/plants.json", "r") as f:
        data = json.load(f)

    for entry in entries:
        if entry.graphics not in data:
            data.append(entry.graphics)

    with open("Data/plants.json", "w") as f:
        json.dump(data, f)

    # Show the new gump
    print(f"Found {len(entries)} seeds!")
    SeedViewer.render(entries)

    # Handle gump actions
    if not Gumps.WaitForGump(SeedViewer.GUMP_ID, 3600000):
        return False

    gd = Gumps.GetGumpData(SeedViewer.GUMP_ID)
    if gd is None:
        return False

    if gd.buttonid == 1:
        SeedViewer.choose_style()
        return True

    return False


def main():
    serial = prompt_target()
    if serial is None:
        return

    open_next = True
    while open_next:
        open_next = show_seed_viewer(serial)


if __name__ == "__main__":
    main()
