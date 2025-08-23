
# Click the reproduction menu
Gumps.WaitForGump(0xd520dfef, 10000)
Gumps.SendAction(0xd520dfef, 1)
# Gather resources
Gumps.WaitForGump(0xbf35f088, 10000)
Gumps.SendAction(0xbf35f088, 7)
# Gather seeds
Gumps.WaitForGump(0xbf35f088, 10000)
Gumps.SendAction(0xbf35f088, 8)
# Make it decorative
Gumps.WaitForGump(0xbf35f088, 10000)
Gumps.SendAction(0xbf35f088, 2)
# Confirm
Gumps.WaitForGump(0xdd1839cf, 10000)
Gumps.SendAction(0xdd1839cf, 3)