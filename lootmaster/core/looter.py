import threading
import time
import os
import sys
from enum import Enum
from typing import List, Dict, Tuple, Any, Optional, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

from core.summary import ItemSummary
from core.match import LootProfile, LootRules, LootMatch

################################################################################
# Looting Logic
################################################################################


IDLIST_CHEST = [
    0x0E3C, 0x0E3D,  # large crate
    0x0E3E, 0x0E3F,  # medium crate
    0x0E7E, 0x09A9,  # small crate
    0x0E40, 0x0E41,  # fancy metal crate
    0x0E42, 0x0E43,  # wooden crate
    0x0E77,  # large barrel
    0x0E7F,  # small barrel
    0x0E7C, 0x09AB,  # metal crate
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

    def attempt_open(self, target) -> Tuple[bool, List[ItemSummary]]:
        """
        Attempt to open a lootable target and update the looting memory.

        Arguments:
            target (Item): The target to be looted.

        Returns:
            return (Tuple[bool, List[ItemSummary]]):
                A tuple containing a boolean indicating if the target was successfully opened,
                and a list of lootable items in the target.
        """
        max_attempts = self.setting.get("max-open-attempts", 3)
        cur_mem = self.target_cache.get(target.Serial, LootingMemory())
        self.target_cache[target.Serial] = cur_mem
        # If the target is not lootable or has been finished, return False.
        if cur_mem.finished:
            if self.setting.get("mark-after-finished", False):
                Items.SetColor(target.Serial, self.setting.get("mark-color", 1014))
            return True, []
        if not cur_mem.lootable:
            return True, []
        # If failed to open the target, increment the attempts and check if it should be marked as not lootable.
        if not (cur_mem.opened or Items.WaitForContents(target.Serial, 1000)):
            cur_mem.attempts += 1
            if cur_mem.attempts >= max_attempts:
                cur_mem.lootable = False
                return True, []
            return False, []
        # Builds the list of lootable items in the target.
        if not cur_mem.opened:
            Misc.Pause(self.setting.get("action-delay", 900))
        target = Items.FindBySerial(target.Serial)
        if target is None:
            return False, []
        cur_mem.opened = True
        lootables = [self.summarize(item) for item in target.Contains]
        lootables = [item for item in lootables if self.profile.test(item)]
        if len(lootables) == 0:
            cur_mem.finished = True
            if self.setting.get("mark-after-finished", False):
                Items.SetColor(target.Serial, self.setting.get("mark-color", 1014))
        return True, lootables

    def scan(self) -> List[ItemSummary]:
        """
        Scan the environment for lootable items based on the current profile and settings.
        """
        if self.scanner is None:
            return []

        is_greedy = self.setting.get("greedy-looting", False)
        # In the greedy mode, we only scan for the first lootable item.
        if is_greedy:
            lootables = []
            for target in self.scanner():
                lootables.extend([self.summarize(item) for item in target.Contains])
            lootables = [item for item in lootables if self.profile.test(item)]
            if len(lootables) > 0:
                return lootables[:1]

        # Open all targets near the player.
        needs_scan = True
        while needs_scan:
            needs_scan = False
            for target in self.scanner():
                success, cur_lootables = self.attempt_open(target)
                if not success:
                    needs_scan = True
                if is_greedy and len(cur_lootables) > 0:
                    return cur_lootables[:1]

        # Scan all the lootable items in the targets.
        lootables = []
        for target in self.scanner():
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
        for i, rule in enumerate(self.profile.rules):
            # Sort the lootables based on the rule
            item_to_loot = None
            for item in lootables:
                if rule.test(item):
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
                    if rule.lootbag.test(summary):
                        lootbag = item.Serial
                        break
            # Move the item to the lootbag
            Items.Move(item_to_loot.serial, lootbag, -1)
            if rule.notify:
                Misc.SendMessage(f"Looter> {rule.name} matched: {item_to_loot.name}")
            return True

        return False

    def loot_loop(self):
        """
        Loop to scan for lootable items and attempt to loot them based on the profile rules.
        """
        delay_refresh = self.setting.get("refresh-rate", 500)
        delay_action = self.setting.get("action-delay", 900)
        while Player.Connected and not self._stop_event.is_set():
            if self.mode == LootingMode.STOPPED:
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

    @classmethod
    def scanner_basic(cls):
        scan_corpse = Items.FindAllByID(0x2006, -1, -1, 2)
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
