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

from System.Collections.Generic import List
from System import Byte
import time


VERSION = "1.1.0"
GUMP_MENU = 0x123546AC
GUMP_BUTTONTEXT_WRAP = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
is_running = True
t_attack = time.time()
t_cast = time.time()


# Mobile class
Mobile = type(Mobiles.FindBySerial(Player.Serial))


def dist(entry):
    d_x = Player.Position.X - entry.Position.X
    d_y = Player.Position.Y - entry.Position.Y
    return max(abs(d_x), abs(d_y))


def gump_menu() -> None:
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Lazy Pally Helper"), False, False)

    if is_running:
        Gumps.AddButton(gd, 10, 30, 40297, 40298, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Disable Helper"), False, False)
    else:
        Gumps.AddButton(gd, 10, 30, 40021, 40031, 2, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Enable Helper"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)


gump_menu()
while Player.Connected:
    if Gumps.WaitForGump(GUMP_MENU, 1):
        gd = Gumps.GetGumpData(GUMP_MENU)
        if gd.buttonid == 1:
            is_running = False
        elif gd.buttonid == 2:
            is_running = True
        gump_menu()

    # Heal self
    if (Player.Hits < Player.HitsMax or Player.Poisoned) and not Player.BuffsExist("Healing"):
        bandage = Items.FindByID(0x0E21, -1, Player.Backpack.Serial, 2)
        if bandage is not None:
            Items.UseItem(bandage.Serial)
            Target.WaitForTarget(1000, True)
            Target.Self()
            Misc.Pause(500)
            continue

    # Clear debuffs
    if (Player.Hits >= (DEBUFF_THRESHOLD * Player.HitsMax / 100)) and (Player.Mana >= 20):
        for debuff in DEBUFFS_TO_REMOVE:
            if Player.BuffsExist(debuff) and time.time() >= t_cast:
                Spells.Cast("Remove Curse")
                if Target.WaitForTarget(3000, True):
                    Target.Self()
                    t_cast = time.time() + (SPELL_DELAY / 1000)
                break

    # If it's not running, skip below
    if not is_running:
        Misc.Pause(100)
        continue

    # Detect enemies
    enemy = Mobiles.Filter()
    enemy.Enabled = True
    enemy.Notorieties = List[Byte](b"\x03\x04\x05\x06")
    enemy.RangeMax = DETECT_RANGE
    enemy.Warmode = True
    find_enemy = Mobiles.ApplyFilter(enemy)
    if len(find_enemy) > 0:
        # Attack the nearest mobile
        if time.time() >= t_attack:
            enemy_near = [enemy for enemy in find_enemy if dist(enemy) <= 1]
            if len(enemy_near) > 0:
                next_emeny = Mobiles.Select(List[Mobile](enemy_near), ATTACK_PRIORITY)
                Player.Attack(next_emeny)
            t_attack = time.time() + 0.5
        # Keep buffs
        for buff in BUFFS_TO_KEEP:
            if not Player.BuffsExist(buff) and time.time() >= t_cast:
                Spells.Cast(buff)
                t_cast = time.time() + (SPELL_DELAY / 1000)
                break

    Misc.Pause(100)
