# stubs/packetlogger.pyi
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Sequence, Tuple, Union

# ---------------------------------------------------------------------------
# Helper definitions
# ---------------------------------------------------------------------------

class PacketPath(str, Enum):
    """Valid paths recognised by PacketLogger.ListenPacketPath()."""

    CLIENT_TO_SERVER = "ClientToServer"
    SERVER_TO_CLIENT = "ServerToClient"
    RAZOR_TO_SERVER = "RazorToServer"  # TODO – not implemented by RE yet
    RAZOR_TO_CLIENT = "RazorToClient"  # TODO – not implemented by RE yet
    PACKET_VIDEO = "PacketVideo"  # TODO – not implemented by RE yet

class FieldType:
    """
    Constants describing how a field is parsed / displayed.
    Use `FieldType.IsValid()` to verify a custom template at run‑time.
    """

    BOOL = "bool"
    DUMP = "dump"
    FIELDS = "fields"
    FIELDSFOR = "fieldsfor"
    HEX = "hex"
    INT = "int"
    MODELID = "modelID"
    PACKETID = "packetID"
    SERIAL = "serial"
    SKIP = "skip"
    SUBPACKET = "subpacket"
    TEXT = "text"
    UINT = "uint"
    UTF8 = "utf8"

    # List of all valid values exposed by the DLL
    VALID_TYPES: List[str]

    @classmethod
    def IsValid(cls, typename: str) -> bool: ...  # → True if recognised

class FieldTemplate:
    """
    Describes a single field inside a packet template.  A field can itself
    contain sub‑fields or reference a sub‑packet (nested PacketTemplate).
    """

    # Required by the template system
    name: str  # Display name
    type: str  # One of FieldType.*
    length: int  # Bytes; ignored for some types
    fields: List["FieldTemplate"]  # Sub‑fields (for 'fields' or 'subpacket')
    subpacket: "PacketTemplate" | None  # Nested packet template (optional)

    # No behaviour – this object is treated as a pure data bag

class PacketTemplate:
    """
    Top‑level template that describes how to decode a packet in the logger.
    """

    packetID: int  # Mandatory
    name: str  # Human‑friendly label
    showHexDump: bool  # If True hex dump is printed
    dynamicLength: bool  # Advanced: dyn‑length packets
    version: int  # Optional template version
    fields: List[FieldTemplate]  # Flat list of top‑level fields

PacketData = Union[bytes, List[int], Sequence[int]]  # accepted by Send* helpers

# ---------------------------------------------------------------------------
# Core static class
# ---------------------------------------------------------------------------

class PacketLogger:
    """
    Razor Enhanced packet logger interface.
    All methods are @classmethods on the C# side; we keep the same shape.
    """

    # ----------------------- global dictionaries --------------------------
    PathToString: Dict[PacketPath, str]
    StringToPath: Dict[str, PacketPath]

    # ------------------------- configuration -----------------------------
    @classmethod
    def AddBlacklist(cls, packetID: int) -> None: ...
    @classmethod
    def AddWhitelist(cls, packetID: int) -> None: ...
    @classmethod
    def DiscardAll(cls, discardAll: bool) -> None: ...
    @classmethod
    def DiscardShowHeader(cls, showHeader: bool) -> None: ...
    @classmethod
    def ListenPacketPath(
        cls,
        packetPath: str | PacketPath | None = ...,
        active: bool | None = ...,
    ) -> List[List[str]]: ...
    @classmethod
    def Reset(cls) -> None: ...

    # ---------------------- template management --------------------------
    @classmethod
    def AddTemplate(cls, packetTemplate: str | PacketTemplate) -> None: ...
    @classmethod
    def RemoveTemplate(cls, packetID: int = ...) -> None: ...

    # ------------------------- I/O helpers -------------------------------
    @classmethod
    def SendToClient(cls, packetData: PacketData) -> None: ...
    @classmethod
    def SendToServer(cls, packetData: PacketData) -> None: ...

    # ------------------------ logger control -----------------------------
    @classmethod
    def SetOutputPath(cls, outputpath: str | None = ...) -> str: ...
    @classmethod
    def Start(cls, outputpath: str | None = ..., appendLogs: bool = False) -> str: ...
    @classmethod
    def Stop(cls) -> str: ...
