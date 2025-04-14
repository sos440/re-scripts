import os
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)

import dev_gump_xml as gump

gump.open_confirm("Hello!", 300, 100)