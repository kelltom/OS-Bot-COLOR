from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import simplejson as JSON
import time

# Requires the status socket plugin in RuneLite. Install and then click on the settings for it and add port 5000. "http://localhost:5000"
# Global to store the data returned from sockets plugin
player_Data = {}

# Http request handler class to handle receiving data from the status socket
class RLSTATUS(BaseHTTPRequestHandler):
    data_bytes: bytes

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        global player_Data
        self._set_headers()
        self.data_bytes = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()
        player_Data = JSON.loads(self.data_bytes)

class API():

    gameTick = 0.603

    def __init__(self) -> None:
        t_server = Thread(target=self.__RSERVER)
        t_server.daemon = True
        t_server.start()
        print('thread alive:', t_server.is_alive())
    
    def __RSERVER(self, port=5000):
        httpd = HTTPServer(('127.0.0.1', port), RLSTATUS)
        httpd.serve_forever()

    def get_PlayerData(self):
        '''
        Fetches the entire blob of player_Data
        '''
        print(player_Data)
        return player_Data
    
    def get_GameTick(self) -> int:
        '''
        Fetches the game tick from the API.
        '''
        return player_Data["tick"]
    
    def get_PlayerRunEnergy(self) -> int:
        return int(player_Data["runEnergy"])

    # TODO: this fucking function is always false from the API, not a problem with the logic here.... FUCK
    def get_IsPlayerAttacking(self) -> bool:
        return bool(player_Data["attack"]["isAttacking"])

    def get_IsInventoryFull(self) -> bool:
        return len(player_Data["inventory"]) >= 28

    # Pass; returns a full list of the players inventory that can be accessed with [0];
    #  test = API.get_PlayersInventory;
    #  test[0] = first inventory item;
    def get_Inventory(self) -> list:
        return player_Data["inventory"]

    # Pass; will return false until prayer is put on following this logic
    def get_IsPlayerPraying(self) -> bool:
        return bool(player_Data["prayers"])

    #pass; TODO: revisit possibly; returns empty list if no prayers and returns a list of active prayers if active;
    # returns the FULL name of the prayer
    def get_PlayersPrayers(self) -> list:
        return player_Data["prayers"] or {}

    #pass; TODO: revisit possibly; returns empty list if no equipment present or returns a list of all worn equipment
    def get_PlayerEquipment(self) -> list:
        return player_Data["equipment"] or {}

    #pass; returns a list of stats like stab, slash, crush, will return all 0s if nothing is worn
    def get_EquipmentStats(self) -> list:
        return player_Data["equipmentStats"]

    #Pass; returns the animationName, animationId, AnimationIsSpecial, and animationBaseSpellDmg
    def get_AnimationData(self) -> list:
        return player_Data["attack"]["animationName"],player_Data["attack"]["animationId"],player_Data["attack"]["animationIsSpecial"],player_Data["attack"]["animationBaseSpellDmg"]

    #Pass
    def get_AnimationName(self) -> str:
        return player_Data["attack"]["animationName"]

    #Pass
    def get_AnimationID(self) -> int:
        return player_Data["attack"]["animationId"] 


# Test Code
if __name__ == "__main__":
    print("Attempting to start server...")
    api = API()

    while True:
        #api.get_PlayerData()
        time.sleep(api.gameTick)
        #print(api.get_AnimationID())
        print(api.get_AnimationName())
