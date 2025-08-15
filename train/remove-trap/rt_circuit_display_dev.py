from enum import Enum


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


class Test:
    DisplayID = 0x12345678
    
    # Display
    @classmethod
    def Display(cls) -> None:
        # Test data
        dim = 5
        moves = [CircuitMoves.RIGHT, CircuitMoves.DOWN, CircuitMoves.DOWN, CircuitMoves.LEFT, CircuitMoves.DOWN]
        path = [CircuitPos(0, 0)]
        for move in moves:
            next_pos = path[-1] + move
            if next_pos in path:
                raise Exception("The path is self-intersecting.")
            path.append(next_pos)
        
        Gumps.CloseGump(cls.DisplayID)
        gd = Gumps.CreateGump(movable=True)
        
        # Draw bg
        cell_size = 30
        gump_size = 10 + dim * cell_size
        Gumps.AddBackground(gd, 0, 0, gump_size, gump_size, 30546)
        Gumps.AddAlphaRegion(gd, 0, 0, gump_size, gump_size)
        
        # Draw cells
        for x in range(dim):
            for y in range(dim):
                pos = CircuitPos(x, y)
                if pos == path[-1]:
                    color = 4
                elif pos in path:
                    color = 2065
                elif x == dim - 1 and y == dim - 1:
                    color = 33
                else:
                    color = 0x3B2
                cx = 5 + cell_size * x + (cell_size - 23) // 2
                cy = 5 + cell_size * y + (cell_size - 23) // 2
                Gumps.AddImage(gd, cx, cy, 1607, color)
        
        # Draw arrows
        for i, move in enumerate(moves):
            p0, p1 = path[i], path[i+1]
            cx = round(5 + cell_size * (2 * p0.x + p1.x) / 3 + (cell_size / 2) - 8)
            cy = round(5 + cell_size * (2 * p0.y + p1.y) / 3 + (cell_size / 2) - 8)
            if move == CircuitMoves.UP:
                grp = 5600
            elif move == CircuitMoves.RIGHT:
                grp = 5601
            elif move == CircuitMoves.DOWN:
                grp = 5602
            elif move == CircuitMoves.LEFT:
                grp = 5603
            else:
                raise ValueError("Invalid move.")
            Gumps.AddImage(gd, cx, cy, grp, 1152)
            
        Gumps.SendGump(cls.DisplayID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


Test.Display()