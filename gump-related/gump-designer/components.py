from AutoComplete import *
from enum import Enum



class GumpComponent:
    class RenderMode(Enum):
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"


    render_mode: RenderMode
    
