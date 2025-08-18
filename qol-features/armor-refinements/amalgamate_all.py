from AutoComplete import *
from typing import List, Dict, Optional, Iterator


LEVEL_MAP = {
    "defense": 1,
    "protection": 2,
    "hardening": 3,
    "fortification": 4,
    "invulnerability": 5,
}

BASE_TYPES = ("wash", "cure", "varnish", "polish", "scour", "gloss")

HEIGHT_MAP = {
    "wash": 59,
    "cure": 92,
    "gloss": 111,
    "varnish": 59,
    "polish": 87,
    "scour": 106,
}

CONT_MAP = {
    "wash": 0x40127DBC,
    "cure": 0x40127DBC,
    "gloss": 0x40127DBC,
    "varnish": 0x5C2260DA,
    "polish": 0x5C2260DA,
    "scour": 0x5C2260DA,
}

COL_SEP = 10


class ArmorRefinement:
    base: str
    """Represents one of the six base types of armor refinements: wash, cure, varnish, polish, scour, gloss"""
    armor_type: str
    """Represents the type of armor this refinement is applied to."""
    bonus_type: str
    """Represents the bonus type of the armor refinement, which is either deflecting or reinforced."""
    level: int
    """Represents the level of the armor refinement, which determines its strength."""
    item: "Item"
    """The item representing this armor refinement."""

    def __init__(self, base: str, armor_type: str, bonus_type: str, level: int, item: "Item"):
        self.base = base
        self.armor_type = armor_type
        self.bonus_type = bonus_type
        self.level = level
        self.item = item

    @property
    def sort_key(self) -> str:
        return f"{self.base}>{self.armor_type}>{self.level}>{self.bonus_type}"

    @classmethod
    def from_item(cls, item: "Item") -> "Optional[ArmorRefinement]":
        name_words = item.Name.lower().split()
        if len(name_words) != 3:
            return None

        base = name_words[0]
        if base not in BASE_TYPES:
            return None

        level = LEVEL_MAP.get(name_words[2], 0)
        if level == 0:
            return None

        armor_type = None
        bonus_type = None
        Items.WaitForProps(item.Serial, 1000)
        for line in Items.GetPropStringList(item.Serial):
            line = line.lower()
            if line.startswith("armor type: "):
                armor_type = line[12:]
                continue
            if line.startswith("bonus type: "):
                bonus_type = line[12:]
                continue

        if armor_type is None or bonus_type is None:
            return None

        entry = ArmorRefinement(base, armor_type, bonus_type, level, item)
        return entry


def amalgamate(alamgam_serial: int, entries: List[ArmorRefinement]):
    Items.UseItem(alamgam_serial)

    for entry in entries:
        item = entry.item
        if item.RootContainer != Player.Backpack.Serial:
            Misc.Pause(1000)
            Items.Move(item.Serial, Player.Backpack.Serial, -1)
        if not Target.WaitForTarget(1000, False):
            return False
        Target.TargetExecute(item.Serial)

    Target.Cancel()
    Misc.Pause(1000)
    return True


def check_if_available():
    # Build the list of items to scan
    item_list = list(Player.Backpack.Contains)
    for serial in set(CONT_MAP.values()):
        cont = Items.FindBySerial(serial)
        if cont is None:
            Misc.SendMessage("Failed to find the container.", 33)
            return False
        if not cont.IsContainer:
            Misc.SendMessage("This is not a container.", 33)
            return False
        if not (cont.ContainerOpened or Items.WaitForContents(serial, 1000)):
            Misc.SendMessage("Failed to open the container.", 33)
            return False
        item_list.extend(list(cont.Contains))

    # Find the amalgamator
    amalgamator = Items.FindByID(0x9966, 0x0480, Player.Backpack.Serial, 3, False)
    if amalgamator is None:
        Misc.SendMessage("An amalgamator must be in your backpack.", 33)
        return False

    # Build the refinement map
    refines: Dict[str, List[ArmorRefinement]] = {}
    for item in item_list:
        entry = ArmorRefinement.from_item(item)
        if entry is None:
            continue
        refines.setdefault(entry.sort_key, []).append(entry)

    # Perform amalgamation
    for key, cur_refine in refines.items():
        if len(cur_refine) == 0:
            continue
        level = cur_refine[0].level
        if len(cur_refine) > level:
            print(f"Amalgamating {key} with {len(cur_refine)} items.")
            return amalgamate(amalgamator.Serial, cur_refine[: level + 1])

    # Arrange
    cur_cols: Dict[str, int] = {base: 0 for base in BASE_TYPES}
    """Keeps track of the current column for each base type."""
    last_entries: Dict[str, Optional[ArmorRefinement]] = {base: None for base in BASE_TYPES}
    """Keeps track of the last refinement for each base type."""

    def iter_refinements() -> Iterator[ArmorRefinement]:
        for key in sorted(refines.keys()):
            for entry in refines[key]:
                yield entry

    for entry in iter_refinements():
        # Compute the current column
        cur_cont = CONT_MAP[entry.base]
        cur_col = cur_cols[entry.base]
        last_entry = last_entries[entry.base]
        # Add extra spacing between different armor types
        if last_entry is not None and last_entry.armor_type != entry.armor_type:
            cur_col += 1
        # Compute the position and move
        cur_x = 50 + 10 * cur_col
        cur_y = HEIGHT_MAP[entry.base]
        item = entry.item
        if item.Position.X != cur_x or item.Position.Y != cur_y or item.Container != cur_cont:
            Items.Move(item.Serial, cur_cont, -1, cur_x, cur_y)
        # Update the history
        cur_cols[entry.base] = cur_col + 1
        last_entries[entry.base] = entry

    return False


def main():
    while check_if_available():
        continue

    Misc.SendMessage("Done", 68)


if __name__ == "__main__":
    main()
