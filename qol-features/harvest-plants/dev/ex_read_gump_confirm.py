from AutoComplete import *
import re


for gumpid in Gumps.AllGumpIDs():
    gd = Gumps.GetGumpData(gumpid)
    if gd is None:
        continue
    if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ tilepic 25 45 3307 }"):
        continue
    if len(gd.gumpData) != 7 or gd.gumpData[4] != "Set plant":
        continue

    print(f"Gump ID: 0x{gumpid:X}")
