import re
from typing import List, Tuple, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


GUMP_ID = 0


class RunicAtlasActions:
    @classmethod
    def close(cls):
        Gumps.CloseGump(GUMP_ID)

    @classmethod
    def rename(cls):
        Gumps.SendAction(GUMP_ID, 1)

    @classmethod
    def set_default(cls):
        Gumps.SendAction(GUMP_ID, 2)

    @classmethod
    def drop_rune(cls):
        Gumps.SendAction(GUMP_ID, 3)

    @classmethod
    def replace_rune(cls):
        Gumps.SendAction(GUMP_ID, 8)

    @classmethod
    def recall(cls):
        Gumps.SendAction(GUMP_ID, 4)

    @classmethod
    def gate_travel(cls):
        Gumps.SendAction(GUMP_ID, 6)

    @classmethod
    def sacred_journey(cls):
        Gumps.SendAction(GUMP_ID, 7)

    @classmethod
    def next_page(cls):
        Gumps.SendAction(GUMP_ID, 1150)

    @classmethod
    def prev_page(cls):
        Gumps.SendAction(GUMP_ID, 1151)

    @classmethod
    def select_rune(cls, index: int):
        Gumps.SendAction(GUMP_ID, 100 + index)

    @classmethod
    def move_up(cls, index: int):
        Gumps.SendAction(GUMP_ID, 2000 + index)

    @classmethod
    def move_down(cls, index: int):
        Gumps.SendAction(GUMP_ID, 3000 + index)


class Rune:
    name: str
    marked: bool
    x: int
    y: int
    facet: int

    def __init__(self):
        self.name = ""
        self.marked = False
        self.x = -1
        self.y = -1
        self.facet = -1


class RunicAtlasContext:
    page: int
    runes: List[Rune]
    selected_index: int

    def __init__(self):
        self.page = 1
        self.runes = [Rune() for _ in range(48)]
        self.selected_index = -1
    
    @property
    def max_count(self) -> int:
        for index, rune in enumerate(self.runes):
            if rune.name == "":
                return index
        return len(self.runes)

    def update(self, gd: Gumps.GumpData) -> None:
        gd_texts = {}
        gd_buttons = []
        selected_text_id = -1
        sextant: Optional[Tuple[int, int]] = None

        for line in gd.layoutPieces:
            line = line.strip()
            args = line.split()
            if args[0] == "button":
                gd_buttons.append(int(args[-1]))
                continue
            if args[0] == "croppedtext":
                text_id = int(args[-1])
                color = int(args[-2])
                gd_texts[text_id] = (gd.stringList[text_id], color)
                if color == 331:
                    selected_text_id = text_id
            if line.startswith("htmlgump 25 254 182 18"):
                text_id = int(args[5])
                sextant = decode_sextant(gd.stringList[text_id])

        # Determine the current page
        if 100 in gd_buttons:
            self.page = 1
        elif 116 in gd_buttons:
            self.page = 2
        elif 132 in gd_buttons:
            self.page = 3

        # Update
        text_id_offsets = {1: 1, 2: 4, 3: 4}
        index_offsets = {1: 0, 2: 16, 3: 32}
        if selected_text_id != -1:
            self.selected_index = selected_text_id - text_id_offsets[self.page]
            if sextant is not None:
                self.runes[self.selected_index].x = sextant[0]
                self.runes[self.selected_index].y = sextant[1]
        for i in range(16):
            index = i + index_offsets[self.page]
            text_id = index + text_id_offsets[self.page]
            if text_id not in gd_texts:
                continue
            name, color = gd_texts[text_id]
            self.runes[index].name = name
            if color == 81:
                self.runes[index].facet = 0  # Felucca
            elif color == 10:
                self.runes[index].facet = 1  # Trammel
            elif color == 0:
                self.runes[index].facet = 2  # Illshenar
            elif color == 1102:
                self.runes[index].facet = 3  # Malas
            elif color == 1154:
                self.runes[index].facet = 4  # Tokuno
            elif color == 1645:
                self.runes[index].facet = 5  # Ter Mur

    def open_page(self, page: int, delay: int = 1500) -> bool:
        assert page in (1, 2, 3), "Invalid page number"

        for trial in range(4):
            if trial == 3:
                # This is normally impossible
                return False
            gd = wait_for_runic_atlas_gump()
            if gd is None:
                return False
            self.update(gd)
            if self.page < page:
                RunicAtlasActions.next_page()
            elif self.page > page:
                RunicAtlasActions.prev_page()
            else:
                break

        return True


def decode_sextant(msg: str) -> Optional[Tuple[int, int]]:
    # Constants
    N_WIDTH = 5120
    N_HEIGHT = 4096
    N_CENTER_X = 1323
    N_CENTER_Y = 1624

    # Parse message
    pattern = r"<center>(\d+)° (\d+)'([NS]), (\d+)° (\d+)'([EW])</center>"
    match = re.search(pattern, msg)
    if not match:
        return

    xdegree = int(match.group(4))
    xminute = int(match.group(5))
    x_type = match.group(6).upper()
    ydegree = int(match.group(1))
    yminute = int(match.group(2))
    y_type = match.group(3).upper()

    # Convert types and normalize input
    xdegree = xdegree + (xminute / 60)
    ydegree = ydegree + (yminute / 60)

    # Apply direction adjustments
    if x_type == "W":
        xdegree = -xdegree
    if y_type == "N":
        ydegree = -ydegree

    # Adjust to Lord British's throne coordinates
    x = int(round(xdegree * N_WIDTH / 360) + N_CENTER_X) % N_WIDTH
    y = int(round(ydegree * N_HEIGHT / 360) + N_CENTER_Y) % N_HEIGHT

    return x, y


def find_runic_atlas_gump() -> Optional[Gumps.GumpData]:
    for gumpid in Gumps.AllGumpIDs():
        gd = Gumps.GetGumpData(gumpid)
        if gd is None:
            continue

        # Checks if the gump is runic atlas
        if not gd.gumpLayout.startswith("{ gumppic 0 0 39923 }"):
            continue
        if len(gd.gumpText) == 0 or not gd.gumpText[0].startswith("Charges:"):
            continue

        return gd
    return None


def wait_for_runic_atlas_gump(delay: int = 1500) -> Optional[Gumps.GumpData]:
    global GUMP_ID

    # If the gump ID is already known
    if GUMP_ID != 0:
        Gumps.WaitForGump(GUMP_ID, delay)
        return Gumps.GetGumpData(GUMP_ID)

    # Otherwise, use some tricks to identify the gump
    for _ in range(delay // 100):
        gd = find_runic_atlas_gump()
        if gd is not None:
            GUMP_ID = gd.gumpId
            return gd
        Misc.Pause(100)

    return None


def open_runic_atlas(serial: int, delay: int = 1500) -> bool:
    obj = Items.FindBySerial(serial)
    if obj is None:
        return False
    if obj.ItemID not in (0x9C16, 0x9C17):
        return False
    Items.UseItem(serial)
    return True


def main():
    if not open_runic_atlas(0x576B2AEF):
        Misc.SendMessage("Failed to find the runic atlas!", 33)
        return

    ctx = RunicAtlasContext()
    if not ctx.open_page(1):
        Misc.SendMessage("Failed to scan the runic atlas!", 33)
        return
    if not ctx.open_page(3):
        Misc.SendMessage("Failed to scan the runic atlas!", 33)
        return

    Misc.SendMessage(f"You will need at least {ctx.max_count} runes!")


main()
