################################################################################
# User setting
################################################################################

# If it is set to True, you will attack any hostile mobs in war mode.
ATTACK_NEAR = True

# If it is set to "Weakest", you will attack the one with lowest health.
# If it is set to "Strongest", you will attack the one with highest health.
ATTACK_PRIORITY = "Weakest"

# Spell delay in milliseconds.
SPELL_DELAY = 1000

# Remove curse will be casted after you are safe for this duration.
REMOVE_CURSE_DELAY = 3000

# Only the enemies within this distance will be scanned.
DETECT_RANGE = 8

# Attempts to remove debuffs only when your health is above this percentage.
DEBUFF_THRESHOLD = 90

# List of buffs to keep when you are engaging in a battle.
BUFFS_TO_KEEP = [
    "Consecrate Weapon",
    "Divine Fury",
]

# List of debuffs to remove. Only include debuffs that can be cured by Remove Curse!
DEBUFFS_TO_REMOVE = [
    "Clumsy",
    "Weaken",
    "Feeble Mind",
    "Curse",
    "Corpse Skin",
    "Evil Omen",
    "Mind Rot",
    "Strangle",
    "Blood Oath",
    "Mortal Strike",
]

################################################################################
# Script starts here
################################################################################

from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from typing import List
import time


VERSION = "1.1.0"
GUMP_MENU = hash("LazyPallyHelperGump") & 0xFFFFFFFF
GUMP_WRAPTXT = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
is_running = True


Mobile = type(Mobiles.FindBySerial(Player.Serial))


def set_cr_timer():
    """Set the casting recovery timer."""
    delay = 2000 - 250 * min(6, Player.FasterCastRecovery)
    Timer.Create("casting-recovery", delay)


SPELL_DATABASE = {
    "Close Wounds": {"cost": 10, "casting-time": 1500, "word": "Obsu Vulni"},
    "Consecrate Weapon": {"cost": 10, "casting-time": 500, "word": "Consecrus Arma"},
    "Divine Fury": {"cost": 10, "casting-time": 1000, "word": "Divinum Furis"},
    "Remove Curse": {"cost": 20, "casting-time": 2000, "word": "Extermo Vomica"},
}


def get_mana_cost(spell: str) -> int:
    """Compute the mana cost of a spell."""
    cost = 20
    if spell in SPELL_DATABASE:
        cost = SPELL_DATABASE[spell]["cost"]
    reduce = int(cost * 0.01 * min(40, Player.LowerManaCost))
    return cost - reduce


def can_cast(spell: str) -> bool:
    """Check if the player can cast a spell."""
    assert spell in SPELL_DATABASE
    if Timer.Check("casting-delay"):
        return False
    if Timer.Check("casting-recovery"):
        return False
    if Player.Mana < get_mana_cost(spell):
        return False
    return True


def wait_for_word(spell: str, delay: int) -> bool:
    """Wait for the spell's incantation to be spoken."""
    assert spell in SPELL_DATABASE
    word = SPELL_DATABASE[spell]["word"]
    Journal.Clear()
    t = time.time()
    Timer.Create("wait-for-word", delay)
    while Timer.Check("wait-for-word"):
        for entry in Journal.GetJournalEntry(t):
            if entry.Name == Player.Name and entry.Text.strip() == word:
                return True
        Journal.Clear()
        Misc.Pause(100)
    return False


def safe_cast(spell: str) -> bool:
    """Attempt to cast a spell safely."""
    assert spell in SPELL_DATABASE
    if not can_cast(spell):
        return False
    Journal.Clear()
    Spells.Cast(spell)
    Timer.Create("casting-delay", 500 + SPELL_DATABASE[spell]["casting-time"])
    if wait_for_word(spell, 500):
        return True
    else:
        Timer.Create("casting-delay", 1)
        return False


def gump_menu() -> None:
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_WRAPTXT.format(text="Lazy Pally Helper"), False, False)

    if is_running:
        Gumps.AddButton(gd, 10, 30, 40297, 40298, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WRAPTXT.format(text="Disable"), False, False)
    else:
        Gumps.AddButton(gd, 10, 30, 40021, 40031, 2, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_WRAPTXT.format(text="Enable"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


def enemy_include(enemy: "Mobile") -> bool:  # type: ignore
    """Check if an enemy should be included."""
    if enemy.Body == 0x33:  # if it's a nature's fury
        return False
    return True


def find_enemies() -> List["Mobile"]:  # type: ignore
    enemy = Mobiles.Filter()
    enemy.Enabled = True
    enemy.Notorieties = CList[Byte](b"\x03\x04\x05\x06")
    enemy.RangeMax = DETECT_RANGE
    enemy.Warmode = True
    enemies = Mobiles.ApplyFilter(enemy)
    enemies = [e for e in enemies if enemy_include(e)]
    return enemies


gump_menu()
while Player.Connected:
    if Gumps.WaitForGump(GUMP_MENU, 1):
        gd = Gumps.GetGumpData(GUMP_MENU)
        if gd.buttonid == 1:
            is_running = False
        elif gd.buttonid == 2:
            is_running = True
        gump_menu()

    # If the player is ghost, skip
    if Player.IsGhost:
        Misc.Pause(100)
        continue

    # Heal self
    if (Player.Hits < Player.HitsMax or Player.Poisoned) and not Player.BuffsExist("Healing", True):
        # If you're damaged, reset the safe timer
        Timer.Create("safe", REMOVE_CURSE_DELAY)
        bandage = Items.FindByID(0x0E21, -1, Player.Backpack.Serial, 2, False)
        if bandage is not None:
            Target.Cancel()
            Items.UseItem(bandage.Serial)
            if not Target.WaitForTarget(500, True):
                continue
            Target.Self()
            Target.Cancel()
            Misc.Pause(250)
            continue

    # Clear debuffs
    if not Timer.Check("safe") and (Player.Hits >= (DEBUFF_THRESHOLD * Player.HitsMax / 100)) and can_cast("Remove Curse"):
        updated = False
        for debuff in DEBUFFS_TO_REMOVE:
            if not Player.BuffsExist(debuff, True):
                continue
            updated = True
            if not safe_cast("Remove Curse"):
                break
            if Target.WaitForTarget(2500, True):
                Target.Self()
                set_cr_timer()
            break
        if updated:
            continue

    # If it's not running, skip below
    if not is_running:
        Misc.Pause(100)
        continue

    # Detect enemies
    enemies = find_enemies()
    # If you're surrounded by multiple enemies, wait before removing curses
    if len(enemies) > 1:
        Timer.Create("safe", REMOVE_CURSE_DELAY)
    if len(enemies) > 0:
        # Attack the nearest mobile
        if not Timer.Check("attack-delay"):
            enemy_near = [enemy for enemy in enemies if Player.DistanceTo(enemy) <= 1]
            if len(enemy_near) > 0:
                next_emeny = Mobiles.Select(CList[Mobile](enemy_near), ATTACK_PRIORITY)
                assert next_emeny is not None
                Player.Attack(next_emeny)
                Timer.Create("attack-delay", 500)
        # Keep buffs
        for buff in BUFFS_TO_KEEP:
            if Player.BuffsExist(buff, True):
                continue
            if not can_cast(buff):
                continue
            safe_cast(buff)
            set_cr_timer()
            break

    Misc.Pause(100)
