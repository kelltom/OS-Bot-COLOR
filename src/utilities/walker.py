import math
from typing import List
import utilities.api.locations as loc
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.pathfinding_api import Pathfinder


class Walking:

    DEGREESPERYAW: float = 360 / 2048
    TILES_PIXELS = 4

    def __init__(self, runeLiteBot):
        self.bot = runeLiteBot
        self.api_m = MorgHTTPSocket()
        self.run_bool = False

    def update_run_energy(self):
        self.run_energy = self.api_m.get_run_energy()

    def update_position(self):
        self.position = self.api_m.get_player_position()

    def update_camera_angle(self) -> None:
        self.camera_angle = self.api_m.get_camera_position().get("yaw")

    def compute_tiles(self, new_x: int, new_y: int) -> List[float]:
        """Returns the range to click from the minimap center in amount of tiles."""
        # Get live camera data.
        self.update_camera_angle()
        # Account for anticlockwise OSRS minimap.
        degrees = 360 - self.DEGREESPERYAW * self.camera_angle
        # Turn degrees into pi-radians.
        theta = math.radians(degrees)
        # Turn position difference into pixels difference.
        self.update_position()
        x_reg = (new_x - self.position[0]) * self.TILES_PIXELS
        y_reg = (self.position[1] - new_y) * self.TILES_PIXELS
        # Formulas to compute norm of a vector in a rotated coordinate system.
        tiles_x = x_reg * math.cos(theta) + y_reg * math.sin(theta)
        tiles_y = -x_reg * math.sin(theta) + y_reg * math.cos(theta)
        return [round(tiles_x, 1), round(tiles_y, 1)]

    def change_position(self, new_pos: List[int]) -> None:
        """Clicks the minimap to change position"""
        self.update_position()
        tiles = self.compute_tiles(new_pos[0], new_pos[1])
        if tiles != []:
            minimap_center = self.bot.win.minimap.get_center()
            new_x = round(minimap_center[0] + tiles[0] - 1)
            new_y = round(minimap_center[1] + tiles[1] - 1)
            self.bot.mouse.move_to([new_x, new_y], mouseSpeed="fast")
            self.bot.mouse.click()
            while abs(self.position[0] - new_pos[0]) > 5 or abs(self.position[1] - new_pos[1]) > 5:
                self.update_position()
                continue

    def get_target_pos(self, path) -> List[int]:
        """Returns furthest possible coord."""
        self.update_position()
        idx = next(i for i in range(len(path) - 1, -1, -1) if (abs(path[i][0] - self.position[0]) <= 12 and abs(path[i][1] - self.position[1]) <= 12))
        self.bot.log_msg(f"Walking progress: {idx}/{len(path)}")
        new_pos = path[idx]
        return new_pos

    def turn_run_on(self) -> None:
        """Turns on run energy."""
        self.bot.mouse.move_to(self.bot.win.run_orb.random_point(), duration=0.2)
        self.bot.mouse.click()

    def check_if_at_destination(self, area_destination) -> bool:
        """Returns whether the player reached his destination."""
        self.update_position()

        bool_x = self.position[0] in range(area_destination[0] - 1, area_destination[2] + 1)
        bool_y = self.position[1] in range(area_destination[1] - 1, area_destination[3] + 1)

        return bool_x and bool_y

    def handle_running(self) -> None:
        """Turns on run if run energy is higher than 60."""
        # If run is off and run energy is larger than 60, turn on run.
        self.run_energy = self.api_m.get_run_energy()
        if self.run_energy < 5000 or self.run_energy == 10000:
            self.run_bool = False
        if self.run_energy > 6000 and self.run_bool is False:
            self.turn_run_on()
            self.run_bool = True

    def walk(self, path, area_destination) -> None:
        """Walks a path by clicking on the minimap"""
        while True:
            # Turn on running if needed
            self.handle_running()
            # Get live position.
            new_pos = self.get_target_pos(path)
            if self.check_if_at_destination(area_destination):
                self.bot.mouse.move_to(self.bot.win.game_view.get_center(), mouseSpeed="fastest")
                if self.bot.mouseover_text("Walk"):
                    self.bot.mouse.click()
                return True
            self.change_position(new_pos)
            if new_pos == path[-1]:
                while not self.check_if_at_destination(area_destination):
                    self.update_position()
                    continue

    def walk_to(self, end_location):
        current_location = self.api_m.get_player_position()
        new_current_position = [current_location[0], current_location[1]]
        if isinstance(end_location, str):
            end_coordinates = getattr(loc, end_location)
            new_end_coordinates = [end_coordinates[0] - 1, end_coordinates[1] - 1, end_coordinates[0] + 1, end_coordinates[1] + 1]
        if isinstance(end_location, list):
            end_coordinates = end_location
            new_end_coordinates = [end_coordinates[0] - 1, end_coordinates[1] - 1, end_coordinates[0] + 1, end_coordinates[1] + 1]
        if isinstance(end_location, tuple):
            end_coordinates = end_location
            new_end_coordinates = [end_coordinates[0] - 1, end_coordinates[1] - 1, end_coordinates[0] + 1, end_coordinates[1] + 1]
        path = []
        while path == []:
            path = self.api_path(new_current_position, end_coordinates)
            if path == []:
                self.bot.take_break(4, 5)

        self.walk(path, new_end_coordinates)

    def api_path(self, start_coordinates, end_coordinates):
        pathfinder = Pathfinder()
        steps = pathfinder.get_path(start_coordinates, end_coordinates)

        if steps.get("status") == "success":
            processed_data = [[item[0], item[1]] for item in steps.get("data")]
            waypoints = self.add_waypoints(processed_data)
            return waypoints
        return []

    def distance(self, p1, p2):
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def add_waypoints(self, coordinates):
        new_coordinates = [coordinates[0]]  # Start with the first coordinate
        for i in range(len(coordinates) - 1):
            p1 = coordinates[i]
            p2 = coordinates[i + 1]
            d = self.distance(p1, p2)  # Calculate distance between consecutive waypoints

            if d > 10:
                num_waypoints = math.ceil(d / 11)  # Calculate number of waypoints needed
                dx = (p2[0] - p1[0]) / num_waypoints
                dy = (p2[1] - p1[1]) / num_waypoints
                for j in range(1, num_waypoints):
                    new_coordinates.append([round(p1[0] + j * dx), round(p1[1] + j * dy)])  # Add intermediate waypoints
            new_coordinates.append(p2)  # Add the next waypoint

        return new_coordinates
