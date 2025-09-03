################################################################################
# User Settings
################################################################################

CAST_CHIVALRY_SKILL_MIN = 100.0
"""Minimum skill required to cast Sacred Journey"""

CAST_CHIVALRY_MANA_MIN = 5
"""Minimum mana required to cast Sacred Journey"""

CAST_MAGERY_SKILL_MIN = 100.0
"""Minimum skill required to cast Recall"""

CAST_MAGERY_MANA_MIN = 18
"""Minimum mana required to cast Recall"""

CAST_RECOVERY_TIME = 1500
"""Time in milliseconds to recover from casting"""

################################################################################
# Imports
################################################################################

from AutoComplete import *
import threading
import re
from typing import List, Tuple, Optional

VERSION = "1.1"

################################################################################
# Helper functions
################################################################################


GUMP_RUNIC_ATLAS = 0


def _decode_sextant(msg: str) -> Optional[Tuple[int, int]]:
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


def _find_runic_atlas_gump() -> Optional[Gumps.GumpData]:
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


def _wait_for_runic_atlas_gump(delay: int = 1500) -> Optional[Gumps.GumpData]:
    global GUMP_RUNIC_ATLAS

    # If the gump ID is already known
    if GUMP_RUNIC_ATLAS != 0:
        if not Gumps.WaitForGump(GUMP_RUNIC_ATLAS, delay):
            return None
        return Gumps.GetGumpData(GUMP_RUNIC_ATLAS)

    # Otherwise, use some tricks to identify the gump
    for _ in range(delay // 100):
        gd = _find_runic_atlas_gump()
        if gd is not None:
            GUMP_RUNIC_ATLAS = gd.gumpId
            return gd
        Misc.Pause(100)

    return None


################################################################################
# Helper functions
################################################################################


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


class RunicAtlasSnapshot:
    """
    Represents a static snapshot of the runic atlas.
    """

    page: int
    runes: List[Rune]
    selected_index: int

    def __init__(self):
        self.page = 1
        self.runes = [Rune() for _ in range(48)]
        self.selected_index = -1


class RunicAtlasControl:
    class Buttons:
        @staticmethod
        def close():
            Gumps.CloseGump(GUMP_RUNIC_ATLAS)

        @staticmethod
        def rename():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 1)

        @staticmethod
        def set_default():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 2)

        @staticmethod
        def drop_rune():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 3)

        @staticmethod
        def replace_rune():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 8)

        @staticmethod
        def recall():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 4)

        @staticmethod
        def gate_travel():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 6)

        @staticmethod
        def sacred_journey():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 7)

        @staticmethod
        def next_page():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 1150)

        @staticmethod
        def prev_page():
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 1151)

        @staticmethod
        def select_rune(index: int):
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 100 + index)

        @staticmethod
        def move_up(index: int):
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 2000 + index)

        @staticmethod
        def move_down(index: int):
            Gumps.SendAction(GUMP_RUNIC_ATLAS, 3000 + index)

    @classmethod
    def update_snapshot(cls, snapshot: RunicAtlasSnapshot, gd: Gumps.GumpData) -> None:
        """
        Read the current state of the runic atlas from the gump data.
        """
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
                    snapshot.page = 1
                elif last_button_id == 116:
                    snapshot.page = 2
                elif last_button_id == 132:
                    snapshot.page = 3
            elif args[0] == "croppedtext":
                if last_button_id < 100 or last_button_id >= 148:
                    continue
                if last_button_ln + 1 != line_no:
                    continue
                index = last_button_id - 100
                rune = snapshot.runes[index]
                text_id = int(args[-1])
                color = int(args[-2])
                rune.name = gd.stringList[text_id]
                if color == 331:
                    snapshot.selected_index = index
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
                sextant = _decode_sextant(gd.stringList[text_id])

        if has_selected_entry and sextant is not None:
            snapshot.runes[snapshot.selected_index].x = sextant[0]
            snapshot.runes[snapshot.selected_index].y = sextant[1]

    @classmethod
    def goto_page(cls, snapshot: RunicAtlasSnapshot, page: int, delay: int = 1500) -> bool:
        """
        Move to the specified page in the runic atlas, if the gump is open.
        """
        assert page in (1, 2, 3), "Invalid page number"

        for trial in range(4):
            if trial == 3:
                # This is normally impossible
                return False
            gd = _wait_for_runic_atlas_gump()
            if gd is None:
                return False
            cls.update_snapshot(snapshot, gd)
            if snapshot.page < page:
                cls.Buttons.next_page()
            elif snapshot.page > page:
                cls.Buttons.prev_page()
            else:
                break

        return True

    @staticmethod
    def close():
        """
        Close the current runic atlas gump if it is open.
        """
        gd = _find_runic_atlas_gump()
        if gd is not None:
            Gumps.CloseGump(gd.gumpId)

    @classmethod
    def read_all(cls, read_coordinates: bool = False) -> Optional[RunicAtlasSnapshot]:
        """
        Move to the specified page in the runic atlas, if the gump is open.
        """
        # Read all pages
        snapshot = RunicAtlasSnapshot()
        if not cls.goto_page(snapshot, 3):
            return None

        # Read all coordinates
        if read_coordinates:
            if not cls.goto_page(snapshot, 1):
                return None
            prev_page = 0
            for index in range(48):
                if snapshot.runes[index].name == "Empty":
                    break
                page = 1 + (index // 16)
                if prev_page != page and not cls.goto_page(snapshot, page):
                    return None
                prev_page = page
                cls.Buttons.select_rune(index)
                if not cls.goto_page(snapshot, page):
                    return None

        return snapshot


################################################################################
# Applications
################################################################################

# Gump related
GUMP_ID = hash("JourneyManagerGump") & 0xFFFFFFFF
GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
ID_NEXT = 1
ID_TOGGLE_AUTO = 2
ID_SET_BOOK = 3
ID_TOGGLE_MAXIMIZED = 4
ID_PAGE_PREV = 5
ID_PAGE_NEXT = 6
ID_QUIT = 7
IDMOD_JUMP_TO = 100


class Journey:
    @staticmethod
    def get_best_skill() -> Optional[str]:
        if Player.GetSkillValue("Chivalry") >= CAST_CHIVALRY_SKILL_MIN:
            return "Chivalry"
        elif Player.GetSkillValue("Magery") >= CAST_MAGERY_SKILL_MIN:
            return "Magery"

    @staticmethod
    def get_player_pos_2d() -> Tuple[int, int]:
        p = Player.Position
        return (p.X, p.Y)

    @staticmethod
    def get_player_pos_3d() -> Tuple[int, int, int]:
        p = Player.Position
        return (p.X, p.Y, p.Z)

    @staticmethod
    def get_runic_atlas() -> Optional["Item"]:
        """
        Ask the player to target the runic atlas and return its serial.
        """
        serial = Target.PromptTarget("Target the runic atlas to use for your journey.", 0x3B2)
        item = Items.FindBySerial(serial)
        if serial == 0:
            Misc.SendMessage("No target selected.", 0x3B2)
            return
        if item is None:
            Misc.SendMessage("Invalid target.", 33)
            return
        if item.ItemID not in (0x9C16, 0x9C17):
            Misc.SendMessage("That is not a runic atlas!", 33)
            return
        if item.RootContainer != Player.Backpack.Serial:
            Misc.SendMessage("The runic atlas must be in your inventory.", 33)
            return
        return item

    class InvalidIndexError(Exception):
        pass

    class NotFoundError(Exception):
        pass

    class ParseError(Exception):
        pass

    class NotReadyToRecallException(Exception):
        pass

    class RecallFailedException(Exception):
        pass

    @classmethod
    def move_to(cls, snapshot: RunicAtlasSnapshot, serial: int, index: int):
        """
        Use the runic atlas and move to the specified rune index.

        :param serial: The serial of the runic atlas.
        :param index: The 0-based index of the rune to move to.
        """
        if index < 0 or index >= len(snapshot.runes):
            raise cls.InvalidIndexError("Invalid rune index.")
        if snapshot.runes[index].name == "Empty":
            raise cls.InvalidIndexError("This is an empty entry.")

        # Validate the serial
        runic_atlas = Items.FindBySerial(serial)
        if runic_atlas is None:
            raise cls.NotFoundError()

        RunicAtlasControl.close()
        Items.UseItem(runic_atlas.Serial)

        rune_page = 1 + (index // 16)
        if not RunicAtlasControl.goto_page(snapshot, rune_page):
            raise cls.ParseError()

        RunicAtlasControl.Buttons.select_rune(index)
        Misc.Pause(250)
        if not RunicAtlasControl.goto_page(snapshot, rune_page):
            raise cls.ParseError()

        rune = snapshot.runes[index]
        if snapshot.selected_index != index:
            raise cls.ParseError()

        if cls.get_player_pos_2d() == (rune.x, rune.y) and Player.Map == rune.facet:
            Misc.SendMessage("You are already at the target location.", 68)
            return

        best_skill = cls.get_best_skill()
        if best_skill == "Chivalry":
            if Player.Mana < CAST_CHIVALRY_MANA_MIN:
                raise cls.NotReadyToRecallException(f"Not enough mana to cast Sacred Journey. Required: {CAST_CHIVALRY_MANA_MIN}")
            RunicAtlasControl.Buttons.sacred_journey()
        elif best_skill == "Magery":
            if Player.Mana < CAST_MAGERY_MANA_MIN:
                raise cls.NotReadyToRecallException(f"Not enough mana to cast Recall. Required: {CAST_MAGERY_MANA_MIN}")
            RunicAtlasControl.Buttons.recall()
        else:
            raise cls.NotReadyToRecallException(f"You need either {CAST_CHIVALRY_SKILL_MIN} Chivalry or {CAST_MAGERY_SKILL_MIN} Magery to use this script!")

        Misc.SendMessage(f"Recalling rune: {rune.name} ({rune.x}, {rune.y})", 0x3B2)

        Timer.Create("recall-delay", 3500)
        while Timer.Check("recall-delay"):
            if cls.get_player_pos_2d() == (rune.x, rune.y) and Player.Map == rune.facet:
                Misc.SendMessage("You have arrived at the target location.", 68)
                return
            Misc.Pause(100)

        raise cls.RecallFailedException()


class JourneyManager:
    PREV_INDEX = -1
    """Previous rune index."""
    NEXT_INDEX = 0
    """Next rune index."""
    RUNIC_ATLAS_SERIAL = 0
    """The serial of the runic atlas."""
    SNAPSHOT = None
    """The current snapshot of the runic atlas."""
    MAXIMIZED = False
    """Whether the gump is maximized."""
    AUTO_TRAVEL = False
    """Whether auto travel is enabled."""
    PAGE = 1
    """The current page of the gump."""
    TRAVEL_ENABLED = False
    """When this is set to True, the script will travel to the next rune."""
    GUMP_ALIVE = True
    """Whether the gump in the thread is alive."""

    @classmethod
    def show_gump(cls):
        Gumps.CloseGump(GUMP_ID)

        show_runes = cls.MAXIMIZED and cls.SNAPSHOT is not None

        # Create the gump
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        if show_runes:
            Gumps.AddBackground(gd, 0, 0, 340, 317, 30546)
            Gumps.AddAlphaRegion(gd, 0, 0, 340, 317)
        else:
            Gumps.AddBackground(gd, 0, 0, 340, 125, 30546)
            Gumps.AddAlphaRegion(gd, 0, 0, 340, 125)

        # Last place
        last_name = "N/A"
        if cls.SNAPSHOT is not None and cls.PREV_INDEX >= 0:
            last_name = cls.SNAPSHOT.runes[cls.PREV_INDEX].name
        Gumps.AddLabel(gd, 10, 10, 53, "Last:")
        Gumps.AddLabelCropped(gd, 45, 10, 260, 18, 53, last_name)

        # Next place
        next_name = "N/A"
        if cls.SNAPSHOT is not None and cls.NEXT_INDEX >= 0 and cls.NEXT_INDEX < len(cls.SNAPSHOT.runes):
            next_name = cls.SNAPSHOT.runes[cls.NEXT_INDEX].name
        Gumps.AddLabel(gd, 10, 30, 88, "Next:")
        Gumps.AddLabelCropped(gd, 45, 30, 260, 18, 88, next_name)

        # Buttons
        Gumps.AddButton(gd, 10, 50, 4005, 4007, ID_NEXT, 1, 0)
        Gumps.AddLabelCropped(gd, 45, 52, 100, 18, 1153, "MOVE")
        Gumps.AddButton(gd, 170, 50, 4005, 4007, ID_SET_BOOK, 1, 0)
        Gumps.AddLabelCropped(gd, 205, 52, 100, 18, 1153, "SET BOOK")

        Gumps.AddButton(gd, 10, 70, 4005, 4007, ID_TOGGLE_MAXIMIZED, 1, 0)
        Gumps.AddLabelCropped(gd, 45, 72, 100, 18, 1153, "HIDE RUNES" if cls.MAXIMIZED else "SHOW RUNES")
        Gumps.AddButton(gd, 170, 70, 4005, 4007, ID_QUIT, 1, 0)
        Gumps.AddLabelCropped(gd, 205, 72, 100, 18, 1153, "QUIT")

        if cls.AUTO_TRAVEL:
            Gumps.AddButton(gd, 10, 95, 9027, 9026, ID_TOGGLE_AUTO, 1, 0)
        else:
            Gumps.AddButton(gd, 10, 95, 9026, 9027, ID_TOGGLE_AUTO, 1, 0)
        Gumps.AddLabelCropped(gd, 35, 95, 300, 18, 1153, "Check this to enable auto travel mode")

        # Runes
        if show_runes and cls.SNAPSHOT is not None:
            for i, rune in enumerate(cls.SNAPSHOT.runes):
                page = 1 + (i // 16)
                if page != cls.PAGE:
                    continue
                parity = (i // 8) % 2
                index = i % 8
                x = 10 + (parity * 160)
                y = 120 + (index * 20)
                Gumps.AddButton(gd, x, y + 5, 2103, 2104, IDMOD_JUMP_TO + i, 1, 0)
                Gumps.AddLabelCropped(gd, x + 16, y, 134, 18, 1153, cls.SNAPSHOT.runes[i].name)

            # Buttons
            if cls.PAGE > 1:
                Gumps.AddButton(gd, 10, 285, 4005, 4007, ID_PAGE_PREV, 1, 0)
                Gumps.AddLabelCropped(gd, 45, 287, 100, 18, 1153, "PREV")
            if cls.PAGE < 3:
                Gumps.AddButton(gd, 90, 285, 4005, 4007, ID_PAGE_NEXT, 1, 0)
                Gumps.AddLabelCropped(gd, 125, 287, 100, 18, 1153, "NEXT")

        Gumps.SendGump(GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

    @classmethod
    def process_response(cls) -> None:
        if not Gumps.WaitForGump(GUMP_ID, 3600000):
            return

        gd = Gumps.GetGumpData(GUMP_ID)
        if gd is None:
            return

        if gd.buttonid == 0:
            return

        if gd.buttonid == ID_QUIT:
            Misc.SendMessage("Bye!", 68)
            cls.GUMP_ALIVE = False
            return

        if gd.buttonid == ID_NEXT:
            if cls.SNAPSHOT is None:
                Misc.SendMessage("Please set a runic atlas first.", 33)
                return
            if cls.TRAVEL_ENABLED:
                Misc.SendMessage("You are already travelling.", 0x3B2)
                return
            cls.TRAVEL_ENABLED = True
            return

        if gd.buttonid == ID_SET_BOOK:
            if cls.TRAVEL_ENABLED:
                Misc.SendMessage("This is disabled while travelling.", 0x3B2)
                return
            cls.action_set_book()
            return

        if gd.buttonid == ID_TOGGLE_MAXIMIZED:
            cls.action_toggle_maximize()
            return

        if gd.buttonid == ID_TOGGLE_AUTO:
            cls.action_toggle_auto()

        index = gd.buttonid - IDMOD_JUMP_TO
        if 0 <= index < 48:
            if cls.SNAPSHOT is None:
                Misc.SendMessage("Please set a runic atlas first.", 33)
                return
            if cls.TRAVEL_ENABLED:
                Misc.SendMessage("You are already travelling.", 0x3B2)
                return
            cls.NEXT_INDEX = index
            cls.TRAVEL_ENABLED = True
            return

        if gd.buttonid == ID_PAGE_PREV:
            if cls.PAGE > 1:
                cls.PAGE -= 1
            return

        if gd.buttonid == ID_PAGE_NEXT:
            if cls.PAGE < 3:
                cls.PAGE += 1
            return

    @classmethod
    def action_next(cls) -> bool:
        try:
            if cls.SNAPSHOT is None:
                Misc.SendMessage("Please set a runic atlas first.", 33)
                return False
            if cls.NEXT_INDEX < 0:
                Misc.SendMessage("Invalid next index.", 33)
                return False
            if cls.NEXT_INDEX >= len(cls.SNAPSHOT.runes):
                Misc.SendMessage("No more runes to travel to.", 33)
                return False
            Journey.move_to(cls.SNAPSHOT, cls.RUNIC_ATLAS_SERIAL, cls.NEXT_INDEX)
            return True
        except Journey.InvalidIndexError as e:
            Misc.SendMessage(str(e), 33)
            return False
        except Journey.NotFoundError:
            Misc.SendMessage("Failed to find the runic atlas.", 33)
            return False
        except Journey.ParseError:
            Misc.SendMessage("Failed to parse the runic atlas gump.", 33)
            return False
        except Journey.NotReadyToRecallException as e:
            Misc.SendMessage(str(e), 33)
            return False
        except Journey.RecallFailedException as e:
            Misc.SendMessage("Failed to recall to the target location.", 33)
            return False
        except Exception as e:
            Misc.SendMessage(f"An unexpected error occurred.", 33)
            print(e)
            return False

    @classmethod
    def action_set_book(cls):
        runic_atlas = Journey.get_runic_atlas()
        if runic_atlas is None:
            Misc.SendMessage("Failed to get the runic atlas.", 33)
            return

        RunicAtlasControl.close()
        Items.UseItem(runic_atlas.Serial)

        snapshot = RunicAtlasControl.read_all()
        if snapshot is None:
            Misc.SendMessage("Failed to read the runic atlas gump.", 33)
            return

        RunicAtlasControl.Buttons.close()
        cls.RUNIC_ATLAS_SERIAL = runic_atlas.Serial
        cls.SNAPSHOT = snapshot
        cls.AUTO_TRAVEL = False
        cls.TRAVEL_ENABLED = False
        cls.PREV_INDEX = -1
        cls.NEXT_INDEX = 0
        cls.PAGE = 1
        Misc.SendMessage(f"Runic atlas set.", 68)

    @classmethod
    def action_toggle_maximize(cls):
        if cls.SNAPSHOT is None:
            Misc.SendMessage("Please set a runic atlas first.", 33)
            return
        cls.MAXIMIZED = not cls.MAXIMIZED

    @classmethod
    def action_toggle_auto(cls):
        cls.AUTO_TRAVEL = not cls.AUTO_TRAVEL
        Misc.SendMessage(f"Runic atlas {'enabled' if cls.AUTO_TRAVEL else 'disabled'}.", 68)

    @classmethod
    def start(cls):
        Timer.Create("async-alive", 10000)

        def _thread_loop(cls):
            while cls.GUMP_ALIVE and Timer.Check("async-alive"):
                cls.show_gump()
                cls.process_response()
            Misc.SendMessage("Journey manager stopped.", 0x3B2)

        thread = threading.Thread(target=_thread_loop, args=(cls,))
        thread.start()

        while cls.GUMP_ALIVE:
            Timer.Create("async-alive", 10000)
            if cls.TRAVEL_ENABLED:
                Journal.Clear()
                success = cls.action_next()
                Gumps.SendAction(GUMP_ID, 0)
                if success:
                    cls.PREV_INDEX = cls.NEXT_INDEX
                    cls.NEXT_INDEX = cls.NEXT_INDEX + 1
                # Determine when to stop traveling
                if Journal.Search("The ground is furiously shaking as you notice"):
                    Misc.SendMessage("Wait, you seem to have found an IDOC!", 68)
                    cls.TRAVEL_ENABLED = False
                elif cls.NEXT_INDEX >= 48:
                    cls.TRAVEL_ENABLED = False
                elif not cls.AUTO_TRAVEL:
                    cls.TRAVEL_ENABLED = False
                else:
                    Misc.Pause(CAST_RECOVERY_TIME)
            Misc.Pause(100)

        Misc.SendMessage("Script stopped.", 0x3B2)


if __name__ == "__main__":
    JourneyManager.start()
