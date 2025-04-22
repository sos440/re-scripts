from typing import List


REFINEMENT_LEVEL_MAP = {
    "defense": 1,
    "protection": 2,
    "hardening": 3,
    "fortification": 4,
    "invulnerability": 5,
}

REFINEMENT_TYPES = ("wash", "cure", "varnish", "polish", "scour", "gloss")

HEIGHT_MAP = {
    "wash": 59,
    "cure": 92,
    "gloss": 111,
    "varnish": 130,
    "polish": 158,
    "scour": 177,
}

COL_SEP = 10


class ArmorRefinement:
    base: str
    armor_type: str
    bonus_type: str
    level: int
    
    def __init__(self, base: str, armor_type: str, bonus_type: str, level: int, item):
        self.base = base
        self.armor_type = armor_type
        self.bonus_type = bonus_type
        self.level = level
        self.item = item
    
    @property
    def sort_key(self) -> str:
        return f"{self.base}>{self.armor_type}>{self.level}>{self.bonus_type}"


def amalgamate(amal_serial: int, entries: List[ArmorRefinement]):
    Items.UseItem(amal_serial)

    for entry in entries:
        item = entry.item
        if item.RootContainer != Player.Backpack.Serial:
            Misc.Pause(1000)
            Items.Move(item.Serial, Player.Backpack.Serial, -1)
        if not Target.WaitForTarget(1000, False):
            break
        Target.TargetExecute(item.Serial)   
        
    Target.Cancel()
    return True


def test(serial):
    cont = Items.FindBySerial(serial)
    if cont is None:
        Misc.SendMessage("Failed to find the target.", 33)
        return False
    if not cont.IsContainer:
        Misc.SendMessage("This is not a container.", 33)
        return False
    if not (cont.ContainerOpened or Items.WaitForContents(serial, 1000)):
        Misc.SendMessage("Failed to open the container.", 33)
        return False
    
    amalgamator = Items.FindByID(0x9966, 0x0480, Player.Backpack.Serial, 3, False)
    if amalgamator is None:
        Misc.SendMessage("An amalgamator must be in the selected container.", 33)
        return False
        

    refines = {}
    
    item_list = list(cont.Contains)
    item_list.extend(list(Player.Backpack.Contains))
    
    # Scan
    for item in item_list:
        name_words = item.Name.lower().split()
        if len(name_words) != 3:
            continue

        base = name_words[0]
        if base not in REFINEMENT_TYPES:
            continue

        level = REFINEMENT_LEVEL_MAP.get(name_words[2], 0)
        if level == 0:
            continue

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
            continue

        entry = ArmorRefinement(base, armor_type, bonus_type, level, item)
        refines.setdefault(entry.sort_key, []).append(entry)

    # Perform amalgamation
    updated = False
    for key, cur_refine in refines.items():
        if len(cur_refine) == 0:
            continue
        level = cur_refine[0].level
        if len(cur_refine) > level:
            amalgamate(amalgamator.Serial, cur_refine[: level + 1])
            updated = True
            Misc.Pause(1000)

    if updated:
        return True
    
    # Arrange
    cols = {base: 0 for base in REFINEMENT_TYPES}
    lasts = {base: None for base in REFINEMENT_TYPES}
    for key in sorted(refines.keys()):
        for entry in refines[key]:
            # Compute the current column
            cur_col = cols.get(entry.base, 0)
            last = lasts.get(entry.base, None)
            if last is not None and last.armor_type != entry.armor_type:
                cur_col += 1
            # Compute the position and move
            cur_x = 50 + 10 * cur_col
            cur_y = HEIGHT_MAP.get(entry.base, 0)
            item = entry.item
            if item.Position.X != cur_x or item.Position.Y != cur_y or item.Container != cont.Serial:
                Items.Move(item.Serial, cont.Serial, -1, cur_x, cur_y)
            # Update the history
            cols[entry.base] = cur_col + 1
            lasts[entry.base] = entry
    
    return False


def main():
    serial = Target.PromptTarget("")
    if serial == 0:
        Misc.SendMessage("You did not choose a target.", 68)
        return

    while test(serial):
        pass

    Misc.SendMessage("Done", 68)


main()
