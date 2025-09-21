from AutoComplete import *
from typing import Tuple, Dict, Optional
import os
import sys
import re

# Explorer gump settings
ROW_HEIGHT = 60
COL_WIDTH = 150
BORDER_WIDTH = 10
ITEMS_PER_PAGE = 10
INSPECTOR_WIDTH = 300
IDMOD_INSPECTOR = 0x100

# This allows the RazorEnhanced to correctly identify the path of the module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

import exp_module as exp


# Useful function
class GumpTools:
    CENTER_POS_CACHE: Dict[int, Tuple[int, int]] = {}

    @classmethod
    def get_centering_pos(cls, item_id: int, px: int = 0, py: int = 0, pw: int = 0, ph: int = 0, abs: bool = True) -> Tuple[int, int]:
        """
        Calculates the left-top position for the item to be centered at the given position or rect:
        * If only `px` and `py` are given, it centers the item at `(px, py)`.
        * If `pw` and `ph` are also given, it centers the item at the center of the rect with left-top `(px, py)` and size `(pw, ph)`.
        """
        if item_id not in cls.CENTER_POS_CACHE:
            bitmap = Items.GetImage(item_id, 0)
            w, h = bitmap.Width, bitmap.Height
            # Find the rectangle bounds
            left, top, right, bottom = w, h, 0, 0
            for y in range(h):
                for x in range(w):
                    pixel = bitmap.GetPixel(x, y)
                    if pixel.R or pixel.G or pixel.B:
                        left = min(x, left)
                        top = min(y, top)
                        right = max(x, right)
                        bottom = max(y, bottom)
            # Calculate the relative posotion of the left-top corner
            if right < left or bottom < top:
                dx, dy = 0, 0
            else:
                dx = -(left + right) // 2
                dy = -(top + bottom) // 2
            cls.CENTER_POS_CACHE[item_id] = (dx, dy)

        x, y = cls.CENTER_POS_CACHE[item_id]
        if abs:
            x, y = x + px, y + py
        x, y = x + (pw // 2), y + (ph // 2)
        return (x, y)

    @staticmethod
    def hashname(name: str) -> int:
        return hash(name) & 0xFFFFFFFF

    @staticmethod
    def tooltip_to_itemproperty(gd: Gumps.GumpData) -> str:
        """
        Converts integer-argument tooltips to item properties.
        """
        return re.sub(r"\{ tooltip (\d+) \}", r"{ itemproperty \1 }", gd.gumpDefinition)


# Gump ID
GUMP_ID = GumpTools.hashname("TestGump")


def create_test_gump():
    Gumps.CloseGump(GUMP_ID)

    gd = Gumps.CreateGump(True)

    # Main page
    INNER_WIDTH = 800
    INNER_HEIGHT = ROW_HEIGHT * ITEMS_PER_PAGE + (ITEMS_PER_PAGE - 1)
    WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
    HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT
    items = Items.FindAllByID(list(range(0xFFFF)), -1, Player.Backpack.Serial, 0, False)
    for i, item in enumerate(items):
        page = i // ITEMS_PER_PAGE
        rel_i = i % ITEMS_PER_PAGE
        if rel_i == 0:
            Gumps.AddPage(gd, page + 1)
            Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)
            # Ruled sheet
            for j in range(ITEMS_PER_PAGE):
                x = BORDER_WIDTH
                y = BORDER_WIDTH + j * (ROW_HEIGHT + 1)
                Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, ROW_HEIGHT, 9274)
                Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, ROW_HEIGHT)
        x = BORDER_WIDTH
        y = BORDER_WIDTH + rel_i * (ROW_HEIGHT + 1)
        px, py = GumpTools.get_centering_pos(item.ItemID, x, y, 80, 60, abs=False)
        Gumps.AddImageTiledButton(gd, x, y, 2328, 2329, 0, Gumps.GumpButtonType.Page, IDMOD_INSPECTOR + i, item.ItemID, item.Color, px, py)
        Gumps.AddTooltip(gd, item.Serial)
        x += 85
        y += 19
        Gumps.AddLabelCropped(gd, x, y, COL_WIDTH, 18, 1153, exp.to_proper_case(item.Name))

    # Item inspector
    INNER_WIDTH = INSPECTOR_WIDTH
    INNER_HEIGHT = 442
    WIDTH = 2 * BORDER_WIDTH + INNER_WIDTH
    HEIGHT = 2 * BORDER_WIDTH + INNER_HEIGHT
    for i, item in zip(range(10), items):
        Items.WaitForProps(item.Serial, 1000)
        props = Items.GetPropStringList(item.Serial)
        lines = [
            f'<center><basefont color="#FFFF00">{exp.to_proper_case(props[0])}</basefont></center>',
            f"Item ID: {item.ItemID} (0x{item.ItemID:04X})",
            f"Color: {item.Color}",
        ]
        lines.extend(map(exp.to_proper_case, props[1:]))

        Gumps.AddPage(gd, IDMOD_INSPECTOR + i)
        Gumps.AddBackground(gd, 0, 0, WIDTH, HEIGHT, 5054)
        x, y = BORDER_WIDTH, BORDER_WIDTH
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 100, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 100)
        px, py = GumpTools.get_centering_pos(item.ItemID, x, y, INSPECTOR_WIDTH, 100)
        Gumps.AddItem(gd, px, py, item.ItemID, item.Color)
        Gumps.AddTooltip(gd, item.Serial)
        y += 105
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 300, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 300)
        Gumps.AddHtml(gd, x + 5, y, INNER_WIDTH - 5, 300, "<br>".join(lines), False, True)
        y += 305
        Gumps.AddImageTiled(gd, x, y, INNER_WIDTH, 32, 9274)
        Gumps.AddAlphaRegion(gd, x, y, INNER_WIDTH, 32)
        Gumps.AddButton(gd, x, y + 5, 4005, 4007, 0, 0, 1)
        Gumps.AddLabelCropped(gd, x + 35, y + 7, 100, 18, 1153, "Return")

    # Send gump
    gd_gumpdef = GumpTools.tooltip_to_itemproperty(gd)
    Gumps.SendGump(GUMP_ID, Player.Serial, 100, 100, gd_gumpdef, gd.gumpStrings)


if Player.Connected:
    create_test_gump()
    if Gumps.WaitForGump(GUMP_ID, 360000):
        gd = Gumps.GetGumpData(GUMP_ID)
        print(gd.buttonid)
    else:
        print("Timeout.")
