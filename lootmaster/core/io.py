import json
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

# This allows the RazorEnhanced to correctly identify the path of the current module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

from match import LootProfile


################################################################################
# I/O
################################################################################


SAVE_DIR = "./Data/LootProfiles"
SETTING_PATH = os.path.join(SAVE_DIR, "settings.json")
PROFILE_DIR = os.path.join(SAVE_DIR, "Profiles")
RULE_DIR = os.path.join(SAVE_DIR, "Rules")


SETTING_SCHEMA = {
    "last-profile-filename": None,
    "last-profile-name": None,
    "refresh-rate": 500,
    "action-delay": 900,
    "max-open-attempts": 3,
    "greedy-looting": False,
    "mark-after-finished": True,
    "mark-color": 1014,
}


def load_setting() -> dict:
    """
    Load the settings from the settings.json file.
    If the file does not exist, return the default settings.
    """
    try:
        if not os.path.exists(SETTING_PATH):
            raise FileNotFoundError(f"Setting file not found.")
        with open(SETTING_PATH, "r") as f:
            setting = json.load(f)
        for option_key in SETTING_SCHEMA:
            if option_key in setting:
                continue
            else:
                setting[option_key] = SETTING_SCHEMA[option_key]
        return setting
    except:
        return SETTING_SCHEMA.copy()


def save_setting(setting: dict):
    with open(SETTING_PATH, "w") as f:
        json.dump(setting, f, indent=4)


def load_profile(profile_filename: str) -> LootProfile:
    # Create a profile directory if necessary
    if not os.path.exists(PROFILE_DIR):
        os.mkdir(PROFILE_DIR)
    # Load the profile from the specified path
    profile_path = os.path.join(PROFILE_DIR, profile_filename)
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile file not found: {profile_path}")
    with open(profile_path, "r") as f:
        profile_dict = json.load(f)
    return LootProfile.load(profile_dict)


def save_profile(profile: LootProfile, profile_filename: str):
    # Create a profile directory if necessary
    if not os.path.exists(PROFILE_DIR):
        os.mkdir(PROFILE_DIR)
    # Save the profile to the specified path
    profile_path = os.path.join(PROFILE_DIR, profile_filename)
    with open(profile_path, "w") as f:
        json.dump(profile.to_dict(), f, indent=4)
