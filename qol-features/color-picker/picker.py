################################################################################
# Settings

VERSION = "1.1"
COLOR_PRESETS = "presets.xml"

################################################################################
# Imports

import os
import sys

# Ensure we can import from the current directory
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(SCRIPT_DIR)

# Import
from gumpradio.templates import CraftingGumpBuilder

# standard imports
from AutoComplete import *
from typing import List, Dict, Set, Tuple, Any, Optional, Union, Iterable
from System.Collections.Generic import List as CList  # type: ignore
from System import Byte  # type: ignore
import xml.etree.ElementTree as ET

################################################################################
# UI


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


DIR_TO_NUM = {
    "North": 0,
    "Right": 1,
    "East": 2,
    "Down": 3,
    "South": 4,
    "Left": 5,
    "West": 6,
    "Up": 7,
}


def render_mobile(
    serial: int,
    body: int,
    x: int,
    y: int,
    z: int,
    facing: int = 0,
    color: int = 0,
    flag: int = 0,
    notoriety: int = 1,
):
    packet = PacketBuilder(0x78)
    packet.add_short(24)
    packet.add_int(serial)
    packet.add_short(body)
    packet.add_short(x)
    packet.add_short(y)
    packet.add_byte(z)
    packet.add_byte(facing)
    packet.add_short(color)
    packet.add_byte(flag)
    packet.add_byte(notoriety)
    packet.add_bytes(b"\x00\x00\x00\x00\x00")
    PacketLogger.SendToClient(CList[Byte](packet.build()))


def change_mobile_color(mobile: "Mobile", color: int):
    pos = mobile.Position
    dir = DIR_TO_NUM.get(mobile.Direction, 0)
    render_mobile(mobile.Serial, mobile.Graphics, pos.X, pos.Y, pos.Z, dir, color, 0, mobile.Notoriety)


class ColorPickerUI:
    COLORS: ET.ElementTree[ET.Element[str]] = ET.ElementTree()

    @classmethod
    def load_colors(cls):
        file_path = os.path.join(SCRIPT_DIR, COLOR_PRESETS)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Color presets file not found: {file_path}")
        cls.COLORS = ET.parse(file_path)

    @classmethod
    def pick_color(cls) -> Optional[Tuple[str, int, int]]:
        serial = Target.PromptTarget(f"Select an item or mobile to pick color from.")
        if serial == -1:
            return
        if Misc.IsItem(serial):
            item = Items.FindBySerial(serial)
            if item is None:
                Misc.SendMessage("Target not found.", 33)
                return
            return (item.Name, item.Color, item.ItemID)
        elif Misc.IsMobile(serial):
            mobile = Mobiles.FindBySerial(serial)
            if mobile is None:
                Misc.SendMessage("Target not found.", 33)
                return
            return (mobile.Name, mobile.Color, 0x2124)
        else:
            Misc.SendMessage("Target is neither an item nor a mobile.", 33)
            return

    @classmethod
    def test_color(cls, color_name: str, color_value: int, model: int):
        serial = Target.PromptTarget(f"Select an item or mobile to apply the color: {color_name}")
        if serial == -1:
            return
        if Misc.IsItem(serial):
            item = Items.FindBySerial(serial)
            if item is None:
                Misc.SendMessage("Target not found.", 33)
                return
            Items.SetColor(serial, color_value)
            Misc.SendMessage(f"Applied color '{color_name}' to the targeted item.", 68)
        elif Misc.IsMobile(serial):
            mobile = Mobiles.FindBySerial(serial)
            if mobile is None:
                Misc.SendMessage("Target not found.", 33)
                return
            change_mobile_color(mobile, color_value)
            Misc.SendMessage(f"Applied color '{color_name}' to the targeted mobile.", 68)
        else:
            Misc.SendMessage("Target is neither an item nor a mobile.", 33)
            return

    @classmethod
    def picker(cls):
        COLOR_PER_PAGE = 16
        SELECTED_INDEX = -1
        SELECTED_PAGE = 0
        LAST_COLORS = []

        def _test_color_and_update(entry):
            if entry in LAST_COLORS:
                LAST_COLORS.remove(entry)
            LAST_COLORS.insert(0, entry)
            if len(LAST_COLORS) > COLOR_PER_PAGE:
                LAST_COLORS.pop()
            cls.test_color(*entry)

        gb = CraftingGumpBuilder(id="ColorPickerGump")
        with gb.MainFrame():
            # Header
            with gb.ShadedColumn(halign="center"):
                gb.Html("Color Picker", centered=True, color="#FFFFFF")
            # Categories
            with gb.Row(spacing=5):
                with gb.ShadedColumn() as c:
                    col_categories = c
                with gb.ShadedColumn(halign="center") as c:
                    col_colors = c
            # Footer
            with gb.ShadedColumn():
                with gb.Row():
                    btn_pick = gb.CraftingButton("PICK FROM ITEM", width=150)
                    gb.CraftingButton("EXIT", width=100, style="x")

        while True:
            col_categories.clear_children()
            col_colors.clear_children()

            # Titles
            gb.current = col_categories
            gb.Html("CATEGORIES", centered=True, width=215, color="#FFFFFF")
            gb.Spacer(5)

            gb.current = col_colors
            gb.Html("COLORS", centered=True, width=300, color="#FFFFFF")
            gb.Spacer(5)

            btn_category = {}
            btn_color = {}
            max_pages = 0
            e_groups = list(cls.COLORS.getroot().findall("group"))
            for idx in range(-1, len(e_groups)):
                # Populate Categories
                gb.current = col_categories
                if idx == -1:
                    e_group = ET.Element("group", attrib={"name": f"LAST {COLOR_PER_PAGE} COLORS"})
                    for name, color, model in LAST_COLORS:
                        e_color = ET.Element("color", attrib={"name": name, "value": str(color), "model": str(model)})
                        e_group.append(e_color)
                else:
                    e_group = e_groups[idx]
                button = gb.CraftingButton(e_group.attrib["name"], width=175)
                btn_category[button] = idx

                if SELECTED_INDEX != idx:
                    continue

                # Populate Colors
                gb.current = col_colors
                e_colors = list(e_group.findall("color"))
                max_pages = len(e_colors) // COLOR_PER_PAGE
                with gb.Row(spacing=10):
                    for j in range(2):
                        with gb.Column(width=210):
                            for i in range(COLOR_PER_PAGE // 2):
                                color_idx = SELECTED_PAGE * COLOR_PER_PAGE + j * (COLOR_PER_PAGE // 2) + i
                                if color_idx >= len(e_colors):
                                    gb.Spacer(60)
                                    continue
                                e_color = e_colors[color_idx]
                                color = int(e_color.attrib["value"], 0)
                                model = int(e_color.attrib.get("model", "0x1F03"), 0)
                                with gb.Row(spacing=5):
                                    button = gb.Checkbox(up=2328, down=2329, width=80, height=60)
                                    button.add_tileart(graphics=model, hue=color)
                                    btn_color[button] = (e_color.attrib["name"], color, model)
                                    gb.Html(e_color.attrib["name"], color="#FFFFFF", width=125, height=60)

            # Color Navigation
            gb.current = col_colors
            gb.Spacer(5)
            with gb.Row():
                btn_prev = gb.CraftingButton("PREV", width=100, style="left")
                btn_next = gb.CraftingButton("NEXT", width=100, style="right")

            block, response = gb.launch().wait_response().unpack()

            if block in btn_category:
                SELECTED_INDEX = btn_category[block]
                SELECTED_PAGE = 0
                continue

            if block in btn_color:
                entry = btn_color[block]
                _test_color_and_update(entry)
                continue

            if block == btn_pick:
                entry = cls.pick_color()
                if entry is not None:
                    _test_color_and_update(entry)
                continue

            if block == btn_prev:
                if SELECTED_PAGE > 0:
                    SELECTED_PAGE -= 1
                continue

            if block == btn_next:
                if SELECTED_PAGE < max_pages:
                    SELECTED_PAGE += 1
                continue

            return


if __name__ == "__main__":
    ColorPickerUI.load_colors()
    ColorPickerUI.picker()
