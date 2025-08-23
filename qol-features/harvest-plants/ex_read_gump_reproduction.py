from AutoComplete import *
import re


for gumpid in Gumps.AllGumpIDs():
    gd = Gumps.GetGumpData(gumpid)
    if gd is None:
        continue
    if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ gumppic 60 90 3607 }"):
        continue
    if len(gd.gumpData) != 17 or gd.gumpData[5] != "Reproduction":
        continue

    print(f"Gump ID: 0x{gumpid:X}")
    print(f"Resources: {gd.gumpData[11]}")
    print(f"Seeds: {gd.gumpData[13]}")
