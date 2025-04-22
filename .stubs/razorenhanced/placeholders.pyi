class Item:
    Name: str
    Serial: int
    ItemID: int
    Color: int
    Contains: list[Item]
    OnGround: bool
    IsContainer: bool
    IsCorpse: bool
    Position: Point3D
    Container: int
    RootContainer: int
    Durability: int
    MaxDurability: int
    def DistanceTo(self, mob: Mobile): ...

class Mobile:
    Name: str
    Serial: int
    Position: Point3D
    def DistanceTo(self, mob: Mobile): ...

class Point2D:
    X: int
    Y: int

class Point3D:
    X: int
    Y: int
    Z: int

class Rectangle: ...
class HotKeyEvent: ...
class Property: ...

class Bitmap:
    Width: int
    Height: int
    def GetPixel(self, x: int, y: int) -> Color: ...

class Color:
    R: int
    G: int
    B: int

class BuffInfo: ...
