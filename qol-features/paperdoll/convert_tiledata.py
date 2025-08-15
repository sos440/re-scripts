import csv
import json


itemid_to_gumpid = {}

with open("C:\\Users\\sosin\\AppData\\Roaming\\UoFiddler\\ItemData.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=";")
    for i, row in enumerate(reader):
        if i == 0:
            continue
        
        itemid = int(row[0], base=16)
        layer = int(row[3])
        gumpid = int(row[4], base=16)
        is_wearable = int(row[34]) == 1

        if not is_wearable:
            continue

        itemid_to_gumpid[itemid] = (layer, gumpid)


with open("data.json", "w", encoding="utf-8") as jsonfile:
    json.dump(itemid_to_gumpid, jsonfile, indent=4)