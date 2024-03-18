from enum import Enum, auto

class SideType(Enum):
    WHITE = auto()
    BLACK = auto()

    def opposite(self) -> 'SideType':
        if self == SideType.WHITE:
            return SideType.BLACK
        else:
            return SideType.WHITE

    def __str__(self) -> str:
        return self.name

class CheckerType(Enum):
    NONE = auto()
    WHITE_REGULAR = auto()
    BLACK_REGULAR = auto()
    WHITE_QUEEN = auto()
    BLACK_QUEEN = auto()

    def __str__(self) -> str:
        return self.name