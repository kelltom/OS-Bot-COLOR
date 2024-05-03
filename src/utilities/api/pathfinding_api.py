import json

import requests


# Example usage
# start_position = (3163, 3474)
# end_position = (2998, 3374)

# pathfinder = Pathfinder()
# print(pathfinder.get_path(start_position, end_position))

API_URL = "https://explv-map.siisiqf.workers.dev/"

ERROR_MESSAGE_MAPPING = {
    "UNMAPPED_REGION": "Unmapped region",
    "BLOCKED": "Tile is blocked",
    "EXCEEDED_SEARCH_LIMIT": "Exceeded search limit",
    "UNREACHABLE": "Unreachable tile",
    "NO_WEB_PATH": "No web path",
    "INVALID_CREDENTIALS": "Invalid credentials",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
    "NO_RESPONSE_FROM_SERVER": "No response from server",
    "UNKNOWN": "Unknown",
}


class Pathfinder:
    def __init__(self):
        pass

    @staticmethod
    def get_path(start, end):
        start_z = start[2] if len(start) > 2 else 0
        end_z = end[2] if len(end) > 2 else 0
        payload = {"start": {"x": start[0], "y": start[1], "z": start_z}, "end": {"x": end[0], "y": end[1], "z": end_z}, "player": {"members": True}}

        headers = {
            "Content-Type": "application/json",
            "Origin": "https://explv.github.io",
        }
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["pathStatus"] != "SUCCESS":
                error_message = ERROR_MESSAGE_MAPPING.get(data["pathStatus"], "Unknown error")
                return {"status": "error", "data": None, "error": error_message}
            else:
                path = data["path"]
                path_positions = [(pos["x"], pos["y"], pos["z"]) for pos in path]
                return {"status": "success", "data": path_positions, "error": None}
        else:
            return {"status": "error", "data": None, "error": "Error occurred while communicating with the server"}
