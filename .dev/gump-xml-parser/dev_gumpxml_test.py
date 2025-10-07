from AutoComplete import *
import os
import sys

# This allows the RazorEnhanced to correctly identify the path of the gumpxml module.
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)
from gumpxml import GumpDOMNode, GumpDOMParser, GumpThemePresets, GumpPresets, ET


RULES_PER_PAGE = 18

EDITOR_FRAME = """
<frame width="800" height="600" bg="frame:9260" alpha="yes" padding="5">
    <vbox width="100%" height="100%" spacing="5">
        <hbox height="40" bg="2624" padding="10 10" alpha="yes">
            <label id="profile_name" width="150" color="1153">{profile_name}</label>
            <button id="profile_rename">Rename</button>
            <button id="profile_load">Load</button>
            <button id="profile_save">Save</button>
        </hbox>
        <hbox flex="1" spacing="5">
            <vbox width="200" bg="2624" padding="0 10" alpha="yes">
                <h color="#FFFFFF">RULES</h>
                <hidden id="selected_rule" value="{selected_rule}" />
                <container id="show_rules" width="100%" padding="0 5" orientation="vertical">
                    {LIST}
                </container>
                <vfill />
                <container width="100%" orientation="vertical">
                    <hbox margin="0 2">
                        <hfill />
                        <button id="rule_prev" src="40016" />
                        <html width="64" height="18" centered="yes" color="#FFFFFF">{cur_pg}/{max_pg}</html>
                        <button id="rule_next" src="40017" />
                        <hfill />
                    </hbox>
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
            <vbox flex="1" bg="2624" padding="10 10" spacing="10" alpha="yes">
                {CORE}
            </vbox>
        </hbox>
    </vbox>
</frame>
"""

EDITOR_RULE_SELECTED = """
<hbox height="23" padding="5 2" bg="9354">
    <button id="rule_{i}_open" index="{i}" src="1209" />
    <label height="18" flex="1" margin="5 0">{name}</label>
    <toggle id="rule_{i}_enabled" index="{i}" checked="{enabled}" />
</hbox>
"""

EDITOR_RULE_DESELECTED = """
<hbox height="23" padding="5 2">
    <button id="rule_{i}_open" index="{i}" src="1209" />
    <label height="18" flex="1" margin="5 0" color="1153">{name}</label>
    <toggle id="rule_{i}_enabled" index="{i}" checked="{enabled}" />
</hbox>
"""

EDITOR_CORE = """
<h>RULE EDITOR</h>
<hbox>
    <label width="50" color="1153">Name:</label>
    <textentry id="rule_name" width="180" bg="frame:30546" color="1153">{name}</textentry>
    <button id="rule_load">Load</button>
    <button id="rule_save">Save</button>
</hbox>
<hbox>
    <label text="Options:" width="50" color="1153" />
    <checkbox id="rule_enabled" checked="{enabled}" />
    <label width="100" padding="5 0" color="1153" tooltip="When unchecked, the lootmaster will bypass this rule.">Enable</label>
    <checkbox id="rule_notify" checked="{notify}" />
    <label width="100" padding="5 0" color="1153" tooltip="When checked, the lootmaster will inform you of the matched items.">Notify</label>
    <checkbox id="rule_highlight" checked="{highlight}" />
    <label width="100" padding="5 0" color="1153" tooltip="When checked, the lootmaster will highlight the matched items with a bright shiny color.">Highlight</label>
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
<html width="100%" flex="1" scrollbar="true">Welcome to the Rule Editor!

This is a simple editor that allows you to create and manage rules for the lootmaster.
</html>
"""


def main():
    # This is a placeholder data for the profile.
    profile_name = "My Profile"
    selected_rule = -1
    selected_page = 1
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
        xml_list = []
        d = RULES_PER_PAGE
        cur_pg = selected_page
        max_pg = 1 + (max(len(rules) - 1, 0) // d)
        for i in range((cur_pg - 1) * d, min(len(rules), cur_pg * d)):
            rule = rules[i]
            cur_temp = EDITOR_RULE_DESELECTED
            if i == selected_rule:
                cur_temp = EDITOR_RULE_SELECTED
            xml_list.append(
                cur_temp.format(
                    i=i,
                    name=rule["name"],
                    enabled=str(rule["enabled"]).lower(),
                )
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
            selected_rule=selected_rule,
            cur_pg=str(cur_pg) if cur_pg > 0 else "-",
            max_pg=str(max_pg) if max_pg > 0 else "-",
            LIST="".join(xml_list),
            CORE=xml_core,
        )

        # Parse the XML string to an ElementTree object
        root = ET.fromstring(xml_string)

        # Render the gump using the parsed XML and the light theme
        g = GumpDOMParser.render(root, GumpThemePresets.Light)

        # Add event listeners
        def f_apply_changes(e: GumpDOMNode):
            nonlocal selected_rule
            if selected_rule != -1:
                rules[selected_rule]["name"] = g.gdom.find_by_id("rule_name").text
                rules[selected_rule]["enabled"] = g.gdom.find_by_id("rule_enabled").checked
                rules[selected_rule]["notify"] = g.gdom.find_by_id("rule_notify").checked
                rules[selected_rule]["highlight"] = g.gdom.find_by_id("rule_highlight").checked

        def f_open_rule(e: GumpDOMNode):
            nonlocal selected_rule, selected_page
            selected_rule = int(e["index"] or -1)
            selected_page = 1 + (max(0, selected_rule) // d)

        def f_toggle_rule(e: GumpDOMNode):
            nonlocal selected_rule
            cur_rule = int(e["index"] or -1)
            if cur_rule != -1:
                rules[cur_rule]["enabled"] = e.checked

        def f_profile_rename(e: GumpDOMNode):
            nonlocal profile_name
            changed, profile_name = GumpPresets.prompt("Enter new profile name:", 350, 100, value=profile_name)
            if changed:
                Misc.SendMessage("Profile renamed.")
            else:
                Misc.SendMessage("Renaming cancelled.")

        def f_add_rule(e: GumpDOMNode):
            nonlocal selected_rule, selected_page
            selected_rule = len(rules)
            selected_page = 1 + (max(0, selected_rule) // d)
            rules.append({"name": "(Unnamed)", "enabled": True, "notify": False, "highlight": False})

        def f_delete_rule(e: GumpDOMNode):
            nonlocal selected_rule, selected_page
            if selected_rule >= 0:
                del rules[selected_rule]
                selected_rule = min(selected_rule, len(rules) - 1)
                selected_page = 1 + (max(0, selected_rule) // d)

        def f_prev_page(e: GumpDOMNode):
            nonlocal selected_page
            if selected_page > 1:
                selected_page -= 1

        def f_next_page(e: GumpDOMNode):
            nonlocal selected_page
            max_pg = 1 + (max(len(rules) - 1, 0) // d)
            if selected_page < max_pg:
                selected_page += 1

        g.add_event_listener("rule_apply_chg", f_apply_changes)
        g.add_event_listener("profile_rename", f_profile_rename)
        g.add_event_listener("rule_add", f_add_rule)
        g.add_event_listener("rule_del", f_delete_rule)
        g.add_event_listener("rule_prev", f_prev_page)
        g.add_event_listener("rule_next", f_next_page)
        for i in range(len(rules)):
            g.add_event_listener(f"rule_{i}_open", f_open_rule)
            g.add_event_listener(f"rule_{i}_enabled", f_toggle_rule)

        # Fix the gump ID to ensure it is consistent across sessions
        g.id = gump_id
        # Send the gump to the client and listen for a response
        button_id, ev_map = g.send_and_listen(300, 200)

        # Handle the button click events
        if button_id is None:
            if GumpPresets.confirm("Are you sure you want to close the editor?", 300, 100):
                break


if __name__ == "__main__":
    main()
