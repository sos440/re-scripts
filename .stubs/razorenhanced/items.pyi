# stubs/items.pyi
from __future__ import annotations
from typing import Any, Iterable, List, Sequence, Tuple, Union

from placeholders import Item, Mobile, Property, Bitmap

UOEntity = Union[int, Item, Mobile]

class ItemsFilter:
    """
    Stores filter options for `Items.ApplyFilter`.
    All numeric flags default to -1 (no restriction), booleans to False.
    Lists support `.add()` / `.extend()` on the C# side; here we model them as Python lists.
    """

    CheckIgnoreObject: bool
    Enabled: bool
    Graphics: List[int]
    Hues: List[int]
    IsContainer: int
    IsCorpse: int
    IsDoor: int
    Layers: List[str]
    Movable: int
    Multi: int
    Name: str
    OnGround: int
    RangeMax: float
    RangeMin: float
    Serials: List[int]
    ZRangeMax: float
    ZRangeMin: float

# ---------------------------------------------------------------------------
# Core static class
# ---------------------------------------------------------------------------
class Items:
    """Static helper class for querying and manipulating in‑game items."""

    # --- Search / filter helpers ------------------------------------------------
    @classmethod
    def Filter(cls) -> ItemsFilter: ...
    @classmethod
    def ApplyFilter(cls, filter: ItemsFilter) -> List[Item]: ...
    @classmethod
    def FindAllByID(
        cls,
        itemids: Union[int, Sequence[int]],
        color: int = ...,
        container: int | Item = ...,
        range: int | None = ...,
        considerIgnoreList: bool = ...,
    ) -> List[Item]: ...
    @classmethod
    def FindByID(
        cls,
        itemid: int,
        color: int = ...,
        container: int | Item = ...,
        recursive: Union[bool, int] = ...,
        considerIgnoreList: bool = ...,
    ) -> Item | None: ...
    @classmethod
    def FindByName(
        cls,
        itemName: str,
        color: int = ...,
        container: int | Item = ...,
        range: int | None = ...,
        considerIgnoreList: bool = ...,
    ) -> Item | None: ...
    @classmethod
    def FindBySerial(cls, serial: int) -> Item | None: ...

    # --- Counters ---------------------------------------------------------------
    @classmethod
    def BackpackCount(cls, itemid: int, color: int = ...) -> int: ...
    @classmethod
    def ContainerCount(
        cls,
        container: int | Item,
        itemid: int,
        color: int = ...,
        recursive: bool = ...,
    ) -> int: ...

    # --- Movement & interaction -------------------------------------------------
    @classmethod
    def Lift(cls, item: Item, amount: int = ...) -> None: ...
    @classmethod
    def DropFromHand(cls, item: Item, container: Item) -> None: ...
    @classmethod
    def Move(
        cls,
        source: int | Item,
        destination: Union[int, Item, Mobile],
        amount: int = ...,
        x: int | None = ...,
        y: int | None = ...,
    ) -> None: ...
    @classmethod
    def MoveOnGround(
        cls,
        source: int | Item,
        amount: int = ...,
        x: int = ...,
        y: int = ...,
        z: int = ...,
    ) -> None: ...
    @classmethod
    def DropItemGroundSelf(cls, item: int | Item, amount: int = ...) -> None: ...
    @classmethod
    def Close(cls, serial: int | Item) -> None: ...
    @classmethod
    def OpenAt(cls, serial: int | Item, x: int, y: int) -> None: ...
    @classmethod
    def OpenContainerAt(cls, bag: Item, x: int, y: int) -> None: ...
    @classmethod
    def WaitForContents(cls, bag: int | Item, delay: int) -> bool: ...
    @classmethod
    def WaitForProps(cls, itemserial: int | Item, delay: int) -> None: ...

    # --- Item usage -------------------------------------------------------------
    @classmethod
    def UseItem(
        cls,
        itemSerial: int | Item,
        targetSerial: UOEntity | None = ...,
        wait: bool = ...,
    ) -> None: ...
    @classmethod
    def UseItemByID(cls, itemid: int, color: int = ...) -> bool: ...

    # --- Cosmetic helpers -------------------------------------------------------
    @classmethod
    def ChangeDyeingTubColor(cls, dyes: Item, dyeingTub: Item, color: int) -> None: ...
    @classmethod
    def SetColor(cls, serial: int | Item, color: int = ...) -> None: ...
    @classmethod
    def Hide(cls, serial: int | Item) -> None: ...
    @classmethod
    def Message(cls, item: int | Item, hue: int, message: str) -> None: ...

    # --- Graphics & properties --------------------------------------------------
    @classmethod
    def GetImage(cls, itemID: int, hue: int = ...) -> Bitmap: ...
    @classmethod
    def GetPropStringByIndex(cls, serial: int | Item, index: int) -> str: ...
    @classmethod
    def GetPropStringList(cls, serial: int | Item) -> List[str]: ...
    @classmethod
    def GetPropValue(cls, serial: int | Item, name: str) -> float: ...
    @classmethod
    def GetPropValueString(cls, serial: int | Item, name: str) -> str: ...
    @classmethod
    def GetProperties(cls, itemserial: int | Item, delay: int) -> List[Property]: ...
    @classmethod
    def GetWeaponAbility(cls, itemId: int) -> Tuple[str, str]: ...

    # --- Context menu -----------------------------------------------------------
    @classmethod
    def ContextExist(cls, serial: int | Item, name: str) -> int: ...
    @classmethod
    def UseContextMenu(
        cls,
        serial: int | Item,
        choice: Union[str, int],
        delay: int,
    ) -> bool: ...

    # --- Misc helpers -----------------------------------------------------------
    @classmethod
    def IgnoreTypes(cls, itemIdList: Sequence[int]) -> None: ...
    @classmethod
    def Select(cls, items: Iterable[Item], selector: str) -> Item | None: ...
    @classmethod
    def SingleClick(cls, item: int | Item) -> None: ...
    @classmethod
    def SetSharedValue(cls, name: str, value: Any) -> None: ...  # exposed via Misc, but handy