from AutoComplete import *
from typing import Dict, List, Tuple
import re


SKILLS = [
    "Alchemy",
    "Anatomy",
    "Animal Lore",
    "Animal Taming",
    "Archery",
    "Arms Lore",
    "Blacksmithing",
    "Bushido",
    "Carpentry",
    "Cartography",
    "Chivalry",
    "Cooking",
    "Discordance",
    "Evaluate Intelligence",
    "Fencing",
    "Fishing",
    "Fletching",
    "Focus",
    "Healing",
    "Hiding",
    "Imbuing",
    "Inscription",
    "Lockpicking",
    "Lumberjacking",
    "Mace Fighting",
    "Magery",
    "Meditation",
    "Mining",
    "Musicianship",
    "Mysticism",
    "Necromancy",
    "Ninjitsu",
    "Parrying",
    "Peacemaking",
    "Poisoning",
    "Provocation",
    "Remove Trap",
    "Resisting Spells",
    "Spellweaving",
    "Spirit Speak",
    "Stealing",
    "Stealth",
    "Swordsmanship",
    "Tactics",
    "Tailoring",
    "Throwing",
    "Tinkering",
    "Veterinary",
    "Wrestling",
]

SCROLLS_PER_BINDER = {105: 8, 110: 12, 115: 10, 120: -1}


class ShortcutGump:
    GUMP_WT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""

    @classmethod
    def prompt(cls, id: str, title: str, text: str) -> bool:
        """
        A minimized gump with a button to ask.
        """
        SHORTCUT_GUMP_ID = hash(id) & 0xFFFFFFFF
        Gumps.CloseGump(SHORTCUT_GUMP_ID)
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
        Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)
        Gumps.AddHtml(gd, 10, 5, 126, 18, cls.GUMP_WT.format(text=title), False, False)
        Gumps.AddButton(gd, 10, 30, 40021, 40031, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 33, 126, 18, cls.GUMP_WT.format(text=text), False, False)
        Gumps.SendGump(SHORTCUT_GUMP_ID, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)

        if not Gumps.WaitForGump(SHORTCUT_GUMP_ID, 1000 * 60 * 60 * 24):
            return False
        gd = Gumps.GetGumpData(SHORTCUT_GUMP_ID)
        if gd is None:
            return False
        return gd.buttonid == 1


def find_scroll_binder(skill: str, level: int) -> Tuple[int, int]:
    results = []
    for binder in Items.FindAllByID(0x14F0, 0x0664, Player.Backpack.Serial, 3):
        Items.WaitForProps(binder.Serial, 1000)
        unused = True
        cur_level = 0
        cur_skill = ""
        cur_remaining = SCROLLS_PER_BINDER.get(level, -1)
        # Check if this binder is suitable
        for prop in Items.GetPropStringList(binder.Serial):
            matchres = re.match(r"^(105|110|115) ([ A-Za-z+]+): (\d+)/(\d+)", prop)
            if matchres:
                unused = False
                cur_level = int(matchres.group(1))
                cur_skill = matchres.group(2)
                cur_remaining = int(matchres.group(4)) - int(matchres.group(3))
                break
        # Only consider if unused or matches our skill and level
        if unused or (level == cur_level and skill == cur_skill):
            results.append((binder.Serial, cur_remaining))

    if not results:
        return -1, -1
    # Find the binder with the least remaining capacity that can still bind
    results.sort(key=lambda x: x[1])
    return results[0]


def find_powerscrolls():
    return Items.FindAllByID(0x14F0, 0x481, Player.Backpack.Serial, 2)


def use_binder(serial: int):
    while True:
        if not Misc.IsItem(serial):
            return False
        Items.UseItem(serial)
        if not Target.WaitForTarget(2000, False):
            Misc.Pause(1000)
            continue
        return True


def build_ps_map():
    ps_map: Dict[int, Dict[str, List[int]]] = {105: {}, 110: {}, 115: {}, 120: {}}
    for ps in find_powerscrolls():
        matchres = re.match(r"^(?:a wondrous|an exalted|a mythical|a legendary) scroll of (.+) \((\d+) Skill\)", ps.Name)
        if not matchres:
            continue
        skill = matchres.group(1)
        level = int(matchres.group(2))
        if skill in SKILLS and level in ps_map:
            ps_map[level].setdefault(skill, []).append(ps.Serial)
    return ps_map


def combine_any() -> bool:
    """
    Combine any available powerscrolls into a single scroll.

    Returns True if the combine process needs to be continued, False otherwise.
    """
    # Build a map of powerscrolls by skill and level
    ps_map = build_ps_map()

    # Try to bind scrolls
    for level in (
        105,
        110,
        115,
    ):
        ps_cur_level = ps_map[level]
        for skill in sorted(ps_cur_level.keys()):
            ps_list = ps_cur_level[skill]
            Misc.SendMessage(f"Found: {len(ps_list)} scrolls of {level} {skill}.", 68)

            # Find a suitable binder
            binder_serial, ps_needed = find_scroll_binder(skill, level)
            if binder_serial == -1 or ps_needed == -1:
                Misc.SendMessage("No matching scroll binder found. Skipping...", 0x22)
                continue

            if len(ps_list) < ps_needed:
                diff = ps_needed - len(ps_list)
                Misc.SendMessage(f"You need {diff} more power scrolls to complete binding. Skipping...", 0x22)
                continue

            # We have enough scrolls to bind
            Misc.SendMessage(f"Trying to bind: {ps_needed} scrolls of {level} {skill}.", 68)
            for ps_serial in ps_list[:ps_needed]:
                success = use_binder(binder_serial)
                if not success:
                    Misc.SendMessage("Failed to use binder", 0x22)
                    return True
                Target.TargetExecute(ps_serial)
                Misc.Pause(1000)

            Misc.SendMessage("Binding complete.", 68)
            return True

    # No more combinations possible
    Misc.SendMessage("There's nothing to bind.", 68)
    return False


def combine_loop():
    while ShortcutGump.prompt("PSBinderGump", "PowerScroll Binder", "Start Binding"):
        while combine_any():
            ...
    Misc.SendMessage("Bye!", 68)


if __name__ == "__main__":
    combine_loop()
