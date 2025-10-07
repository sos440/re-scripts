from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import List, Dict, Tuple, Optional, Any, Callable


MAX_FISHING_DIST = 12


class LineOfSight:
    @classmethod
    def test_impassable(cls, p: Tuple[int, int, int]) -> bool:
        x, y, z = p

        # Test land tile
        static_id = Statics.GetLandID(x, y, Player.Map)
        if Statics.GetLandFlag(static_id, "Impassable"):
            z_up = Statics.GetLandZ(x, y, Player.Map)
            z_down = Statics.GetLandZ(x + 1, y + 1, Player.Map)
            z_right = Statics.GetLandZ(x + 1, y, Player.Map)
            z_left = Statics.GetLandZ(x, y + 1, Player.Map)

            if abs(z_up - z_down) <= abs(z_right - z_left):
                z_top = (z_up + z_down) // 2
            else:
                z_top = (z_right + z_left) // 2
            z_bottom = min(z_up, z_down, z_right, z_left)

            if z_bottom <= z < z_top:
                return True

        # Test static tile
        for tile in Statics.GetStaticsTileInfo(x, y, Player.Map):
            if not Statics.GetTileFlag(tile.StaticID, "Impassable"):
                continue
            z_bottom = tile.Z
            z_top = z_bottom + Statics.GetTileHeight(tile.StaticID)
            if z_bottom <= z < z_top:
                return True

        # Test dynamic object
        filter = Items.Filter()
        filter.Enabled = True
        filter.OnGround = True
        for obj in Items.ApplyFilter(filter):
            pos = obj.Position
            if (pos.X, pos.Y) != (x, y):
                continue
            if not Statics.GetTileFlag(obj.ItemID, "Impassable"):
                continue
            z_bottom = pos.Z
            z_top = z_bottom + Statics.GetTileHeight(obj.ItemID)
            if z_bottom <= z < z_top:
                return True

        # No collision!
        return False

    @classmethod
    def check(cls, p1: Tuple[int, int, int], p2: Tuple[int, int, int]) -> bool:
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        if x1 == x2 and y1 == y2 and z1 == z2:
            return True

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        dist = max(abs(dx), abs(dy))
        if dist == 0:
            return True

        # Step through the line and test each point
        for i in range(1, dist):
            x = int(x1 + dx * i / dist)
            y = int(y1 + dy * i / dist)
            z = int(z1 + dz * i / dist)
            if cls.test_impassable((x, y, z)):
                return False

        return True


class FishingPole:
    NEIGHBORHOOD = []

    @classmethod
    def find_fishing_pole(cls) -> Optional["Item"]:
        filter = Items.Filter()
        filter.Enabled = True
        filter.Graphics = CList[Int32]([0x0DC0])
        filter.OnGround = False
        owners = (Player.Serial, Player.Backpack.Serial)
        for item in Items.ApplyFilter(filter):
            if item.RootContainer in owners:
                return item

    @classmethod
    def use_fishing_pole(cls) -> Tuple[bool, str]:
        pole = cls.find_fishing_pole()
        if pole is None:
            return False, ""
        Journal.Clear()
        Items.UseItem(pole.Serial)
        return Journal.WaitJournal("What water do you want to fish in?", 500)

    @classmethod
    def dist_to(cls, x: int, y: int) -> int:
        pos = Player.Position
        return Misc.Distance(pos.X, pos.Y, x, y)

    @classmethod
    def find_water(cls) -> Optional[Tuple[int, int, int, int]]:
        """
        Find the nearest fishing spot.
        """
        # Initialize the neighborhood
        if not cls.NEIGHBORHOOD:
            d = MAX_FISHING_DIST
            nbd = [(x, y) for x in range(-d, d + 1) for y in range(-d, d + 1)]
            cls.NEIGHBORHOOD = sorted(nbd, key=lambda p: max(abs(p[0]), abs(p[1])))

        pos = Player.Position
        for dx, dy in cls.NEIGHBORHOOD:
            x = pos.X + dx
            y = pos.Y + dy
            # Find land tile with "Wet" flag
            static_id = Statics.GetLandID(x, y, Player.Map)
            if Statics.GetLandFlag(static_id, "Wet"):
                z = Statics.GetLandZ(x, y, Player.Map)
                if LineOfSight.check((pos.X, pos.Y, pos.Z), (x, y, z)):
                    return (x, y, z, static_id)
            # Find static tile with "Wet" flag
            for tile in Statics.GetStaticsTileInfo(x, y, Player.Map):
                if Statics.GetTileFlag(tile.StaticID, "Wet"):
                    z = tile.Z
                    if LineOfSight.check((pos.X, pos.Y, pos.Z), (x, y, z)):
                        return (x, y, z, tile.StaticID)


def main():
    p1 = Target.PromptGroundTarget("Target fishing spot.", 0x3B2)
    if p1.X == -1 or p1.Y == -1:
        Misc.SendMessage("No fishing spot selected.", 33)
        return

    p2 = Player.Position
    test = LineOfSight.check((p1.X, p1.Y, p1.Z), (p2.X, p2.Y, p2.Z))
    Misc.SendMessage(f"Line of sight test: {test}", 68)


if __name__ == "__main__":
    while True:
        main()
