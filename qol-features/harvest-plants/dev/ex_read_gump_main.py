from AutoComplete import *
import re


for gumpid in Gumps.AllGumpIDs():
    gd = Gumps.GetGumpData(gumpid)
    if gd is None:
        continue
    if not gd.gumpLayout.startswith("{ resizepic 50 50 3600 200 150 }{ tilepic 45 45 3311 }"):
        continue
    if len(gd.gumpData) < 21:
        continue
    match = re.search(r"tilepichue 130 96 (\d+) (\d+)", gd.gumpLayout)
    if match is None:
        continue

    print(f"Gump ID: 0x{gumpid:X}")
    print(f"Plant: {match.group(1)}")
    print(f"Color: {match.group(2)}")
    print(f"Day: {gd.gumpData[21]}")
