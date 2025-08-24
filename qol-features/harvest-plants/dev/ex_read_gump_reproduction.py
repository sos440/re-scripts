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

    text_res = gd.gumpData[11]
    text_seed = gd.gumpData[13]
    match_res = re.search(r"(\d+)/(\d+)", text_res)
    match_seed = re.search(r"(\d+)/(\d+)", text_seed)

    print(f"Gump ID: 0x{gumpid:X}")

    if text_res == "X":
        print("Resources: Depleted")
    elif match_res is None:
        print("Resources: Failed to parse")
    else:
        print(f"Resources: {match_res.group(1)}/{match_res.group(2)}")

    if text_seed == "X":
        print("Seeds: Depleted")
    elif match_seed is None:
        print("Seeds: Failed to parse")
    else:
        print(f"Seeds: {match_seed.group(1)}/{match_seed.group(2)}")
