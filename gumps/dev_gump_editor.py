GUMP_ID = 0x5AFEC0DE
GUMP_W = 800
GUMP_H = 600

GUMP_PRESET_RENAME = 101
GUMP_PRESET_LOAD = 102
GUMP_PRESET_SAVE = 103
GUMP_RULE_EDIT = 200
GUMP_RULE_ADD = 601
GUMP_RULE_DELETE = 602
GUMP_RULE_MOVE_UP = 603
GUMP_RULE_MOVE_DOWN = 604
GUMP_EDIT_NAME = 700
GUMP_EDIT_LOAD = 701
GUMP_EDIT_SAVE = 702
GUMP_EDIT_ENABLED = 703
GUMP_EDIT_NOTIFY = 704
GUMP_EDIT_APPLY = 705
GUMP_EDIT_DISCARD = 706
GUMP_EDIT_ITEMBASE = 800

GUMP_EDIT_NAME_TOOLTIP = "Set a custom name for this rule for easier identification."
GUMP_EDIT_ENABLED_TOOLTIP = "Disable this option to skip this rule during looting."
GUMP_EDIT_NOTIFY_TOOLTIP = "Enable this option to receive notifications when an item matches this rule."

GUMP_TEXT_WELCOME = """Thank you for using Lootmaster!

What you are seeing is the Lootmaster Gump Editor.
This is a tool to help you create and edit your own loot rules.

The column on the left shows the rules you have created.
You can add, delete, move up and down the rules in this column.
Click on the blue button to select a rule to edit.

You can also load and save your rules to a preset.
"""


def editor_show(gump_status):
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    # (1) Background
    Gumps.AddBackground(gd, 0, 0, GUMP_W, GUMP_H, 9270)
    Gumps.AddBackground(gd, 5, 5, GUMP_W - 10, GUMP_H - 10, 3000)

    # (2) Menubar
    Gumps.AddBackground(gd, 5, 5, GUMP_W - 10, 50, 3500)
    # Load Preset
    Gumps.AddGroup(gd, 0)
    Gumps.AddLabel(gd, 25, 21, 0, "Profile:")
    Gumps.AddBackground(gd, 85, 19, 170, 22, 9350)
    Gumps.AddTextEntry(gd, 90, 21, 160, 18, 0, 102, gump_status["preset"]["name"])
    Gumps.AddButton(gd, 260, 19, 40018, 40028, GUMP_PRESET_RENAME, 1, 0)
    Gumps.AddHtml(gd, 260, 21, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Rename</BASEFONT></CENTER>', 0, 0)
    Gumps.AddButton(gd, 325, 19, 40018, 40028, GUMP_PRESET_LOAD, 1, 0)
    Gumps.AddHtml(gd, 325, 21, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Load</BASEFONT></CENTER>', 0, 0)
    Gumps.AddButton(gd, 390, 19, 40018, 40028, GUMP_PRESET_SAVE, 1, 0)
    Gumps.AddHtml(gd, 390, 21, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Save</BASEFONT></CENTER>', 0, 0)
    # Close
    # Gumps.AddButton(gd, GUMP_W - 58, 20, 4017, 4019, 0, 1, 0)

    # (3) Sidebar
    Gumps.AddBackground(gd, 5, 50, 180, GUMP_H - 55, 3500)
    Gumps.AddHtml(gd, 5, 63, 180, 18, "<CENTER>RULES</CENTER>", 0, 0)
    # Add
    Gumps.AddButton(gd, 30, GUMP_H - 62, 40018, 40028, GUMP_RULE_ADD, 1, 0)
    Gumps.AddHtml(gd, 30, GUMP_H - 60, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">New</BASEFONT></CENTER>', 0, 0)
    # Delect
    Gumps.AddButton(gd, 95, GUMP_H - 62, 40018, 40028, GUMP_RULE_DELETE, 1, 0)
    Gumps.AddHtml(gd, 95, GUMP_H - 60, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Delete</BASEFONT></CENTER>', 0, 0)
    # Move Up
    Gumps.AddButton(gd, 30, GUMP_H - 42, 40018, 40028, GUMP_RULE_MOVE_UP, 1, 0)
    Gumps.AddHtml(gd, 30, GUMP_H - 40, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Up</BASEFONT></CENTER>', 0, 0)
    # Move Down
    Gumps.AddButton(gd, 95, GUMP_H - 42, 40018, 40028, GUMP_RULE_MOVE_DOWN, 1, 0)
    Gumps.AddHtml(gd, 95, GUMP_H - 40, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Down</BASEFONT></CENTER>', 0, 0)
    # Existing Rules
    rules = gump_status["preset"]["rules"]
    for i, rule in enumerate(rules):
        if i == gump_status["entry"]:
            Gumps.AddImageTiled(gd, 15, 80 + 20 * i, 160, 20, 9304)
            Gumps.AddImage(gd, 20, 82 + 20 * i, 1210)
            Gumps.AddLabelCropped(gd, 40, 80 + 20 * i, 110, 18, 88, rule["name"])
        else:
            Gumps.AddButton(gd, 20, 82 + 20 * i, 1209, 1210, GUMP_RULE_EDIT + i, 1, 0)
            Gumps.AddLabelCropped(gd, 40, 80 + 20 * i, 110, 18, 0, rule["name"])
        if rule["enabled"]:
            Gumps.AddLabel(gd, 155, 82 + 20 * i, 0, "√")

    # (4) Editor View
    cur_idx = gump_status["entry"]
    if cur_idx == -1:
        Gumps.AddHtml(gd, 190, 60, GUMP_W - 205, GUMP_H - 75, GUMP_TEXT_WELCOME, 1, 1)
    else:
        Gumps.AddGroup(gd, 1)
        Gumps.AddBackground(gd, 180, 50, GUMP_W - 185, GUMP_H - 55, 3500)
        Gumps.AddHtml(gd, 180, 63, GUMP_W - 185, 18, "<CENTER>RULE SETTING</CENTER>", 0, 0)
        cur_rule = rules[cur_idx]
        # Name Field
        Gumps.AddHtml(gd, 200, 90, 50, 18, "Name:", 0, 0)
        Gumps.AddTooltip(gd, GUMP_EDIT_NAME_TOOLTIP)
        Gumps.AddBackground(gd, 250, 88, 210, 22, 9350)
        Gumps.AddTextEntry(gd, 255, 90, 200, 18, 0, GUMP_EDIT_NAME, cur_rule["name"])
        Gumps.AddButton(gd, 465, 88, 40018, 40028, GUMP_EDIT_LOAD, 1, 0)
        Gumps.AddHtml(gd, 465, 90, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Load</BASEFONT></CENTER>', 0, 0)
        Gumps.AddButton(gd, 530, 88, 40018, 40028, GUMP_EDIT_SAVE, 1, 0)
        Gumps.AddHtml(gd, 530, 90, 66, 18, '<CENTER><BASEFONT COLOR="#FFFFFF">Save</BASEFONT></CENTER>', 0, 0)
        # Enabled Checkbox
        Gumps.AddCheck(gd, 200, 118, 210, 211, int(cur_rule["enabled"]), GUMP_EDIT_ENABLED)
        Gumps.AddLabel(gd, 225, 120, 0, "Enable")
        Gumps.AddTooltip(gd, GUMP_EDIT_ENABLED_TOOLTIP)
        # Notify Checkbox
        Gumps.AddCheck(gd, 280, 118, 210, 211, int(cur_rule["notify"]), GUMP_EDIT_NOTIFY)
        Gumps.AddLabel(gd, 305, 120, 0, "Notify")
        Gumps.AddTooltip(gd, GUMP_EDIT_NOTIFY_TOOLTIP)
        # Apply
        Gumps.AddButton(gd, GUMP_W - 275, GUMP_H - 43, 40021, 40031, GUMP_EDIT_APPLY, 1, 1)
        Gumps.AddHtml(
            gd,
            GUMP_W - 275,
            GUMP_H - 40,
            125,
            18,
            '<CENTER><BASEFONT COLOR="#FFFFFF">Apply Changes</BASEFONT></CENTER>',
            0,
            0,
        )
        # Discard
        Gumps.AddButton(gd, GUMP_W - 150, GUMP_H - 43, 40297, 40298, GUMP_EDIT_DISCARD, 1, 1)
        Gumps.AddHtml(
            gd,
            GUMP_W - 150,
            GUMP_H - 40,
            125,
            18,
            '<CENTER><BASEFONT COLOR="#FFFFFF">Discard Changes</BASEFONT></CENTER>',
            0,
            0,
        )

        # Base Items Field
        rect_l, rect_r = 200, GUMP_W - 25
        rect_t, rect_b = 170, 290
        rect_w = rect_r - rect_l
        rect_h = rect_b - rect_t
        Gumps.AddHtml(gd, rect_l, 150, rect_w, 18, "This rule matches any of the following item types:", 0, 0)

        item_w = 100
        item_per_row = (rect_w - 20) // item_w
        assert item_per_row > 0, "Gump is not wide enough!"
        item_w = (rect_w - 20) // item_per_row

        item_data = cur_rule["item-base"]

        scr_btn_w, scr_btn_h = 32, 22
        scr_bar_l = rect_l + scr_btn_w
        scr_bar_r = rect_r - scr_btn_w
        scr_bar_w = scr_bar_r - scr_bar_l
        scr_bar_h = scr_btn_h

        Gumps.AddImageTiled(gd, rect_l, rect_t, rect_w, rect_h, 1759)
        Gumps.AddImageTiled(gd, scr_bar_l, rect_t, scr_bar_w, scr_bar_h, 39929)

        scr_enable = item_per_row < len(item_data)
        scr_w = int(scr_bar_w * item_per_row / len(item_data)) if scr_enable else 0

        for scroll in range(max(len(item_data) - item_per_row, 0) + 1):
            Gumps.AddPage(gd, scroll + 1)
            scr_l = int(scr_bar_l + scr_bar_w * scroll / len(item_data)) if scr_enable else 0
            # Scrollbar
            if scr_enable:
                Gumps.AddImageTiled(gd, scr_l, rect_t, scr_w, scr_bar_h, 9504)
            # Left scroll
            if scr_enable and scroll > 0:
                Gumps.AddButton(gd, rect_l, rect_t, 40016, 40026, 0, 0, scroll)
            else:
                Gumps.AddImage(gd, rect_l, rect_t, 40016, 0x3B2)
            # Right scroll
            if scr_enable and (scroll + item_per_row) < len(item_data):
                Gumps.AddButton(gd, scr_bar_r, rect_t, 40017, 40027, 0, 0, scroll + 2)
            else:
                Gumps.AddImage(gd, scr_bar_r, rect_t, 40017, 0x3B2)
            # Display entries
            for i, (item_id, hue, item_name) in enumerate(item_data[scroll : scroll + item_per_row]):
                x = rect_l + 10 + item_w * i
                y = rect_t + scr_btn_h + 5
                Gumps.AddButton(gd, x, y + 2, 1209, 1210, GUMP_EDIT_ITEMBASE + scroll + i, 1, 0)
                Gumps.AddLabelCropped(gd, x + 20, y, item_w - 30, 18, 1153, item_name)
                Gumps.AddItem(gd, x + 20, y + 20, item_id, hue)

    # Render
    Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd.gumpDefinition, gd.gumpStrings)


def editor_response(gump_status):
    Gumps.WaitForGump(GUMP_ID, 3600000)
    gd = Gumps.GetGumpData(GUMP_ID)

    rules = gump_status["preset"]["rules"]
    cur_idx = gump_status["entry"]
    assert -1 <= cur_idx < len(rules), f"Index out of range! {cur_idx}"

    if gd.buttonid == 0:
        # Add confirmation dialog if unsaved changes exist
        return False
    elif gd.buttonid == GUMP_PRESET_RENAME:
        name_new = gd.text[0].strip()[:60]
        Misc.SendMessage(f"The preset has been renamed as: {name_new}", 0x47E)
        gump_status["preset"]["name"] = name_new
        return True
    elif GUMP_RULE_EDIT <= gd.buttonid < GUMP_RULE_ADD:
        gump_status["entry"] = gd.buttonid - GUMP_RULE_EDIT
        gump_status["item-base-scroll"] = 0
        return True
    elif gd.buttonid == GUMP_RULE_ADD:
        gump_status["entry"] = len(rules)
        rules.append({"name": "Unnamed", "enabled": True, "notify": False, "item-base": []})
        return True
    elif gd.buttonid == GUMP_RULE_DELETE:
        # ToDo: Add confirmation dialog
        if len(rules) > 0 and cur_idx >= 0:
            del rules[cur_idx]
            gump_status["entry"] = min(cur_idx, len(rules) - 1)
        return True
    elif gd.buttonid == GUMP_RULE_MOVE_UP:
        if cur_idx > 0:
            rules[cur_idx - 1], rules[cur_idx] = rules[cur_idx], rules[cur_idx - 1]
            gump_status["entry"] -= 1
        return True
    elif gd.buttonid == GUMP_RULE_MOVE_DOWN:
        if 0 <= cur_idx < len(rules) - 1:
            rules[cur_idx], rules[cur_idx + 1] = rules[cur_idx + 1], rules[cur_idx]
            gump_status["entry"] += 1
        return True
    elif gd.buttonid == GUMP_EDIT_APPLY:
        if cur_idx >= 0:
            cur_rule = rules[cur_idx]
            cur_rule["name"] = gd.text[1]
            cur_rule["enabled"] = GUMP_EDIT_ENABLED in gd.switches
            cur_rule["notify"] = GUMP_EDIT_NOTIFY in gd.switches
        return True
    elif gd.buttonid == GUMP_EDIT_DISCARD:
        # ToDo: Add confirmation dialog
        return True
    elif GUMP_EDIT_ITEMBASE <= gd.buttonid < GUMP_EDIT_ITEMBASE + 100:
        item_idx = gd.buttonid - GUMP_EDIT_ITEMBASE
        Misc.SendMessage(f"SelectedIndex = {item_idx}", 0x47E)
        return True


def main():
    gump_status = {
        "entry": -1,
        "entry-scroll": 0,
        "preset": {
            "name": Player.Name,
            "rules": [
                {
                    "name": "Gold",
                    "enabled": True,
                    "notify": False,
                    "item-base": [
                        (3804, 0, "Gravestone"),
                        (3823, 1152, "Ice Coins"),
                        (0x1086, 0, "Jewelry"),
                        (0x0DF2, 0, "Wand"),
                        (0x1B72, 2112, "Shield"),
                        (3804, 0, "Gravestone"),
                        (3823, 1152, "Ice Coins"),
                        (0x1086, 0, "Jewelry"),
                        (0x0DF2, 0, "Wand"),
                        (0x1B72, 2112, "Shield"),
                    ],
                },
                {
                    "name": "Gem",
                    "enabled": True,
                    "notify": False,
                    "item-base": [
                        (0x0DF2, 0, "Wand"),
                    ],
                },
                {"name": "Artifacts", "enabled": True, "notify": True, "item-base": []},
                {"name": "Melee Magic Items", "enabled": True, "notify": False, "item-base": []},
                {"name": "Caster Magic Items", "enabled": True, "notify": False, "item-base": []},
            ],
        },
    }

    Gumps.CloseGump(GUMP_ID)
    while Player.Connected:
        editor_show(gump_status)
        res = editor_response(gump_status)
        if not res:
            break


if __name__ == "__main__":
    main()
