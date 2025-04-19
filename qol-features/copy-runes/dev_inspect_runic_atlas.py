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

    def update(self, gd: Gumps.GumpData) -> None:
        sextant: Optional[Tuple[int, int]] = None

        last_button_id = -1
        last_button_ln = -1
        has_selected_entry = False
        for line_no, line_str in enumerate(gd.layoutPieces):
            line_str = line_str.strip()
            args = line_str.split()
            if args[0] == "button":
                last_button_id = int(args[-1])
                last_button_ln = line_no
                if last_button_id == 100:
                    self.page = 1
                elif last_button_id == 116:
                    self.page = 2
                elif last_button_id == 132:
                    self.page = 3
            elif args[0] == "croppedtext":
                if last_button_id < 100 or last_button_id >= 148:
                    continue
                if last_button_ln + 1 != line_no:
                    continue
                index = last_button_id - 100
                rune = self.runes[index]
                text_id = int(args[-1])
                color = int(args[-2])
                rune.name = gd.stringList[text_id]
                if color == 331:
                    self.selected_index = index
                    has_selected_entry = True
                elif color == 81:
                    rune.facet = 0  # Felucca
                elif color == 10:
                    rune.facet = 1  # Trammel
                elif color == 0:
                    rune.facet = 2  # Illshenar
                elif color == 1102:
                    rune.facet = 3  # Malas
                elif color == 1154:
                    rune.facet = 4  # Tokuno
                elif color == 1645:
                    rune.facet = 5  # Ter Mur
            elif line_str.startswith("htmlgump 25 254 182 18"):
                text_id = int(args[5])
                sextant = decode_sextant(gd.stringList[text_id])
        
        if has_selected_entry and sextant is not None:
            self.runes[self.selected_index].x = sextant[0]
            self.runes[self.selected_index].y = sextant[1]

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
        if not Gumps.WaitForGump(GUMP_ID, delay):
            return None
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
    # Close any existing page for safety
    gd = find_runic_atlas_gump()
    if gd is not None:
        Gumps.CloseGump(gd.gumpId)
        Misc.Pause(500)
    
    # Open the runic atlas
    book_serial = Target.PromptTarget("Select the runic atlas.", 0x47E)
    if not open_runic_atlas(book_serial):
        Misc.SendMessage("Failed to find the runic atlas!", 33)
        return
    
    # Initial scan
    ctx = RunicAtlasContext()
    if not ctx.open_page(3):
        Misc.SendMessage("Failed to scan the runic atlas!", 33)
        return
    
    RunicAtlasActions.select_rune(47)
    
    # Debug: sojourn
    for index, rune in enumerate(ctx.runes):
        if not find_runic_atlas_gump():
            if not open_runic_atlas(book_serial):
                Misc.SendMessage(f"DEBUG|{index}> Failed to use the book.", 33)
                continue
        
        page = 1 + (index // 16)
        if not ctx.open_page(page):
            Misc.SendMessage(f"DEBUG|{index}> Failed to open the page.", 33)
            continue
        
        RunicAtlasActions.select_rune(index)
        Misc.Pause(250)
        if not ctx.open_page(page):
            Misc.SendMessage(f"DEBUG|{index}> Failed to select the entry.", 33)
            continue
        
        if ctx.selected_index != index:
            if rune.name == "Empty":
                Misc.SendMessage(f"DEBUG|{index}> Reached the end?", 68)
            else:
                Misc.SendMessage(f"DEBUG|{index}> Failed to parse the selected index.", 33)
            return
    
        if rune.x == -1 or rune.y == -1:
            if rune.name == "Empty":
                Misc.SendMessage(f"DEBUG|{index}> Reached the end?", 68)
            else:
                Misc.SendMessage(f"DEBUG|{index}> Failed to parse the coordinates.", 33)
            return
            
        RunicAtlasActions.recall()
        Misc.Pause(5000)

main()
