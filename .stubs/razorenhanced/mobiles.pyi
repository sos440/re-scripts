# stubs/mobiles.pyi
from __future__ import annotations

from datetime import datetime
from typing import Any, List, Sequence, Union

# ---------------------------------------------------------------------------
# Forward declarations – replace these with your own stubs if you already
# have Item / Mobile / Point3D / Property defined elsewhere.
# ---------------------------------------------------------------------------
from placeholders import Item, Mobile, HotKeyEvent, Point2D, Point3D, Rectangle

Serial = int
UOEntity = Union[Serial, Item, Mobile]

# ---------------------------------------------------------------------------
# Filter object used by Mobiles.ApplyFilter
# ---------------------------------------------------------------------------
class MobilesFilter:
    """
    Stores filter options for `Mobiles.ApplyFilter`.
    Numeric flags default to -1 (no restriction), booleans to False.
    Lists support `.add()` / `.extend()` in C#; here we model them as Python lists.
    """

    Blessed: int
    Bodies: List[int]
    CheckIgnoreObject: bool
    CheckLineOfSight: bool
    Enabled: bool
    Female: int
    Friend: int
    Graphics: List[int]
    Hues: List[int]
    IgnorePets: bool
    IsGhost: int
    IsHuman: int
    Name: str
    Notorieties: List[int]
    Paralized: int
    Poisoned: int
    RangeMax: float
    RangeMin: float
    Serials: List[int]
    Warmode: int
    ZLevelMax: float
    ZLevelMin: float

# ---------------------------------------------------------------------------
# Tracking information returned by Mobiles.GetTrackingInfo
# ---------------------------------------------------------------------------
class TrackingInfo:
    """Holds the most recent data returned by the in‑game Tracking cursor."""

    lastUpdate: datetime
    serial: int
    x: int
    y: int

# ---------------------------------------------------------------------------
# Core static class
# ---------------------------------------------------------------------------
class Mobiles:
    """Static helper class for querying and interacting with mobiles."""

    # -------------------- Search / Filtering -------------------------------
    @classmethod
    def ApplyFilter(cls, filter: MobilesFilter) -> List[Mobile]: ...
    @classmethod
    def FindBySerial(cls, serial: Serial) -> Mobile | None: ...
    @classmethod
    def FindMobile(
        cls,
        graphic: Sequence[int] | int,
        notoriety: Sequence[int] | int | None = ...,
        rangemax: int | None = ...,
        selector: str | None = ...,
        highlight: bool = ...,
    ) -> Mobile | None: ...
    @classmethod
    def GetTargetingFilter(cls, target_name: str) -> MobilesFilter: ...

    # -------------------- Property helpers --------------------------------
    @classmethod
    def GetPropStringByIndex(cls, serial: Serial | Mobile, index: int) -> str: ...
    @classmethod
    def GetPropStringList(cls, serial: Serial | Mobile) -> List[str]: ...
    @classmethod
    def GetPropValue(cls, serial: Serial | Mobile, name: str) -> float: ...
    @classmethod
    def WaitForProps(cls, m: Serial | Mobile, delay: int) -> bool: ...
    @classmethod
    def WaitForStats(cls, m: Serial | Mobile, delay: int) -> bool: ...

    # -------------------- Tracking ----------------------------------------
    @classmethod
    def GetTrackingInfo(cls) -> TrackingInfo: ...

    # -------------------- Context menu ------------------------------------
    @classmethod
    def ContextExist(
        cls,
        mob: Serial | Mobile,
        name: str,
        showContext: bool = ...,
    ) -> int: ...

    # -------------------- Interaction & UI --------------------------------
    @classmethod
    def Message(
        cls,
        mobile: Serial | Mobile,
        hue: int,
        message: str,
        wait: bool = ...,
    ) -> None: ...
    @classmethod
    def Select(cls, mobiles: Sequence[Mobile], selector: str) -> Mobile | None: ...
    @classmethod
    def SingleClick(cls, mobile: Serial | Mobile) -> None: ...
    @classmethod
    def UseMobile(cls, mobile: Serial | Mobile) -> None: ...
