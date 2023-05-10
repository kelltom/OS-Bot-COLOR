from morg_http_client import MorgHTTPSocket
from area import Tile, Area


class Player:
    def __int__(self):
        self.morg_http_client = MorgHTTPSocket()


    def is_player_in_area(self, area: Area):
        player_location = self.morg_http_client.get_player_position()
        player_tile = Tile(player_location[0],player_location[1])
        return area.is_tile_in_area(player_tile)