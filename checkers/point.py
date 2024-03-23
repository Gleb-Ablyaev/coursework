class Point:
    def __init__(self, x: int = -1, y: int = -1):
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def __eq__(self, other: 'Point') -> bool:
        if isinstance(other, Point):
            return (self.x, self.y) == (other.x, other.y)
        return False

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"

    def move(self, dx: int, dy: int) -> None:
        self.__x += dx
        self.__y += dy

    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def clone(self) -> 'Point':
        return Point(self.x, self.y)
