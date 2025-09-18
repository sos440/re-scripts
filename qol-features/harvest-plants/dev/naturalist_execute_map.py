from AutoComplete import *
import os


script_path = os.path.dirname(__file__)


x0, y0 = 5631, 1775
tiles = {}
with open(os.path.join(script_path, "assets/solen_map.txt"), "r", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        for j, c in enumerate(line):
            if c not in (" ", "X"):
                tiles[(x0 + j, y0 + i)] = c


def get_player_pos():
    pos = Player.Position
    return (pos.X, pos.Y)


def execute_naturalist_map(timeout=60000):
    Timer.Create("timeout", timeout)
    while Timer.Check("timeout"):
        pos = get_player_pos()
        if pos not in tiles:
            Misc.SendMessage("Out of bound!", 33)
            return False
        tile = tiles[pos]
        if tile == "@":
            # Reached the end
            return True
        if tile == "→":
            Player.Run("East")
        elif tile == "←":
            Player.Run("West")
        elif tile == "↑":
            Player.Run("North")
        elif tile == "↓":
            Player.Run("South")
        elif tile == "↗":
            Player.Run("Right")
        elif tile == "↙":
            Player.Run("Left")
        elif tile == "↖":
            Player.Run("Up")
        elif tile == "↘":
            Player.Run("Down")
        else:
            Misc.SendMessage("Unknown direction", 33)
            return False
        Misc.Pause(100)


if __name__ == "__main__":
    success = execute_naturalist_map()
    print(success)