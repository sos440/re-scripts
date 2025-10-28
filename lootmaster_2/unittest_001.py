import os
import sys
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import modules.match as match


root = ET.Element("root")
for preset_key, preset in match.PRESETS.items():
    root.append(preset.to_xml())

root.append(match.PropMatch(pattern=r"(Silver|.+ Slayer)", name="Slayer").to_xml())

with open(os.path.dirname(os.path.abspath(__file__)) + "/unittest_001_result.xml", "w") as f:
    f.write(ET.tostring(root, encoding="unicode"))
