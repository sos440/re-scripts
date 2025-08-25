from AutoComplete import *
from typing import List, Tuple, Dict, Iterable, Any
from enum import Enum


class SortKey(Enum):
    COLOR = 1
    NAME = 2


class _Dir(Enum):
    Right = 1
    Left = 2
    Up = 3
    Down = 4


class SortDir(Enum):
    RightThenDown = (_Dir.Right, _Dir.Down)
    RightThenUp = (_Dir.Right, _Dir.Up)
    LeftThenDown = (_Dir.Left, _Dir.Down)
    LeftThenUp = (_Dir.Left, _Dir.Up)
    UpThenRight = (_Dir.Up, _Dir.Right)
    UpThenLeft = (_Dir.Up, _Dir.Left)
    DownThenRight = (_Dir.Down, _Dir.Right)
    DownThenLeft = (_Dir.Down, _Dir.Left)


class SortCriteria:
    def __init__(
        self,
        sort_key: Iterable[SortKey],
        dir: SortDir = SortDir.DownThenRight,
        dx: int = 22,
        dy: int = 22,
        line_size: int = 40,
    ):
        self.sort_key = tuple(sort_key)
        self.dir = dir
        self.dx = dx
        self.dy = dy
        self.line_size = line_size

    def get_sort_key(self, item: "Item") -> Any:
        key = []
        if SortKey.COLOR in self.sort_key:
            key.append(item.Color)
        if SortKey.NAME in self.sort_key:
            key.append(item.Name)
        return tuple(key)

    def categorize(self, items: List["Item"]) -> Dict[Any, List["Item"]]:
        categories = {}
        items = sorted(items, key=lambda item: (item.Color, item.Name, item.Serial))
        for item in items:
            key = self.get_sort_key(item)
            if key not in categories:
                categories[key] = []
            categories[key].append(item)
        return categories


settings = {
    0x0E75: SortCriteria(sort_key=[SortKey.COLOR], dx=10, dy=22, line_size=15),
    # mysterious fragment
    0x1F13: SortCriteria(sort_key=[SortKey.COLOR], dx=5, dy=15, line_size=40),
    # gold-trimmed metal box (facing south)
    0x0E40: SortCriteria(sort_key=[SortKey.COLOR, SortKey.NAME], dir=SortDir.RightThenDown, dx=30, dy=25, line_size=40),
    # dull metal box (facing south)
    0x0E7C: SortCriteria(sort_key=[SortKey.COLOR, SortKey.NAME], dir=SortDir.RightThenDown, dx=30, dy=25, line_size=40),
    # pickaxe (facing south)
    0x0E85: SortCriteria(sort_key=[SortKey.COLOR], dx=5, dy=44, line_size=40),
    # pickaxe (facing south)
    0x0E86: SortCriteria(sort_key=[SortKey.COLOR], dx=5, dy=44, line_size=40),
    # skull
    0x1AE1: SortCriteria(sort_key=[SortKey.COLOR], dx=5, dy=10, line_size=40),
    # primer
    0x1E22: SortCriteria(sort_key=[SortKey.NAME], dir=SortDir.RightThenUp, dx=20, dy=10, line_size=40),
}


def main():
    # Get the reference item
    ref_serial = Target.PromptTarget("Choose the reference item", 0x47E)
    if ref_serial == -1:
        Misc.SendMessage("Target not selected!", 0x21)
        return
    ref = Items.FindBySerial(ref_serial)
    if ref is None:
        Misc.SendMessage("Target not found!", 0x21)
        return

    x0 = ref.Position.X
    y0 = ref.Position.Y
    cont = ref.Container

    criteria = settings.get(ref.ItemID, SortCriteria(sort_key=[SortKey.COLOR]))
    categories = criteria.categorize(Items.FindAllByID(ref.ItemID, -1, ref.Container, 0))
    dir = criteria.dir.value

    # Sort item
    pos_i, pos_j = 0, 0
    key_sorted = sorted(categories.keys())
    dx, dy = criteria.dx, criteria.dy
    for i, key in enumerate(key_sorted):
        category = categories[key]
        Misc.SendMessage(f"{len(category)} entries in category {i+1}", 0x3B2)
        pos_j = 0
        for item in category:
            x, y = x0, y0
            # Compute the coordinates associated with pos_i
            if dir[0] == _Dir.Right:
                x += pos_i * dx
            elif dir[0] == _Dir.Left:
                x -= pos_i * dx
            elif dir[0] == _Dir.Up:
                y -= pos_i * dy
            elif dir[0] == _Dir.Down:
                y += pos_i * dy
            # Compute the coordinates associated with pos_j
            if dir[1] == _Dir.Right:
                x += pos_j * dx
            elif dir[1] == _Dir.Left:
                x -= pos_j * dx
            elif dir[1] == _Dir.Up:
                y -= pos_j * dy
            elif dir[1] == _Dir.Down:
                y += pos_j * dy
            # Current item position
            if (x, y) != (item.Position.X, item.Position.Y):
                Items.Move(item.Serial, cont, -1, x, y)
                Misc.Pause(900)

            # Update the position arguments
            pos_j += 1
            if pos_j >= criteria.line_size:
                pos_i += 1
                pos_j = 0
        pos_i += 1

    Misc.SendMessage("Done!", 0x3B2)


if __name__ == "__main__":
    main()
