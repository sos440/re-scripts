import os
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from razorenhanced import *

PATH = os.path.dirname(os.path.abspath(__file__))


################################################################################
# Constants
################################################################################

VERSION = "1.0.0"
GUMPID_DESIGNER = hash("GumpDesigner") & 0xFFFFFFFF
GUMPID_VIEWER = hash("GumpViewer") & 0xFFFFFFFF


################################################################################
# Editor
################################################################################


class GumpComponent:
    class Base:
        def __init__(self) -> None:
            ...

class GumpDesigner:
    def __init__(self) -> None:
        self.components = []