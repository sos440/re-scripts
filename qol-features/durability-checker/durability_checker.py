from AutoComplete import *

# User Configuration:
REFRESH_DURATION = 1000
"""Duration (in milliseconds) between refreshes of the durability information."""
DANGER_THRESHOLD = 40
"""Alert when durability (in percent) is below the danger threshold."""
ROW_HEIGHT = 20
"""Height of each row in the durability display."""
GUMP_ID = 0xBEEFDADE
"""Unique Gump ID for the durability checker."""


def proper_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


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
                layer,
                item.Durability,
                item.MaxDurability,
                proper_case(item.Name),
            )

    def __init__(self, layer: str, dur: int, max_dur: int, name: str):
        self.layer = layer
        self.dur = dur
        self.max_dur = max_dur
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LayerEntry):
            raise ValueError("Cannot compare LayerEntry with non-LayerEntry object")
        return self.layer == other.layer and self.dur == other.dur and self.max_dur == other.max_dur and self.name == other.name


prev_layers = []
while Player.Connected:
    gump_closed = Gumps.WaitForGump(GUMP_ID, REFRESH_DURATION)
    cur_layers = list(LayerEntry.iter_layers())

    if not gump_closed and cur_layers == prev_layers:
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
        dur_ratio = entry.dur / entry.max_dur
        dur_perc = 100 * dur_ratio
        dur_level = int(5 * dur_ratio)
        cur_y = 5 + ROW_HEIGHT * i
        cur_hue = 0x21 + 5 * dur_level
        tooltip_msg = f'<BASEFONT COLOR="#FFFF00">{entry.name}</BASEFONT><BR />{entry.dur} / {entry.max_dur} ({dur_perc:.1f}%)'
        # Display the durability status
        Gumps.AddLabel(gd, 10, cur_y, 0x47E, entry.layer)
        Gumps.AddTooltip(gd, tooltip_msg)
        Gumps.AddImageTiled(gd, 130, cur_y + 2, 90, ROW_HEIGHT - 4, 40004)
        Gumps.AddTooltip(gd, tooltip_msg)
        Gumps.AddImageTiled(gd, 130, cur_y + 2, int(90 * dur_ratio), ROW_HEIGHT - 4, 9354)
        Gumps.AddLabel(gd, 90, cur_y, cur_hue, f"{dur_perc:.0f}%")

    Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd.gumpDefinition, gd.gumpStrings)
