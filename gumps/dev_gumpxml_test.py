import os
import sys
from typing import Dict, TYPE_CHECKING

# This code is purely for type hinting and will not be executed in the actual environment.
# If you are not using type hinting, you can safely remove the following lines.
if TYPE_CHECKING:
    from uo_runtime.gumps import Gumps
    from uo_runtime.player import Player
    from uo_runtime.misc import Misc

# This allows the RazorEnhanced to correctly identify the path of the gumpxml module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)
from gumpxml import GumpDOMNode, GumpDOMParser, GumpThemePresets, GumpPresets, ET


EDITOR_FRAME = """
<frame width="800" height="600" bg="frame:30546" alpha="yes" padding="5">
    <vbox width="100%" height="100%" spacing="5">
        <hbox height="40" bg="3504" padding="10 10">
            <label id="profile_name" width="150">{profile_name}</label>
            <button id="profile_rename">Rename</button>
            <button id="profile_load">Load</button>
            <button id="profile_save">Save</button>
        </hbox>
        <hbox flex="1" spacing="5">
            <vbox width="200" bg="3504" padding="0 10">
                <h>RULES</h>
                <hidden id="rule_selected" value="{rule_selected}" />
                <container id="show_rules" width="100%" padding="0 5" orientation="vertical">
                    {LIST}
                </container>
                <vfill />
                <container width="100%" orientation="vertical">
                    <hbox margin="0 2">
                        <hfill />
                        <button id="rule_add">Add</button>
                        <button id="rule_del">Delete</button>
                        <hfill />
                    </hbox>
                    <hbox margin="0 2">
                        <hfill />
                        <button id="rule_move_up">Up</button>
                        <button id="rule_move_dn">Down</button>
                        <hfill />
                    </hbox>
                </container>
            </vbox>
            <vbox flex="1" bg="3504" padding="10 10" spacing="10">
                {CORE}
            </vbox>
        </hbox>
    </vbox>
</frame>
"""

EDITOR_RULE_SELECTED = """
<hbox height="22" padding="5 2" bg="9304">
    <button id="rule_{i}_open" index="{i}" src="1209" />
    <label height="18" flex="1" margin="5 0">{name}</label>
    <toggle id="rule_{i}_enabled" index="{i}" checked="{enabled}" />
</hbox>
"""

EDITOR_RULE_DESELECTED = """
<hbox height="22" padding="5 2">
    <button id="rule_{i}_open" index="{i}" src="1209" />
    <label height="18" flex="1" margin="5 0">{name}</label>
    <toggle id="rule_{i}_enabled" index="{i}" checked="{enabled}" />
</hbox>
"""

EDITOR_CORE = """
<h>RULE EDITOR</h>
<hbox>
    <label width="50">Name:</label>
    <textentry id="rule_name" width="180" bg="frame:3000">{name}</textentry>
    <button id="rule_load">Load</button>
    <button id="rule_save">Save</button>
</hbox>
<hbox>
    <label text="Options:" width="50" />
    <checkbox id="rule_enabled" checked="{enabled}" />
    <label width="100" padding="5 0" tooltip="When unchecked, the lootmaster will bypass this rule.">Enable</label>
    <checkbox id="rule_notify" checked="{notify}" />
    <label width="100" padding="5 0" tooltip="When checked, the lootmaster will inform you of the matched items.">Notify</label>
    <checkbox id="rule_highlight" checked="{highlight}" />
    <label width="100" padding="5 0" tooltip="When checked, the lootmaster will highlight the matched items with a bright shiny color.">Highlight</label>
</hbox>
<vfill />
<hbox>
    <hfill />
    <button id="rule_apply_chg" src="40020">Apply Change</button>
    <button id="rule_discard_chg" src="40297">Discard Change</button>
</hbox>
"""

EDITOR_WELCOM = """
<h>RULE EDITOR</h>
<html width="100%" flex="1" scrollbar="true" color="#000000">Welcome to the Rule Editor!

This is a simple editor that allows you to create and manage rules for the lootmaster.
</html>
"""


def main():
    # This is a placeholder data for the profile.
    profile_name = "My Profile"
    selected_rule = -1
    rules = [
        {"name": "Gold", "enabled": True, "notify": False, "highlight": True},
        {"name": "Gem", "enabled": False, "notify": True, "highlight": False},
        {"name": "Artifact", "enabled": True, "notify": True, "highlight": True},
    ]

    # Pick a unique ID for the gump. This is a hash of the profile name.
    gump_id = hash(profile_name) & 0xFFFFFFFF

    # Loops to keep the gump open until the user decides to close it
    while True:
        # Build the XML string based on the current profile
        xml_list = "\n".join(
            (EDITOR_RULE_SELECTED if i == selected_rule else EDITOR_RULE_DESELECTED).format(
                i=i,
                name=rule["name"],
                enabled=str(rule["enabled"]).lower(),
            )
            for i, rule in enumerate(rules)
        )

        if 0 <= selected_rule < len(rules):
            rule = rules[selected_rule]
            xml_core = EDITOR_CORE.format(
                name=rule["name"],
                enabled=str(rule["enabled"]).lower(),
                notify=str(rule["notify"]).lower(),
                highlight=str(rule["highlight"]).lower(),
            )
        else:
            xml_core = EDITOR_WELCOM

        xml_string = EDITOR_FRAME.format(
            profile_name=profile_name,
            rule_selected=selected_rule,
            LIST=xml_list,
            CORE=xml_core,
        )

        # Parse the XML string to an ElementTree object
        root = ET.fromstring(xml_string)

        # Render the gump using the parsed XML and the light theme
        g = GumpDOMParser.render(root, GumpThemePresets.Light)

        # Add event listeners
        def apply_changes(e: GumpDOMNode):
            nonlocal selected_rule
            if selected_rule != -1:
                rules[selected_rule]["name"] = g.gdom.find_by_id("rule_name").text
                rules[selected_rule]["enabled"] = g.gdom.find_by_id("rule_enabled").checked
                rules[selected_rule]["notify"] = g.gdom.find_by_id("rule_notify").checked
                rules[selected_rule]["highlight"] = g.gdom.find_by_id("rule_highlight").checked

        def open_rule(e: GumpDOMNode):
            nonlocal selected_rule
            selected_rule = int(e["index"] or -1)

        def toggle_rule(e: GumpDOMNode):
            nonlocal selected_rule
            cur_rule = int(e["index"] or -1)
            if cur_rule != -1:
                rules[cur_rule]["enabled"] = e.checked

        g.add_event_listener("rule_apply_chg", apply_changes)
        for i in range(len(rules)):
            g.add_event_listener(f"rule_{i}_open", open_rule)
            g.add_event_listener(f"rule_{i}_enabled", toggle_rule)

        # Fix the gump ID to ensure it is consistent across sessions
        g.id = gump_id
        # Send the gump to the client and listen for a response
        button_id, ev_map = g.send_and_listen(300, 200)

        # Handle the button click events
        if button_id is None:
            if GumpPresets.confirm("Are you sure you want to close the editor?", 300, 100):
                break
        elif button_id == "profile_rename":
            changed, profile_name = GumpPresets.prompt("Enter new profile name:", 350, 100, value=profile_name)
            if changed:
                Misc.SendMessage("Profile renamed.")
            else:
                Misc.SendMessage("Renaming cancelled.")
            continue


if __name__ == "__main__":
    main()
