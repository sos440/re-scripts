import sys
from System import Byte, Int32  # type: ignore
from enum import Enum
from typing import List, Tuple, Dict, Set, Any, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


################################################################################
# Setting
################################################################################


# Serial of the cylinder trap
# If this is set to zero, the script will ask you to choose one at the beginning
CT_KIT_SERIAL = 0

# Gump ID of the cylinder trap puzzle board
GUMP_PUZZLE_ID = 0

# Gump ID of the cylinder trap result dialog
GUMP_RESULT_ID = 0


################################################################################
# Logic Part
################################################################################


class CylTypes(Enum):
    Empty = -1
    White = 0
    Blue = 1
    Green = 2
    Orange = 3
    Purple = 4
    Red = 5
    Navy = 6
    Yellow = 7


CylTypeList = [
    CylTypes.White,
    CylTypes.Blue,
    CylTypes.Green,
    CylTypes.Orange,
    CylTypes.Purple,
    CylTypes.Red,
    CylTypes.Navy,
    CylTypes.Yellow,
]


class CylPuzzleState:
    guess: List[CylTypes]
    first: CylTypes
    used: List[CylTypes]

    def __init__(self):
        self.guess = [CylTypes.Empty] * 5
        self.first = CylTypes.Empty
        self.used = []

    def __repr__(self) -> str:
        return f"guess: {self.guess}, first: {self.first}, used: {self.used}"


class CylPuzzle:
    state: CylPuzzleState
    sol_space: List[Set[CylTypes]]

    def __init__(self):
        self.state = CylPuzzleState()
        self.sol_space = [set(CylTypeList) for _ in range(5)]


################################################################################
# Agent Part
################################################################################


def _get_gump_by_text(text: str) -> int:
    """Find the ID of a gump containing the provided text."""
    for gumpid in Gumps.AllGumpIDs():
        for line in Gumps.GetLineList(gumpid, False):
            if text in line:
                return gumpid
    return 0


def _wait_for_gump_by_text(text: str, delay: int) -> int:
    """Wait until the ID of a gump containing the provided text is found."""
    Timer.Create("gump-detect", delay)
    while Timer.Check("gump-detect"):
        gumpid = _get_gump_by_text(text)
        if gumpid != 0:
            return gumpid
        Misc.Pause(100)
    return 0


class CylinderAgent:
    class GumpNotFoundException(Exception):
        pass

    class GumpParseException(Exception):
        pass

    class StateMismatchException(Exception):
        pass

    class ResultNotFoundException(Exception):
        pass

    class Result(Enum):
        MoveFound = 1
        MoveNotFound = 2
        PuzzleSolved = 3

    class Buttons(Enum):
        Close = 0
        Submit = 1
        SelectWhite = 10
        SelectBlue = 11
        SelectGreen = 12
        SelectOrange = 13
        SelectPurple = 14
        SelectRed = 15
        SelectNavy = 16
        SelectYellow = 17

    class GumpScanMode(Enum):
        ReadFirstSlot = 1
        ReadUsedColors = 2
        ReadGuess = 3
        ReadCorrectSlots = 4
        ReadIncorrectSlots = 5

    GraphicMap: Dict[int, CylTypes] = {
        3699: CylTypes.Empty,
        6255: CylTypes.White,
        6250: CylTypes.Blue,
        6251: CylTypes.Green,
        6252: CylTypes.Orange,
        6253: CylTypes.Purple,
        6254: CylTypes.Red,
        6249: CylTypes.Navy,
        6256: CylTypes.Yellow,
    }

    @classmethod
    def WaitForPuzzleGump(cls, delay: int) -> bool:
        global GUMP_PUZZLE_ID
        if delay == 0:
            if GUMP_PUZZLE_ID == 0:
                GUMP_PUZZLE_ID = _get_gump_by_text("A Puzzle Lock")
            return Gumps.HasGump(GUMP_PUZZLE_ID)
        else:
            if GUMP_PUZZLE_ID == 0:
                GUMP_PUZZLE_ID = _wait_for_gump_by_text("A Puzzle Lock", delay)
                return GUMP_PUZZLE_ID != 0
            return Gumps.WaitForGump(GUMP_PUZZLE_ID, delay)

    @classmethod
    def WaitForResultGump(cls, delay: int) -> bool:
        global GUMP_RESULT_ID
        if delay == 0:
            if GUMP_RESULT_ID == 0:
                GUMP_RESULT_ID = _get_gump_by_text("Thou hast failed to solve the puzzle!")
            return Gumps.HasGump(GUMP_RESULT_ID)
        else:
            if GUMP_RESULT_ID == 0:
                GUMP_RESULT_ID = _wait_for_gump_by_text("Thou hast failed to solve the puzzle!", delay)
                return GUMP_RESULT_ID != 0
            return Gumps.WaitForGump(GUMP_RESULT_ID, delay)

    @classmethod
    def Open(cls) -> None:
        if cls.WaitForPuzzleGump(0):
            Gumps.SendAction(GUMP_PUZZLE_ID, 0)

        Gumps.ResetGump()

        Timer.Create("skill-cooldown", 10000)
        while Timer.Check("skill-cooldown"):
            Player.UseSkill("Remove Trap")
            if not Target.WaitForTarget(1000, False):
                continue
            Target.TargetExecute(CT_KIT_SERIAL)
            if not cls.WaitForPuzzleGump(1500):
                Misc.SendMessage("Remove Trap is applied onto the target, but no gump is detected.", 0x21)
                raise cls.GumpNotFoundException("Failed to open the gump.")
            return
        raise cls.GumpNotFoundException("Failed to open the gump.")

    @classmethod
    def ParsePuzzleGump(cls) -> CylPuzzleState:
        gd = Gumps.GetGumpData(GUMP_PUZZLE_ID)
        if gd is None:
            raise cls.GumpParseException("Failed to find the gump.")

        res = CylPuzzleState()
        mode = cls.GumpScanMode.ReadFirstSlot
        slot = 0
        for line in gd.layoutPieces:
            args = line.strip().split()
            if args[0] == "xmfhtmlgump":
                if args[5] == "1018312":
                    mode = cls.GumpScanMode.ReadFirstSlot
                    continue
                if args[5] == "1018313":
                    mode = cls.GumpScanMode.ReadUsedColors
                    continue
                if args[5] == "1018311":
                    mode = cls.GumpScanMode.ReadGuess
                    continue
            if args[0] == "tilepic":
                grp = int(args[3])
                if not grp in cls.GraphicMap:
                    continue
                if mode == cls.GumpScanMode.ReadFirstSlot:
                    res.first = cls.GraphicMap[grp]
                    continue
                if mode == cls.GumpScanMode.ReadUsedColors:
                    res.used.append(cls.GraphicMap[grp])
                    continue
                if mode == cls.GumpScanMode.ReadGuess:
                    if slot >= len(res.guess):
                        break  # Done reading
                    res.guess[slot] = cls.GraphicMap[grp]
                    slot += 1
                    continue

        return res

    @classmethod
    def ParseResultGump(cls) -> Tuple[int, int]:
        gd = Gumps.GetGumpData(GUMP_RESULT_ID)
        if gd is None:
            raise cls.GumpParseException("Failed to find the gump.")

        mode = None
        correct_slot = 0
        incorrect_slot = 0
        for line in gd.layoutPieces:
            args = line.strip().split()
            if args[0] == "xmfhtmlgump":
                if args[5] == "1018315":
                    mode = cls.GumpScanMode.ReadCorrectSlots
                    continue
                if args[5] == "1018316":
                    mode = cls.GumpScanMode.ReadIncorrectSlots
                    continue
            if args[0] == "text":
                if mode == cls.GumpScanMode.ReadCorrectSlots:
                    index = int(args[4])
                    if index >= len(gd.gumpData):
                        raise cls.GumpParseException("Failed to parse the gump.")
                    correct_slot = int(gd.gumpData[index])
                    continue
                if mode == cls.GumpScanMode.ReadIncorrectSlots:
                    index = int(args[4])
                    if index >= len(gd.gumpData):
                        raise cls.GumpParseException("Failed to parse the gump.")
                    incorrect_slot = int(gd.gumpData[index])
                    continue

        return correct_slot, incorrect_slot

    @classmethod
    def Command(cls, button: "CylinderAgent.Buttons", slot: int = -1) -> None:
        if button == cls.Buttons.Close:
            Gumps.CloseGump(GUMP_PUZZLE_ID)
        if button == cls.Buttons.Submit:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 1, [0], [], [])

        assert slot != -1, "Slot must be specified for the color selection."
        if button == cls.Buttons.SelectWhite:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 10, [slot], [], [])
        if button == cls.Buttons.SelectBlue:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 11, [slot], [], [])
        if button == cls.Buttons.SelectGreen:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 12, [slot], [], [])
        if button == cls.Buttons.SelectOrange:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 13, [slot], [], [])
        if button == cls.Buttons.SelectPurple:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 14, [slot], [], [])
        if button == cls.Buttons.SelectRed:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 15, [slot], [], [])
        if button == cls.Buttons.SelectNavy:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 16, [slot], [], [])
        if button == cls.Buttons.SelectYellow:
            Gumps.SendAdvancedAction(GUMP_PUZZLE_ID, 17, [slot], [], [])


################################################################################
# Unit Test
################################################################################

if __name__ == "__main__":
    CT_KIT_SERIAL = Target.PromptTarget("Select the cylinder trap kit.")
    CylinderAgent.Open()
    res = CylinderAgent.ParsePuzzleGump()
    
    