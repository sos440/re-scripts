################################################################################
# User setting
################################################################################


# Only the enemies within this distance will be scanned.
DETECT_RANGE = 18

# Only the enemies in war mode will be attacked
WARMODE_ONLY = False

# Delay between attacks, in seconds
ATTACK_DELAY = 1.0


################################################################################
# Script starts here
################################################################################

from System.Collections.Generic import List
from System import Byte
import time


VERSION = "1.0.0"
GUMP_MENU = hash("AttackSpammerGump") & 0xFFFFFFFF
GUMP_BUTTONTEXT_WRAP = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""
is_running = False
t_attack = time.time()


def gump_menu() -> None:
    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 65, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 65)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Attack Spammer"), False, False)

    if is_running:
        Gumps.AddButton(gd, 10, 30, 40297, 40298, 1, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Stop Attack"), False, False)
    else:
        Gumps.AddButton(gd, 10, 30, 40021, 40031, 2, 1, 0)
        Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Start Attack"), False, False)

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

    # If it's not running, skip
    if not is_running:
        Misc.Pause(100)
        continue
        
    # If not cooled down, skip
    if time.time() < t_attack:
        Misc.Pause(100)
        continue

    # Detect enemies
    enemy = Mobiles.Filter()
    enemy.Enabled = True
    enemy.Notorieties = List[Byte](b"\x03\x04\x05\x06")
    enemy.RangeMax = DETECT_RANGE
    if WARMODE_ONLY:
        enemy.Warmode = True
    find_enemy = Mobiles.ApplyFilter(enemy)
    for enemy in find_enemy:
        Player.Attack(enemy)
    if len(find_enemy) > 0:
        t_attack = time.time() + ATTACK_DELAY

    Misc.Pause(100)
