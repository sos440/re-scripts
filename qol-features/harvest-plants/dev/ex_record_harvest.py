from AutoComplete import *

# Click the reproduction menu
Gumps.WaitForGump(0xD520DFEF, 10000)
Gumps.SendAction(0xD520DFEF, 1)
# Gather resources
Gumps.WaitForGump(0xBF35F088, 10000)
Gumps.SendAction(0xBF35F088, 7)
# Gather seeds
Gumps.WaitForGump(0xBF35F088, 10000)
Gumps.SendAction(0xBF35F088, 8)
# Make it decorative
Gumps.WaitForGump(0xBF35F088, 10000)
Gumps.SendAction(0xBF35F088, 2)
# Confirm
Gumps.WaitForGump(0xDD1839CF, 10000)
Gumps.SendAction(0xDD1839CF, 3)
