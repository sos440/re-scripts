from typing import Tuple, Any, overload
from placeholders import Point3D


class Target:
    @classmethod
    def PromptGroundTarget(cls, message: str, color: int = 0) -> Point3D: ...
    @classmethod
    def PromptTarget(cls, message: str, color: int = 0) -> int: ...
    @classmethod
    def WaitForTarget(cls, delay: int, noshow: bool = False) -> bool: ...
    @classmethod
    def Last(cls) -> None: ...

    @overload
    @classmethod
    def TargetExecute(cls, x: int, y: int, z: int, staticid: int) -> None: ...
    @overload
    @classmethod
    def TargetExecute(cls, serial: int) -> None: ...