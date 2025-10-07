from AutoComplete import *
from typing import Dict, Tuple, Optional
import re


class LockerEntry:
    def __init__(self):
        self.facet: int = -1
        self.coords: Tuple[int, int] = (-1, -1)
        self.level = ""
        self.type = ""
        self.status = ""


class LockerStatus:
    def __init__(self):
        self.maps: Dict[int, LockerEntry] = {}
        self.page = 0
        self.page_max = 0
        self.count = 0

    def export(self):
        with open("Data/Client/TreasureMaps.map", "w") as f:
            f.write("3\n")
            for key in range(self.count):
                if key not in self.maps:
                    Misc.SendMessage(f"Entry #{key+1} is missing.", 0x21)
                entry = self.maps[key]
                # Only export decoded maps with valid data
                if entry.coords == (-1, -1):
                    Misc.SendMessage(f"The coordinates of entry #{key+1} are unknown.", 0x21)
                    continue
                if entry.facet == -1:
                    Misc.SendMessage(f"The facet of entry #{key+1} is unknown.", 0x21)
                    continue
                if entry.level == "":
                    Misc.SendMessage(f"The lavel of entry #{key+1} is unknown.", 0x21)
                    continue
                if entry.type == "":
                    Misc.SendMessage(f"The type of entry #{key+1} is unknown.", 0x21)
                    continue
                if entry.status != "Decoded":
                    Misc.SendMessage(f"Entry #{key+1} is either not decoded or completed.", 0x21)
                    continue
                page = (key // 10) + 1
                idx = (key % 10) + 1
                label = f"({key+1}) {entry.level} {entry.type}"
                f.write(f"+PIN: {entry.coords[0]} {entry.coords[1]} {entry.facet} {label}\n")
        Misc.SendMessage("SOS map exported to: Data/Client/TreasureMaps.map", 68)


class LockerReader:
    GUMP_ID: Optional[int] = None

    @classmethod
    def obtain_gump(cls, delay: int = 1000) -> Optional[Gumps.GumpData]:
        if cls.GUMP_ID == None:
            Timer.Create("gump-delay", delay)
            while Timer.Check("gump-delay"):
                for gump_id in Gumps.AllGumpIDs():
                    gd = Gumps.GetGumpData(gump_id)
                    if len(gd.gumpText) >= 1 and gd.gumpText[0] == '<DIV ALIGN="CENTER">Davies\' Locker</DIV>':
                        cls.GUMP_ID = gd.gumpId
                        return gd
                Misc.Pause(100)
        else:
            Gumps.WaitForGump(cls.GUMP_ID, delay)
            return Gumps.GetGumpData(cls.GUMP_ID)

    @staticmethod
    def is_locker(item: "Item") -> bool:
        if 0x4BF6 <= item.ItemID <= 0x4C01:  # Davies' Lockers
            return True
        if 0xA833 <= item.ItemID <= 0xA848:  # Cartography Table
            return True
        return False

    @classmethod
    def close_gump(cls):
        gd = cls.obtain_gump(1)
        if gd is not None:
            Gumps.CloseGump(gd.gumpId)

    @classmethod
    def read_page(cls, gd: Gumps.GumpData, status: LockerStatus):
        page = 0
        page_max = 0
        count = 0
        maps = status.maps
        for line in gd.layoutPieces:
            args = line.split(" ")
            if line.startswith("xmfhtmltok 35 430 280 20 0 0 17183 1153560"):
                count, _ = map(int, args[9].strip("@").split("@"))
                status.count = count
                continue
            if line.startswith("xmfhtmltok 35 450 280 20 0 0 17183 1153561"):
                page, page_max = map(int, args[9].strip("@").split("@"))
                status.page = page
                status.page_max = page_max
                continue

            # Match facet
            matchres = re.match(r"xmfhtmlgumpcolor 78 (\d+) 110 20 (\d+) 0 0 32752", line)
            if matchres:
                y = int(matchres.group(1))
                idx = (page - 1) * 10 + (y - 73) // 35
                entry = maps.setdefault(idx, LockerEntry())

                facet = int(matchres.group(2))
                if facet == 1012001:  # Felucca
                    entry.facet = 0
                elif facet == 1012000:  # Trammel
                    entry.facet = 1
                elif facet == 1012002:  # Ilshenar
                    entry.facet = 2
                elif facet == 1060643:  # Malas
                    entry.facet = 3
                elif facet == 1063258:  # Tokuno Islands
                    entry.facet = 4
                elif facet == 1112178:  # Ter Mur
                    entry.facet = 5
                elif facet == 1156262:  # Valley of Eodon (verification needed)
                    entry.facet = 5

            # Match coordinates
            matchres = re.match(r"xmfhtmltok 198 (\d+) 140 20 0 0 32752 1060847 @(\d+), (\d+)@", line)
            if matchres:
                y = int(matchres.group(1))
                idx = (page - 1) * 10 + (y - 73) // 35
                entry = maps.setdefault(idx, LockerEntry())

                pos_x = int(matchres.group(2))
                pos_y = int(matchres.group(3))
                entry.coords = (pos_x, pos_y)

            # Match type
            matchres = re.match(r"xmfhtmlgumpcolor 410 (\d+) 110 20 (\d+) 0 0 32752", line)
            if matchres:
                y = int(matchres.group(1))
                idx = (page - 1) * 10 + (y - 73) // 35
                entry = maps.setdefault(idx, LockerEntry())

                map_type = int(matchres.group(2))
                if map_type == 1158997:  # Mage's
                    entry.type = "Mage"
                elif map_type == 1158998:  # Assassin's
                    entry.type = "Assassin"
                elif map_type == 1158999:  # Warrior's
                    entry.type = "Warrior"
                elif map_type == 1159000:  # Artisan's
                    entry.type = "Artisan"
                elif map_type == 1159002:  # Ranger's
                    entry.type = "Ranger"

            # Match level
            matchres = re.match(r"xmfhtmlgumpcolor 373 (\d+) 110 20 (\d+) 0 0 32752", line)
            if matchres:
                y = int(matchres.group(1))
                idx = (page - 1) * 10 + (y - 73) // 35
                entry = maps.setdefault(idx, LockerEntry())

                level = int(matchres.group(2))
                if level == 1158992:  # Stash
                    entry.level = "Stash"
                elif level == 1158993:  # Supply
                    entry.level = "Supply"
                elif level == 1158994:  # Cache
                    entry.level = "Cache"
                elif level == 1158995:  # Hoard
                    entry.level = "Hoard"
                elif level == 1158996:  # Trove
                    entry.level = "Trove"

            # Match status
            matchres = re.match(r"xmfhtmlgumpcolor 473 (\d+) 150 20 (\d+) 0 0 32752", line)
            if matchres:
                y = int(matchres.group(1))
                idx = (page - 1) * 10 + (y - 73) // 35
                entry = maps.setdefault(idx, LockerEntry())

                decode_status = int(matchres.group(2))
                if decode_status == 1153580:  # Not Decoded
                    entry.status = "Not Decoded"
                elif decode_status == 1153581:  # Decoded
                    entry.status = "Decoded"
                elif decode_status == 1153582:  # Completed
                    entry.status = "Completed"

    @classmethod
    def read_all(cls) -> Optional[LockerStatus]:
        cls.close_gump()

        serial = Target.PromptTarget("Choose a locker to scan.", 0x3B2)
        if serial == -1:
            return
        item = Items.FindBySerial(serial)
        if item is None:
            Misc.SendMessage("Failed to identify the target.", 0x21)
            return
        if not cls.is_locker(item):
            Misc.SendMessage("That is not a locker.", 0x21)
            return
        if Player.DistanceTo(item) > 2:
            Misc.SendMessage("You must be within 2 tiles from the target.", 0x21)
            return

        Items.UseItem(item.Serial)
        status = LockerStatus()
        while True:
            gd = cls.obtain_gump()
            if gd is None:
                Misc.SendMessage("Failed to find the gump.", 0x21)
                return
            status.page = 0
            cls.read_page(gd, status)
            if status.page == 0:
                Misc.SendMessage("Failed to parse the gump.", 0x21)
                return
            Misc.SendMessage(f"Page {status.page} successfully parsed.", 68)
            if status.page == status.page_max:
                Gumps.CloseGump(gd.gumpId)
                break
            Gumps.SendAction(gd.gumpId, 42)

        return status


def test():
    status = LockerReader.read_all()
    if status is None:
        return
    status.export()


if __name__ == "__main__":
    test()
