from AutoComplete import *
from typing import Optional, List, Dict, Tuple, Any
import re


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


class SeedboxEntry:
    def __init__(self, index: int = 0, color: int = 0, amount: int = 1, color_cliloc: str = "", graphics_cliloc: str = "", graphics: int = 0):
        self.index = index
        self.color = color
        self.amount = amount
        self.color_cliloc = color_cliloc
        self.graphics_cliloc = graphics_cliloc
        self.graphics = graphics

    def __repr__(self):
        return f"SeedboxEntry(index={self.index}, color={self.color}, amount={self.amount}, color_cliloc='{self.color_cliloc}', graphics={self.graphics})"


def find_seedbox_gump(gump_id: Optional[int] = None, delay: int = 1000) -> Optional[Gumps.GumpData]:
    if gump_id is None:
        Timer.Create("scan-gumps", delay)
        while Timer.Check("scan-gumps"):
            for gump_id in Gumps.AllGumpIDs():
                gd = Gumps.GetGumpData(gump_id)
                if gd is None:
                    continue
                if gd.gumpLayout.startswith("{ page 0 }{ gumppic 30 30 2172 }{ page 1 }"):
                    return gd
            Misc.Pause(100)
        return None
    else:
        if not Gumps.WaitForGump(gump_id, 1000):
            return None
        return Gumps.GetGumpData(gump_id)


def parse_seedbox_gump(gd: Gumps.GumpData) -> Tuple[List[SeedboxEntry], bool]:
    lines = re.split(r"\}\{", gd.gumpLayout)
    entries: List[SeedboxEntry] = []
    is_last_page = True
    last_entry: Optional[SeedboxEntry] = None
    for line in lines:
        line = re.split(r"\s+", line.strip("{} "))
        if line[0] == "buttontileart" and len(line) == 12:
            index = int(line[7]) - 100
            color = int(line[9])
            last_entry = SeedboxEntry(index=index, color=color)
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

GUMP_ID = GumpTools.hashname("SeedboxReimaginedGump")
GUMP_CELL_W = 125
GUMP_CELL_H = 150
GUMP_NUM_ROWS = 5
GUMP_NUM_COLS = 4
GUMP_OUTER_BORDER = 10
GUMP_INNER_BORDER = 5


def render_new_seedbox_gump(entries: List[SeedboxEntry]):
    Gumps.CloseGump(GUMP_ID)

    # Calculate gump size
    GUMP_INNER_W = GUMP_CELL_W * GUMP_NUM_COLS + GUMP_INNER_BORDER * (GUMP_NUM_COLS - 1)
    GUMP_INNER_H = (GUMP_CELL_H + GUMP_INNER_BORDER) * GUMP_NUM_ROWS + 30  # Extra space for the page text
    GUMP_W = GUMP_INNER_W + GUMP_OUTER_BORDER * 2
    GUMP_H = GUMP_INNER_H + GUMP_OUTER_BORDER * 2

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, GUMP_W, GUMP_H, 5054)
    y = GUMP_OUTER_BORDER
    for i in range(GUMP_NUM_ROWS):
        for j in range(GUMP_NUM_COLS):
            x = GUMP_OUTER_BORDER + j * (GUMP_CELL_W + GUMP_INNER_BORDER)
            Gumps.AddImageTiled(gd, x, y, GUMP_CELL_W, GUMP_CELL_H, 2624)
        y += GUMP_CELL_H + GUMP_INNER_BORDER
    Gumps.AddImageTiled(gd, GUMP_OUTER_BORDER, y, GUMP_INNER_W, 30, 2624)
    Gumps.AddAlphaRegion(gd, GUMP_OUTER_BORDER, GUMP_OUTER_BORDER, GUMP_INNER_W, GUMP_INNER_H)

    # Add pages
    num_pages = (len(entries) - 1) // (GUMP_NUM_ROWS * GUMP_NUM_COLS) + 1
    for page in range(num_pages):
        page_1based = page + 1
        Gumps.AddPage(gd, page_1based)

        # Add entries
        for i in range(GUMP_NUM_ROWS):
            for j in range(GUMP_NUM_COLS):
                index = page * (GUMP_NUM_ROWS * GUMP_NUM_COLS) + i * GUMP_NUM_COLS + j
                if index >= len(entries):
                    break
                entry = entries[index]
                x = GUMP_OUTER_BORDER + j * (GUMP_CELL_W + GUMP_INNER_BORDER)
                y = GUMP_OUTER_BORDER + i * (GUMP_CELL_H + GUMP_INNER_BORDER)

                # Item image
                img_x, img_y = GumpTools.get_centering_pos(entry.graphics, x, y, GUMP_CELL_W, GUMP_CELL_H)
                Gumps.AddItem(gd, img_x, img_y, entry.graphics, entry.color)

                # Amount text
                if entry.amount > 1:
                    args = [str(entry.amount), entry.color_cliloc, entry.graphics_cliloc]
                    cliloc = 1113492
                    if entry.graphics == 9324:  # sugar cane
                        cliloc = 1113715
                    if entry.graphics == 3230:  # cocoa tree
                        cliloc = 1113716
                    Gumps.AddHtmlLocalized(gd, x + 5, y, GUMP_CELL_W - 10, 60, cliloc, f"@{'@'.join(args)}@", 28539, False, False)
                else:
                    args = [entry.color_cliloc, entry.graphics_cliloc]
                    cliloc = 1061917
                    if entry.graphics == 9324:  # sugar cane
                        cliloc = 1095221
                    if entry.graphics == 3230:  # cocoa tree
                        cliloc = 1080533
                    Gumps.AddHtmlLocalized(gd, x + 5, y, GUMP_CELL_W - 10, 60, cliloc, f"@{'@'.join(args)}@", 28539, False, False)

        # Next / Previous page buttons
        y = GUMP_OUTER_BORDER + GUMP_NUM_ROWS * (GUMP_CELL_H + GUMP_INNER_BORDER)
        if page_1based > 1:
            Gumps.AddButton(gd, GUMP_OUTER_BORDER + 5, y + 4, 4014, 4016, 0, 0, page_1based - 1)
            Gumps.AddLabelCropped(gd, GUMP_OUTER_BORDER + 40, y + 6, 100, 18, 1153, "PREV")
        if page_1based < num_pages:
            Gumps.AddButton(gd, GUMP_OUTER_BORDER + 105, y + 4, 4005, 4007, 0, 0, page_1based + 1)
            Gumps.AddLabelCropped(gd, GUMP_OUTER_BORDER + 140, y + 6, 100, 18, 1153, "NEXT")

    Gumps.SendGump(GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


################################################################################
# Main
################################################################################


def scan_seedbox():
    seedbox_serial = Target.PromptTarget("Target your seedbox.", 0x3B2)
    seedbox = Items.FindBySerial(seedbox_serial)

    if seedbox is None:
        Misc.SendMessage("Invalid seed box.", 33)
        return None
    if seedbox.ItemID in (0x4B58, 0x4B5A):
        Misc.SendMessage("This seed box is empty.", 33)
        return None
    if seedbox.ItemID not in (0x4B59, 0x4B5B):
        Misc.SendMessage("This is not a seed box.", 33)
        return None

    gump_id = None
    entries: List[SeedboxEntry] = []

    gd = find_seedbox_gump(gump_id, 1000)
    if gd is not None:
        gump_id = gd.gumpId
        Gumps.CloseGump(gump_id)

    Items.UseItem(seedbox_serial)
    while True:
        gd = find_seedbox_gump(gump_id, 1000)
        if gd is None:
            break
        gump_id = gd.gumpId
        entries_new, is_last_page = parse_seedbox_gump(gd)
        entries.extend(entries_new)
        if is_last_page:
            Gumps.CloseGump(gump_id)
            break
        Gumps.SendAction(gump_id, 2)

    entries = sorted(entries, key=lambda e: e.index)
    if not all(e.index == i for i, e in enumerate(entries)):
        Misc.SendMessage("Failed to parse seed box entries.", 33)

    print(f"Found {len(entries)} seed box entries!")

    render_new_seedbox_gump(entries)


if __name__ == "__main__":
    scan_seedbox()
