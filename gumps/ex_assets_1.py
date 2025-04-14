GUMP_ID = 0xDEADBEE3

Gumps.CloseGump(GUMP_ID)
gd = Gumps.CreateGump(movable=True)
Gumps.AddPage(gd, 0)

gump_ids = [
    83,
    302,
    311,
    1460,
    1579,
    1755,
    2520,
    2600,
    2620,
    3000,
    3500,
    3600,
    5054,
    5100,
    5120,
    5150,
    5170,
    9100,
    9150,
    9200,
    9250,
    9260,
    9270,
    9300,
    9350,
    9380,
    9390,
    9400,
    9450,
    9500,
    9550,
    9559,
    9568,
    12024,
    30536,
    30546,
    39925,
    40000,
    40288,
]

cols = 7
w_size = 150
h_size = 150

for idx, gump_id in enumerate(gump_ids):
    row, col = idx // cols, idx % cols
    x = w_size * col
    y = h_size * row
    Gumps.AddBackground(gd, x, y, w_size, h_size, gump_id)
    Gumps.AddLabel(gd, x + 20, y + h_size // 2, 0x47E, f"ID: {gump_id}")

Gumps.SendGump(GUMP_ID, Player.Serial, 25, 25, gd.gumpDefinition, gd.gumpStrings)
