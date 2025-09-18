from AutoComplete import *
from typing import Optional, Tuple
import re


class PSBook:
    serial: int
    count: int
    skills: Dict[str, "PSBook.SkillEntry"]

    SKILL_LIST = [
        "Alchemy",
        "Anatomy",
        "AnimalLore",
        "AnimalTaming",
        "Archery",
        "ArmsLore",
        "Begging",
        "Blacksmith",
        "Bushido",
        "Camping",
        "Carpentry",
        "Cartography",
        "Chivalry",
        "Cooking",
        "DetectHidden",
        "Discordance",
        "EvalInt",
        "Fencing",
        "Fishing",
        "Fletching",
        "Focus",
        "Forensics",
        "Healing",
        "Herding",
        "Hiding",
        "Imbuing",
        "Inscribe",
        "ItemID",
        "Lockpicking",
        "Lumberjacking",
        "Macing",
        "Magery",
        "MagicResist",
        "Meditation",
        "Mining",
        "Musicianship",
        "Mysticism",
        "Necromancy",
        "Ninjitsu",
        "Parry",
        "Peacemaking",
        "Poisoning",
        "Provocation",
        "RemoveTrap",
        "Snooping",
        "Spellweaving",
        "SpiritSpeak",
        "Stealing",
        "Stealth",
        "Swords",
        "Tactics",
        "Tailoring",
        "TasteID",
        "Throwing",
        "Tinkering",
        "Tracking",
        "Veterinary",
        "Wrestling",
    ]

    class SkillEntry:
        level_105: int
        level_110: int
        level_115: int
        level_120: int

        def __init__(self, level_105=0, level_110=0, level_115=0, level_120=0):
            self.level_105 = level_105
            self.level_110 = level_110
            self.level_115 = level_115
            self.level_120 = level_120

        def __add__(self, other: "PSBook.SkillEntry") -> "PSBook.SkillEntry":
            if not isinstance(other, PSBook.SkillEntry):
                return NotImplemented
            return PSBook.SkillEntry(
                self.level_105 + other.level_105,
                self.level_110 + other.level_110,
                self.level_115 + other.level_115,
                self.level_120 + other.level_120,
            )

    def __init__(self, serial: int):
        self.serial = serial
        self.count = 0
        self.skills = {skill: PSBook.SkillEntry() for skill in self.SKILL_LIST}

    def __add__(self, other: "PSBook") -> "PSBook":
        if not isinstance(other, PSBook):
            return NotImplemented
        res = PSBook(self.serial or other.serial)
        res.count = self.count or other.count
        for skills in PSBook.SKILL_LIST:
            res.skills[skills] = self.skills[skills] + other.skills[skills]
        return res


class OldPSGumpManager:
    GUMP_ID: Optional[int] = None

    @classmethod
    def wait_for_gump(cls, timeout: int = 1000) -> Optional[Gumps.GumpData]:
        if cls.GUMP_ID is None:
            Timer.Create("gump-delay", timeout)
            while Timer.Check("gump-delay"):
                for gump_id in Gumps.AllGumpIDs():
                    gd = Gumps.GetGumpData(gump_id)
                    if gd is None:
                        continue
                    if len(gd.gumpData) > 0 and gd.gumpData[0] == "<DIV ALIGN=CENTER><BASEFONT COLOR=#FFFFFF>Power Scroll Book</BASEFONT></DIV>":
                        cls.GUMP_ID = gump_id
                        return gd
                Misc.Pause(100)
        else:
            if not Gumps.WaitForGump(cls.GUMP_ID, timeout):
                return None
            return Gumps.GetGumpData(cls.GUMP_ID)

    @classmethod
    def close_gump(cls):
        gd = cls.wait_for_gump(100)
        if cls.GUMP_ID is not None and gd is not None:
            Gumps.CloseGump(cls.GUMP_ID)

    @staticmethod
    def strip_html_tags(text: str) -> str:
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    @classmethod
    def parse_gump(cls, gd: Gumps.GumpData) -> Tuple[PSBook, int, int]:
        # Parse the gump layout to find textboxes and their positions
        lines = gd.gumpLayout.strip("{} ").split("}{")
        textbox_map = {}
        for line in lines:
            line = line.strip().split(" ")
            if line[0] == "htmlgump":
                if len(line) < 8:
                    raise ValueError(f"Incomplete htmlgump line: {line}")
                x, y, _, _, idx = map(int, line[1:6])
                if idx >= len(gd.stringList):
                    raise ValueError(f"Index {idx} out of range")
                textbox_map[(x, y)] = cls.strip_html_tags(gd.stringList[idx])
                continue
            if line[0] == "text":
                if len(line) < 5:
                    raise ValueError(f"Incomplete text line: {line}")
                x, y, color, idx = map(int, line[1:5])
                if idx >= len(gd.stringList):
                    raise ValueError(f"Index {idx} out of range")
                textbox_map[(x, y)] = cls.strip_html_tags(gd.stringList[idx])
                continue

        ps_book = PSBook(0)  # Dummy serial=

        # Read the PS count
        PS_COUNT_BOX = (348, 19)
        if PS_COUNT_BOX not in textbox_map:
            raise ValueError("Failed to read the power scroll count from the gump.")
        matchres = re.match(r"^Total: (\d+)/300$", textbox_map[PS_COUNT_BOX])
        if not matchres:
            raise ValueError(f"Failed to parse power scroll count from text: {textbox_map[PS_COUNT_BOX]}")
        ps_book.count = int(matchres.group(1))

        # Read the page
        PAGE_BOX = (12, 480)
        if PAGE_BOX not in textbox_map:
            raise ValueError("Failed to read the page number from the gump.")
        matchres = re.match(r"^Page (\d+)/(\d+)$", textbox_map[PAGE_BOX])
        if not matchres:
            raise ValueError(f"Failed to parse page number from text: {textbox_map[PAGE_BOX]}")
        page = int(matchres.group(1))
        max_page = int(matchres.group(2))

        def parse_skill_value(box):
            if box not in textbox_map:
                raise ValueError(f"Failed to read skill value from box {box}")
            val_str = textbox_map[box]
            return int(val_str)

        for i in range(14):
            y = 84 + 26 * i
            SKILL_NAME_BOX = (20, y)
            SKILL_105_BOX = (240, y)
            SKILL_110_BOX = (324, y)
            SKILL_115_BOX = (408, y)
            SKILL_120_BOX = (491, y)

            if SKILL_NAME_BOX not in textbox_map:
                continue
            skill_name = textbox_map[SKILL_NAME_BOX]
            if skill_name not in ps_book.SKILL_LIST:
                continue

            ps_book.skills[skill_name] = PSBook.SkillEntry(
                level_105=parse_skill_value(SKILL_105_BOX),
                level_110=parse_skill_value(SKILL_110_BOX),
                level_115=parse_skill_value(SKILL_115_BOX),
                level_120=parse_skill_value(SKILL_120_BOX),
            )

        return ps_book, page, max_page

    @classmethod
    def read_all(cls, serial: int) -> PSBook:
        cls.close_gump()
        Items.UseItem(serial)

        ps_book = PSBook(serial)
        for page in range(1, 6):
            # Wait for the gump to be ready
            gd = cls.wait_for_gump(1000)
            if cls.GUMP_ID is None:
                raise ValueError("Failed to find the gump.")
            if gd is None:
                raise ValueError("Failed to find the gump.")
            # Parse the gump data
            parsed, cur_page, max_page = cls.parse_gump(gd)
            if page != cur_page:
                raise ValueError(f"Page number mismatch: expected {page}, got {cur_page}")
            # Update the merged results
            ps_book += parsed
            # If not the last page, click next
            if page < max_page:
                Gumps.SendAction(cls.GUMP_ID, 2)
            
        cls.close_gump()
        return ps_book


def unit_test():
    serial = Target.PromptTarget("Target the Power Scroll Book", 0x3B2)
    item = Items.FindBySerial(serial)
    if item is None:
        Misc.SendMessage("Invalid item.", 0x21)
        return
    if item.ItemID not in (0x9A95, 0x9AA7) or item.Color != 0x481:
        Misc.SendMessage("Targeted item is not a Power Scroll Book.", 0x21)
        return

    try:
        ps_book = OldPSGumpManager.read_all(serial)
    except ValueError as e:
        Misc.SendMessage(f"Error: {e}", 0x21)
        return
    Misc.SendMessage(f"Total Power Scrolls: {ps_book.count}", 0x481)
    for skill, vals in ps_book.skills.items():
        Misc.SendMessage(f"Skill: {skill}, 105: {vals.level_105}, 110: {vals.level_110}, 115: {vals.level_115}, 120: {vals.level_120}", 0x481)


if __name__ == "__main__":
    unit_test()
