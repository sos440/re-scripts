import os
import sys
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

# Import the modules
import core.io as io
from core.match import *
from core.presets import LootMatchPresets
from core.looter import Looter, LootingMode


################################################################################
# Logger
################################################################################


class Logger:
    @classmethod
    def Error(cls, msg: str):
        Misc.SendMessage(msg, 33)

    @classmethod
    def Warn(cls, msg: str):
        Misc.SendMessage(msg, 43)

    @classmethod
    def Info(cls, msg: str):
        Misc.SendMessage(msg, 63)

    @classmethod
    def Debug(cls, msg: str):
        Misc.SendMessage(msg, 0x3B2)


################################################################################
# Application
################################################################################


def create_template_profile() -> LootProfile:
    profile = LootProfile(f"{Player.Name}")
    # Rule: Daily Rares
    rule = profile.add_rule(LootRules("Daily Rares"))
    rule.add_match_props(LootMatchPresets.DailyRare())
    rule.notify = True
    rule.highlight = True
    # Rule: Artifacts
    rule = profile.add_rule(LootRules("Artifacts"))
    rule.add_match_props(LootMatchPresets.Artifact())
    rule.notify = True
    rule.highlight = True
    rule.lootbag = LootMatchItemBase(name="Red Backpack", id=0x0E75, color=33)
    # Rule: Jewelry with High SSI
    rule = profile.add_rule(LootRules("Jewelry, High SSI"))
    rule.add_match_base(LootMatchPresets.Jewelry())
    rule.add_match_props(LootMatchMagicProperty(name="SSI", prop="Swing Speed Increase", min_value=10))
    rule.notify = True
    rule.highlight = True
    rule.lootbag = LootMatchItemBase(name="Red Backpack", id=0x0E75, color=33)
    # Rule: High LRC
    rule = profile.add_rule(LootRules("High LRC"))
    rule.add_match_props(LootMatchMagicProperty(name="LRC", prop="Lower Reagent Cost", min_value=25))
    rule.notify = True
    rule.highlight = True
    rule.lootbag = LootMatchItemBase(name="Red Backpack", id=0x0E75, color=33)
    # Rule: 100% Elemental Damage
    rule = profile.add_rule(LootRules("100% Elemental Damage"))
    rule.add_match_props(
        LootMatchAny(
            name="100% Elemental Damage",
            match_list=[
                LootMatchMagicProperty(name="Cold Damage", prop="Cold Damage", min_value=100),
                LootMatchMagicProperty(name="Energy Damage", prop="Energy Damage", min_value=100),
                LootMatchMagicProperty(name="Fire Damage", prop="Fire Damage", min_value=100),
                LootMatchMagicProperty(name="Poison Damage", prop="Poison Damage", min_value=100),
                LootMatchMagicProperty(name="Chaos Damage", prop="Chaos Damage", min_value=100),
            ],
        )
    )
    rule.notify = True
    rule.highlight = True
    rule.highlight_color = 1152
    rule.lootbag = LootMatchItemBase(name="Red Backpack", id=0x0E75, color=33)
    # Rule: Gold
    rule = profile.add_rule(LootRules("Gold"))
    rule.add_match_base(LootMatchPresets.Gold())
    # Rule: Seeds
    rule = profile.add_rule(LootRules("Seeds"))
    rule.add_match_base(LootMatchItemBase(name="Seeds", id=0x0DCF))
    rule.notify = True
    rule.highlight = True
    # Rule: Paragon Loots
    rule = profile.add_rule(LootRules("Paragon Loots"))
    rule.add_match_base(LootMatchItemBase(name="Vanilla", id=0x0E2A))
    rule.add_match_base(LootMatchItemBase(name="Sack of Sugar", id=0x1039, color=0x0461))
    rule.add_match_base(LootMatchItemBase(name="Cocoa Liquor", id=0x103F, color=0x046A))
    rule.add_match_base(LootMatchItemBase(name="Cocoa Butter", id=0x1044, color=0x0457))
    rule.notify = True
    rule.highlight = True
    # Rule: Solen Loots
    rule = profile.add_rule(LootRules("Solen Loots"))
    rule.add_match_base(LootMatchItemBase(name="Crystal Ball", id=0x0E2E))
    rule.add_match_base(LootMatchItemBase(name="Picnic Basket", id=0x0E7A))
    rule.add_match_base(LootMatchItemBase(name="Bracelet of Binding", id=0x1086, color=0x0489))
    rule.notify = True
    rule.highlight = True
    # Rule: Map
    rule = profile.add_rule(LootRules("Maps"))
    rule.add_match_base(LootMatchPresets.Map())
    # Rule: Gems
    rule = profile.add_rule(LootRules("Gems"))
    rule.add_match_base(LootMatchPresets.Gem())
    rule.lootbag = LootMatchItemBase(name="Teal Backpack", id=0x0E75, color=88)
    # Rule: Any Magic Items
    rule = profile.add_rule(LootRules("Magic Items"))
    rule.add_match_props(LootMatchPresets.MagicItem())
    rule.add_match_except(LootMatchPresets.UnwieldyMagicItem())
    rule.lootbag = LootMatchItemBase(name="Teal Backpack", id=0x0E75, color=88)
    # Rule: Wands
    rule = profile.add_rule(LootRules("Wands"))
    rule.add_match_base(LootMatchPresets.Wand())
    rule.lootbag = LootMatchItemBase(name="Teal Backpack", id=0x0E75, color=88)
    # Rule: Reagents
    rule = profile.add_rule(LootRules("Reagents"))
    rule.add_match_base(LootMatchPresets.Reagent())
    rule.lootbag = LootMatchItemBase(name="Teal Backpack", id=0x0E75, color=88)
    # Rule: Scrolls
    rule = profile.add_rule(LootRules("Scrolls"))
    rule.add_match_base(LootMatchPresets.Scroll())
    rule.lootbag = LootMatchItemBase(name="Teal Backpack", id=0x0E75, color=88)
    # Rule: Arrows and Bolts
    rule = profile.add_rule(LootRules("Arrows and Bolts"))
    rule.add_match_base(LootMatchPresets.Arrow())
    rule.add_match_base(LootMatchPresets.Bolt())
    rule.lootbag = LootMatchItemBase(name="Teal Backpack", id=0x0E75, color=88)

    return profile


################################################################################
# Application
################################################################################


GUMP_MENU = 0x1234ABCD
GUMP_BUTTONTEXT_WRAP = """<CENTER><BASEFONT COLOR="#FFFFFF">{text}</BASEFONT></CENTER>"""

SETTING = None
PROFILE = None
LOOTER = None


def gump_menu() -> int:
    global SETTING
    global PROFILE
    global LOOTER
    assert LOOTER is not None, "LOOTER is not initialized."

    Gumps.CloseGump(GUMP_MENU)

    # Create the gump
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 146, 115, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 146, 115)

    Gumps.AddHtml(gd, 10, 5, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Lootmaster"), False, False)

    Gumps.AddButton(gd, 10, 30, 40020, 40030, 1001, 1, 0)
    Gumps.AddHtml(gd, 10, 32, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Manual Loot"), False, False)

    if LOOTER.mode == LootingMode.STOPPED:
        Gumps.AddButton(gd, 10, 55, 40021, 40031, 1002, 1, 0)
        Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Enable Autoloot"), False, False)
    else:
        Gumps.AddButton(gd, 10, 55, 40297, 40298, 1003, 1, 0)
        Gumps.AddHtml(gd, 10, 57, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Stop Looter"), False, False)

    Gumps.AddButton(gd, 10, 80, 40299, 40300, 1004, 1, 0)
    Gumps.AddHtml(gd, 10, 82, 126, 18, GUMP_BUTTONTEXT_WRAP.format(text="Edit Profile"), False, False)

    # Send the gump and listen for the response
    Gumps.SendGump(GUMP_MENU, Player.Serial, 100, 100, gd.gumpDefinition, gd.gumpStrings)
    if not Gumps.WaitForGump(GUMP_MENU, 3600000):
        return 0

    gd = Gumps.GetGumpData(GUMP_MENU)
    if gd is None:
        return 0
    return gd.buttonid


def refresh_gump_menu():
    Gumps.SendAction(GUMP_MENU, 0)


def main():
    global SETTING
    global PROFILE
    global LOOTER

    # Load the setting if exists
    SETTING = io.load_setting()
    Logger.Info("Lootmaster has been initialized.")

    # Load the last profile if exists, or create a new one
    profile_filename = SETTING["last-profile-filename"]
    if profile_filename is not None:
        try:
            PROFILE = io.load_profile(profile_filename)
            Logger.Info(f"Profile loaded: {profile_filename}")
        except FileNotFoundError:
            Logger.Error(f"Last profile not found: {profile_filename}")
            PROFILE = create_template_profile()
    else:
        PROFILE = create_template_profile()
        Logger.Info("No last profile found. Created a new profile.")

    # Save the profile
    filename = f"{PROFILE.name}.json"
    io.save_profile(PROFILE, filename)
    Logger.Info(f"Profile saved as: {filename}")

    # Update the setting with the last profile path and name
    SETTING["last-profile-filename"] = filename
    SETTING["last-profile-name"] = PROFILE.name
    io.save_setting(SETTING)
    Logger.Info("Setting saved.")

    # Initialize the looter
    LOOTER = Looter(SETTING, PROFILE)
    LOOTER.callback = refresh_gump_menu
    LOOTER.scanner = Looter.scanner_basic
    LOOTER.start(LootingMode.LOOP)
    Logger.Info("Looter started.")

    # Main loop
    while Player.Connected:
        response = gump_menu()

        if response == 0:
            continue
        if response == 1001:
            # Manual loot
            target_serial = Target.PromptTarget("Select a container to loot.", 0x47E)
            target_obj = Items.FindBySerial(target_serial)
            if target_obj is None:
                Logger.Error("Target not found.")
                continue
            if LOOTER.is_running:
                LOOTER.stop()
            # Start the looter in manual mode
            if target_serial in LOOTER.target_cache:
                # If the target is already in the cache, remove it
                del LOOTER.target_cache[target_serial]
            LOOTER.scanner = Looter.generate_scanner(target_serial)
            LOOTER.start(LootingMode.SINGLE)
            Logger.Info("Manual loot mode enabled.")
            continue
        if response == 1002:
            # Enable autoloot
            if LOOTER.mode == LootingMode.LOOP:
                continue
            if LOOTER.is_running:
                LOOTER.stop()
            # Start the looter in autoloot mode
            LOOTER.scanner = Looter.scanner_basic
            LOOTER.start(LootingMode.LOOP)
            Logger.Info("Autoloot mode enabled.")
            continue
        if response == 1003:
            # Disable autoloot
            if LOOTER.is_running:
                LOOTER.stop()
                Logger.Info("Looter has stopped.")
            continue
        if response == 1004:
            # Edit profile
            Misc.SendMessage("This is currently not supported.")
            # Open the profile editor here
            continue


if __name__ == "__main__":
    main()
