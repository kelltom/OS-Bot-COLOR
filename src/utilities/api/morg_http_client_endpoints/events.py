# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = event_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast

T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Camera:
    yaw: int
    pitch: int
    x: int
    y: int
    z: int
    x2: int
    y2: int
    z2: int

    @staticmethod
    def from_dict(obj: Any) -> 'Camera':
        assert isinstance(obj, dict)
        yaw = from_int(obj.get("yaw"))
        pitch = from_int(obj.get("pitch"))
        x = from_int(obj.get("x"))
        y = from_int(obj.get("y"))
        z = from_int(obj.get("z"))
        x2 = from_int(obj.get("x2"))
        y2 = from_int(obj.get("y2"))
        z2 = from_int(obj.get("z2"))
        return Camera(yaw, pitch, x, y, z, x2, y2, z2)

    def to_dict(self) -> dict:
        result: dict = {}
        result["yaw"] = from_int(self.yaw)
        result["pitch"] = from_int(self.pitch)
        result["x"] = from_int(self.x)
        result["y"] = from_int(self.y)
        result["z"] = from_int(self.z)
        result["x2"] = from_int(self.x2)
        result["y2"] = from_int(self.y2)
        result["z2"] = from_int(self.z2)
        return result


@dataclass
class Mouse:
    x: int
    y: int

    @staticmethod
    def from_dict(obj: Any) -> 'Mouse':
        assert isinstance(obj, dict)
        x = from_int(obj.get("x"))
        y = from_int(obj.get("y"))
        return Mouse(x, y)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = from_int(self.x)
        result["y"] = from_int(self.y)
        return result


@dataclass
class WorldPoint:
    x: int
    y: int
    plane: int
    region_id: int
    region_x: int
    region_y: int

    @staticmethod
    def from_dict(obj: Any) -> 'WorldPoint':
        assert isinstance(obj, dict)
        x = from_int(obj.get("x"))
        y = from_int(obj.get("y"))
        plane = from_int(obj.get("plane"))
        region_id = from_int(obj.get("regionID"))
        region_x = from_int(obj.get("regionX"))
        region_y = from_int(obj.get("regionY"))
        return WorldPoint(x, y, plane, region_id, region_x, region_y)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = from_int(self.x)
        result["y"] = from_int(self.y)
        result["plane"] = from_int(self.plane)
        result["regionID"] = from_int(self.region_id)
        result["regionX"] = from_int(self.region_x)
        result["regionY"] = from_int(self.region_y)
        return result


@dataclass
class Event:
    animation: int
    animation_pose: int
    run_energy: int
    game_tick: int
    health: str
    interacting_code: str
    npc_name: str
    npc_health: int
    max_distance: int
    world_point: WorldPoint
    camera: Camera
    mouse: Mouse

    @staticmethod
    def from_dict(obj: Any) -> 'Event':
        assert isinstance(obj, dict)
        animation = from_int(obj.get("animation"))
        animation_pose = from_int(obj.get("animation pose"))
        run_energy = from_int(obj.get("run energy"))
        game_tick = from_int(obj.get("game tick"))
        health = from_str(obj.get("health"))
        interacting_code = from_str(obj.get("interacting code"))
        npc_name = from_str(obj.get("npc name"))
        npc_health = from_int(obj.get("npc health "))
        max_distance = from_int(obj.get("MAX_DISTANCE"))
        world_point = WorldPoint.from_dict(obj.get("worldPoint"))
        camera = Camera.from_dict(obj.get("camera"))
        mouse = Mouse.from_dict(obj.get("mouse"))
        return Event(animation, animation_pose, run_energy, game_tick, health, interacting_code, npc_name, npc_health, max_distance, world_point, camera, mouse)

    def to_dict(self) -> dict:
        result: dict = {}
        result["animation"] = from_int(self.animation)
        result["animation pose"] = from_int(self.animation_pose)
        result["run energy"] = from_int(self.run_energy)
        result["game tick"] = from_int(self.game_tick)
        result["health"] = from_str(self.health)
        result["interacting code"] = from_str(self.interacting_code)
        result["npc name"] = from_str(self.npc_name)
        result["npc health "] = from_int(self.npc_health)
        result["MAX_DISTANCE"] = from_int(self.max_distance)
        result["worldPoint"] = to_class(WorldPoint, self.world_point)
        result["camera"] = to_class(Camera, self.camera)
        result["mouse"] = to_class(Mouse, self.mouse)
        return result


def event_from_dict(s: Any) -> Event:
    return Event.from_dict(s)


def event_to_dict(x: Event) -> Any:
    return to_class(Event, x)
