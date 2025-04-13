# stubs/gumps.pyi
from __future__ import annotations
from enum import IntEnum
from typing import Any, List, Sequence, overload

class GumpButtonType(IntEnum):
    PAGE = 0
    REPLY = 1

class Gumps:
    class GumpData:
        buttonid: int
        gumpData: List[str]
        gumpDefinition: str
        gumpId: int
        gumpLayout: str
        gumpStrings: List[str]
        gumpText: List[str]
        hasResponse: bool
        layoutPieces: List[str]
        serial: int
        stringList: List[str]
        switches: List[int]
        text: List[str]
        textID: List[int]
        x: int
        y: int

    @classmethod
    def CreateGump(
        cls,
        movable: bool = True,
        closable: bool = True,
        disposable: bool = True,
        resizeable: bool = False,
    ) -> GumpData: ...
    @classmethod
    def CurrentGump(cls) -> int: ...
    @classmethod
    def AllGumpIDs(cls) -> List[int]: ...
    @classmethod
    def HasGump(cls, gumpId: int) -> bool: ...
    @classmethod
    def IsValid(cls, gumpId: int) -> bool: ...
    @classmethod
    def ResetGump(cls) -> None: ...
    @classmethod
    def GetGumpData(cls, gumpid: int) -> GumpData: ...
    @classmethod
    def GetGumpRawLayout(cls, gumpid: int) -> str: ...
    @classmethod
    def GetGumpText(cls, gumpid: int) -> List[str]: ...
    @classmethod
    def GetLine(cls, gumpId: int, line_num: int) -> str: ...
    @classmethod
    def GetLineList(cls, gumpId: int, dataOnly: bool) -> List[str]: ...
    @classmethod
    def LastGumpRawLayout(cls) -> str: ...
    @classmethod
    def LastGumpGetLine(cls, line_num: int) -> str: ...
    @classmethod
    def LastGumpGetLineList(cls) -> List[str]: ...
    @classmethod
    def LastGumpTextExist(cls, text: str) -> bool: ...
    @classmethod
    def LastGumpTextExistByLine(cls, line_num: int, text: str) -> bool: ...
    @classmethod
    def LastGumpTile(cls) -> List[int]: ...
    @classmethod
    def SendAction(cls, gumpid: int, buttonid: int) -> None: ...
    @classmethod
    def SendAdvancedAction(
        cls,
        gumpid: int,
        buttonid: int,
        inSwitches: Sequence[int] | None,
        textlist_id: Sequence[int] | None,
        textlist_str: Sequence[str] | None,
    ) -> None: ...
    @classmethod
    def SendGump(
        cls,
        gumpid: int,
        serial: int,
        x: int,
        y: int,
        gumpDefinition: str,
        gumpStrings: Sequence[str] | None,
    ) -> None: ...
    @classmethod
    def CloseGump(cls, gumpid: int) -> None: ...
    @classmethod
    def WaitForGump(cls, gumpid: int, delay: int) -> bool: ...
    @classmethod
    def AddAlphaRegion(cls, gd: GumpData, x: int, y: int, width: int, height: int) -> None: ...
    @classmethod
    def AddBackground(cls, gd: GumpData, x: int, y: int, width: int, height: int, gumpId: int) -> None: ...
    @classmethod
    def AddButton(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        normalID: int,
        pressedID: int,
        buttonID: int,
        type: int,
        param: int,
    ) -> None: ...
    @classmethod
    def AddCheck(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        inactiveID: int,
        activeID: int,
        initialState: bool,
        switchID: int,
    ) -> None: ...
    @classmethod
    def AddGroup(cls, gd: GumpData, group: int) -> None: ...
    @classmethod
    def AddHtml(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        background: bool,
        scrollbar: bool,
    ) -> None: ...
    @overload
    @classmethod
    def AddHtmlLocalized(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        width: int,
        height: int,
        number: int,
        args: str | None,
        color: int,
        background: bool,
        scrollbar: bool,
    ) -> None: ...
    @overload
    @classmethod
    def AddHtmlLocalized(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        width: int,
        height: int,
        number: int,
        color: int,
        background: bool,
        scrollbar: bool,
    ) -> None: ...
    @overload
    @classmethod
    def AddHtmlLocalized(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        width: int,
        height: int,
        number: int,
        background: bool,
        scrollbar: bool,
    ) -> None: ...
    @classmethod
    def AddImage(cls, gd: GumpData, x: int, y: int, gumpId: int, hue: int = 0) -> None: ...
    @classmethod
    def AddImageTiled(cls, gd: GumpData, x: int, y: int, width: int, height: int, gumpId: int) -> None: ...
    @classmethod
    def AddImageTiledButton(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        normalID: int,
        pressedID: int,
        buttonID: int,
        type: GumpButtonType,
        param: int,
        itemID: int,
        hue: int,
        width: int,
        height: int,
        localizedTooltip: int,
    ) -> None: ...
    @classmethod
    def AddItem(cls, gd: GumpData, x: int, y: int, itemID: int, hue: int) -> None: ...
    @classmethod
    def AddLabel(cls, gd: GumpData, x: int, y: int, hue: int, text: str) -> None: ...
    @classmethod
    def AddLabelCropped(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        width: int,
        height: int,
        hue: int,
        text: str,
    ) -> None: ...
    @classmethod
    def AddPage(cls, gd: GumpData, page: int) -> None: ...
    @classmethod
    def AddRadio(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        inactiveID: int,
        activeID: int,
        initialState: bool,
        switchID: int,
    ) -> None: ...
    @classmethod
    def AddSpriteImage(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        gumpId: int,
        spriteX: int,
        spriteY: int,
        spriteW: int,
        spriteH: int,
    ) -> None: ...
    @classmethod
    def AddTextEntry(
        cls,
        gd: GumpData,
        x: int,
        y: int,
        width: int,
        height: int,
        hue: int,
        entryID: int,
        initialText: str,
    ) -> None: ...
    @overload
    @classmethod
    def AddTooltip(cls, gd: GumpData, text: str) -> None: ...
    @overload
    @classmethod
    def AddTooltip(cls, gd: GumpData, cliloc: str, text: str | None = ...) -> None: ...