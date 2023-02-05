import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image


class OSRSWikiSpriteScraper:
    def __init__(self):
        self.base_url = "https://oldschool.runescape.wiki"
        self.logs = []

    def download_file(self, url):
        response = requests.get(url)
        filename = url.split("/")[-1].split("?")[0]
        open(f"src/images/bot/sprites/{filename.lower()}", "wb").write(response.content)

    # TODO: Adjust this function so it properly utilizes the notify_callback function
    def search_and_download(self, search_param, bank_checkbox, bank_only_checkbox, notify_callback):
        try:
            if "," in search_param:
                search_params = search_param.split(",")
            else:
                search_params = [search_param]
            for param in search_params:
                search_param = param.strip()
                search_param_query = f"w/File:{search_param.capitalize()}.png"
                search_url = urljoin(self.base_url, search_param_query)
                response = requests.get(search_url)
                soup = BeautifulSoup(response.content, "html.parser")
                img = soup.find("img", alt=lambda x: search_param.lower() in x.lower())
                if not img:
                    self.logs.append(f"No image found for: {search_param}.")
                    return
                img_url = urljoin(self.base_url, img["src"])
                if bank_only_checkbox == 1 & bank_checkbox == 1:
                    self.logs.append("Error, you've selected both checkboxes. Please select one")
                    return
                self.download_file(img_url)
                self.logs.append(f"Success: {search_param} saved.")
                if bank_checkbox == 1:
                    img = Image.open(f"src/images/bot/sprites/{search_param}.png")
                    img_cropped = img.crop((0, 10, img.width, 30))
                    img_cropped.save(f"src/images/bot/bank/{search_param}_bank.png")
                if bank_only_checkbox == 1:
                    img = Image.open(f"src/images/bot/sprites/{search_param}.png")
                    img_cropped = img.crop((0, 10, img.width, 30))
                    img_cropped.save(f"src/images/bot/bank/{search_param}_bank.png")
                    os.remove(f"src/images/bot/sprites/{search_param}.png")
        except Exception as e:
            self.logs.append(f"An error occured: \n {e}")
