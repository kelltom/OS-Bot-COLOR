# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = stats_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, Callable, cast

T = TypeVar("T")


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Stat:
    xp_gained: Optional[int] = None
    username: Optional[str] = None
    player_name: Optional[str] = None
    stat: Optional[str] = None
    level: Optional[int] = None
    boosted_level: Optional[int] = None
    xp: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Stat':
        assert isinstance(obj, dict)
        xp_gained = from_union([from_none, lambda x: int(from_str(x))], obj.get("xp gained"))
        username = from_union([from_str, from_none], obj.get("username"))
        player_name = from_union([from_str, from_none], obj.get("player name"))
        stat = from_union([from_str, from_none], obj.get("stat"))
        level = from_union([from_int, from_none], obj.get("level"))
        boosted_level = from_union([from_int, from_none], obj.get("boostedLevel"))
        xp = from_union([from_int, from_none], obj.get("xp"))
        return Stat(xp_gained, username, player_name, stat, level, boosted_level, xp)

    def to_dict(self) -> dict:
        result: dict = {}
        result["xp gained"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.xp_gained)
        result["username"] = from_union([from_str, from_none], self.username)
        result["player name"] = from_union([from_str, from_none], self.player_name)
        result["stat"] = from_union([from_str, from_none], self.stat)
        result["level"] = from_union([from_int, from_none], self.level)
        result["boostedLevel"] = from_union([from_int, from_none], self.boosted_level)
        result["xp"] = from_union([from_int, from_none], self.xp)
        return result


def stats_from_dict(s: Any) -> List[Stat]:
    return from_list(Stat.from_dict, s)