# stubs/player.pyi
from __future__ import annotations

from enum import IntEnum
from typing import Any, Hashable, Iterable, List, Sequence, Set

class Item: ...
class Mobile: ...
class Point3D: ...
class BuffInfo: ...

UOEntity = Hashable | int | Item | Mobile

class SkillStatus(IntEnum):
    UP = 0
    DOWN = 1
    LOCKED = 2

class Direction(str, IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    UP = 4
    DOWN = 5
    LEFT = 6
    RIGHT = 7

class Player:
    """Represents the currently‑logged‑in character."""

    # ────────────────────────────────
    #           ─ Properties ─
    # ────────────────────────────────
    AR: int
    Backpack: Item
    Bank: Item
    Body: int
    Buffs: List[str]
    BuffsInfo: List[BuffInfo]
    ColdResistance: int
    Connected: bool
    Corpses: Set[Item]
    DamageChanceIncrease: int
    DefenseChanceIncrease: int
    Dex: int
    DexterityIncrease: int
    Direction: str
    EnergyResistance: int
    EnhancePotions: int
    Fame: int
    FasterCastRecovery: int
    FasterCasting: int
    Female: bool
    FireResistance: int
    Followers: int
    FollowersMax: int
    Gold: int
    HasPrimarySpecial: bool
    HasSecondarySpecial: bool
    HasSpecial: bool
    HitPointsIncrease: int
    HitPointsRegeneration: int
    Hits: int
    HitsMax: int
    InParty: bool
    Int: int
    IntelligenceIncrease: int
    IsGhost: bool
    Karma: int
    KarmaTitle: str
    LowerManaCost: int
    LowerReagentCost: int
    Luck: int
    Mana: int
    ManaIncrease: int
    ManaMax: int
    ManaRegeneration: int
    Map: int
    MaxWeight: int
    MaximumHitPointsIncrease: int
    MaximumStaminaIncrease: int
    MobileID: int
    Mount: Item
    Name: str
    Notoriety: int  # Byte
    Paralized: bool
    Pets: List[Mobile]
    PoisonResistance: int
    Poisoned: bool
    Position: Point3D
    PrimarySpecial: int
    Quiver: Item
    ReflectPhysicalDamage: int
    SecondarySpecial: int
    Serial: int
    SpellDamageIncrease: int
    Stam: int
    StamMax: int
    StaminaIncrease: int
    StaminaRegeneration: int
    StatCap: int
    StaticMount: int
    Str: int
    StrengthIncrease: int
    SwingSpeedIncrease: int
    Visible: bool
    WarMode: bool
    Weight: int
    YellowHits: bool

    # ────────────────────────────────
    #             ─ Methods ─
    # ────────────────────────────────

    @classmethod
    def Area(cls) -> str: ...
    @classmethod
    def DistanceTo(cls, target: UOEntity) -> int: ...
    @classmethod
    def InRange(cls, entity: UOEntity, range: int) -> bool: ...
    @classmethod
    def InRangeItem(cls, item: Item | int, range: int) -> bool: ...
    @classmethod
    def InRangeMobile(cls, mobile: Mobile | int, range: int) -> bool: ...
    @classmethod
    def PathFindTo(cls, x: int | Point3D, y: int | None = ..., z: int | None = ...) -> None: ...
    @classmethod
    def TrackingArrow(cls, x: int, y: int, display: bool, target: int) -> None: ...

    @classmethod
    def Walk(cls, direction: str | Direction) -> bool: ...
    @classmethod
    def Run(cls, direction: str | Direction) -> bool: ...
    @classmethod
    def ToggleAlwaysRun(cls) -> None: ...
    @classmethod
    def Attack(cls, serial: Mobile | int) -> None: ...
    @classmethod
    def AttackLast(cls) -> None: ...
    @classmethod
    def AttackType(
        cls,
        graphic: Sequence[int] | int,
        rangemax: int,
        selector: str,
        color: Sequence[int] | int | None = ...,
        notoriety: Sequence[int] | int | None = ...,
    ) -> bool: ...
    @classmethod
    def WeaponPrimarySA(cls) -> None: ...
    @classmethod
    def WeaponSecondarySA(cls) -> None: ...
    @classmethod
    def WeaponDisarmSA(cls) -> None: ...
    @classmethod
    def WeaponStunSA(cls) -> None: ...
    @classmethod
    def WeaponClearSA(cls) -> None: ...
    @classmethod
    def SetWarMode(cls, warflag: bool) -> None: ...

    @classmethod
    def EquipItem(cls, serial: Item | int) -> None: ...
    @classmethod
    def EquipLastWeapon(cls) -> None: ...
    @classmethod
    def EquipUO3D(cls, serials: Sequence[int]) -> None: ...
    @classmethod
    def UnEquipItemByLayer(cls, layer: str, wait: bool = ...) -> None: ...
    @classmethod
    def UnEquipUO3D(cls, _layers: Sequence[str]) -> None: ...
    @classmethod
    def CheckLayer(cls, layer: str) -> bool: ...
    @classmethod
    def GetItemOnLayer(cls, layer: str) -> Item | None: ...
    @classmethod
    def SetStaticMount(cls, serial: int) -> None: ...

    @classmethod
    def ChatSay(cls, color: int | str, msg: str) -> None: ...
    @classmethod
    def ChatWhisper(cls, color: int, msg: str) -> None: ...
    @classmethod
    def ChatYell(cls, color: int, msg: str) -> None: ...
    @classmethod
    def ChatGuild(cls, msg: str) -> None: ...
    @classmethod
    def ChatAlliance(cls, msg: str) -> None: ...
    @classmethod
    def ChatChannel(cls, msg: str) -> None: ...
    @classmethod
    def ChatEmote(cls, color: int, msg: str) -> None: ...
    @classmethod
    def HeadMessage(cls, color: int, msg: str) -> None: ...
    @classmethod
    def MapSay(cls, msg: str) -> None: ...
    @classmethod
    def EmoteAction(cls, action: str) -> None: ...

    @classmethod
    def PartyInvite(cls) -> None: ...
    @classmethod
    def PartyAccept(cls, from_serial: int | None = ..., force: bool = ...) -> bool: ...
    @classmethod
    def LeaveParty(cls, force: bool = ...) -> None: ...
    @classmethod
    def KickMember(cls, serial: int) -> None: ...
    @classmethod
    def PartyCanLoot(cls, CanLoot: bool) -> None: ...
    @classmethod
    def ChatParty(cls, msg: str, recepient_serial: int | None = ...) -> None: ...

    @classmethod
    def BuffsExist(cls, buffname: str, okayToGuess: bool = ...) -> bool: ...
    @classmethod
    def BuffTime(cls, buffname: str) -> int: ...
    @classmethod
    def GetBuffInfo(cls, buffName: str, okayToGuess: bool = ...) -> BuffInfo | None: ...

    @classmethod
    def GetRealSkillValue(cls, skillname: str) -> float: ...
    @classmethod
    def GetSkillValue(cls, skillname: str) -> float: ...
    @classmethod
    def GetSkillCap(cls, skillname: str) -> float: ...
    @classmethod
    def GetSkillStatus(cls, skillname: str) -> int: ...
    @classmethod
    def SetSkillStatus(cls, skillname: str, status: int | SkillStatus) -> None: ...
    @classmethod
    def GetStatStatus(cls, statname: str) -> int: ...
    @classmethod
    def SetStatStatus(cls, statname: str, status: int | SkillStatus) -> None: ...
    @classmethod
    def UseSkill(
        cls,
        skillname: str,
        target: Mobile | Item | int | None = ...,
        wait: bool = ...,
    ) -> None: ...
    @classmethod
    def UseSkillOnly(cls, skillname: str, wait: bool = ...) -> None: ...

    @classmethod
    def OpenPaperDoll(cls) -> None: ...
    @classmethod
    def GuildButton(cls) -> None: ...
    @classmethod
    def QuestButton(cls) -> None: ...
    @classmethod
    def Zone(cls) -> str: ...
    @classmethod
    def InvokeVirtue(cls, virtue: str) -> None: ...
    @classmethod
    def Fly(cls, status: bool) -> None: ...
    @classmethod
    def ClearCorpseList(cls) -> None: ...
    @classmethod
    def UpdateKarma(cls) -> bool: ...
    @classmethod
    def SumAttribute(cls, attributename: str) -> float: ...
    @classmethod
    def GetPropStringByIndex(cls, index: int) -> str: ...
    @classmethod
    def GetPropStringList(cls) -> List[str]: ...
    @classmethod
    def GetPropValue(cls, name: str) -> int: ...
