from AutoComplete import *
from typing import List, Tuple, Dict, Optional, Any
import os
import json

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
        def __init__(self) -> None: ...

        def compile(self) -> str:
            raise NotImplementedError

        def apply(self, gd: Gumps.GumpData) -> None:
            raise NotImplementedError

    class Page(Base):
        def __init__(self, page: int) -> None:
            self.page = page

        def compile(self) -> str:
            return f"Gumps.AddPage(gd, {self.page})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddPage(gd, self.page)

    class AlphaRegion(Base):
        def __init__(self, x: int, y: int, width: int, height: int) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def compile(self) -> str:
            return f"Gumps.AddAlphaRegion(gd, {self.x}, {self.y}, {self.width}, {self.height})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddAlphaRegion(gd, self.x, self.y, self.width, self.height)

    class Background(Base):
        def __init__(self, x: int, y: int, width: int, height: int, gumppic: int) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.gumppic = gumppic

        def compile(self) -> str:
            return f"Gumps.AddBackground(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.gumppic})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddBackground(gd, self.x, self.y, self.width, self.height, self.gumppic)

    class Button(Base):
        def __init__(self, x: int, y: int, gumppic_up: int, gumppic_down: int, id: int, type: int, param: int) -> None:
            self.x = x
            self.y = y
            self.gumppic_up = gumppic_up
            self.gumppic_down = gumppic_down
            self.id = id
            self.type = type
            self.param = param

        def compile(self) -> str:
            return f"Gumps.AddButton(gd, {self.x}, {self.y}, {self.gumppic_up}, {self.gumppic_down}, {self.id}, {self.type}, {self.param})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddButton(gd, self.x, self.y, self.gumppic_up, self.gumppic_down, self.id, self.type, self.param)

    class Check(Base):
        def __init__(self, x: int, y: int, gumppic_unchecked: int, gumppic_checked: int, initial_state: bool, id: int) -> None:
            self.x = x
            self.y = y
            self.gumppic_unchecked = gumppic_unchecked
            self.gumppic_checked = gumppic_checked
            self.initial_state = initial_state
            self.id = id

        def compile(self) -> str:
            return f"Gumps.AddCheck(gd, {self.x}, {self.y}, {self.gumppic_unchecked}, {self.gumppic_checked}, {self.initial_state}, {self.id})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddCheck(gd, self.x, self.y, self.gumppic_unchecked, self.gumppic_checked, self.initial_state, self.id)

    class Group(Base):
        def __init__(self, group: int) -> None:
            self.group = group

        def compile(self) -> str:
            return f"Gumps.AddGroup(gd, {self.group})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddGroup(gd, self.group)

    class Html(Base):
        def __init__(self, x: int, y: int, width: int, height: int, text: str, background: bool = False, scrollbar: bool = False) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.text = text
            self.background = background
            self.scrollbar = scrollbar

        def compile(self) -> str:
            return f"Gumps.AddHtml(gd, {self.x}, {self.y}, {self.width}, {self.height}, {json.dumps(self.text)}, {self.background}, {self.scrollbar})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddHtml(gd, self.x, self.y, self.width, self.height, self.text, self.background, self.scrollbar)

    class HtmlLocalized(Html):
        def __init__(self, x: int, y: int, width: int, height: int, number: int, args: Union[str, int, bool], color: int, background: bool = False, scrollbar: bool = False) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.number = number
            self.args = args
            self.color = color

        def compile(self) -> str:
            return f"Gumps.AddHtmlLocalized(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.number}, {self.args}, {self.color}, {self.background}, {self.scrollbar})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddHtmlLocalized(gd, self.x, self.y, self.width, self.height, self.number, self.args, self.color, self.background, self.scrollbar)

    class Image(Base):
        def __init__(self, x: int, y: int, gumppic: int, hue: Optional[int] = None) -> None:
            self.x = x
            self.y = y
            self.gumppic = gumppic
            self.hue = hue

        def compile(self) -> str:
            if self.hue is None:
                return f"Gumps.AddImage(gd, {self.x}, {self.y}, {self.gumppic})"
            else:
                return f"Gumps.AddImage(gd, {self.x}, {self.y}, {self.gumppic}, {self.hue})"

        def apply(self, gd: Gumps.GumpData) -> None:
            if self.hue is None:
                Gumps.AddImage(gd, self.x, self.y, self.gumppic)
            else:
                Gumps.AddImage(gd, self.x, self.y, self.gumppic, self.hue)

    class ImageTiled(Base):
        def __init__(self, x: int, y: int, width: int, height: int, gumppic: int) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.gumppic = gumppic

        def compile(self) -> str:
            return f"Gumps.AddImageTiled(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.gumppic})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddImageTiled(gd, self.x, self.y, self.width, self.height, self.gumppic)

    class ImageTiledButton(Base):
        def __init__(self, x: int, y: int, gumppic_up: int, gumppic_down: int, id: int, type: int, param: int, itemID: int, hue: int, width: int, height: int, localizedTooltip: Optional[int] = None) -> None:
            self.x = x
            self.y = y
            self.gumppic_up = gumppic_up
            self.gumppic_down = gumppic_down
            self.id = id
            self.type = type
            self.param = param
            self.itemID = itemID
            self.hue = hue
            self.width = width
            self.height = height
            self.localizedTooltip = localizedTooltip

        def compile(self) -> str:
            button_type = "Gumps.GumpButtonType.Reply" if self.type else "Gumps.GumpButtonType.Page"
            if self.localizedTooltip is not None:
                return f"Gumps.AddImageTiledButton(gd, {self.x}, {self.y}, {self.gumppic_up}, {self.gumppic_down}, {self.id}, {button_type}, {self.param}, {self.itemID}, {self.hue}, {self.width}, {self.height}, {self.localizedTooltip})"
            else:
                return f"Gumps.AddImageTiledButton(gd, {self.x}, {self.y}, {self.gumppic_up}, {self.gumppic_down}, {self.id}, {button_type}, {self.param}, {self.itemID}, {self.hue}, {self.width}, {self.height})"

        def apply(self, gd: Gumps.GumpData) -> None:
            button_type = Gumps.GumpButtonType.Reply if self.type else Gumps.GumpButtonType.Page
            if self.localizedTooltip is not None:
                Gumps.AddImageTiledButton(gd, self.x, self.y, self.gumppic_up, self.gumppic_down, self.id, button_type, self.param, self.itemID, self.hue, self.width, self.height, self.localizedTooltip)
            else:
                Gumps.AddImageTiledButton(gd, self.x, self.y, self.gumppic_up, self.gumppic_down, self.id, button_type, self.param, self.itemID, self.hue, self.width, self.height)

    class Item(Base):
        def __init__(self, x: int, y: int, tilepic: int, hue: Optional[int] = None) -> None:
            self.x = x
            self.y = y
            self.tilepic = tilepic
            self.hue = hue

        def compile(self) -> str:
            if self.hue is None:
                return f"Gumps.AddItem(gd, {self.x}, {self.y}, {self.tilepic})"
            else:
                return f"Gumps.AddItem(gd, {self.x}, {self.y}, {self.tilepic}, {self.hue})"

        def apply(self, gd: Gumps.GumpData) -> None:
            if self.hue is None:
                Gumps.AddItem(gd, self.x, self.y, self.tilepic)
            else:
                Gumps.AddItem(gd, self.x, self.y, self.tilepic, self.hue)

    class Label(Base):
        def __init__(self, x: int, y: int, hue: int, text: Union[str, int]) -> None:
            self.x = x
            self.y = y
            self.hue = hue
            self.text = text

        def compile(self) -> str:
            if isinstance(self.text, int):
                return f"Gumps.AddLabel(gd, {self.x}, {self.y}, {self.hue}, {json.dumps(self.text)})"
            else:
                return f"Gumps.AddLabel(gd, {self.x}, {self.y}, {self.hue}, {json.dumps(self.text)})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddLabel(gd, self.x, self.y, self.hue, self.text)

    class LabelCropped(Base):
        def __init__(self, x: int, y: int, width: int, height: int, hue: int, text: Union[str, int]) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.hue = hue
            self.text = text

        def compile(self) -> str:
            if isinstance(self.text, int):
                return f"Gumps.AddLabelCropped(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.hue}, {json.dumps(self.text)})"
            else:
                return f"Gumps.AddLabelCropped(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.hue}, {json.dumps(self.text)})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddLabelCropped(gd, self.x, self.y, self.width, self.height, self.hue, self.text)

    class Radio(Base):
        def __init__(self, x: int, y: int, gumppic_inactive: int, gumppic_active: int, initial_state: bool, id: int) -> None:
            self.x = x
            self.y = y
            self.gumppic_inactive = gumppic_inactive
            self.gumppic_active = gumppic_active
            self.initial_state = initial_state
            self.id = id

        def compile(self) -> str:
            return f"Gumps.AddRadio(gd, {self.x}, {self.y}, {self.gumppic_inactive}, {self.gumppic_active}, {self.initial_state}, {self.id})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddRadio(gd, self.x, self.y, self.gumppic_inactive, self.gumppic_active, self.initial_state, self.id)

    class SpriteImage(Base):
        def __init__(self, x: int, y: int, gumpId: int, spriteX: int, spriteY: int, spriteW: int, spriteH: int) -> None:
            self.x = x
            self.y = y
            self.gumpId = gumpId
            self.spriteX = spriteX
            self.spriteY = spriteY
            self.spriteW = spriteW
            self.spriteH = spriteH

        def compile(self) -> str:
            return f"Gumps.AddSpriteImage(gd, {self.x}, {self.y}, {self.gumpId}, {self.spriteX}, {self.spriteY}, {self.spriteW}, {self.spriteH})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddSpriteImage(gd, self.x, self.y, self.gumpId, self.spriteX, self.spriteY, self.spriteW, self.spriteH)

    class TextEntry(Base):
        def __init__(self, x: int, y: int, width: int, height: int, hue: int, entryID: int, initialTextID: Union[int, str]) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.hue = hue
            self.entryID = entryID
            self.initialTextID = initialTextID

        def compile(self) -> str:
            if isinstance(self.initialTextID, int):
                return f"Gumps.AddTextEntry(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.hue}, {self.entryID}, {json.dumps(self.initialTextID)})"
            else:
                return f"Gumps.AddTextEntry(gd, {self.x}, {self.y}, {self.width}, {self.height}, {self.hue}, {self.entryID}, {json.dumps(self.initialTextID)})"

        def apply(self, gd: Gumps.GumpData) -> None:
            Gumps.AddTextEntry(gd, self.x, self.y, self.width, self.height, self.hue, self.entryID, self.initialTextID)

    class Tooltip(Base):
        def __init__(self, cliloc: Union[int, str], text: Optional[str] = None) -> None:
            self.cliloc = cliloc
            self.text = text

        def compile(self) -> str:
            if self.text is not None:
                return f"Gumps.AddTooltip(gd, {json.dumps(self.cliloc)}, {json.dumps(self.text)})"
            else:
                return f"Gumps.AddTooltip(gd, {json.dumps(self.cliloc)})"

        def apply(self, gd: Gumps.GumpData) -> None:
            if self.text is not None:
                Gumps.AddTooltip(gd, self.cliloc, self.text)
            else:
                Gumps.AddTooltip(gd, self.cliloc)


class GumpDesigner:
    def __init__(self) -> None:
        self.components: List[GumpComponent.Base] = []

    def compile(self) -> str:
        return "\n".join([component.compile() for component in self.components])
