from typing import Optional, Tuple, List
from System.Collections.Generic import List as CList  # type:ignore
from System import Int32  # type:ignore


# List of ItemIDs (Types) to drop nearby
DROP_ITEMIDS = [
    0x09F1,  # raw meat
]


def build_neighbors() -> List[Tuple[int, int]]:
    neighbors = []
    for x in (-2, -1, 0, 1, 2):
        for y in (-2, -1, 0, 1, 2):
            if x == 0 and y == 0:
                continue
            neighbors.append((x, y))
    return sorted(neighbors, key=lambda pos: max(abs(pos[0]), abs(pos[1])))


NEIGHBORS = build_neighbors()


def get_surface_at(x, y) -> Optional[Tuple[int, int, int, int]]:
    arg = (x, y, Player.Map)
    land_tile = Statics.GetLandID(*arg)
    if not Statics.GetLandFlag(land_tile, "Impassable"):
        return (x, y, Statics.GetLandZ(*arg), None)
    for tile in Statics.GetStaticsTileInfo(*arg):
        if not Statics.GetTileFlag(tile.StaticID, "Impassable"):
            return (x, y, tile.Z, tile.StaticID)


def get_surface_nearby() -> Optional[Tuple[int, int, int, int]]:
    x = Player.Position.X
    y = Player.Position.Y
    for dx, dy in NEIGHBORS:
        result = get_surface_at(x + dx, y + dy)
        if result is not None:
            return result


def get_item_nearby(itemid) -> List["Item"]:
    filter = Items.Filter()
    filter.Enabled = True
    filter.RangeMax = 2
    filter.OnGround = True
    filter.Graphics = CList[Int32]([itemid])
    return Items.ApplyFilter(filter)


def drop_nearby(item: "Item"):
    if item is None:
        return
    
    items_ground = get_item_nearby(item.ItemID)
    if items_ground:
        Items.Move(item.Serial, items_ground[0].Serial, -1)
        Misc.Pause(1000)
        return
    
    result = get_surface_nearby()
    if result is None:
        Misc.SendMessage("No surface available nearby.", 0x21)
        return
    
    x, y, z, tile = result
    Items.MoveOnGround(item.Serial, -1, x, y, z)
    Misc.Pause(1000)


def drop_all():
    if Player.IsGhost:
        return
    
    filter = Items.Filter()
    filter.Enabled = True
    filter.Graphics = CList[Int32](DROP_ITEMIDS)
    filter.OnGround = False
    for item in Items.ApplyFilter(filter):
        if item.RootContainer != Player.Backpack.Serial:
            continue
        drop_nearby(item)


if __name__ == "__main__":
    drop_all()