from AutoComplete import *
from System.Collections.Generic import List as CList
from System import String

GUMP_ID = 0xdeadbeef

gump_layout = """
{ resizepic 50 50 3600 200 150 }
{ gumppic 60 90 3607 }
{ gumppic 120 90 3607 }
{ gumppic 60 145 3607 }
{ gumppic 120 145 3607 }
{ tilepic 45 45 3311 }
{ tilepic 45 118 3312 }
{ tilepic 211 45 3307 }
{ tilepic 211 118 3308 }
{ button 70 67 212 212 1 0 1 }
{ tilepic 57 65 5632 }
{ text 108 67 2101 0 }
{ button 212 67 212 212 1 0 2 }
{ tilepic 202 68 3169 }
{ text 216 66 33 1 }
{ button 80 116 212 212 1 0 3 }
{ tilepic 66 117 6818 }
{ text 106 116 63 2 }
{ button 128 116 212 212 1 0 4 }
{ tilepic 113 120 4129 }
{ text 149 116 43 3 }
{ button 177 116 212 212 1 0 5 }
{ tilepic 160 121 3535 }
{ text 199 116 43 4 }
{ button 70 163 210 210 1 0 6 }
{ tilepic 56 164 6818 }
{ button 138 163 210 210 1 0 7 }
{ tilepic 123 167 4129 }
{ button 212 163 210 210 1 0 8 }
{ tilepic 195 168 3535 }
"""

gump_strings = CList[String](["A", "B", "C", "D", "E"])

Gumps.SendGump(GUMP_ID, Player.Serial, 100, 100, gump_layout, gump_strings)