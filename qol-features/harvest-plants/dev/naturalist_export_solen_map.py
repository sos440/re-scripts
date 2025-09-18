from AutoComplete import *
from typing import Optional, Tuple
import queue


def get_player_pos():
    pos = Player.Position
    return pos.X, pos.Y, pos.Z


def check_impassable(x, y, map):
    if Statics.GetLandFlag(Statics.GetLandID(x, y, map), "Impassable"):
        return True
    for static in Statics.GetStaticsTileInfo(x, y, map):
        flags = str(Statics.GetItemData(static.StaticID).Flags)
        if "Impassable" in flags:
            return True
    return False


class PathfindTile:
    x: int
    y: int
    passable: bool
    next: Tuple[int, int]
    cost: float

    def __init__(
        self,
        x: int,
        y: int,
        passable: bool,
        cost: float = float("inf"),
    ):
        self.x = x
        self.y = y
        self.passable = passable
        self.next = (0, 0)
        self.cost = cost

    def __lt__(self, other: "PathfindTile"):
        return self.cost < other.cost

    def __gt__(self, other: "PathfindTile"):
        return self.cost > other.cost

    def neighbors_perp(self):
        """Get the 4 perpendicular neighbors (N, E, W, S)"""
        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            yield (self.x + dx, self.y + dy)

    def neighbors_diag(self):
        """Get the 4 diagonal neighbors (Left, Up, Right, Down)"""
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            yield (self.x + dx, self.y + dy)


# Build the map
x0, y0 = 5631, 1775
w, h = 305, 261
tiles = {}
for i in range(h):
    for j in range(w):
        x = x0 + j
        y = y0 + i
        flag = check_impassable(x, y, 1)
        tiles[(x, y)] = PathfindTile(x, y, not flag)


goals = [
    (5661, 1955),  # Tunnel F
    (5739, 1941),  # Trinsic nest
    (5901, 1878),  # Tunnel A
    (5868, 1795),  # Minoc nest
    (5912, 1944),  # Desert nest
    (5742, 1820),  # Yew nest
    (5671, 1866),  # Secret nest
]

for goal in goals:
    print(f"Calculating minimal flow map to {goal}...")
    goal_tile = tiles[goal]
    if not goal_tile.passable:
        print(f"  Goal {goal} is not passable, skipping.")
        continue

    goal_tile.cost = 0
    q = queue.PriorityQueue()
    q.put(goal_tile)

    def _update_tile(prev: PathfindTile, cur: PathfindTile):
        next = (prev.x - cur.x, prev.y - cur.y)
        if prev.next == (0, 0) or prev.next == next:
            new_cost = prev.cost + 1
        else:
            # Turning incurs a penalty
            new_cost = prev.cost + 2.5

        if new_cost < cur.cost:
            cur.cost = new_cost
            cur.next = next
            q.put(cur)
        if new_cost == cur.cost and next == prev.next:
            # Break ties by preferring straight paths
            cur.next = next
            q.put(cur)

    while not q.empty():
        tile = q.get()
        for nbd in tile.neighbors_diag():
            # Get the passable neighbor
            if nbd not in tiles:
                continue
            nbd_tile = tiles[nbd]
            if not nbd_tile.passable:
                continue
            # Check if both adjacent perpendicular tiles are passable
            adj1 = (tile.x, nbd[1])
            adj2 = (nbd[0], tile.y)
            if adj1 in tiles and adj2 in tiles and tiles[adj1].passable and tiles[adj2].passable:
                _update_tile(tile, nbd_tile)
        for nbd in tile.neighbors_perp():
            # Get the passable neighbor
            if nbd not in tiles:
                continue
            nbd_tile = tiles[nbd]
            if not nbd_tile.passable:
                continue
            _update_tile(tile, nbd_tile)


with open("Data/solen_map.txt", "w", encoding="utf-8") as f:
    for i in range(h):
        for j in range(w):
            x = x0 + j
            y = y0 + i
            tile = tiles[(x, y)]
            if not tile.passable:
                f.write(" ")
            elif tile.cost == float("inf"):
                f.write("X")
            elif tile.next == (0, 0):
                f.write("@")
            elif tile.next == (1, 0):
                f.write("→")  # East
            elif tile.next == (-1, 0):
                f.write("←")  # West
            elif tile.next == (0, 1):
                f.write("↓")  # South
            elif tile.next == (0, -1):
                f.write("↑")  # North
            elif tile.next == (-1, -1):
                f.write("↖")  # Up
            elif tile.next == (1, 1):
                f.write("↘")  # Down
            elif tile.next == (1, -1):
                f.write("↗")  # Right
            elif tile.next == (-1, 1):
                f.write("↙")  # Left
            else:
                f.write("?")  # Unknown
        f.write("\n")


print("Done.")
