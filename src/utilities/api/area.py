from shapely.geometry import Point, Polygon

class Tile:
    """
    This class is a representation of a tile in an x,y,z coordinate scheme
    """
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x},{self.y},{self.z})"

class Area:
    """
    https://explv.github.io/ can be used to help generate areas
    This Area class is used to create areas within RS. This can be used to tell if a player is within
    the area or not. You can provide a list of coordinates which it will generate a polygon of the enclosed area or
    you can provide it the northwest and southeast tiles, and it will generate a rectangle representing the area
    """
    def __init__(self, *tiles: Tile):
        self.input_tiles = []
        self.computed_tiles = []
        self.polygon = Polygon()
        self.plane = 0

        if len(tiles) == 2:
            t1, t2 = tiles
            l_area = Area(
                Tile(min(t1.x, t2.x), min(t1.y, t2.y), t1.z),
                Tile(max(t1.x, t2.x), min(t1.y, t2.y), t1.z),
                Tile(max(t1.x, t2.x), max(t1.y, t2.y), t2.z),
                Tile(min(t1.x, t2.x), max(t1.y, t2.y), t2.z)
            )
            self.input_tiles = l_area.input_tiles
            self.computed_tiles = l_area.computed_tiles
            self.polygon = l_area.polygon
            self.plane = l_area.plane

        elif isinstance(tiles[0], list):
            tiles = tiles[0]

        self.plane = tiles[0].z

        for tile in tiles:
            self.input_tiles.append(Tile(tile.x, tile.y, tile.z))

        self.compute_area_tiles()

    def compute_area_tiles(self):
        """
        This method is used to generate all the tiles within the given input boundary tiles
        """
        # Create a polygon from the tiles
        poly_tuple = []
        for tile in self.input_tiles:
            poly_tuple += [[tile.x, tile.y]]
        self.polygon = Polygon(poly_tuple)

        # Convert the polygon to all tiles that would be associated with this area
        r = self.polygon.bounds
        width = int(r[2]+1 - r[0])
        height = int(r[3]+1 - r[1])

        c = 0
        l_tiles = [Tile() for _ in range(width * height)]

        for x in range(width):
            for y in range(height):
                _x = r[0] + x
                _y = r[1] + y
                p = Point(_x,_y)
                if self.polygon.contains(p) or self.polygon.intersects(p):
                    l_tiles[c] = Tile(_x, _y, self.plane)
                    c += 1

        # make sure we dont have any negative tiles
        self.computed_tiles = []
        for tile in l_tiles:
            if tile.x > -1 and tile.y > -1:
                self.computed_tiles.append(Tile(tile.x, tile.y, tile.z))

    def is_tile_in_area(self,tile):
        point = Point(tile.x,tile.y)
        return self.polygon.contains(point) or self.polygon.intersects(point)
