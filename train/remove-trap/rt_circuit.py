import sys
from System import Byte, Int32  # type: ignore
from enum import Enum
from queue import Queue
from typing import List, Tuple, Set, Any, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *


################################################################################
# Setting
################################################################################


# Serial of the circuit trap
# If this is set to zero, the script will ask you to choose one at the beginning
CT_KIT_SERIAL = 0

# Gump ID of the circuit trap
CT_GUMP_ID = 0


################################################################################
# Circuit Logic Part
################################################################################


class CircuitMoves(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class CircuitPos:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, CircuitPos):
            return False
        return self.x == other.x and self.y == other.y

    def __gt__(self, other: "CircuitPos"):
        """Lexicographical comparison."""
        return self.x > other.x or (self.x == other.x and self.y > other.y)

    def __lt__(self, other: "CircuitPos"):
        """Lexicographical comparison."""
        return self.x < other.x or (self.x == other.x and self.y < other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other: "CircuitPos | CircuitMoves"):
        if isinstance(other, CircuitMoves):
            other = CircuitPos.from_move(other)
        return CircuitPos(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "CircuitPos | CircuitMoves"):
        if isinstance(other, CircuitMoves):
            other = CircuitPos.from_move(other)
        return CircuitPos(self.x - other.x, self.y - other.y)

    def __iadd__(self, other: "CircuitPos | CircuitMoves"):
        if isinstance(other, CircuitMoves):
            other = CircuitPos.from_move(other)
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: "CircuitPos | CircuitMoves"):
        if isinstance(other, CircuitMoves):
            other = CircuitPos.from_move(other)
        self.x -= other.x
        self.y -= other.y
        return self

    def copy(self):
        return CircuitPos(self.x, self.y)

    @classmethod
    def from_move(cls, move: CircuitMoves):
        if move == CircuitMoves.UP:
            return CircuitPos(0, -1)
        elif move == CircuitMoves.RIGHT:
            return CircuitPos(1, 0)
        elif move == CircuitMoves.DOWN:
            return CircuitPos(0, 1)
        elif move == CircuitMoves.LEFT:
            return CircuitPos(-1, 0)
        else:
            raise ValueError("Invalid move.")


class CircuitProjection:
    dim: int
    occupied: Set[CircuitPos]
    last_pos: Optional[CircuitPos]

    def __init__(self):
        self.dim = 0
        self.occupied = set()
        self.last_pos = None

    def __eq__(self, other: Any):
        if not isinstance(other, CircuitProjection):
            return False
        return self.dim == other.dim and self.occupied == other.occupied and self.last_pos == other.last_pos
    
    def __repr__(self) -> str:
        return f"dim: {self.dim}, occupied: <set of size {len(self.occupied)}>, last_pos: {self.last_pos}"


class CircuitPuzzle:
    class InvalidException(Exception):
        pass

    symbol_dict = {
        CircuitMoves.UP: "↑",
        CircuitMoves.RIGHT: "→",
        CircuitMoves.DOWN: "↓",
        CircuitMoves.LEFT: "←",
    }

    dim: int
    moves: List[CircuitMoves]

    def __init__(self, dim: int):
        self.dim = dim
        self.moves = []

    def __eq__(self, other: Any):
        if not isinstance(other, CircuitPuzzle):
            return False
        return self.dim == other.dim and self.moves == other.moves

    def get_start(self) -> CircuitPos:
        return CircuitPos(0, 0)

    def get_goal(self) -> CircuitPos:
        return CircuitPos(self.dim - 1, self.dim - 1)

    def is_on_board(self, pos: CircuitPos) -> bool:
        """Test if the position is valid."""
        return 0 <= pos.x < self.dim and 0 <= pos.y < self.dim

    def is_solved(self) -> bool:
        """Check if the puzzle is solved."""
        return self.get_goal() in self.build_path()

    def build_path(self) -> List[CircuitPos]:
        """Build the path from the moves."""
        path: list[CircuitPos] = [self.get_start()]
        for move in self.moves:
            next_pos = path[-1] + move
            if next_pos in path:
                raise CircuitPuzzle.InvalidException("The path is self-intersecting.")
            path.append(next_pos)
        return path

    def project(self, end: Optional[int] = None) -> CircuitProjection:
        """Project the current state of the puzzle."""
        path = self.build_path()
        if end is not None:
            assert end > 0 and end <= len(path), "Invalid end index."
            path = path[:end]
        proj = CircuitProjection()
        proj.dim = self.dim
        proj.occupied = set(path)
        proj.last_pos = path[-1]
        return proj

    def get_next_moves(self) -> List[CircuitMoves]:
        path = self.build_path()

        # If the goal is reached, return an empty list
        if path[-1] == self.get_goal():
            return []

        # Calculate the set of valid future positions
        # This is essentially the connected complement containing the goal
        set_valid_pos: set[CircuitPos] = set()
        q: Queue[CircuitPos] = Queue()
        q.put(self.get_goal())
        while not q.empty():
            cur_pos = q.get()
            # Check if the position is valid
            if cur_pos in path:
                continue
            if cur_pos in set_valid_pos:
                continue
            if not self.is_on_board(cur_pos):
                continue
            set_valid_pos.add(cur_pos)
            # Add the neighbors to the queue
            for move in CircuitMoves:
                q.put(cur_pos + move)

        # Check the possible moves
        next_moves = [move for move in CircuitMoves if ((path[-1] + move) in set_valid_pos)]
        if len(next_moves) == 0:
            raise CircuitPuzzle.InvalidException("No moves available.")

        return next_moves

    def copy(self) -> "CircuitPuzzle":
        copy = CircuitPuzzle(self.dim)
        copy.moves = self.moves.copy()
        return copy

    def print_moves(self) -> str:
        return "".join(CircuitPuzzle.symbol_dict[char] for char in self.moves)


################################################################################
# Execution Part
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


class CircuitAgent:
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

    @classmethod
    def WaitForGump(cls, delay: int) -> bool:
        """
        Wait for the gump to appear and returns whether it is open or not.
        """
        global CT_GUMP_ID
        if delay == 0:
            if CT_GUMP_ID == 0:
                CT_GUMP_ID = _get_gump_by_text("Use the Directional Controls to")
            return Gumps.HasGump(CT_GUMP_ID)
        else:
            if CT_GUMP_ID == 0:
                CT_GUMP_ID = _wait_for_gump_by_text("Use the Directional Controls to", delay)
                return CT_GUMP_ID != 0
            return Gumps.WaitForGump(CT_GUMP_ID, delay)

    @classmethod
    def Open(cls) -> None:
        if cls.WaitForGump(0):
            Gumps.SendAction(CT_GUMP_ID, 0)

        Gumps.ResetGump()

        Timer.Create("skill-cooldown", 10000)
        while Timer.Check("skill-cooldown"):
            Player.UseSkill("Remove Trap")
            if not Target.WaitForTarget(1000, False):
                continue
            Target.TargetExecute(CT_KIT_SERIAL)
            if not cls.WaitForGump(1500):
                Misc.SendMessage("Remove Trap is applied onto the target, but no gump is detected.", 0x21)
                raise cls.GumpNotFoundException("Failed to open the gump.")
            return
        raise cls.GumpNotFoundException("Failed to open the gump.")

    @classmethod
    def Command(cls, move: CircuitMoves) -> None:
        assert CT_GUMP_ID != 0, "Gump ID is not set."
        if move == CircuitMoves.UP:
            Gumps.SendAction(CT_GUMP_ID, 1)
        elif move == CircuitMoves.RIGHT:
            Gumps.SendAction(CT_GUMP_ID, 2)
        elif move == CircuitMoves.DOWN:
            Gumps.SendAction(CT_GUMP_ID, 3)
        elif move == CircuitMoves.LEFT:
            Gumps.SendAction(CT_GUMP_ID, 4)

    @classmethod
    def ParseGump(cls) -> CircuitProjection:
        """
        Parse the gump data and return the current state of the puzzle.
        """
        gd = Gumps.GetGumpData(CT_GUMP_ID)
        if gd is None:
            raise cls.GumpNotFoundException("Failed to get the gump data.")

        res = CircuitProjection()
        for line in gd.layoutPieces:
            args = line.lower().strip().split(" ")
            if not args[0] == "gumppic":
                continue
            x, y, grpid = int(args[1]), int(args[2]), int(args[3])
            # Blue cells
            if grpid == 2152:
                px = (x - 110) // 40
                py = (y - 135) // 40
                res.occupied.add(CircuitPos(px, py))
            # Red cell
            if grpid == 2472:
                px = (x - 110) // 40
                py = (y - 135) // 40
                if px == py and px in (2, 3, 4):
                    res.dim = px + 1
            # White blob
            if grpid == 5032:
                px = (x - 110) // 40
                py = (y - 135) // 40
                res.last_pos = CircuitPos(px, py)

        if res.dim == 0:
            raise cls.GumpParseException("Failed to parse the puzzle dimension.")
        if res.last_pos is None:
            raise cls.GumpParseException("Failed to find the last successful position.")
        if len(res.occupied) == 0:
            raise cls.GumpParseException("Failed to find the occupied cells.")
        return res

    @classmethod
    def ValidatePuzzle(cls, puzzle: CircuitPuzzle, end: Optional[int] = None) -> None:
        cur_proj = cls.ParseGump()
        if cur_proj != puzzle.project(end):
            raise cls.StateMismatchException(
                "The current state of the board does not match the agent's internal state."
            )

    @classmethod
    def WaitForResult(cls, puzzle: CircuitPuzzle, move: CircuitMoves) -> "CircuitAgent.Result":
        """
        Wait for the result of the move and update the puzzle state accordingly.
        Returns True if the puzzle is solved, False otherwise.
        """
        Timer.Create("result-wait", 1500)
        while Timer.Check("result-wait"):
            if cls.WaitForGump(100):
                puzzle.moves.append(move)
                cls.ValidatePuzzle(puzzle)
                return cls.Result.MoveFound
            if Journal.Search("You successfully disarm the trap!"):
                return cls.Result.PuzzleSolved
            if Journal.Search("You fail to disarm the trap and reset it."):
                Misc.Pause(9000)  # You already know you need to wait 9 seconds
                cls.Open()
                for j, move in enumerate(puzzle.moves):
                    cls.Command(move)
                    if not cls.WaitForGump(1500):
                        raise cls.GumpNotFoundException("Failed to follow the path.")
                    cls.ValidatePuzzle(puzzle, j + 2)
                return cls.Result.MoveNotFound

        raise cls.ResultNotFoundException("Failed to determine the next move.")

    # Solver
    @classmethod
    def Solve(cls) -> None:
        # Open the gump
        cls.Open()

        # Initialize the puzzle
        cur_proj = cls.ParseGump()
        puzzle = CircuitPuzzle(cur_proj.dim)

        # Main loop
        while not puzzle.is_solved():
            if not cls.WaitForGump(0):
                raise cls.GumpNotFoundException("This should never happen by the logic. Something is wrong.")

            if len(puzzle.moves) > 0:
                Misc.SendMessage(f"Currently {len(puzzle.moves)} correct moves are known.", 0x47E)

            for i, move in enumerate(puzzle.get_next_moves()):
                Journal.Clear()
                cls.Command(move)

                res = cls.WaitForResult(puzzle, move)
                if res == cls.Result.MoveFound:
                    Misc.SendMessage(f"Next move found: {CircuitPuzzle.symbol_dict[move]}", 0x47E)
                    break
                elif res == cls.Result.PuzzleSolved:
                    Misc.SendMessage("Puzzle solved!", 0x47E)
                    return
                elif res == cls.Result.MoveNotFound:
                    continue
                else:
                    raise cls.ResultNotFoundException("This should never happen.")


################################################################################
# Main Loop
################################################################################


if __name__ == "__main__":
    # Set the training kit
    if CT_KIT_SERIAL == 0x00000000:
        target_id = Target.PromptTarget("Choose a circuit trap training kit.", 0x47E)
        if target_id == 0:
            Misc.SendMessage("Targeting cancelled.", 0x47E)
            sys.exit(99)

        item = Items.FindBySerial(target_id)
        if item is None:
            Misc.SendMessage("Failed to identify the target.", 0x21)
            sys.exit(99)
        if item.ItemID != 0xA393:
            Misc.SendMessage("This is not a circuit training kit!", 0x21)
            sys.exit(99)
        if "circuit trap training kit" not in item.Name.lower():
            Misc.SendMessage("This is not a circuit training kit!", 0x21)
            sys.exit(99)

        CT_KIT_SERIAL = target_id

    # Let's get to the puzzle hell
    while Player.Connected:
        cur_skill = Player.GetSkillValue("Remove Trap")
        if cur_skill >= 100.0:
            Misc.SendMessage("You are a grandmaster!", 0x47E)
            sys.exit(99)
        # elif cur_skill >= 100.0:
        #     CT_DIM = 5
        # elif cur_skill >= 80.0:
        #     CT_DIM = 4
        # else:
        #     CT_DIM = 3

        # try:
        #     CircuitAgent.Solve()
        # except CircuitPuzzle.InvalidException as e:
        #     Misc.SendMessage("Something went wrong within the internal puzzle-solving logic.", 0x21)
        # except CircuitAgent.GumpNotFoundException as e:
        #     Misc.SendMessage("I've waited long but failed to detect the gump. Well, let's start over!", 0x21)
        # except CircuitAgent.GumpParseException as e:
        #     Misc.SendMessage(
        #         "Failed to parse the gump. This should not happen, so shame the developer! Also, let's start over!",
        #         0x21,
        #     )
        # except CircuitAgent.StateMismatchException as e:
        #     Misc.SendMessage(
        #         "The state of the gump does not match the internal state. This can happen, but anyway, let's start over!",
        #         0x21,
        #     )
        # except CircuitAgent.ResultNotFoundException as e:
        #     Misc.SendMessage(
        #         "Failed to determine what came out of the last attempt. I'm lost, so let's start over!", 0x21
        #     )
        # except Exception as e:
        #     Misc.SendMessage(f"Error: {e}")

        # Debugging, errors are not handled
        CircuitAgent.Solve()

        Misc.Pause(9000)
