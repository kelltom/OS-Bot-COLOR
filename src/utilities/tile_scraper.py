import json
from pathlib import Path

"""
To document a tile path, you can
- Manually mark ground markers and export them. The order you
  mark them in should be the order in which they are exported (I think)
  This is ideal for short paths.

- Install the Tileman plugin, turn on the auto-mark tiles feature, and
  run from A to B. After a few moments, run this script to scrape them.
  Some manual work is likely required if tiles span across regions.

  ! NOTE: this is not perfect. It is best to manually vet your tile paths.
"""


PATH_TITLE = "_PATH_TITLE_"

# Load all relevant lines
temp_settings: Path = Path(__file__).parent.parent.joinpath("runelite_settings/temp.properties")


# * If you want to manually sort a collection of tiles from another source,
# * just dump them in this variable, and comment out the context block

extended_path = []

with temp_settings.open() as f:
    print(f)
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith("tilemanMode.region_"):
            value = line.split("=")[1][:-1].replace("\\", "")  # slice off \n, replace backslashes
            extended_path.extend(json.loads(value))


# Set this to the overall direction your path is travelling
overall_direction = "NW"

"""
Sort intra-region
Within one region, tile coordinates are directionally are akin to a usual quadrant coordinate plan
N: +y
E: +x
S: -y
W: -x
"""
if overall_direction == "NW":
    print("WTF")
    extended_path.sort(key=lambda p: -p["regionX"])
    extended_path.sort(key=lambda p: p["regionY"])

"""
Sort inter-region
N: +1
S: -1
E: +256
W: -256
"""
# TODO Manually sorting region chunks in JSON file atm
extended_path.sort(key=lambda p: p["regionId"])  # Roughly northeast


f = open(f"{PATH_TITLE}.json", "w")
f.write(json.dumps(extended_path))
f.close()
