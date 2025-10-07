from AutoComplete import *

# This allows the RazorEnhanced to correctly identify the path of the gumpxml module.
import os
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

# Imports the gump builder module
import gump_builder


gb = gump_builder.GumpBuilder("Test Gump")

bg = gb.AddBackground((0, 0), size=(0, 0), gumpart=5054)
alpha = gb.AddAlphaRegion((10, 10), size=(600, 20))

y = 20
for i in range(10):
    gb.AddReplyButton((20, y), id=f"button_{i}", normal=4005, pressed=4007)
    gb.AddTooltip(args=f"Click the buttion {i}!")
    gb.AddText((55, y + 2), text=f"This is button {i}", hue=1152)
    
    gb.AddRadio((220, y), id=f"radio_{i}")
    gb.AddText((255, y + 2), text=f"This is radio {i}", hue=88)
    
    gb.AddCheckbox((420, y), id=f"check_{i}")
    gb.AddText((455, y + 2), text=f"This is check {i}", hue=68)
    
    y += 20

y += 10
gb.AddTextEntry((20, y), id="text_1", size=(200, 22), text="Hello, Gump!", hue=1152)
y += 22
gb.AddTextEntry((20, y), id="text_2", size=(200, 22), text="Test successful?", hue=1152)
y += 22

alpha.height = y
bg.width = alpha.width + 20
bg.height = alpha.height + 20


gb._compile()

response = gb.Launch(100, 100, wait_for_response=True)
if response is not None:
    print(response.button)
    print(response.switches)
    print(response.texts)
