from typing import List

class Statics:
    class TileInfo:
        Hue: int
        StaticHue: int
        StaticID: int
        StaticZ: int

    @classmethod
    def GetStaticsTileInfo(cls, x: int, y: int, facet: int) -> List[TileInfo]: ...
