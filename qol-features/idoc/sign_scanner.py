from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from System import Int32  # type: ignore
from typing import List
import re
import os
import json
from datetime import datetime


DATA_PATH = "Data/idoc_sign_data.json"
MARKER_PATH = "Data/Client/Houses.map"
HOUSE_SIGNS = [2966, 3140] + list(range(2980, 3087, 2))
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

filter = Items.Filter()
filter.Enabled = True
filter.OnGround = True
filter.Graphics = CList[Int32](HOUSE_SIGNS)


decay_level = {
    "This structure is like new.": 0,
    "This structure is slightly worn.": 1,
    "This structure is somewhat worn.": 2,
    "This structure is fairly worn.": 3,
    "This structure is greatly worn.": 4,
    "This structure is in danger of collapsing.": 5,
}

color_map = [0x3B2, 88, 68, 48, 28, 0x481]


if __name__ == "__main__":
    sign_data = {}
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r") as f:
                sign_data = json.load(f)
    except Exception as e:
        Misc.SendMessage(f"Failed to load existing sign data: {e}", 0x21)

    def add_record(item: "Item"):
        Items.WaitForProps(item.Serial, 1000)
        if item.Name.lower() != "a house sign":
            return

        props = Items.GetPropStringList(item.Serial)
        house_name = "Unnamed"
        for prop in props:
            matchres = re.match(r"^Name: (.+)$", prop)
            if matchres:
                house_name = matchres.group(1)
                continue

            matchres = re.match(r"^Condition: (.+)$", prop)
            if not matchres:
                continue

            condition = matchres.group(1)
            decay = decay_level.get(condition, None)
            if decay is None:
                return

            color = color_map[decay]
            text = "■" * decay + "□" * (5 - decay)
            Items.Message(item, color, text)

            pos = item.Position
            key = (pos.X, pos.Y, Player.Map)
            sign_data[str(key)] = {
                "serial": int(item.Serial),
                "last-seen": datetime.now().strftime(DATETIME_FORMAT),
                "decay-level": decay,
                "house-name": house_name,
                "properties": [str(p) for p in props],
            }
            return

    def save_data():
        with open(DATA_PATH, "w") as f:
            json.dump(sign_data, f, indent=4)
        with open(MARKER_PATH, "w") as f:
            f.write("3\n")
            for key, info in sign_data.items():
                x, y, m = map(int, key.strip("()").split(", "))
                decay_level = info["decay-level"]
                last_seen = info["last-seen"]
                f.write(f"+DECAY{decay_level}: {x} {y} {m} {last_seen}\n")

    while Player.Connected:
        # Clean up old records near player
        for dx in range(-10, 11):
            for dy in range(-10, 11):
                x, y = Player.Position.X + dx, Player.Position.Y + dy
                pos = str((x, y, Player.Map))
                if pos in sign_data:
                    del sign_data[pos]

        # Record new signs
        for item in Items.ApplyFilter(filter):
            add_record(item)

        save_data()

        Misc.Pause(1000)
