################################################################################
# User configuration
# You can modify these variables to customize the behavior of the script.
################################################################################

REFRESH_DURATION = 1000
"""Duration (in milliseconds) between refreshes of the durability information."""

ALERT_LOW_DURABILITY = True
"""Use the alert system."""

ALERT_THRESHOLD = 10
"""Alert when the durability (in percent) is below this threshold."""


################################################################################
# Imports and system configuration
################################################################################

from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
from typing import Union, Tuple
import re


ROW_HEIGHT = 20
"""Height of each row in the durability display."""

GUMP_ID = hash("DurabilityGump") & 0xFFFFFFFF
"""Unique Gump ID for the durability checker."""


################################################################################
# From visualizer library
################################################################################


def VisualEffect(
    type: int,
    src_id: int,
    dst_id: int,
    tile_type: int,
    src_pos: Tuple[int, int, int],
    dst_pos: Tuple[int, int, int],
    speed: int,
    duration: int,
    unk1: int,
    unk2: int,
    fixed_dir: bool,
    explodes: bool,
    hue: int,
    render_mode: int,
) -> None:
    packet = b"\xc0"
    packet += (type & 0xFF).to_bytes(1, "big")
    packet += (src_id & 0xFFFFFFFF).to_bytes(4, "big")
    packet += (dst_id & 0xFFFFFFFF).to_bytes(4, "big")
    packet += (tile_type & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[0] & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[1] & 0xFFFF).to_bytes(2, "big")
    packet += (src_pos[2] & 0xFF).to_bytes(1, "big")
    packet += (dst_pos[0] & 0xFFFF).to_bytes(2, "big")
    packet += (dst_pos[1] & 0xFFFF).to_bytes(2, "big")
    packet += (dst_pos[2] & 0xFF).to_bytes(1, "big")
    packet += (speed & 0xFF).to_bytes(1, "big")
    packet += (duration & 0xFF).to_bytes(1, "big")
    packet += (unk1 & 0xFF).to_bytes(1, "big")
    packet += (unk2 & 0xFF).to_bytes(1, "big")
    packet += (int(fixed_dir) & 0xFF).to_bytes(1, "big")
    packet += (int(explodes) & 0xFF).to_bytes(1, "big")
    packet += (hue & 0xFFFFFFFF).to_bytes(4, "big")
    packet += (render_mode & 0xFFFFFFFF).to_bytes(4, "big")

    PacketLogger.SendToClient(CList[Byte](packet))


def VisualEffectSelf(
    src: int,
    tile_type: int,
    duration: int,
    hue: int = 0,
    render_mode: int = 0,
    speed: int = 1,
    unk1: int = 0,
    unk2: int = 0,
):
    """
    Creates a graphical effect at the source object.

    :param src: The ID of the source object.
    :param tile_type: The tile ID of the effect.
    :param duration: The number of frames in a single cycle of the animation.
    :param hue: The hue of the effect.
    :param render_mode: The render mode of the effect. (0 to 7)
    """
    VisualEffect(3, src, 0, tile_type, (0, 0, 0), (0, 0, 0), speed, duration, unk1, unk2, False, False, hue, render_mode)


################################################################################
# Helpers
################################################################################


def proper_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def _to_colored(matchobj) -> str:
    """Replace the durability progression bar to a colored one."""
    x = matchobj.group(1)
    y = matchobj.group(2)
    w = matchobj.group(3)
    h = matchobj.group(4)
    dur_level = int(8 * int(w) / 90)
    hue = 0x22 + 5 * dur_level
    return f"picinpichued {x} {y} 9354 0 0 {w} {h} {hue}"


################################################################################
# Layer entry class
################################################################################


class LayerEntry:
    LAYERS = [
        "RightHand",
        "LeftHand",
        "Shoes",
        "Pants",
        "Shirt",
        "Head",
        "Gloves",
        "Ring",
        "Neck",
        "Waist",
        "InnerTorso",
        "Bracelet",
        "MiddleTorso",
        "Earrings",
        "Arms",
        "Cloak",
        "OuterTorso",
        "OuterLegs",
        "InnerLegs",
        "Talisman",
    ]

    @classmethod
    def iter_layers(cls):
        for layer in cls.LAYERS:
            item = Player.GetItemOnLayer(layer)
            if item is None:
                continue
            Items.WaitForProps(item.Serial, 1000)
            if item.MaxDurability == 0:
                continue
            yield cls(
                item.Serial,
                layer,
                item.Durability,
                item.MaxDurability,
                proper_case(item.Name),
            )

    def __init__(self, serial: int, layer: str, dur: int, max_dur: int, name: str):
        self.serial = serial
        self.layer = layer
        self.dur = dur
        self.max_dur = max_dur
        self.dur_ratio = dur / max(1, max_dur)
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LayerEntry):
            raise ValueError("Cannot compare LayerEntry with non-LayerEntry object")
        return self.serial == other.serial and self.layer == other.layer and self.dur == other.dur and self.max_dur == other.max_dur


################################################################################
# Main logic
################################################################################


prev_layers = []
while Player.Connected:
    gump_closed = Gumps.WaitForGump(GUMP_ID, REFRESH_DURATION)
    cur_layers = list(LayerEntry.iter_layers())

    if ALERT_LOW_DURABILITY and not Timer.Check("blink"):
        has_low_dur = any(100 * entry.dur_ratio <= ALERT_THRESHOLD for entry in cur_layers)
        if has_low_dur:
            Misc.SendMessage("Some of your equipments has low durability!", 53)
            Timer.Create("blink", 3000)
            VisualEffectSelf(Player.Serial, 14284, 25, 53, 3, 1)

    if (not gump_closed) and (cur_layers == prev_layers):
        continue

    prev_layers = cur_layers

    # Sort layers by durability
    cur_layers = sorted(cur_layers, key=lambda x: x.dur / x.max_dur)
    num_entries = len(cur_layers)

    # Render the gump
    Gumps.CloseGump(GUMP_ID)
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    Gumps.AddBackground(gd, 0, 0, 230, 10 + ROW_HEIGHT * num_entries, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 230, 10 + ROW_HEIGHT * num_entries)

    for i, entry in enumerate(cur_layers):
        # Compute various quantities for visualization
        r = entry.dur_ratio
        dur_perc = 100 * r
        dur_level = int(8 * r)
        cur_y = 5 + ROW_HEIGHT * i
        cur_hue = 0x21 + 5 * dur_level
        tooltip_msg = f'<BASEFONT COLOR="#FFFF00">{entry.name}</BASEFONT><BR />{entry.dur} / {entry.max_dur} ({dur_perc:.1f}%)'
        # Display the durability status
        Gumps.AddLabel(gd, 10, cur_y, 0x47E, entry.layer)
        Gumps.AddTooltip(gd, tooltip_msg)
        Gumps.AddImageTiled(gd, 130, cur_y + 2, 90, ROW_HEIGHT - 4, 40004)
        Gumps.AddTooltip(gd, entry.serial)
        Gumps.AddImageTiled(gd, 130, cur_y + 2, int(90 * r), ROW_HEIGHT - 4, 9354)
        Gumps.AddTooltip(gd, entry.serial)
        Gumps.AddLabel(gd, 90, cur_y, cur_hue, f"{dur_perc:.0f}%")

    gd_def = re.sub(r"gumppictiled (\d+) (\d+) (\d+) (\d+) 9354", _to_colored, gd.gumpDefinition)
    gd_def = re.sub(r"\{ tooltip (\d+) \}", r"{ itemproperty \1 }", gd_def)
    Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd_def, gd.gumpStrings)
