from AutoComplete import *
import threading
import time
import os
import sys
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from enum import Enum
from typing import List, Dict, Tuple, Any, Optional, Callable, Union

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

from core.summary import ItemSummary
from core.match import LootProfile, LootRules, LootMatch


################################################################################
# Helper Functions
################################################################################


class PacketBuilder:
    def __init__(self, header: int) -> None:
        self.header = header
        self.packet = bytearray()

    def add_byte(self, value: int) -> None:
        self.packet.append(value & 0xFF)

    def add_short(self, value: int) -> None:
        value &= 0xFFFF
        self.packet += value.to_bytes(2, "big")

    def add_int(self, value: int) -> None:
        value &= 0xFFFFFFFF
        self.packet += value.to_bytes(4, "big")

    def add_bytes(self, value: bytes) -> None:
        self.packet += value

    def __len__(self) -> int:
        return len(self.packet) + 1

    def build(self, prefix: Optional[bytes] = None) -> bytes:
        if prefix is None:
            prefix = bytes()
        return bytes(self.header.to_bytes(1, "big") + prefix + self.packet)


def render_object(
    serial: int,
    itemid: int,
    x: int,
    y: int,
    z: int,
    amount: int = 1,
    color: int = 0,
    flag: int = 0,
    facing: int = 0,
    itemid_inc: int = 0,
    data_type: int = 0,
):
    assert data_type in [0, 2], "Invalid data type. Must be 0 or 2."

    packet = PacketBuilder(0xF3)
    packet.add_short(0x0001)
    packet.add_byte(data_type)
    packet.add_int(serial)
    packet.add_short(itemid)
    packet.add_byte(itemid_inc)
    packet.add_short(amount)
    packet.add_short(amount)
    packet.add_short(x)
    packet.add_short(y)
    packet.add_byte(z)
    packet.add_byte(facing)
    packet.add_short(color)
    packet.add_byte(flag)
    packet.add_bytes(b"\x00\x00")

    PacketLogger.SendToClient(CList[Byte](packet.build()))


def close_container(serial: int):
    serial = serial & 0xFFFFFFFF
    packet = b"\xbf"  # command
    packet += b"\x00\x0d"  # length
    packet += b"\x00\x16"  # subcommand
    packet += b"\x00\x00\x00\x0c"  # close container
    packet += serial.to_bytes(4, "big")
    PacketLogger.SendToClient(CList[Byte](packet))


def root_dist_to_player(serial) -> Union[int, float]:
    """
    Calculate the distance between the player and the top container of the object with the provided serial.
    """
    item = Items.FindBySerial(serial)
    mob = None

    while item is not None and not item.OnGround:
        serial = item.RootContainer
        item = Items.FindBySerial(item.RootContainer)

    player = Mobiles.FindBySerial(Player.Serial)
    assert player is not None, "Player is not found."
    if item is None:
        mob = Mobiles.FindBySerial(serial)
        if mob is None:
            return int("inf")
        else:
            return mob.DistanceTo(player)
    else:
        return int(item.DistanceTo(player))


################################################################################
# Looting Logic
################################################################################


IDLIST_CHEST = [
    0x0E3C,
    0x0E3D,  # large crate
    0x0E3E,
    0x0E3F,  # medium crate
    0x0E7E,
    0x09A9,  # small crate
    0x0E40,
    0x0E41,  # fancy metal crate
    0x0E42,
    0x0E43,  # wooden crate
    0x0E77,  # large barrel
    0x0E7F,  # small barrel
    0x0E7C,
    0x09AB,  # metal crate
]


class LootingMode(Enum):
    STOPPED = 0
    LOOP = 1
    SINGLE = 2


class LootingMemory:
    def __init__(self, lootable: bool = True):
        self.lootable = lootable
        self.attempts = 0
        self.opened = False
        self.finished = False
        self.name_checked = False


class Looter:
    """
    A conceptual object representing the "looter" in the game.

    It contains the current profile, settings, and mode of looting.
    This object is used as an "agent" to perform looting actions based on the provided profile and settings.

    Attributes:
        profile (LootProfile): The loot profile used for looting.
        setting (dict): The settings for the looter.
        target_cache (dict): A dictionary storing the looter's interaction with the lootable targets.
        summary_cache (dict): A dictionary storing the summary of the lootable items.
        mode (LootingMode): The current mode of the looter.
        scanner (Callable[[], List[Item]]): A callable function to be used for scanning lootable targets.
    """

    def __init__(self, setting: Dict[str, Any], profile: LootProfile, mode: LootingMode = LootingMode.STOPPED):
        self.profile = profile
        self.setting = setting
        self.target_cache: Dict[int, LootingMemory] = {}
        """This stores the looter's interaction with the lootable targets."""
        self.summary_cache: Dict[int, ItemSummary] = {}
        """This stores the summary of the lootable items."""
        self.mode = mode
        """This stores the current mode of the looter."""
        self.scanner: Optional[Callable] = None
        """This stores the scanner function to be used for scanning lootable targets."""
        self.callback: Optional[Callable] = None
        """This stores the callback function to be used for looting."""

        self._thread = None
        self._stop_event = threading.Event()
        self._stop_event.set()

    def summarize(self, item) -> ItemSummary:
        """
        Summarizes the item and caches it for later use.

        Arguments:
            item (Item): The item to be summarized.

        Returns:
            ItemSummary: The summary of the item.
        """
        if item.Serial in self.summary_cache:
            return self.summary_cache[item.Serial]
        # Clear the cache if it exceeds 10,000 items.
        if len(self.summary_cache) >= 10000:
            self.summary_cache.clear()
        summary = ItemSummary(item)
        self.summary_cache[item.Serial] = summary
        return summary

    def dehighlight_finished(self, target):
        close_container(target.Serial)
        color = self.setting.get("mark-color", 1014)
        if target.ItemID == 0x2006:
            render_object(
                target.Serial,
                target.ItemID,
                target.Position.X,
                target.Position.Y,
                target.Position.Z,
                amount=0x33,
                color=color,
                facing=(target.Serial % 8),
            )
        else:
            Items.SetColor(target.Serial, color)

    def _raw_check_lootability(self):
        for entry in Journal.GetJournalEntry(-1):
            item = Items.FindBySerial(entry.Serial)
            if item is None:
                continue
            if item.ItemID != 0x2006:
                continue
            if entry.Type != "Label":
                continue
            cur_mem = self.target_cache.setdefault(entry.Serial, LootingMemory())
            if cur_mem.name_checked or not cur_mem.lootable:
                continue
            cur_mem.name_checked = True
            if entry.Color == 89:
                Misc.SendMessage(f"Looter> {item.Name} is not lootable.", 88)
                cur_mem.lootable = False
        Journal.Clear()

    def global_check_lootability(self) -> None:
        self._raw_check_lootability()
        # Display the name of all corpses in the vicinity.
        for corpse in Items.FindAllByID(0x2006, -1, -1, 8):
            if corpse.Serial in self.target_cache:
                continue
            Items.SingleClick(corpse.Serial)

    def attempt_open(self, target) -> Tuple[bool, List[ItemSummary]]:
        """
        Attempt to open a lootable target and update the looting memory.

        Arguments:
            target (Item): The target to be looted.

        Returns:
            return (Tuple[bool, List[ItemSummary]]):
                A tuple containing a boolean indicating if the target was successfully opened or no retry is needed,
                and a list of lootable items in the target.
        """
        max_attempts = self.setting.get("max-open-attempts", 3)
        cur_mem = self.target_cache.setdefault(target.Serial, LootingMemory())
        # If the target is not lootable or has been finished, return False.
        if cur_mem.finished:
            return True, []
        if not cur_mem.lootable:
            return True, []
        if target.ItemID == 0x2006 and not cur_mem.name_checked:
            Items.SingleClick(target.Serial)
            Misc.Pause(500)
            self._raw_check_lootability()
        if not cur_mem.lootable:
            return True, []
        # If failed to open the target, increment the attempts and check if it should be marked as not lootable.
        cont_opened = target.ContainerOpened
        if not cont_opened:
            Misc.Pause(Timer.Remaining("action-delay"))
            Timer.Create("action-delay", self.setting.get("action-delay", 900))
            cont_opened = Items.WaitForContents(target.Serial, 1000)
        if not cont_opened:
            cur_mem.attempts += 1
            if cur_mem.attempts >= max_attempts:
                cur_mem.lootable = False
                return True, []
            return False, []
        # Builds the list of lootable items in the target.
        Misc.Pause(Timer.Remaining("action-delay"))
        target = Items.FindBySerial(target.Serial)
        if target is None:
            return False, []
        cur_mem.opened = True
        lootables = [self.summarize(item) for item in target.Contains]
        lootables = [item for item in lootables if self.profile.test(item)]
        if len(lootables) == 0:
            cur_mem.finished = True
            if self.setting.get("mark-after-finished", False):
                self.dehighlight_finished(target)
        return True, lootables

    def scan(self) -> List[ItemSummary]:
        """
        Scan the environment for lootable items based on the current profile and settings.
        """
        if self.scanner is None:
            return []

        # Dehighlight all finished targets.
        if self.setting.get("mark-after-finished", False):
            for target in self.scanner():
                cur_mem = self.target_cache.get(target.Serial, None)
                if cur_mem is None or not cur_mem.finished:
                    continue
                self.dehighlight_finished(target)

        self.global_check_lootability()

        is_greedy = self.setting.get("greedy-looting", False)
        # In the greedy mode, we only scan for the first lootable item.
        if is_greedy:
            lootables = []
            for target in self.scan_nearby_targets():
                cur_lootables = [self.summarize(item) for item in target.Contains]
                cur_lootables = [item for item in cur_lootables if self.profile.test(item)]
                if len(cur_lootables) > 0:
                    lootables.extend(cur_lootables)
            if len(lootables) > 0:
                return lootables[:1]

        # Open all targets near the player.
        needs_scan = True
        while needs_scan:
            # Emergency stop
            if self._stop_event.is_set():
                return []
            needs_scan = False
            for target in self.scan_nearby_targets():
                success, cur_lootables = self.attempt_open(target)
                if not success:
                    needs_scan = True
                if is_greedy and len(cur_lootables) > 0:
                    return cur_lootables[:1]

        # Scan all the lootable items in the targets.
        lootables = []
        for target in self.scan_nearby_targets():
            lootables.extend([self.summarize(item) for item in target.Contains])
        lootables = [item for item in lootables if self.profile.test(item)]
        return lootables

    def loot_single(self, lootables: List[ItemSummary]):
        """
        Attempt to loot the first item that matches the profile rules.
        If the item is successfully looted, it will be moved to the specified lootbag.

        Arguments:
            lootables (List[ItemSummary]): The list of lootable items.

        Returns:
            bool: True if an item was looted, False otherwise.
        """
        if len(lootables) == 0:
            return False

        # TODO: Add weight/count check
        inventory = ItemSummary(Player.Backpack)
        if inventory.content_count >= inventory.content_maxcount:
            Misc.SendMessage("Looter> Inventory is full.")
            return False
        for i, rule in enumerate(self.profile.rules):
            # Sort the lootables based on the rule
            item_to_loot = None
            for item in lootables:
                if rule.test(item):
                    # Skip if the item is too heavy for the player
                    # This is only a temporary solution, and should be improved later.
                    if item.weight + Player.Weight > Player.MaxWeight:
                        Items.SetColor(item.serial, 33)
                        continue
                    if item.weight + inventory.content_weight > inventory.content_maxweight:
                        Items.SetColor(item.serial, 33)
                        continue
                    if rule.highlight:
                        Items.SetColor(item.serial, rule.highlight_color)
                    item_to_loot = item
            if item_to_loot is None:
                continue
            # Determine the lootbag for the current rule
            lootbag = Player.Backpack.Serial
            if rule.lootbag is not None:
                for item in Player.Backpack.Contains:
                    summary = self.summarize(item)
                    if summary.content_count >= summary.content_maxcount:
                        continue
                    if rule.lootbag.test(summary):
                        lootbag = item.Serial
                        break
            # Move the item to the lootbag
            Items.Move(item_to_loot.serial, lootbag, -1)
            if rule.notify:
                Misc.SendMessage(f"Looter> {rule.name} matched: {item_to_loot.name}", 88)
            return True

        return False

    def loot_loop(self):
        """
        Loop to scan for lootable items and attempt to loot them based on the profile rules.
        """
        delay_refresh = self.setting.get("refresh-rate", 500)
        delay_action = self.setting.get("action-delay", 900)
        while Player.Connected and (not Player.IsGhost) and (not self._stop_event.is_set()):
            if self.mode == LootingMode.STOPPED:
                break

            if not Timer.Check("session-timeout"):
                Misc.SendMessage("Looter> Session timeout reached, stopping looter.", 0x3B2)
                break

            # Scan for lootable items
            lootables = self.scan()
            if len(lootables) == 0:
                if self.mode == LootingMode.SINGLE:
                    break
                Misc.Pause(delay_refresh)
                continue

            # Attempt to loot the first item that matches the profile rules
            success = self.loot_single(lootables)
            if success:
                Misc.Pause(delay_action)
            else:
                Misc.Pause(delay_refresh)

        self._stop_event.set()
        self.mode = LootingMode.STOPPED
        if self.callback is not None:
            self.callback()
        self._thread = None

    def start(self, mode: LootingMode = LootingMode.LOOP):
        assert self.scanner is not None, "Scanner function must be set before starting the looter."
        assert self.mode == LootingMode.STOPPED, "Looter is already running."
        assert self._thread is None, "Thread is already alive."
        assert self._stop_event.is_set(), "Stop event is not set."

        self.mode = mode
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.loot_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        assert self._thread is not None, "Thread is not alive."
        assert not self._stop_event.is_set(), "Stop event is already set."

        self._stop_event.set()
        self._thread.join()

    @property
    def is_running(self) -> bool:
        return self.mode != LootingMode.STOPPED and self._thread is not None

    def scan_nearby_targets(self):
        if self.scanner is None:
            return []

        target_list = self.scanner()
        target_list = [target for target in target_list if root_dist_to_player(target.Serial) <= 2]
        return target_list

    @classmethod
    def scanner_basic(cls):
        scan_corpse = Items.FindAllByID(0x2006, -1, -1, 256)
        scan_t_chest = Items.FindAllByID(IDLIST_CHEST, -1, -1, 2)
        scan_t_chest = [chest for chest in scan_t_chest if "treasure chest" in chest.Name.lower()]
        return scan_corpse + scan_t_chest

    @classmethod
    def generate_scanner(cls, serial: int) -> Callable:
        def scanner():
            result = Items.FindBySerial(serial)
            if result is None:
                return []
            return [result]

        return scanner


__all__ = [
    "LootingMode",
    "LootingMemory",
    "Looter",
]
